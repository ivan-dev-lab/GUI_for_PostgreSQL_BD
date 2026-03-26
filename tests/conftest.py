from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.base import Base
from app.db.session import create_engine_and_session_factory
from app.models import Contract, Flower, PurchaseOrder, Supplier  # noqa: F401
from app.services.contract_service import ContractService
from app.services.flower_service import FlowerService
from app.services.purchase_order_service import PurchaseOrderService
from app.services.supplier_service import SupplierService


@pytest.fixture
def session_factory(tmp_path):
    database_path = tmp_path / "test_app.sqlite"
    engine, factory = create_engine_and_session_factory(f"sqlite:///{database_path}")
    Base.metadata.create_all(bind=engine)
    yield factory
    engine.dispose()


@pytest.fixture
def services(session_factory):
    return {
        "supplier": SupplierService(session_factory),
        "flower": FlowerService(session_factory),
        "contract": ContractService(session_factory),
        "order": PurchaseOrderService(session_factory),
    }


@pytest.fixture
def sample_entities(services):
    supplier = services["supplier"].create_supplier(
        {
            "name": "ООО Тест Поставка",
            "contact_person": "Иван Тестов",
            "phone": "+7 (900) 000-00-00",
            "email": "supplier@test.local",
            "address": "г. Екатеринбург, ул. Тестовая, 1",
            "inn": "6677000000",
            "is_active": True,
        }
    )
    flower = services["flower"].create_flower(
        {
            "supplier_id": supplier["id"],
            "name": "Петуния",
            "variety": "Каскад",
            "color": "Красный",
            "unit": "шт",
            "purchase_price": "125.50",
            "min_batch": "10",
            "season": "лето",
            "notes": "",
            "is_active": True,
        }
    )
    contract = services["contract"].create_contract(
        {
            "contract_number": "TEST-001",
            "contract_date": "2026-03-01",
            "customer_name": "ООО Тест Заказчик",
            "customer_phone": "+7 (901) 111-11-11",
            "customer_email": "customer@test.local",
            "object_name": "Тестовый объект",
            "object_address": "г. Екатеринбург, ул. Демонстрационная, 2",
            "start_date": "2026-04-01",
            "end_date": "2026-05-01",
            "price_coefficient": "1.25",
            "status": "active",
            "notes": "",
        }
    )
    return {
        "supplier": supplier,
        "flower": flower,
        "contract": contract,
    }
