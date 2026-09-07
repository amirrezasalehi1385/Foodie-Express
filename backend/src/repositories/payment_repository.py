from sqlalchemy.orm import Session

from models.payment import Payment, PaymentStatus, PaymentMethod


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        order_id: int,
        amount,
        method: PaymentMethod = PaymentMethod.CARD,
    ):
        payment = Payment(
            order_id=order_id,
            amount=amount,
            method=method,
        )

        self.db.add(payment)
        self.db.flush()

        return payment

    def get_by_id(
        self,
        payment_id: int,
    ):
        return (
            self.db.query(Payment)
            .filter(
                Payment.id == payment_id
            )
            .first()
        )

    def get_by_token(
        self,
        payment_token: str,
    ):
        return (
            self.db.query(Payment)
            .filter(
                Payment.payment_token == payment_token
            )
            .first()
        )

    def get_by_order_id(
        self,
        order_id: int,
    ):
        return (
            self.db.query(Payment)
            .filter(
                Payment.order_id == order_id
            )
            .first()
        )

    def update(self, payment: Payment):
        self.db.add(payment)
        self.db.flush()

        return payment

    def get_all(
        self,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(Payment)
            .order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )