from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db.session import get_session_factory, session_scope
from app.models.supplier import Supplier
from app.repositories.supplier_repository import SupplierRepository
from app.utils.validators import ValidationError, optional_text, require_text, validate_email


class SupplierService:
    def __init__(self, session_factory: sessionmaker | None = None):
        self.session_factory = session_factory or get_session_factory()

    @staticmethod
    def _to_dict(entity: Supplier) -> dict:
        return {
            "id": entity.id,
            "name": entity.name,
            "contact_person": entity.contact_person,
            "phone": entity.phone,
            "email": entity.email,
            "address": entity.address,
            "inn": entity.inn,
            "is_active": entity.is_active,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def list_suppliers(self, search: str | None = None, is_active: bool | None = None) -> list[dict]:
        with session_scope(self.session_factory) as session:
            items = SupplierRepository(session).list(search=search, is_active=is_active)
            return [self._to_dict(item) for item in items]

    def get_supplier(self, supplier_id: int) -> dict:
        with session_scope(self.session_factory) as session:
            entity = SupplierRepository(session).get(supplier_id)
            if entity is None:
                raise ValidationError("Поставщик не найден.")
            return self._to_dict(entity)

    def get_supplier_choices(self, active_only: bool = False) -> list[dict]:
        return self.list_suppliers(is_active=True if active_only else None)

    def create_supplier(self, payload: dict) -> dict:
        with session_scope(self.session_factory) as session:
            entity = Supplier(
                name=require_text(payload.get("name"), "Наименование"),
                contact_person=optional_text(payload.get("contact_person")),
                phone=optional_text(payload.get("phone")),
                email=validate_email(payload.get("email"), "Email"),
                address=optional_text(payload.get("address")),
                inn=optional_text(payload.get("inn")),
                is_active=bool(payload.get("is_active", True)),
            )
            SupplierRepository(session).add(entity)
            return self._to_dict(entity)

    def update_supplier(self, supplier_id: int, payload: dict) -> dict:
        with session_scope(self.session_factory) as session:
            repository = SupplierRepository(session)
            entity = repository.get(supplier_id)
            if entity is None:
                raise ValidationError("Поставщик не найден.")

            entity.name = require_text(payload.get("name"), "Наименование")
            entity.contact_person = optional_text(payload.get("contact_person"))
            entity.phone = optional_text(payload.get("phone"))
            entity.email = validate_email(payload.get("email"), "Email")
            entity.address = optional_text(payload.get("address"))
            entity.inn = optional_text(payload.get("inn"))
            entity.is_active = bool(payload.get("is_active", True))
            session.flush()
            return self._to_dict(entity)

    def delete_supplier(self, supplier_id: int) -> None:
        try:
            with session_scope(self.session_factory) as session:
                repository = SupplierRepository(session)
                entity = repository.get(supplier_id)
                if entity is None:
                    raise ValidationError("Поставщик не найден.")
                repository.delete(entity)
        except IntegrityError as error:
            raise ValidationError(
                "Нельзя удалить поставщика, пока на него ссылаются позиции цветов."
            ) from error
