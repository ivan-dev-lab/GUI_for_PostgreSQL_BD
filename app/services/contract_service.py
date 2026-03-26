from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.constants import CONTRACT_STATUS_LABELS
from app.db.session import get_session_factory, session_scope
from app.models.contract import Contract
from app.repositories.contract_repository import ContractRepository
from app.utils.validators import (
    ValidationError,
    optional_text,
    parse_date,
    parse_positive_decimal,
    require_text,
    validate_date_range,
    validate_email,
)


class ContractService:
    def __init__(self, session_factory: sessionmaker | None = None):
        self.session_factory = session_factory or get_session_factory()

    @staticmethod
    def _to_dict(entity: Contract) -> dict:
        return {
            "id": entity.id,
            "contract_number": entity.contract_number,
            "contract_date": entity.contract_date,
            "customer_name": entity.customer_name,
            "customer_phone": entity.customer_phone,
            "customer_email": entity.customer_email,
            "object_name": entity.object_name,
            "object_address": entity.object_address,
            "start_date": entity.start_date,
            "end_date": entity.end_date,
            "price_coefficient": entity.price_coefficient,
            "status": entity.status,
            "status_label": CONTRACT_STATUS_LABELS.get(entity.status, entity.status),
            "notes": entity.notes,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def list_contracts(
        self,
        number_search: str | None = None,
        customer_search: str | None = None,
        status: str | None = None,
    ) -> list[dict]:
        with session_scope(self.session_factory) as session:
            items = ContractRepository(session).list(
                number_search=number_search,
                customer_search=customer_search,
                status=status,
            )
            return [self._to_dict(item) for item in items]

    def get_contract(self, contract_id: int) -> dict:
        with session_scope(self.session_factory) as session:
            entity = ContractRepository(session).get(contract_id)
            if entity is None:
                raise ValidationError("Договор не найден.")
            return self._to_dict(entity)

    def get_contract_choices(self) -> list[dict]:
        return self.list_contracts()

    def create_contract(self, payload: dict) -> dict:
        with session_scope(self.session_factory) as session:
            repository = ContractRepository(session)
            contract_number = require_text(payload.get("contract_number"), "Номер договора")
            if repository.exists_by_number(contract_number):
                raise ValidationError("Договор с таким номером уже существует.")

            start_date = parse_date(payload.get("start_date"), "Дата начала")
            end_date = parse_date(payload.get("end_date"), "Дата окончания")
            validate_date_range(start_date, end_date, "Дата начала", "Дата окончания")

            status = payload.get("status") or "draft"
            if status not in CONTRACT_STATUS_LABELS:
                raise ValidationError("Выберите корректный статус договора.")

            entity = Contract(
                contract_number=contract_number,
                contract_date=parse_date(payload.get("contract_date"), "Дата договора"),
                customer_name=require_text(payload.get("customer_name"), "Заказчик"),
                customer_phone=optional_text(payload.get("customer_phone")),
                customer_email=validate_email(payload.get("customer_email"), "Email заказчика"),
                object_name=require_text(payload.get("object_name"), "Объект"),
                object_address=require_text(payload.get("object_address"), "Адрес объекта"),
                start_date=start_date,
                end_date=end_date,
                price_coefficient=parse_positive_decimal(payload.get("price_coefficient"), "Коэффициент"),
                status=status,
                notes=optional_text(payload.get("notes")),
            )
            repository.add(entity)
            return self._to_dict(entity)

    def update_contract(self, contract_id: int, payload: dict) -> dict:
        with session_scope(self.session_factory) as session:
            repository = ContractRepository(session)
            entity = repository.get(contract_id)
            if entity is None:
                raise ValidationError("Договор не найден.")

            contract_number = require_text(payload.get("contract_number"), "Номер договора")
            if repository.exists_by_number(contract_number, exclude_id=contract_id):
                raise ValidationError("Договор с таким номером уже существует.")

            start_date = parse_date(payload.get("start_date"), "Дата начала")
            end_date = parse_date(payload.get("end_date"), "Дата окончания")
            validate_date_range(start_date, end_date, "Дата начала", "Дата окончания")

            status = payload.get("status") or "draft"
            if status not in CONTRACT_STATUS_LABELS:
                raise ValidationError("Выберите корректный статус договора.")

            entity.contract_number = contract_number
            entity.contract_date = parse_date(payload.get("contract_date"), "Дата договора")
            entity.customer_name = require_text(payload.get("customer_name"), "Заказчик")
            entity.customer_phone = optional_text(payload.get("customer_phone"))
            entity.customer_email = validate_email(payload.get("customer_email"), "Email заказчика")
            entity.object_name = require_text(payload.get("object_name"), "Объект")
            entity.object_address = require_text(payload.get("object_address"), "Адрес объекта")
            entity.start_date = start_date
            entity.end_date = end_date
            entity.price_coefficient = parse_positive_decimal(payload.get("price_coefficient"), "Коэффициент")
            entity.status = status
            entity.notes = optional_text(payload.get("notes"))
            session.flush()
            return self._to_dict(entity)

    def delete_contract(self, contract_id: int) -> None:
        try:
            with session_scope(self.session_factory) as session:
                repository = ContractRepository(session)
                entity = repository.get(contract_id)
                if entity is None:
                    raise ValidationError("Договор не найден.")
                repository.delete(entity)
        except IntegrityError as error:
            raise ValidationError(
                "Нельзя удалить договор, пока по нему существуют заказы."
            ) from error
