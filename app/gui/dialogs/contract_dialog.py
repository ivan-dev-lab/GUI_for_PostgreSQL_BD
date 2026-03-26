from __future__ import annotations

import tkinter as tk

from app.constants import CONTRACT_STATUS_LABELS
from app.gui.dialogs.base_dialog import BaseDialog
from app.utils.formatters import format_date, format_decimal


class ContractDialog(BaseDialog):
    def __init__(self, parent, title: str, submit_callback, item: dict | None = None):
        self.item = item or {}
        self.status_map = {label: code for code, label in CONTRACT_STATUS_LABELS.items()}
        current_status = CONTRACT_STATUS_LABELS.get(self.item.get("status", "draft"), "Черновик")
        self.number_var = tk.StringVar(value=self.item.get("contract_number", ""))
        self.contract_date_var = tk.StringVar(value=format_date(self.item.get("contract_date")))
        self.customer_name_var = tk.StringVar(value=self.item.get("customer_name", ""))
        self.customer_phone_var = tk.StringVar(value=self.item.get("customer_phone", ""))
        self.customer_email_var = tk.StringVar(value=self.item.get("customer_email", ""))
        self.object_name_var = tk.StringVar(value=self.item.get("object_name", ""))
        self.object_address_var = tk.StringVar(value=self.item.get("object_address", ""))
        self.start_date_var = tk.StringVar(value=format_date(self.item.get("start_date")))
        self.end_date_var = tk.StringVar(value=format_date(self.item.get("end_date")))
        self.price_coefficient_var = tk.StringVar(value=format_decimal(self.item.get("price_coefficient")))
        self.status_var = tk.StringVar(value=current_status)
        super().__init__(parent, title, submit_callback, width=700, height=560)

    def build_form(self) -> None:
        self.add_label(0, "Номер договора")
        self.add_entry(0, self.number_var)
        self.add_label(1, "Дата договора")
        self.add_entry(1, self.contract_date_var, width=20)
        self.add_label(2, "Заказчик")
        self.add_entry(2, self.customer_name_var)
        self.add_label(3, "Телефон заказчика")
        self.add_entry(3, self.customer_phone_var)
        self.add_label(4, "Email заказчика")
        self.add_entry(4, self.customer_email_var)
        self.add_label(5, "Объект")
        self.add_entry(5, self.object_name_var)
        self.add_label(6, "Адрес объекта")
        self.add_entry(6, self.object_address_var)
        self.add_label(7, "Дата начала")
        self.add_entry(7, self.start_date_var, width=20)
        self.add_label(8, "Дата окончания")
        self.add_entry(8, self.end_date_var, width=20)
        self.add_label(9, "Коэффициент")
        self.add_entry(9, self.price_coefficient_var, width=20)
        self.add_label(10, "Статус")
        self.add_combobox(10, self.status_var, list(self.status_map.keys()))
        self.add_label(11, "Примечание")
        self.notes_text = self.add_text(11)
        self.notes_text.insert("1.0", self.item.get("notes", "") or "")

    def get_payload(self) -> dict:
        return {
            "contract_number": self.number_var.get(),
            "contract_date": self.contract_date_var.get(),
            "customer_name": self.customer_name_var.get(),
            "customer_phone": self.customer_phone_var.get(),
            "customer_email": self.customer_email_var.get(),
            "object_name": self.object_name_var.get(),
            "object_address": self.object_address_var.get(),
            "start_date": self.start_date_var.get(),
            "end_date": self.end_date_var.get(),
            "price_coefficient": self.price_coefficient_var.get(),
            "status": self.status_map.get(self.status_var.get(), "draft"),
            "notes": self.notes_text.get("1.0", "end").strip(),
        }
