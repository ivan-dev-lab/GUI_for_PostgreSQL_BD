from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.db.session import get_session_factory, session_scope
from app.models.contract import Contract
from app.models.flower import Flower
from app.models.purchase_order import PurchaseOrder
from app.models.supplier import Supplier
from app.utils.formatters import contract_status_label, format_date, format_decimal, order_status_label
from app.utils.validators import parse_date, validate_date_range


@dataclass
class ReportResult:
    title: str
    headers: list[str]
    rows: list[list[str]]


class ReportService:
    def __init__(self, session_factory: sessionmaker | None = None):
        self.session_factory = session_factory or get_session_factory()

    def generate_report(
        self,
        report_key: str,
        date_from: str | date | None = None,
        date_to: str | date | None = None,
    ) -> ReportResult:
        parsed_from = parse_date(date_from, "Дата с") if isinstance(date_from, str) else date_from
        parsed_to = parse_date(date_to, "Дата по") if isinstance(date_to, str) else date_to
        validate_date_range(parsed_from, parsed_to, "Дата с", "Дата по")

        if report_key == "orders_period":
            return self._orders_period(parsed_from, parsed_to)
        if report_key == "contracts_finance":
            return self._contracts_finance(parsed_from, parsed_to)
        if report_key == "suppliers_summary":
            return self._suppliers_summary(parsed_from, parsed_to)
        if report_key == "overdue_deliveries":
            return self._overdue_deliveries(parsed_from, parsed_to)
        raise ValueError(f"Unsupported report key: {report_key}")

    def _orders_period(self, date_from: date | None, date_to: date | None) -> ReportResult:
        with session_scope(self.session_factory) as session:
            final_amount = (PurchaseOrder.line_amount * Contract.price_coefficient).label("final_amount")
            stmt = (
                select(
                    PurchaseOrder.id,
                    Contract.contract_number,
                    Contract.customer_name,
                    Contract.object_name,
                    Supplier.name.label("supplier_name"),
                    Flower.name,
                    Flower.variety,
                    PurchaseOrder.quantity,
                    PurchaseOrder.unit_price_snapshot,
                    PurchaseOrder.line_amount,
                    Contract.price_coefficient,
                    final_amount,
                    PurchaseOrder.order_date,
                    PurchaseOrder.planned_delivery_date,
                    PurchaseOrder.actual_delivery_date,
                    PurchaseOrder.status,
                )
                .join(Contract, PurchaseOrder.contract_id == Contract.id)
                .join(Flower, PurchaseOrder.flower_id == Flower.id)
                .join(Supplier, Flower.supplier_id == Supplier.id)
                .order_by(PurchaseOrder.order_date.desc(), PurchaseOrder.id.desc())
            )
            if date_from:
                stmt = stmt.where(PurchaseOrder.order_date >= date_from)
            if date_to:
                stmt = stmt.where(PurchaseOrder.order_date <= date_to)
            records = session.execute(stmt).all()

        headers = [
            "№ заказа",
            "№ договора",
            "Заказчик",
            "Объект",
            "Поставщик",
            "Цветок",
            "Количество",
            "Цена",
            "Сумма без коэффициента",
            "Коэффициент",
            "Итоговая сумма",
            "Дата заказа",
            "Плановая поставка",
            "Фактическая поставка",
            "Статус",
        ]
        rows = [
            [
                str(record.id),
                record.contract_number,
                record.customer_name,
                record.object_name,
                record.supplier_name,
                f"{record.name} ({record.variety})" if record.variety else record.name,
                format_decimal(record.quantity),
                format_decimal(record.unit_price_snapshot),
                format_decimal(record.line_amount),
                format_decimal(record.price_coefficient),
                format_decimal(record.final_amount),
                format_date(record.order_date),
                format_date(record.planned_delivery_date),
                format_date(record.actual_delivery_date),
                order_status_label(record.status),
            ]
            for record in records
        ]
        return ReportResult("Заказы за период", headers, rows)

    def _contracts_finance(self, date_from: date | None, date_to: date | None) -> ReportResult:
        with session_scope(self.session_factory) as session:
            total_amount = func.coalesce(func.sum(PurchaseOrder.line_amount), 0).label("total_amount")
            stmt = (
                select(
                    Contract.contract_number,
                    Contract.customer_name,
                    Contract.object_name,
                    func.count(PurchaseOrder.id).label("orders_count"),
                    total_amount,
                    Contract.price_coefficient,
                    (total_amount * Contract.price_coefficient).label("final_amount"),
                    Contract.status,
                    Contract.contract_date,
                )
                .outerjoin(PurchaseOrder, PurchaseOrder.contract_id == Contract.id)
                .group_by(Contract.id)
                .order_by(Contract.contract_date.desc(), Contract.contract_number)
            )
            if date_from:
                stmt = stmt.where(Contract.contract_date >= date_from)
            if date_to:
                stmt = stmt.where(Contract.contract_date <= date_to)
            records = session.execute(stmt).all()

        headers = [
            "№ договора",
            "Дата договора",
            "Заказчик",
            "Объект",
            "Количество заказов",
            "Сумма без коэффициента",
            "Коэффициент",
            "Итоговая сумма",
            "Статус",
        ]
        rows = [
            [
                record.contract_number,
                format_date(record.contract_date),
                record.customer_name,
                record.object_name,
                str(record.orders_count),
                format_decimal(record.total_amount),
                format_decimal(record.price_coefficient),
                format_decimal(record.final_amount),
                contract_status_label(record.status),
            ]
            for record in records
        ]
        return ReportResult("Финансовый отчет по договорам", headers, rows)

    def _suppliers_summary(self, date_from: date | None, date_to: date | None) -> ReportResult:
        with session_scope(self.session_factory) as session:
            stmt = (
                select(
                    Supplier.name,
                    func.count(PurchaseOrder.id).label("orders_count"),
                    func.coalesce(func.sum(PurchaseOrder.quantity), 0).label("total_quantity"),
                    func.coalesce(func.sum(PurchaseOrder.line_amount), 0).label("total_amount"),
                )
                .join(Flower, Flower.supplier_id == Supplier.id)
                .join(PurchaseOrder, PurchaseOrder.flower_id == Flower.id)
                .group_by(Supplier.id)
                .order_by(Supplier.name)
            )
            if date_from:
                stmt = stmt.where(PurchaseOrder.order_date >= date_from)
            if date_to:
                stmt = stmt.where(PurchaseOrder.order_date <= date_to)
            records = session.execute(stmt).all()

        headers = [
            "Поставщик",
            "Количество заказов",
            "Общее количество материала",
            "Общая сумма закупок",
        ]
        rows = [
            [
                record.name,
                str(record.orders_count),
                format_decimal(record.total_quantity),
                format_decimal(record.total_amount),
            ]
            for record in records
        ]
        return ReportResult("Отчет по поставщикам", headers, rows)

    def _overdue_deliveries(self, date_from: date | None, date_to: date | None) -> ReportResult:
        today = date.today()
        with session_scope(self.session_factory) as session:
            stmt = (
                select(
                    PurchaseOrder.id,
                    Contract.contract_number,
                    Contract.object_name,
                    Supplier.name.label("supplier_name"),
                    Flower.name,
                    Flower.variety,
                    PurchaseOrder.quantity,
                    PurchaseOrder.order_date,
                    PurchaseOrder.planned_delivery_date,
                    PurchaseOrder.status,
                )
                .join(Contract, PurchaseOrder.contract_id == Contract.id)
                .join(Flower, PurchaseOrder.flower_id == Flower.id)
                .join(Supplier, Flower.supplier_id == Supplier.id)
                .where(PurchaseOrder.planned_delivery_date.is_not(None))
                .where(PurchaseOrder.planned_delivery_date < today)
                .where(PurchaseOrder.actual_delivery_date.is_(None))
                .where(PurchaseOrder.status.not_in(["delivered", "cancelled"]))
                .order_by(PurchaseOrder.planned_delivery_date, PurchaseOrder.id)
            )
            if date_from:
                stmt = stmt.where(PurchaseOrder.planned_delivery_date >= date_from)
            if date_to:
                stmt = stmt.where(PurchaseOrder.planned_delivery_date <= date_to)
            records = session.execute(stmt).all()

        headers = [
            "№ заказа",
            "№ договора",
            "Объект",
            "Поставщик",
            "Цветок",
            "Количество",
            "Дата заказа",
            "Плановая поставка",
            "Статус",
        ]
        rows = [
            [
                str(record.id),
                record.contract_number,
                record.object_name,
                record.supplier_name,
                f"{record.name} ({record.variety})" if record.variety else record.name,
                format_decimal(record.quantity),
                format_date(record.order_date),
                format_date(record.planned_delivery_date),
                order_status_label(record.status),
            ]
            for record in records
        ]
        return ReportResult("Просроченные поставки", headers, rows)
