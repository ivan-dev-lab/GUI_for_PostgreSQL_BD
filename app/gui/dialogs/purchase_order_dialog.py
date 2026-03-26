from __future__ import annotations

from decimal import Decimal, InvalidOperation
import tkinter as tk

from app.constants import ORDER_STATUS_LABELS
from app.gui.dialogs.base_dialog import BaseDialog
from app.utils.formatters import format_date, format_decimal


class PurchaseOrderDialog(BaseDialog):
    def __init__(
        self,
        parent,
        title: str,
        submit_callback,
        contract_choices: list[dict],
        flower_choices: list[dict],
        item: dict | None = None,
    ):
        self.item = item or {}
        self.contract_data = {
            f"{contract['contract_number']} | {contract['customer_name']}": contract
            for contract in contract_choices
        }
        self.flower_data = {
            f"{flower['name']} {('(' + flower['variety'] + ')') if flower.get('variety') else ''} | {flower['supplier_name']}": flower
            for flower in flower_choices
        }
        self.status_map = {label: code for code, label in ORDER_STATUS_LABELS.items()}

        contract_display = next(
            (label for label, contract in self.contract_data.items() if contract["id"] == self.item.get("contract_id")),
            "",
        )
        flower_display = next(
            (label for label, flower in self.flower_data.items() if flower["id"] == self.item.get("flower_id")),
            "",
        )

        self.original_flower_id = self.item.get("flower_id")
        self.original_unit_price = self.item.get("unit_price_snapshot")

        self.contract_var = tk.StringVar(value=contract_display)
        self.flower_var = tk.StringVar(value=flower_display)
        self.quantity_var = tk.StringVar(value=format_decimal(self.item.get("quantity")))
        self.order_date_var = tk.StringVar(value=format_date(self.item.get("order_date")))
        self.planned_delivery_var = tk.StringVar(value=format_date(self.item.get("planned_delivery_date")))
        self.actual_delivery_var = tk.StringVar(value=format_date(self.item.get("actual_delivery_date")))
        self.status_var = tk.StringVar(value=ORDER_STATUS_LABELS.get(self.item.get("status", "created"), "Создан"))
        self.unit_price_var = tk.StringVar(value=format_decimal(self.item.get("unit_price_snapshot")))
        self.line_amount_var = tk.StringVar(value=format_decimal(self.item.get("line_amount")))
        super().__init__(parent, title, submit_callback, width=700, height=520)
        self.quantity_var.trace_add("write", self._refresh_amount)
        self.flower_var.trace_add("write", self._refresh_amount)
        self._refresh_amount()

    def build_form(self) -> None:
        self.add_label(0, "Договор")
        self.add_combobox(0, self.contract_var, list(self.contract_data.keys()))
        self.add_label(1, "Цветок")
        self.add_combobox(1, self.flower_var, list(self.flower_data.keys()))
        self.add_label(2, "Количество")
        self.add_entry(2, self.quantity_var, width=20)
        self.add_label(3, "Цена на момент заказа")
        ttk_label = tk.Label(self.body, textvariable=self.unit_price_var, anchor="w")
        ttk_label.grid(row=3, column=1, sticky="w", pady=4)
        self.add_label(4, "Сумма")
        amount_label = tk.Label(self.body, textvariable=self.line_amount_var, anchor="w")
        amount_label.grid(row=4, column=1, sticky="w", pady=4)
        self.add_label(5, "Дата заказа")
        self.add_entry(5, self.order_date_var, width=20)
        self.add_label(6, "Плановая дата поставки")
        self.add_entry(6, self.planned_delivery_var, width=20)
        self.add_label(7, "Фактическая дата поставки")
        self.add_entry(7, self.actual_delivery_var, width=20)
        self.add_label(8, "Статус")
        self.add_combobox(8, self.status_var, list(self.status_map.keys()))
        self.add_label(9, "Примечание")
        self.notes_text = self.add_text(9)
        self.notes_text.insert("1.0", self.item.get("notes", "") or "")

    def _selected_flower(self) -> dict | None:
        return self.flower_data.get(self.flower_var.get())

    def _price_for_current_selection(self) -> Decimal | None:
        flower = self._selected_flower()
        if flower is None:
            return None
        if flower["id"] == self.original_flower_id and self.original_unit_price is not None:
            return Decimal(str(self.original_unit_price))
        return Decimal(str(flower["purchase_price"]))

    def _refresh_amount(self, *_args) -> None:
        price = self._price_for_current_selection()
        if price is None:
            self.unit_price_var.set("")
            self.line_amount_var.set("")
            return
        self.unit_price_var.set(format_decimal(price))
        try:
            quantity_text = (self.quantity_var.get() or "").replace(",", ".").strip()
            if not quantity_text:
                self.line_amount_var.set("")
                return
            quantity = Decimal(quantity_text)
            if quantity <= 0:
                self.line_amount_var.set("")
                return
            self.line_amount_var.set(format_decimal(quantity * price))
        except InvalidOperation:
            self.line_amount_var.set("")

    def get_payload(self) -> dict:
        contract = self.contract_data.get(self.contract_var.get())
        flower = self.flower_data.get(self.flower_var.get())
        return {
            "contract_id": contract["id"] if contract else None,
            "flower_id": flower["id"] if flower else None,
            "quantity": self.quantity_var.get(),
            "order_date": self.order_date_var.get(),
            "planned_delivery_date": self.planned_delivery_var.get(),
            "actual_delivery_date": self.actual_delivery_var.get(),
            "status": self.status_map.get(self.status_var.get(), "created"),
            "notes": self.notes_text.get("1.0", "end").strip(),
        }
