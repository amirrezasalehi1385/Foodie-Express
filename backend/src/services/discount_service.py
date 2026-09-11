from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User, UserRole
from models.discount import Discount, DiscountType
from decimal import Decimal
from repositories.discount_repository import DiscountRepository
from repositories.discount_usage_repository import DiscountUsageRepository
from repositories.restaurant_repository import RestaurantRepository
from repositories.user_repository import UserRepository
from repositories.order_repository import OrderRepository

class DiscountService:
    def __init__(self, db: Session):
        self.discount_repository = DiscountRepository(db)
        self.discount_usage_repository = DiscountUsageRepository(db)
        self.restaurant_repository = RestaurantRepository(db)
        self.user_repository = UserRepository(db)
        self.order_repository = OrderRepository(db)
        

    def validate_and_calculate(
        self,
        code: str,
        user_id: int,
        restaurant_id: int,
        subtotal: Decimal,
    ) -> tuple[Discount, Decimal]:

        discount = self.discount_repository.get_by_code_for_update(
            code=code
        )

        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount code not found",
            )

        restaurant = self.restaurant_repository.get_by_id(
            id=restaurant_id
        )

        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        if discount.restaurant_id is not None and discount.restaurant_id != restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code is not valid for this restaurant",
            )

        if not discount.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This discount code is no longer active",
            )

        now = datetime.now(timezone.utc)

        if discount.valid_from is not None and now < discount.valid_from:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This discount code is not yet valid",
            )

        if discount.valid_until is not None and now > discount.valid_until:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This discount code has expired",
            )

        total_usage_count = self.discount_usage_repository.get_total_usage_count(
            discount_id=discount.id,
        )

        if discount.usage_limit is not None and total_usage_count >= discount.usage_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code usage limit reached",
            )

        usage_count = self.discount_usage_repository.get_user_usage_count(
            discount_id=discount.id,
            user_id=user_id,
        )

        if discount.usage_limit_per_user is not None and usage_count >= discount.usage_limit_per_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already used this discount code the maximum number of times allowed",
            )

        if discount.min_order_amount is not None and discount.min_order_amount > subtotal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order amount must be at least {discount.min_order_amount} to use this discount code",
            )

        if discount.type == DiscountType.PERCENTAGE:
            discount_amount = subtotal * (discount.value / Decimal(100))
        else:
            if discount.value > subtotal:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Fixed discount value cannot exceed the order subtotal",
                )
            discount_amount = discount.value

        if discount.max_discount_amount is not None:
            discount_amount = min(discount_amount, discount.max_discount_amount)

        discount_amount = min(discount_amount, subtotal)

        return discount, discount_amount
        
    def record_usage(
            self,
            discount_id: int, 
            user_id: int, 
            order_id: int, 
            amount_saved: Decimal
    ): 
        self.discount_usage_repository.create(
            discount_id=discount_id,
            user_id=user_id,
            order_id=order_id,
            amount_saved=amount_saved,
        )
    def create_discount(
        self,
        current_user: User,
        code: str,
        type: DiscountType,
        value: Decimal,
        restaurant_id: int | None,
        min_order_amount: Decimal | None,
        max_discount_amount: Decimal | None,
        usage_limit: int | None,
        usage_limit_per_user: int | None,
        valid_from: datetime | None,
        valid_until: datetime | None,
    ) -> Discount:

        if current_user.role != UserRole.ADMIN and current_user.role != UserRole.RESTAURANT_OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to create discounts",
            )

        if current_user.role == UserRole.RESTAURANT_OWNER and restaurant_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Restaurant owners must scope discounts to their own restaurant",
            )

        if restaurant_id is not None:
            restaurant = self.restaurant_repository.get_by_id(restaurant_id)

            if not restaurant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurant not found",
                )

            if current_user.role == UserRole.RESTAURANT_OWNER and restaurant.owner_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to create discounts for this restaurant",
                )

        if type == DiscountType.PERCENTAGE and not (0 < value <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Percentage discount value must be between 0 and 100",
            )

        if type == DiscountType.FIXED_AMOUNT and value <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fixed discount amount must be greater than 0",
            )

        existing = self.discount_repository.get_by_code(code=code)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A discount with this code already exists",
            )

        discount = self.discount_repository.create(
            code=code,
            type=type,
            value=value,
            restaurant_id=restaurant_id,
            min_order_amount=min_order_amount,
            max_discount_amount=max_discount_amount,
            usage_limit=usage_limit,
            usage_limit_per_user=usage_limit_per_user,
            valid_from=valid_from,
            valid_until=valid_until,
        )

        if current_user.role == UserRole.ADMIN:
            self.admin_action_log_repository.create(
                admin_id=current_user.id,
                action="CREATE_DISCOUNT",
                target_type="discount",
                target_id=discount.id,
                description=f"Created discount code '{code}' ({type.value}, value={value})",
            )

        return discount


    def get_discount(
        self,
        current_user: User,
        discount_id: int,
    ) -> Discount:
        discount = self.discount_repository.get_by_id(
            discount_id=discount_id,
        )

        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount not found",
            )

        if current_user.role == UserRole.ADMIN:
            return discount

        if current_user.role == UserRole.RESTAURANT_OWNER:
            if discount.restaurant_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this discount",
                )

            restaurant = self.restaurant_repository.get_by_id(discount.restaurant_id)

            if not restaurant or restaurant.owner_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this discount",
                )

            return discount

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this discount",
        )


    def get_all_discounts(
        self,
        current_user: User,
        page: int = 1,
        limit: int = 10,
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this resource",
            )

        offset = (page - 1) * limit

        return self.discount_repository.get_all(
            offset=offset,
            limit=limit,
        )


    def get_restaurant_discounts(
        self,
        current_user: User,
        restaurant_id: int,
        page: int = 1,
        limit: int = 10,
    ):
        restaurant = self.restaurant_repository.get_by_id(restaurant_id)

        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        if current_user.role != UserRole.ADMIN and restaurant.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this restaurant's discounts",
            )

        offset = (page - 1) * limit

        return self.discount_repository.get_by_restaurant_id(
            restaurant_id=restaurant_id,
            offset=offset,
            limit=limit,
        )


    def deactivate_discount(
        self,
        current_user: User,
        discount_id: int,
    ) -> Discount:
        discount = self.discount_repository.get_by_id(
            discount_id=discount_id,
        )

        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount not found",
            )

        if current_user.role == UserRole.ADMIN:
            pass
        elif current_user.role == UserRole.RESTAURANT_OWNER:
            if discount.restaurant_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to deactivate this discount",
                )

            restaurant = self.restaurant_repository.get_by_id(discount.restaurant_id)

            if not restaurant or restaurant.owner_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to deactivate this discount",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to deactivate this discount",
            )

        discount.is_active = False

        self.discount_repository.update(discount)

        if current_user.role == UserRole.ADMIN:
            self.admin_action_log_repository.create(
                admin_id=current_user.id,
                action="DEACTIVATE_DISCOUNT",
                target_type="discount",
                target_id=discount.id,
                description=f"Deactivated discount code '{discount.code}'",
            )

        return discount

    