from __future__ import annotations

from sqlalchemy import func, select

from app.models.contract import Contract
from app.repositories.base_repository import BaseRepository


class ContractRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Contract)

    def list(
        self,
        number_search: str | None = None,
        customer_search: str | None = None,
        status: str | None = None,
    ) -> list[Contract]:
        stmt = select(Contract).order_by(Contract.contract_date.desc(), Contract.contract_number)
        if number_search:
            stmt = stmt.where(Contract.contract_number.ilike(f"%{number_search.strip()}%"))
        if customer_search:
            stmt = stmt.where(Contract.customer_name.ilike(f"%{customer_search.strip()}%"))
        if status:
            stmt = stmt.where(Contract.status == status)
        return list(self.session.scalars(stmt))

    def exists_by_number(self, contract_number: str, exclude_id: int | None = None) -> bool:
        stmt = select(func.count()).select_from(Contract).where(Contract.contract_number == contract_number)
        if exclude_id is not None:
            stmt = stmt.where(Contract.id != exclude_id)
        return bool(self.session.scalar(stmt))
