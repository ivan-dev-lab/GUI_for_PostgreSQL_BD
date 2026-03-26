from __future__ import annotations

from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from app.models.contract import Contract
from app.models.flower import Flower
from app.models.purchase_order import PurchaseOrder
from app.repositories.base_repository import BaseRepository


class PurchaseOrderRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, PurchaseOrder)

    def list(
        self,
        search: str | None = None,
        contract_id: int | None = None,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[PurchaseOrder]:
        stmt = (
            select(PurchaseOrder)
            .join(PurchaseOrder.contract)
            .join(PurchaseOrder.flower)
            .options(
                joinedload(PurchaseOrder.contract),
                joinedload(PurchaseOrder.flower).joinedload(Flower.supplier),
            )
            .order_by(PurchaseOrder.order_date.desc(), PurchaseOrder.id.desc())
        )
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Contract.contract_number.ilike(pattern),
                    Contract.customer_name.ilike(pattern),
                    Contract.object_name.ilike(pattern),
                    Flower.name.ilike(pattern),
                    Flower.variety.ilike(pattern),
                )
            )
        if contract_id:
            stmt = stmt.where(PurchaseOrder.contract_id == contract_id)
        if status:
            stmt = stmt.where(PurchaseOrder.status == status)
        if date_from:
            stmt = stmt.where(PurchaseOrder.order_date >= date_from)
        if date_to:
            stmt = stmt.where(PurchaseOrder.order_date <= date_to)
        return list(self.session.scalars(stmt).unique())
