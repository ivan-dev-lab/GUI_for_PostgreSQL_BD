from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import sessionmaker

from app.constants import ORDER_STATUS_LABELS
from app.db.session import get_session_factory, session_scope
from app.models.purchase_order import PurchaseOrder
from app.repositories.contract_repository import ContractRepository
from app.repositories.flower_repository import FlowerRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.utils.validators import ValidationError, optional_text, parse_date, parse_positive_decimal, validate_date_range


class PurchaseOrderService:
    def __init__(self, session_factory: sessionmaker | None = None):
        self.session_factory = session_factory or get_session_factory()

    @staticmethod
    def _calculate_line_amount(quantity: Decimal, unit_price_snapshot: Decimal) -> Decimal:
        return (quantity * unit_price_snapshot).quantize(Decimal("0.01"))

    @staticmethod
    def _to_dict(entity: PurchaseOrder) -> dict:
        supplier_name = entity.flower.supplier.name if entity.flower and entity.flower.supplier else ""
        final_amount = (
            entity.line_amount * entity.contract.price_coefficient
            if entity.contract and entity.contract.price_coefficient is not None
            else entity.line_amount
        )
        return {
            "id": entity.id,
            "contract_id": entity.contract_id,
            "contract_number": entity.contract.contract_number if entity.contract else "",
            "customer_name": entity.contract.customer_name if entity.contract else "",
            "object_name": entity.contract.object_name if entity.contract else "",
            "flower_id": entity.flower_id,
            "flower_name": entity.flower.name if entity.flower else "",
            "flower_variety": entity.flower.variety if entity.flower else "",
            "supplier_name": supplier_name,
            "quantity": entity.quantity,
            "unit_price_snapshot": entity.unit_price_snapshot,
            "line_amount": entity.line_amount,
            "final_amount": final_amount.quantize(Decimal("0.01")) if final_amount else Decimal("0.00"),
            "order_date": entity.order_date,
            "planned_delivery_date": entity.planned_delivery_date,
            "actual_delivery_date": entity.actual_delivery_date,
            "status": entity.status,
            "status_label": ORDER_STATUS_LABELS.get(entity.status, entity.status),
            "notes": entity.notes,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def list_purchase_orders(
        self,
        search: str | None = None,
        contract_id: int | None = None,
        status: str | None = None,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
    ) -> list[dict]:
        parsed_from = parse_date(date_from, "Дата с") if isinstance(date_from, str) else date_from
        parsed_to = parse_date(date_to, "Дата по") if isinstance(date_to, str) else date_to
        validate_date_range(parsed_from, parsed_to, "Дата с", "Дата по")

        with session_scope(self.session_factory) as session:
            items = PurchaseOrderRepository(session).list(
                search=search,
                contract_id=contract_id,
                status=status,
                date_from=parsed_from,
                date_to=parsed_to,
            )
            return [self._to_dict(item) for item in items]

    def get_purchase_order(self, order_id: int) -> dict:
        with session_scope(self.session_factory) as session:
            entity = PurchaseOrderRepository(session).get(order_id)
            if entity is None:
                raise ValidationError("Заказ не найден.")
            return self._to_dict(entity)

    def _validate_common(self, session, payload: dict, current_entity: PurchaseOrder | None = None):
        contract_id = int(payload.get("contract_id") or 0)
        flower_id = int(payload.get("flower_id") or 0)
        contract = ContractRepository(session).get(contract_id)
        if contract is None:
            raise ValidationError("Выберите договор из списка.")
        flower = FlowerRepository(session).get(flower_id)
        if flower is None:
            raise ValidationError("Выберите позицию цветка из списка.")

        quantity = parse_positive_decimal(payload.get("quantity"), "Количество")
        order_date_value = parse_date(payload.get("order_date"), "Дата заказа")
        planned_delivery_date = parse_date(payload.get("planned_delivery_date"), "Плановая дата поставки")
        actual_delivery_date = parse_date(payload.get("actual_delivery_date"), "Фактическая дата поставки")
        if order_date_value and actual_delivery_date and actual_delivery_date < order_date_value:
            raise ValidationError("Фактическая дата поставки не может быть раньше даты заказа.")

        status = payload.get("status") or "created"
        if status not in ORDER_STATUS_LABELS:
            raise ValidationError("Выберите корректный статус заказа.")

        if current_entity is None or current_entity.flower_id != flower_id:
            unit_price_snapshot = flower.purchase_price
        else:
            unit_price_snapshot = current_entity.unit_price_snapshot

        return (
            contract_id,
            flower_id,
            quantity,
            order_date_value,
            planned_delivery_date,
            actual_delivery_date,
            status,
            unit_price_snapshot,
        )

    def create_purchase_order(self, payload: dict) -> dict:
        with session_scope(self.session_factory) as session:
            (
                contract_id,
                flower_id,
                quantity,
                order_date_value,
                planned_delivery_date,
                actual_delivery_date,
                status,
                unit_price_snapshot,
            ) = self._validate_common(session, payload)

            entity = PurchaseOrder(
                contract_id=contract_id,
                flower_id=flower_id,
                quantity=quantity,
                unit_price_snapshot=unit_price_snapshot,
                line_amount=self._calculate_line_amount(quantity, unit_price_snapshot),
                order_date=order_date_value,
                planned_delivery_date=planned_delivery_date,
                actual_delivery_date=actual_delivery_date,
                status=status,
                notes=optional_text(payload.get("notes")),
            )
            session.add(entity)
            session.flush()
            return self._to_dict(entity)

    def update_purchase_order(self, order_id: int, payload: dict) -> dict:
        with session_scope(self.session_factory) as session:
            repository = PurchaseOrderRepository(session)
            entity = repository.get(order_id)
            if entity is None:
                raise ValidationError("Заказ не найден.")

            (
                contract_id,
                flower_id,
                quantity,
                order_date_value,
                planned_delivery_date,
                actual_delivery_date,
                status,
                unit_price_snapshot,
            ) = self._validate_common(session, payload, current_entity=entity)

            entity.contract_id = contract_id
            entity.flower_id = flower_id
            entity.quantity = quantity
            entity.unit_price_snapshot = unit_price_snapshot
            entity.line_amount = self._calculate_line_amount(quantity, unit_price_snapshot)
            entity.order_date = order_date_value
            entity.planned_delivery_date = planned_delivery_date
            entity.actual_delivery_date = actual_delivery_date
            entity.status = status
            entity.notes = optional_text(payload.get("notes"))
            session.flush()
            return self._to_dict(entity)

    def delete_purchase_order(self, order_id: int) -> None:
        with session_scope(self.session_factory) as session:
            repository = PurchaseOrderRepository(session)
            entity = repository.get(order_id)
            if entity is None:
                raise ValidationError("Заказ не найден.")
            repository.delete(entity)

    def get_calculated_amount(self, quantity: str, flower_id: int) -> dict:
        with session_scope(self.session_factory) as session:
            flower = FlowerRepository(session).get(flower_id)
            if flower is None:
                raise ValidationError("Позиция не найдена.")
            quantity_decimal = parse_positive_decimal(quantity, "Количество")
            line_amount = self._calculate_line_amount(quantity_decimal, flower.purchase_price)
            return {
                "unit_price_snapshot": flower.purchase_price,
                "line_amount": line_amount,
            }
