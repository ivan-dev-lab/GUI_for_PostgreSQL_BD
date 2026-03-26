from __future__ import annotations

from sqlalchemy import Boolean, CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin


class Supplier(Base, IdMixin, TimestampMixin):
    __tablename__ = "suppliers"
    __table_args__ = (
        CheckConstraint("trim(name) <> ''", name="ck_suppliers_name_not_blank"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    inn: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    flowers = relationship("Flower", back_populates="supplier")
