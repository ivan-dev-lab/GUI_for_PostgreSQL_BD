from __future__ import annotations

from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db.session import get_session_factory, session_scope
from app.models.flower import Flower
from app.repositories.flower_repository import FlowerRepository
from app.repositories.supplier_repository import SupplierRepository
from app.utils.validators import (
    ValidationError,
    optional_text,
    parse_positive_decimal,
    parse_positive_int,
    require_text,
)


class FlowerService:
    def __init__(self, session_factory: sessionmaker | None = None):
        self.session_factory = session_factory or get_session_factory()

    @staticmethod
    def _to_dict(entity: Flower) -> dict:
        return {
            "id": entity.id,
            "supplier_id": entity.supplier_id,
            "supplier_name": entity.supplier.name if entity.supplier else "",
            "name": entity.name,
            "variety": entity.variety,
            "color": entity.color,
            "unit": entity.unit,
            "purchase_price": entity.purchase_price,
            "min_batch": entity.min_batch,
            "season": entity.season,
            "notes": entity.notes,
            "is_active": entity.is_active,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def list_flowers(
        self,
        search: str | None = None,
        supplier_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[dict]:
        with session_scope(self.session_factory) as session:
            items = FlowerRepository(session).list(
                search=search,
                supplier_id=supplier_id,
                is_active=is_active,
            )
            return [self._to_dict(item) for item in items]

    def get_flower(self, flower_id: int) -> dict:
        with session_scope(self.session_factory) as session:
            entity = FlowerRepository(session).get(flower_id)
            if entity is None:
                raise ValidationError("Позиция не найдена.")
            return self._to_dict(entity)

    def get_flower_choices(self, active_only: bool = False) -> list[dict]:
        return self.list_flowers(is_active=True if active_only else None)

    def create_flower(self, payload: dict) -> dict:
        with session_scope(self.session_factory) as session:
            supplier_id = int(payload.get("supplier_id") or 0)
            supplier = SupplierRepository(session).get(supplier_id)
            if supplier is None:
                raise ValidationError("Выберите поставщика из списка.")

            entity = Flower(
                supplier_id=supplier_id,
                name=require_text(payload.get("name"), "Название"),
                variety=optional_text(payload.get("variety")),
                color=optional_text(payload.get("color")),
                unit=require_text(payload.get("unit"), "Единица измерения"),
                purchase_price=parse_positive_decimal(payload.get("purchase_price"), "Закупочная цена"),
                min_batch=parse_positive_int(payload.get("min_batch"), "Минимальная партия"),
                season=optional_text(payload.get("season")),
                notes=optional_text(payload.get("notes")),
                is_active=bool(payload.get("is_active", True)),
            )
            session.add(entity)
            session.flush()
            return self._to_dict(entity)

    def update_flower(self, flower_id: int, payload: dict) -> dict:
        with session_scope(self.session_factory) as session:
            repository = FlowerRepository(session)
            entity = repository.get(flower_id)
            if entity is None:
                raise ValidationError("Позиция не найдена.")

            supplier_id = int(payload.get("supplier_id") or 0)
            supplier = SupplierRepository(session).get(supplier_id)
            if supplier is None:
                raise ValidationError("Выберите поставщика из списка.")

            entity.supplier_id = supplier_id
            entity.name = require_text(payload.get("name"), "Название")
            entity.variety = optional_text(payload.get("variety"))
            entity.color = optional_text(payload.get("color"))
            entity.unit = require_text(payload.get("unit"), "Единица измерения")
            entity.purchase_price = parse_positive_decimal(payload.get("purchase_price"), "Закупочная цена")
            entity.min_batch = parse_positive_int(payload.get("min_batch"), "Минимальная партия")
            entity.season = optional_text(payload.get("season"))
            entity.notes = optional_text(payload.get("notes"))
            entity.is_active = bool(payload.get("is_active", True))
            session.flush()
            return self._to_dict(entity)

    def delete_flower(self, flower_id: int) -> None:
        try:
            with session_scope(self.session_factory) as session:
                repository = FlowerRepository(session)
                entity = repository.get(flower_id)
                if entity is None:
                    raise ValidationError("Позиция не найдена.")
                repository.delete(entity)
        except IntegrityError as error:
            raise ValidationError(
                "Нельзя удалить цветок, пока на него ссылаются заказы."
            ) from error

    def get_purchase_price(self, flower_id: int) -> Decimal:
        with session_scope(self.session_factory) as session:
            entity = FlowerRepository(session).get(flower_id)
            if entity is None:
                raise ValidationError("Позиция не найдена.")
            return entity.purchase_price
