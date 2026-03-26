from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.constants import ACTIVE_FILTER_OPTIONS
from app.gui.base_frame import BaseEntityFrame
from app.gui.dialogs.supplier_dialog import SupplierDialog
from app.utils.formatters import format_bool


class SuppliersFrame(BaseEntityFrame):
    def __init__(self, parent, supplier_service, can_write: bool):
        self.supplier_service = supplier_service
        self.search_var = tk.StringVar()
        self.active_filter_var = tk.StringVar(value="Все")
        columns = [
            ("name", "Наименование", 220),
            ("contact_person", "Контактное лицо", 180),
            ("phone", "Телефон", 140),
            ("email", "Email", 180),
            ("is_active", "Активен", 90),
        ]
        super().__init__(parent, "Поставщики", columns, can_write)
        self._build_filters()
        self.refresh()

    def _build_filters(self) -> None:
        ttk.Label(self.filters_frame, text="Поиск по названию").pack(side="left")
        search_entry = ttk.Entry(self.filters_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=(6, 12))
        search_entry.bind("<Return>", lambda _e: self.refresh())

        ttk.Label(self.filters_frame, text="Активность").pack(side="left")
        active_combo = ttk.Combobox(
            self.filters_frame,
            textvariable=self.active_filter_var,
            values=list(ACTIVE_FILTER_OPTIONS.keys()),
            state="readonly",
            width=22,
        )
        active_combo.pack(side="left", padx=(6, 12))
        active_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

    def refresh(self) -> None:
        rows = self.supplier_service.list_suppliers(
            search=self.search_var.get(),
            is_active=ACTIVE_FILTER_OPTIONS[self.active_filter_var.get()],
        )
        self.populate_rows(
            rows,
            lambda row: (
                row["name"],
                row.get("contact_person") or "",
                row.get("phone") or "",
                row.get("email") or "",
                format_bool(row["is_active"]),
            ),
        )

    def open_create(self) -> None:
        dialog = SupplierDialog(self, "Добавление поставщика", self._create)
        self.wait_window(dialog)

    def _create(self, payload: dict) -> None:
        self.supplier_service.create_supplier(payload)
        self.refresh()

    def open_edit(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        dialog = SupplierDialog(
            self,
            "Редактирование поставщика",
            lambda payload: self._update(selected_id, payload),
            item=self.supplier_service.get_supplier(selected_id),
        )
        self.wait_window(dialog)

    def _update(self, supplier_id: int, payload: dict) -> None:
        self.supplier_service.update_supplier(supplier_id, payload)
        self.refresh()

    def delete_selected(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        if not messagebox.askyesno("Удаление", "Удалить выбранного поставщика?", parent=self):
            return
        self.supplier_service.delete_supplier(selected_id)
        self.refresh()

    def view_selected(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        row = self.supplier_service.get_supplier(selected_id)
        self.show_card(
            "Карточка поставщика",
            [
                f"Наименование: {row['name']}",
                f"Контактное лицо: {row.get('contact_person') or '-'}",
                f"Телефон: {row.get('phone') or '-'}",
                f"Email: {row.get('email') or '-'}",
                f"Адрес: {row.get('address') or '-'}",
                f"ИНН: {row.get('inn') or '-'}",
                f"Активен: {format_bool(row['is_active'])}",
            ],
        )
