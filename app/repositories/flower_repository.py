from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.models.flower import Flower
from app.repositories.base_repository import BaseRepository


class FlowerRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Flower)

    def list(
        self,
        search: str | None = None,
        supplier_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[Flower]:
        stmt = select(Flower).options(selectinload(Flower.supplier)).order_by(Flower.name, Flower.variety)
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(or_(Flower.name.ilike(pattern), Flower.variety.ilike(pattern)))
        if supplier_id:
            stmt = stmt.where(Flower.supplier_id == supplier_id)
        if is_active is not None:
            stmt = stmt.where(Flower.is_active.is_(is_active))
        return list(self.session.scalars(stmt))
