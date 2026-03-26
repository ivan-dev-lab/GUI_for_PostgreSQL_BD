from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.constants import ORDER_STATUS_LABELS
from app.gui.base_frame import BaseEntityFrame
from app.gui.dialogs.purchase_order_dialog import PurchaseOrderDialog
from app.utils.formatters import format_date, format_decimal, order_status_label


class PurchaseOrdersFrame(BaseEntityFrame):
    def __init__(self, parent, purchase_order_service, contract_service, flower_service, can_write: bool):
        self.purchase_order_service = purchase_order_service
        self.contract_service = contract_service
        self.flower_service = flower_service
        self.search_var = tk.StringVar()
        self.contract_filter_var = tk.StringVar(value="Все")
        self.status_filter_var = tk.StringVar(value="Все")
        self.date_from_var = tk.StringVar()
        self.date_to_var = tk.StringVar()
        self.contract_filter_map = {"Все": None}
        self.status_map = {"Все": None}
        self.status_map.update({label: code for code, label in ORDER_STATUS_LABELS.items()})
        columns = [
            ("contract", "Договор", 130),
            ("flower", "Цветок", 180),
            ("supplier", "Поставщик", 180),
            ("quantity", "Количество", 90),
            ("line_amount", "Сумма", 100),
            ("order_date", "Дата заказа", 110),
            ("status", "Статус", 110),
        ]
        super().__init__(parent, "Заказы на поставку", columns, can_write)
        self._build_filters()
        self.refresh()

    def _reload_contracts(self) -> None:
        contracts = self.contract_service.get_contract_choices()
        self.contract_filter_map = {"Все": None}
        self.contract_filter_map.update(
            {
                f"{contract['contract_number']} | {contract['customer_name']}": contract["id"]
                for contract in contracts
            }
        )
        self.contract_combo.configure(values=list(self.contract_filter_map.keys()))
        if self.contract_filter_var.get() not in self.contract_filter_map:
            self.contract_filter_var.set("Все")

    def _build_filters(self) -> None:
        ttk.Label(self.filters_frame, text="Поиск").grid(row=0, column=0, sticky="w")
        search_entry = ttk.Entry(self.filters_frame, textvariable=self.search_var, width=24)
        search_entry.grid(row=0, column=1, padx=(6, 10), pady=4, sticky="w")
        search_entry.bind("<Return>", lambda _e: self.refresh())

        ttk.Label(self.filters_frame, text="Договор").grid(row=0, column=2, sticky="w")
        self.contract_combo = ttk.Combobox(self.filters_frame, textvariable=self.contract_filter_var, state="readonly", width=28)
        self.contract_combo.grid(row=0, column=3, padx=(6, 10), pady=4, sticky="w")
        self.contract_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        ttk.Label(self.filters_frame, text="Статус").grid(row=0, column=4, sticky="w")
        status_combo = ttk.Combobox(
            self.filters_frame,
            textvariable=self.status_filter_var,
            values=list(self.status_map.keys()),
            state="readonly",
            width=16,
        )
        status_combo.grid(row=0, column=5, padx=(6, 10), pady=4, sticky="w")
        status_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        ttk.Label(self.filters_frame, text="Дата с").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.filters_frame, textvariable=self.date_from_var, width=18).grid(row=1, column=1, padx=(6, 10), pady=4, sticky="w")
        ttk.Label(self.filters_frame, text="Дата по").grid(row=1, column=2, sticky="w")
        ttk.Entry(self.filters_frame, textvariable=self.date_to_var, width=18).grid(row=1, column=3, padx=(6, 10), pady=4, sticky="w")
        ttk.Button(self.filters_frame, text="Применить", command=self.refresh).grid(row=1, column=4, padx=(0, 10), pady=4)
        ttk.Button(self.filters_frame, text="Сбросить", command=self._reset_filters).grid(row=1, column=5, pady=4)

    def _reset_filters(self) -> None:
        self.search_var.set("")
        self.contract_filter_var.set("Все")
        self.status_filter_var.set("Все")
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.refresh()

    def refresh(self) -> None:
        self._reload_contracts()
        rows = self.purchase_order_service.list_purchase_orders(
            search=self.search_var.get(),
            contract_id=self.contract_filter_map.get(self.contract_filter_var.get()),
            status=self.status_map.get(self.status_filter_var.get()),
            date_from=self.date_from_var.get(),
            date_to=self.date_to_var.get(),
        )
        self.populate_rows(
            rows,
            lambda row: (
                row["contract_number"],
                f"{row['flower_name']} ({row['flower_variety']})" if row.get("flower_variety") else row["flower_name"],
                row.get("supplier_name") or "",
                format_decimal(row["quantity"]),
                format_decimal(row["line_amount"]),
                format_date(row["order_date"]),
                order_status_label(row["status"]),
            ),
        )

    def open_create(self) -> None:
        dialog = PurchaseOrderDialog(
            self,
            "Добавление заказа",
            self._create,
            contract_choices=self.contract_service.get_contract_choices(),
            flower_choices=self.flower_service.get_flower_choices(),
        )
        self.wait_window(dialog)

    def _create(self, payload: dict) -> None:
        self.purchase_order_service.create_purchase_order(payload)
        self.refresh()

    def open_edit(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        dialog = PurchaseOrderDialog(
            self,
            "Редактирование заказа",
            lambda payload: self._update(selected_id, payload),
            contract_choices=self.contract_service.get_contract_choices(),
            flower_choices=self.flower_service.get_flower_choices(),
            item=self.purchase_order_service.get_purchase_order(selected_id),
        )
        self.wait_window(dialog)

    def _update(self, order_id: int, payload: dict) -> None:
        self.purchase_order_service.update_purchase_order(order_id, payload)
        self.refresh()

    def delete_selected(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        if not messagebox.askyesno("Удаление", "Удалить выбранный заказ?", parent=self):
            return
        self.purchase_order_service.delete_purchase_order(selected_id)
        self.refresh()

    def view_selected(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        row = self.purchase_order_service.get_purchase_order(selected_id)
        flower_label = f"{row['flower_name']} ({row['flower_variety']})" if row.get("flower_variety") else row["flower_name"]
        self.show_card(
            "Карточка заказа",
            [
                f"Договор: {row['contract_number']}",
                f"Заказчик: {row.get('customer_name') or '-'}",
                f"Объект: {row.get('object_name') or '-'}",
                f"Цветок: {flower_label}",
                f"Поставщик: {row.get('supplier_name') or '-'}",
                f"Количество: {format_decimal(row['quantity'])}",
                f"Цена на момент заказа: {format_decimal(row['unit_price_snapshot'])}",
                f"Сумма: {format_decimal(row['line_amount'])}",
                f"Дата заказа: {format_date(row['order_date']) or '-'}",
                f"Плановая поставка: {format_date(row['planned_delivery_date']) or '-'}",
                f"Фактическая поставка: {format_date(row['actual_delivery_date']) or '-'}",
                f"Статус: {order_status_label(row['status'])}",
                f"Примечание: {row.get('notes') or '-'}",
            ],
        )
