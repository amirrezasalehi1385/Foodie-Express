from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.order import Order, OrderStatus
from models.order_items import OrderItem
from models.cancelation_reason import CancellationReason
from models.user import User, UserRole

from repositories.cart_item_repository import CartItemRepository
from repositories.order_repository import OrderRepository
from repositories.order_item_repository import OrderItemRepository
from repositories.food_repository import FoodRepository
from repositories.restaurant_repository import RestaurantRepository
from repositories.delivery_repository import DeliveryRepository

from services.cart_service import CartService
from services.address_service import AddressService
from services.discount_service import DiscountService
from services.restaurant_service import RestaurantService
from services.delivery_service import DeliveryService
from services.order_status_history_service import OrderStatusHistoryService

class OrderService:
    def __init__(self, db: Session):
        self.cart_item_repository = CartItemRepository(db)
        self.order_repository = OrderRepository(db)
        self.order_item_repository = OrderItemRepository(db)
        self.food_repository = FoodRepository(db)

        self.cart_service = CartService(db)
        self.address_service = AddressService(db)
        self.restaruant_service = RestaurantService(db)
        self.restaurant_repository = RestaurantRepository(db)
        self.discount_service = DiscountService(db)
        self.delivery_repository = DeliveryRepository(db)
        self.delivery_service = DeliveryService(db)
        self.order_status_history_repository = OrderStatusHistoryService(db)

    def create_order(
        self,
        user_id: int,
        delivery_address_id: int,
        discount_code: str | None = None,
    ):
        cart = self.cart_service.get_cart(user_id)

        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found",
            )

        if cart.restaurant_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart does not belong to a restaurant",
            )

        restaurant_id = cart.restaurant_id

        cart_items = self.cart_item_repository.get_by_cart_id(
            cart_id=cart.id
        )

        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty",
            )

        address = self.address_service.get_address_by_id(
            address_id=delivery_address_id,
            user_id=user_id,
        )

        if address is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery address not found",
            )

        subtotal = Decimal("0.00")
        foods = []

        for cart_item in cart_items:
            food = self.food_repository.get_by_id(
                cart_item.food_id
            )

            if food is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Food {cart_item.food_id} not found",
                )

            if food.restaurant_id != restaurant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Food does not belong to this restaurant",
                )

            if not food.is_available:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Food '{food.name}' is not available",
                )

            item_total = food.price * cart_item.quantity
            subtotal += item_total

            foods.append(
                {
                    "cart_item": cart_item,
                    "food": food,
                }
            )

        discount = None
        discount_amount = Decimal("0.00")

        if discount_code:
            discount, discount_amount = self.discount_service.validate_and_calculate(
                code=discount_code,
                user_id=user_id,
                restaurant_id=restaurant_id,
                subtotal=subtotal,
            )

        

        delivery_fee = Decimal("0.00")
        tax_amount = Decimal("0.00")

        total_amount = (
            subtotal
            - discount_amount
            + delivery_fee
            + tax_amount
        )

        order = self.order_repository.create(
            Order(
                user_id=user_id,
                restaurant_id=restaurant_id,
                delivery_address_id=delivery_address_id,
                subtotal=subtotal,
                discount_amount=discount_amount,
                discount_id=discount.id if discount else None,
                delivery_fee=delivery_fee,
                tax_amount=tax_amount,
                total_amount=total_amount,
                status=OrderStatus.PENDING_PAYMENT,
            )
        )

        for item in foods:
            cart_item = item["cart_item"]
            food = item["food"]

            order_item = OrderItem(
                order_id=order.id,
                food_id=food.id,
                quantity=cart_item.quantity,
                unit_price=food.price,
                total_price=food.price * cart_item.quantity,
            )

            self.order_item_repository.create(
                order_item=order_item
            )
        if discount is not None:
            self.discount_service.record_usage(
                discount_id=discount.id,
                user_id=user_id,
                order_id=order.id,
                amount_saved=discount_amount,
            )

        self.cart_service.clear_cart(user_id=user_id)

        self.order_status_history_repository.create(
            order_id=order.id,
            status=OrderStatus.PENDING_PAYMENT,
            changed_by=user_id,
        )

        return order

    def get_order_by_id(
            self,
            user_id: int,
            order_id: int,
    ):
        order = self.order_repository.get_by_id(order_id=order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this order",
            )

        return order

    def get_user_orders(
            self,
            user_id: int,
            page: int = 1,
            limit: int = 10,
    ):
        offset = (page - 1) * limit

        orders = self.order_repository.get_by_user_id(
            user_id=user_id,
            offset=offset,
            limit=limit,
        )

        return orders

    def get_order_items(
            self,
            user_id: int,
            order_id: int,
            page: int = 1,
            limit: int = 10,
    ):
        order = self.order_repository.get_by_id(order_id=order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this order",
            )

        offset = (page - 1) * limit

        return self.order_item_repository.get_by_order_id(
            order_id=order_id,
            offset=offset,
            limit=limit,
        )

    def cancel_order(
        self,
        user_id: int,
        order_id: int,
        reason: CancellationReason,
        note: str | None = None,
    ):
        order = self.get_order_by_id(
            user_id=user_id,
            order_id=order_id,
        )

        if order.status not in {
            OrderStatus.PENDING_PAYMENT,
            OrderStatus.PAID,
            OrderStatus.ACCEPTED,
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order cannot be cancelled",
            )

        order.status = OrderStatus.CANCELLED

        order.cancellation_reason = reason.value

        if note:
            order.cancellation_reason += f": {note}"

        self.order_repository.update(order)

        return order
    def get_restaurant_orders(
            self,
            restaurant_id: int,
            owner_id: int,
            page: int = 1,
            limit: int = 10,
    ):
        restaurant = self.restaurant_repository.get_by_id_and_owner(
            restaurant_id=restaurant_id,
            owner_id=owner_id,
        )

        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this restaurant",
            )

        offset = (page - 1) * limit

        return self.order_repository.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )
        
    def change_order_status(
            self,
            current_user: User,
            order_id: int,
            new_status: OrderStatus,
    ):
        order = self.order_repository.get_by_id(order_id=order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        if current_user.role == UserRole.CUSTOMER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this order",
            )

        if current_user.role == UserRole.RESTAURANT_OWNER:
            restaruant = self.restaruant_service.get_restaurant_by_id(restaurant_id=order.restaurant_id)

            if restaruant.owner_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this order",
                )

        delivery = None

        if current_user.role == UserRole.DELIVERY_MAN:
            delivery = self.delivery_repository.get_by_order_id(order_id=order.id)

            if not delivery or delivery.delivery_man_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this order",
                )

        if current_user.role == UserRole.RESTAURANT_OWNER:
            allowed_transitions = {
                OrderStatus.PAID: {OrderStatus.ACCEPTED},
                OrderStatus.ACCEPTED: {OrderStatus.PREPARING},
                OrderStatus.PREPARING: {OrderStatus.READY},
            }

        elif current_user.role == UserRole.DELIVERY_MAN:
            allowed_transitions = {
                OrderStatus.ASSIGNED: {OrderStatus.DELIVERING},
                OrderStatus.DELIVERING: {OrderStatus.DELIVERED},
            }

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to change order status",
            )

        if new_status not in allowed_transitions.get(order.status, set()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change order status from {order.status} to {new_status}",
            )

        order.status = new_status

        self.order_repository.update(order)

        self.order_status_history_repository.create(
            order_id=order.id,
            status=new_status,
            changed_by=current_user.id,
        )

        if delivery is not None:
            if new_status == OrderStatus.DELIVERING:
                self.delivery_service.mark_picked_up(delivery)
            elif new_status == OrderStatus.DELIVERED:
                self.delivery_service.mark_delivered(delivery)

        return order

    def get_available_orders(
        self,
        current_user: User,
        page: int = 1,
        limit: int = 10,
    ):
        offset = (page - 1) * limit

        return self.order_repository.get_available_for_delivery(
            offset=offset,
            limit=limit,
        )