from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

APP_TITLE = "ИС учета покупки посадочного материала"
DATE_FORMAT = "%Y-%m-%d"
DECIMAL_QUANT = Decimal("0.01")

ROLE_LABELS = {
    "purchase_manager": "Менеджер по закупкам",
    "sales_manager": "Менеджер по продажам",
    "warehouse_manager": "Заведующий складом",
    "analyst": "Аналитик / Бухгалтер",
}

CONTRACT_STATUS_LABELS = {
    "draft": "Черновик",
    "active": "Активен",
    "completed": "Завершен",
    "cancelled": "Отменен",
}

ORDER_STATUS_LABELS = {
    "created": "Создан",
    "approved": "Согласован",
    "ordered": "Заказан",
    "delivered": "Поставлен",
    "cancelled": "Отменен",
}

CONTRACT_STATUS_OPTIONS = list(CONTRACT_STATUS_LABELS.items())
ORDER_STATUS_OPTIONS = list(ORDER_STATUS_LABELS.items())

ACTIVE_FILTER_OPTIONS = {
    "Все": None,
    "Только активные": True,
    "Только неактивные": False,
}

PERMISSIONS = {
    "purchase_manager": {
        "suppliers": "crud",
        "flowers": "crud",
        "contracts": "none",
        "purchase_orders": "read",
        "reports": "none",
    },
    "sales_manager": {
        "suppliers": "read",
        "flowers": "read",
        "contracts": "crud",
        "purchase_orders": "crud",
        "reports": "none",
    },
    "warehouse_manager": {
        "suppliers": "none",
        "flowers": "read",
        "contracts": "read",
        "purchase_orders": "read",
        "reports": "none",
    },
    "analyst": {
        "suppliers": "read",
        "flowers": "read",
        "contracts": "read",
        "purchase_orders": "read",
        "reports": "read",
    },
}

SECTION_TITLES = {
    "suppliers": "Поставщики",
    "flowers": "Цветы",
    "contracts": "Договоры",
    "purchase_orders": "Заказы",
    "reports": "Отчеты",
}


@dataclass(frozen=True)
class DemoUser:
    username: str
    password: str
    role: str
    display_name: str


DEFAULT_USERS = {
    "purchase_manager": DemoUser(
        username="purchase_manager",
        password="purchase123",
        role="purchase_manager",
        display_name="Ольга Соколова",
    ),
    "sales_manager": DemoUser(
        username="sales_manager",
        password="sales123",
        role="sales_manager",
        display_name="Андрей Крылов",
    ),
    "warehouse_manager": DemoUser(
        username="warehouse_manager",
        password="warehouse123",
        role="warehouse_manager",
        display_name="Марина Логинова",
    ),
    "analyst": DemoUser(
        username="analyst",
        password="analyst123",
        role="analyst",
        display_name="Ирина Демидова",
    ),
}

REPORT_OPTIONS = {
    "orders_period": "Заказы за период",
    "contracts_finance": "Финансовый отчет по договорам",
    "suppliers_summary": "Отчет по поставщикам",
    "overdue_deliveries": "Просроченные поставки",
}
