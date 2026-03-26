from __future__ import annotations


def test_crud_smoke_for_all_entities(services, sample_entities):
    supplier = sample_entities["supplier"]
    flower = sample_entities["flower"]
    contract = sample_entities["contract"]

    updated_supplier = services["supplier"].update_supplier(
        supplier["id"],
        {
            "name": "ООО Тест Поставка Обновлено",
            "contact_person": supplier["contact_person"],
            "phone": supplier["phone"],
            "email": supplier["email"],
            "address": supplier["address"],
            "inn": supplier["inn"],
            "is_active": True,
        },
    )
    assert updated_supplier["name"] == "ООО Тест Поставка Обновлено"

    updated_flower = services["flower"].update_flower(
        flower["id"],
        {
            "supplier_id": supplier["id"],
            "name": "Петуния",
            "variety": "Каскад",
            "color": "Белый",
            "unit": "шт",
            "purchase_price": "130.00",
            "min_batch": "12",
            "season": "лето",
            "notes": "Обновлено",
            "is_active": True,
        },
    )
    assert str(updated_flower["purchase_price"]) == "130.00"

    updated_contract = services["contract"].update_contract(
        contract["id"],
        {
            "contract_number": "TEST-001",
            "contract_date": "2026-03-02",
            "customer_name": "ООО Тест Заказчик",
            "customer_phone": contract["customer_phone"],
            "customer_email": contract["customer_email"],
            "object_name": "Тестовый объект 2",
            "object_address": contract["object_address"],
            "start_date": "2026-04-01",
            "end_date": "2026-05-05",
            "price_coefficient": "1.30",
            "status": "active",
            "notes": "Обновлено",
        },
    )
    assert updated_contract["object_name"] == "Тестовый объект 2"

    order = services["order"].create_purchase_order(
        {
            "contract_id": contract["id"],
            "flower_id": flower["id"],
            "quantity": "5",
            "order_date": "2026-03-20",
            "planned_delivery_date": "2026-03-25",
            "actual_delivery_date": "",
            "status": "approved",
            "notes": "",
        }
    )
    assert order["status"] == "approved"

    updated_order = services["order"].update_purchase_order(
        order["id"],
        {
            "contract_id": contract["id"],
            "flower_id": flower["id"],
            "quantity": "7",
            "order_date": "2026-03-20",
            "planned_delivery_date": "2026-03-26",
            "actual_delivery_date": "",
            "status": "ordered",
            "notes": "Обновлено",
        },
    )
    assert str(updated_order["line_amount"]) == "910.00"

    services["order"].delete_purchase_order(order["id"])
    services["flower"].delete_flower(flower["id"])
    services["contract"].delete_contract(contract["id"])
    services["supplier"].delete_supplier(supplier["id"])

    assert services["supplier"].list_suppliers(search="Обновлено") == []
