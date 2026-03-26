from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.gui.base_frame import BaseEntityFrame
from app.gui.dialogs.flower_dialog import FlowerDialog
from app.utils.formatters import format_bool, format_decimal


class FlowersFrame(BaseEntityFrame):
    def __init__(self, parent, flower_service, supplier_service, can_write: bool):
        self.flower_service = flower_service
        self.supplier_service = supplier_service
        self.search_var = tk.StringVar()
        self.supplier_filter_var = tk.StringVar(value="Все")
        self.supplier_filter_map = {"Все": None}
        columns = [
            ("name", "Название", 160),
            ("variety", "Сорт", 160),
            ("supplier", "Поставщик", 220),
            ("unit", "Ед.", 70),
            ("price", "Цена", 90),
            ("min_batch", "Мин. партия", 100),
            ("active", "Активен", 90),
        ]
        super().__init__(parent, "Цветы", columns, can_write)
        self._build_filters()
        self.refresh()

    def _reload_suppliers(self) -> None:
        suppliers = self.supplier_service.get_supplier_choices()
        self.supplier_filter_map = {"Все": None}
        self.supplier_filter_map.update(
            {f"{supplier['name']} (#{supplier['id']})": supplier["id"] for supplier in suppliers}
        )
        self.supplier_combo.configure(values=list(self.supplier_filter_map.keys()))
        if self.supplier_filter_var.get() not in self.supplier_filter_map:
            self.supplier_filter_var.set("Все")

    def _build_filters(self) -> None:
        ttk.Label(self.filters_frame, text="Поиск").pack(side="left")
        search_entry = ttk.Entry(self.filters_frame, textvariable=self.search_var, width=28)
        search_entry.pack(side="left", padx=(6, 12))
        search_entry.bind("<Return>", lambda _e: self.refresh())

        ttk.Label(self.filters_frame, text="Поставщик").pack(side="left")
        self.supplier_combo = ttk.Combobox(
            self.filters_frame,
            textvariable=self.supplier_filter_var,
            state="readonly",
            width=28,
        )
        self.supplier_combo.pack(side="left", padx=(6, 12))
        self.supplier_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

    def refresh(self) -> None:
        self._reload_suppliers()
        rows = self.flower_service.list_flowers(
            search=self.search_var.get(),
            supplier_id=self.supplier_filter_map.get(self.supplier_filter_var.get()),
        )
        self.populate_rows(
            rows,
            lambda row: (
                row["name"],
                row.get("variety") or "",
                row.get("supplier_name") or "",
                row["unit"],
                format_decimal(row["purchase_price"]),
                str(row["min_batch"]),
                format_bool(row["is_active"]),
            ),
        )

    def open_create(self) -> None:
        dialog = FlowerDialog(
            self,
            "Добавление цветка",
            self._create,
            supplier_choices=self.supplier_service.get_supplier_choices(),
        )
        self.wait_window(dialog)

    def _create(self, payload: dict) -> None:
        self.flower_service.create_flower(payload)
        self.refresh()

    def open_edit(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        dialog = FlowerDialog(
            self,
            "Редактирование цветка",
            lambda payload: self._update(selected_id, payload),
            supplier_choices=self.supplier_service.get_supplier_choices(),
            item=self.flower_service.get_flower(selected_id),
        )
        self.wait_window(dialog)

    def _update(self, flower_id: int, payload: dict) -> None:
        self.flower_service.update_flower(flower_id, payload)
        self.refresh()

    def delete_selected(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        if not messagebox.askyesno("Удаление", "Удалить выбранную позицию?", parent=self):
            return
        self.flower_service.delete_flower(selected_id)
        self.refresh()

    def view_selected(self) -> None:
        selected_id = self.ensure_selection()
        if selected_id is None:
            return
        row = self.flower_service.get_flower(selected_id)
        self.show_card(
            "Карточка цветка",
            [
                f"Название: {row['name']}",
                f"Сорт: {row.get('variety') or '-'}",
                f"Поставщик: {row.get('supplier_name') or '-'}",
                f"Цвет: {row.get('color') or '-'}",
                f"Ед. измерения: {row['unit']}",
                f"Закупочная цена: {format_decimal(row['purchase_price'])}",
                f"Минимальная партия: {row['min_batch']}",
                f"Сезон: {row.get('season') or '-'}",
                f"Примечание: {row.get('notes') or '-'}",
                f"Активен: {format_bool(row['is_active'])}",
            ],
        )
