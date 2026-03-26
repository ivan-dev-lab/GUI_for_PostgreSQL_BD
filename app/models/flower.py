from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin


class Flower(Base, IdMixin, TimestampMixin):
    __tablename__ = "flowers"
    __table_args__ = (
        CheckConstraint("trim(name) <> ''", name="ck_flowers_name_not_blank"),
        CheckConstraint("trim(unit) <> ''", name="ck_flowers_unit_not_blank"),
        CheckConstraint("purchase_price > 0", name="ck_flowers_purchase_price_positive"),
        CheckConstraint("min_batch > 0", name="ck_flowers_min_batch_positive"),
    )

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    variety: Mapped[str | None] = mapped_column(String(255))
    color: Mapped[str | None] = mapped_column(String(100))
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    min_batch: Mapped[int] = mapped_column(Integer, nullable=False)
    season: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    supplier = relationship("Supplier", back_populates="flowers")
    purchase_orders = relationship("PurchaseOrder", back_populates="flower")
