from __future__ import annotations

from decimal import Decimal


def test_purchase_order_amounts_are_calculated_from_flower_price(services, sample_entities):
    order = services["order"].create_purchase_order(
        {
            "contract_id": sample_entities["contract"]["id"],
            "flower_id": sample_entities["flower"]["id"],
            "quantity": "12",
            "order_date": "2026-03-10",
            "planned_delivery_date": "2026-03-15",
            "actual_delivery_date": "",
            "status": "created",
            "notes": "Тестовый заказ",
        }
    )

    assert order["unit_price_snapshot"] == Decimal("125.50")
    assert order["line_amount"] == Decimal("1506.00")
    assert order["final_amount"] == Decimal("1882.50")
