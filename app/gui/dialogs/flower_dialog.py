from __future__ import annotations

from decimal import Decimal, InvalidOperation
import tkinter as tk

from app.gui.dialogs.base_dialog import BaseDialog


class FlowerDialog(BaseDialog):
    def __init__(
        self,
        parent,
        title: str,
        submit_callback,
        supplier_choices: list[dict],
        item: dict | None = None,
    ):
        self.item = item or {}
        self.supplier_choices = supplier_choices
        self.supplier_map = {
            f"{supplier['name']} (#{supplier['id']})": supplier["id"] for supplier in supplier_choices
        }
        current_supplier_display = next(
            (label for label, supplier_id in self.supplier_map.items() if supplier_id == self.item.get("supplier_id")),
            "",
        )
        self.supplier_var = tk.StringVar(value=current_supplier_display)
        self.name_var = tk.StringVar(value=self.item.get("name", ""))
        self.variety_var = tk.StringVar(value=self.item.get("variety", ""))
        self.color_var = tk.StringVar(value=self.item.get("color", ""))
        self.unit_var = tk.StringVar(value=self.item.get("unit", "шт"))
        self.purchase_price_var = tk.StringVar(value=str(self.item.get("purchase_price", "")))
        self.min_batch_var = tk.StringVar(value=str(self.item.get("min_batch", "")))
        self.season_var = tk.StringVar(value=self.item.get("season", ""))
        self.is_active_var = tk.BooleanVar(value=self.item.get("is_active", True))
        super().__init__(parent, title, submit_callback, width=620, height=500)

    def build_form(self) -> None:
        self.add_label(0, "Поставщик")
        self.add_combobox(0, self.supplier_var, list(self.supplier_map.keys()))
        self.add_label(1, "Название")
        self.add_entry(1, self.name_var)
        self.add_label(2, "Сорт")
        self.add_entry(2, self.variety_var)
        self.add_label(3, "Цвет")
        self.add_entry(3, self.color_var)
        self.add_label(4, "Ед. измерения")
        self.add_entry(4, self.unit_var, width=20)
        self.add_label(5, "Закупочная цена")
        self.add_entry(5, self.purchase_price_var, width=20)
        self.add_label(6, "Минимальная партия")
        self.add_entry(6, self.min_batch_var, width=20)
        self.add_label(7, "Сезон")
        self.add_entry(7, self.season_var)
        self.add_label(8, "Примечание")
        self.notes_text = self.add_text(8)
        self.notes_text.insert("1.0", self.item.get("notes", "") or "")
        self.add_label(9, "Статус")
        self.add_checkbutton(9, "Активная позиция", self.is_active_var)

    def get_payload(self) -> dict:
        return {
            "supplier_id": self.supplier_map.get(self.supplier_var.get()),
            "name": self.name_var.get(),
            "variety": self.variety_var.get(),
            "color": self.color_var.get(),
            "unit": self.unit_var.get(),
            "purchase_price": self.purchase_price_var.get(),
            "min_batch": self.min_batch_var.get(),
            "season": self.season_var.get(),
            "notes": self.notes_text.get("1.0", "end").strip(),
            "is_active": self.is_active_var.get(),
        }
