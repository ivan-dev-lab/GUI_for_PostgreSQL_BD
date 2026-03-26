from __future__ import annotations

from sqlalchemy import select

from app.models.supplier import Supplier
from app.repositories.base_repository import BaseRepository


class SupplierRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Supplier)

    def list(self, search: str | None = None, is_active: bool | None = None) -> list[Supplier]:
        stmt = select(Supplier).order_by(Supplier.name)
        if search:
            stmt = stmt.where(Supplier.name.ilike(f"%{search.strip()}%"))
        if is_active is not None:
            stmt = stmt.where(Supplier.is_active.is_(is_active))
        return list(self.session.scalars(stmt))
