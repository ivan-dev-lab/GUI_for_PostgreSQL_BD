from __future__ import annotations

import tkinter as tk

from app.gui.dialogs.base_dialog import BaseDialog


class SupplierDialog(BaseDialog):
    def __init__(self, parent, title: str, submit_callback, item: dict | None = None):
        self.item = item or {}
        self.name_var = tk.StringVar(value=self.item.get("name", ""))
        self.contact_person_var = tk.StringVar(value=self.item.get("contact_person", ""))
        self.phone_var = tk.StringVar(value=self.item.get("phone", ""))
        self.email_var = tk.StringVar(value=self.item.get("email", ""))
        self.address_var = tk.StringVar(value=self.item.get("address", ""))
        self.inn_var = tk.StringVar(value=self.item.get("inn", ""))
        self.is_active_var = tk.BooleanVar(value=self.item.get("is_active", True))
        super().__init__(parent, title, submit_callback, width=560, height=360)

    def build_form(self) -> None:
        self.add_label(0, "Наименование")
        self.add_entry(0, self.name_var)
        self.add_label(1, "Контактное лицо")
        self.add_entry(1, self.contact_person_var)
        self.add_label(2, "Телефон")
        self.add_entry(2, self.phone_var)
        self.add_label(3, "Email")
        self.add_entry(3, self.email_var)
        self.add_label(4, "Адрес")
        self.add_entry(4, self.address_var)
        self.add_label(5, "ИНН")
        self.add_entry(5, self.inn_var)
        self.add_label(6, "Статус")
        self.add_checkbutton(6, "Активный поставщик", self.is_active_var)

    def get_payload(self) -> dict:
        return {
            "name": self.name_var.get(),
            "contact_person": self.contact_person_var.get(),
            "phone": self.phone_var.get(),
            "email": self.email_var.get(),
            "address": self.address_var.get(),
            "inn": self.inn_var.get(),
            "is_active": self.is_active_var.get(),
        }
