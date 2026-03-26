from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class BaseEntityFrame(ttk.Frame):
    def __init__(self, parent, title: str, columns: list[tuple[str, str, int]], can_write: bool):
        super().__init__(parent, padding=12)
        self.title = title
        self.can_write = can_write
        self.columns = columns
        self.rows_by_id: dict[int, dict] = {}

        title_label = ttk.Label(self, text=title, font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))

        self.filters_frame = ttk.LabelFrame(self, text="Фильтры", padding=10)
        self.filters_frame.pack(fill="x", pady=(0, 8))

        tree_container = ttk.Frame(self)
        tree_container.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_container, show="headings", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.bind("<Double-1>", self._on_double_click)

        self._configure_tree(columns)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=(8, 0))

        ttk.Button(button_frame, text="Обновить", command=self.refresh).pack(side="left")
        self.add_button = ttk.Button(button_frame, text="Добавить", command=self.open_create)
        self.add_button.pack(side="left", padx=(6, 0))
        self.edit_button = ttk.Button(button_frame, text="Изменить", command=self.open_edit)
        self.edit_button.pack(side="left", padx=(6, 0))
        self.delete_button = ttk.Button(button_frame, text="Удалить", command=self.delete_selected)
        self.delete_button.pack(side="left", padx=(6, 0))
        self.view_button = ttk.Button(button_frame, text="Просмотр", command=self.view_selected)
        self.view_button.pack(side="left", padx=(6, 0))

        if not self.can_write:
            self.add_button.state(["disabled"])
            self.edit_button.state(["disabled"])
            self.delete_button.state(["disabled"])

    def _configure_tree(self, columns: list[tuple[str, str, int]]) -> None:
        self.tree["columns"] = [key for key, _, _ in columns]
        for key, heading, width in columns:
            self.tree.heading(key, text=heading)
            self.tree.column(key, width=width, anchor="w", stretch=True)

    def populate_rows(self, rows: list[dict], values_builder) -> None:
        self.rows_by_id = {row["id"]: row for row in rows}
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", iid=str(row["id"]), values=values_builder(row))

    def get_selected_id(self) -> int | None:
        selection = self.tree.selection()
        if not selection:
            return None
        return int(selection[0])

    def get_selected_row(self) -> dict | None:
        selected_id = self.get_selected_id()
        return self.rows_by_id.get(selected_id) if selected_id is not None else None

    def ensure_selection(self) -> int | None:
        selected_id = self.get_selected_id()
        if selected_id is None:
            messagebox.showwarning("Выбор записи", "Сначала выберите запись в таблице.")
            return None
        return selected_id

    def show_card(self, title: str, lines: list[str]) -> None:
        messagebox.showinfo(title, "\n".join(lines), parent=self)

    def _on_double_click(self, _event) -> None:
        if self.can_write:
            self.open_edit()
        else:
            self.view_selected()

    def refresh(self) -> None:
        raise NotImplementedError

    def open_create(self) -> None:
        raise NotImplementedError

    def open_edit(self) -> None:
        raise NotImplementedError

    def delete_selected(self) -> None:
        raise NotImplementedError

    def view_selected(self) -> None:
        raise NotImplementedError
