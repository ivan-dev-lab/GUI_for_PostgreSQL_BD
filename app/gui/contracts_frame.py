from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.constants import CONTRACT_STATUS_LABELS
from app.gui.base_frame import BaseEntityFrame
from app.gui.dialogs.contract_dialog import ContractDialog
from app.utils.formatters import contract_status_label, format_date, format_decimal


class ContractsFrame(BaseEntityFrame):
    def __init__(self, parent, contract_service, can_write: bool):
        self.contract_service = contract_service
        self.number_search_var = tk.StringVar()
        self.customer_search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Все")
        self.status_map = {"Все": None}
        self.status_map.update({label: code for code, label in CONTRACT_STATUS_LABELS.items()})
        columns = [
            ("number", "Номер", 140),
            ("date", "Дата", 100),
            ("customer", "Заказчик", 220),
            ("object", "Объект", 220),
            ("coef", "Коэфф.", 80),
            ("status", "Статус", 110),
        ]
        super().__init__(parent, "Договоры", columns, can_write)
        self._build_filters()
        self.refresh()

    def _build_filters(self) -> None:
        ttk.Label(self.filters_frame, text="Номер").pack(side="left")
        number_entry = ttk.Entry(self.filters_frame, textvariable=self.number_search_var, width=18)
        number_entry.pack(side="left", padx=(6, 10))
        number_entry.bind("<Return>", lambda _e: self.refresh())

        ttk.Label(self.filters_frame, text="Заказчик").pack(side="left")
        customer_entry = ttk.Entry(self.filters_frame, textvariable=self.customer_search_var, width=24)
        customer_entry.pack(side="left", padx=(6, 10))
        customer_entry.bind("<Return>", lambda _e: self.refresh())

        ttk.Label(self.filters_frame, text="Статус").pack(side="left")
        combo = ttk.Combobox(
            self.filters_frame,
            textvariable=self.status_var,
            values=list(self.status_map.keys()),
            state="readonly",
            width=18,
        )
        combo.pack(side="left", padx=(6, 10))
        combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

    def refresh(self) -> None:
        rows = self.contract_service.list_contracts(
            number_search=self.number_search_var.get(),
            customer_search=self.customer_search_var.get(),
            status=self.status_map.get(self.status_var.get()),
        )
        self.populate_rows(
            rows,
            lambda row: (
                row["contract_number"],
                format_date(row["contract_date"]),
                row["customer_name"],
                row["object_name"],
                format_decimal(row["price_coefficient"]),
                contract_status_label(row["status"]),
            ),
        )

    def open_create(self) -> None:
        dialog = ContractDialog(self, "Добавление договора", self._create)
        self.wait_window(dialog)

    def _create(self, payload: dict) -> None:
        self.contract_service.create_contract(payload)
        self.refresh()

    def open_edit(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        dialog = ContractDialog(
            self,
            "Редактирование договора",
            lambda payload: self._update(selected_id, payload),
            item=self.contract_service.get_contract(selected_id),
        )
        self.wait_window(dialog)

    def _update(self, contract_id: int, payload: dict) -> None:
        self.contract_service.update_contract(contract_id, payload)
        self.refresh()

    def delete_selected(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        if not messagebox.askyesno("Удаление", "Удалить выбранный договор?", parent=self):
            return
        self.contract_service.delete_contract(selected_id)
        self.refresh()

    def view_selected(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        row = self.contract_service.get_contract(selected_id)
        self.show_card(
            "Карточка договора",
            [
                f"Номер договора: {row['contract_number']}",
                f"Дата договора: {format_date(row['contract_date']) or '-'}",
                f"Заказчик: {row['customer_name']}",
                f"Телефон: {row.get('customer_phone') or '-'}",
                f"Email: {row.get('customer_email') or '-'}",
                f"Объект: {row['object_name']}",
                f"Адрес объекта: {row['object_address']}",
                f"Период работ: {format_date(row['start_date']) or '-'} - {format_date(row['end_date']) or '-'}",
                f"Коэффициент: {format_decimal(row['price_coefficient'])}",
                f"Статус: {contract_status_label(row['status'])}",
                f"Примечание: {row.get('notes') or '-'}",
            ],
        )
