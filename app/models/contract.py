from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin


class Contract(Base, IdMixin, TimestampMixin):
    __tablename__ = "contracts"
    __table_args__ = (
        CheckConstraint("trim(contract_number) <> ''", name="ck_contracts_number_not_blank"),
        CheckConstraint("trim(customer_name) <> ''", name="ck_contracts_customer_not_blank"),
        CheckConstraint("trim(object_name) <> ''", name="ck_contracts_object_not_blank"),
        CheckConstraint("trim(object_address) <> ''", name="ck_contracts_address_not_blank"),
        CheckConstraint("price_coefficient > 0", name="ck_contracts_price_coefficient_positive"),
        CheckConstraint(
            "status IN ('draft', 'active', 'completed', 'cancelled')",
            name="ck_contracts_status_valid",
        ),
    )

    contract_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    contract_date: Mapped[date | None] = mapped_column(Date)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str | None] = mapped_column(String(50))
    customer_email: Mapped[str | None] = mapped_column(String(255))
    object_name: Mapped[str] = mapped_column(String(255), nullable=False)
    object_address: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    price_coefficient: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        default=Decimal("1.00"),
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    notes: Mapped[str | None] = mapped_column(Text)

    purchase_orders = relationship("PurchaseOrder", back_populates="contract")
