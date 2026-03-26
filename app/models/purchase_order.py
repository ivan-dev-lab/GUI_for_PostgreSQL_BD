from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin


class PurchaseOrder(Base, IdMixin, TimestampMixin):
    __tablename__ = "purchase_orders"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_purchase_orders_quantity_positive"),
        CheckConstraint(
            "unit_price_snapshot > 0",
            name="ck_purchase_orders_unit_price_snapshot_positive",
        ),
        CheckConstraint("line_amount > 0", name="ck_purchase_orders_line_amount_positive"),
        CheckConstraint(
            "status IN ('created', 'approved', 'ordered', 'delivered', 'cancelled')",
            name="ck_purchase_orders_status_valid",
        ),
    )

    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    flower_id: Mapped[int] = mapped_column(
        ForeignKey("flowers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    order_date: Mapped[date | None] = mapped_column(Date)
    planned_delivery_date: Mapped[date | None] = mapped_column(Date)
    actual_delivery_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="created")
    notes: Mapped[str | None] = mapped_column(Text)

    contract = relationship("Contract", back_populates="purchase_orders")
    flower = relationship("Flower", back_populates="purchase_orders")
