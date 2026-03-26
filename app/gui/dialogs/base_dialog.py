from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title: str, submit_callback, width: int = 520, height: int = 500):
        super().__init__(parent)
        self.submit_callback = submit_callback
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.body = ttk.Frame(self, padding=12)
        self.body.pack(fill="both", expand=True)
        self.body.columnconfigure(1, weight=1)

        self.build_form()

        buttons = ttk.Frame(self.body)
        buttons.grid(column=0, row=999, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(buttons, text="Сохранить", command=self.on_save).pack(side="left")
        ttk.Button(buttons, text="Отмена", command=self.destroy).pack(side="left", padx=(6, 0))

    def add_label(self, row: int, text: str):
        ttk.Label(self.body, text=text).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 10))

    def add_entry(self, row: int, textvariable, width: int = 40):
        entry = ttk.Entry(self.body, textvariable=textvariable, width=width)
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        return entry

    def add_combobox(self, row: int, textvariable, values: list[str]):
        combo = ttk.Combobox(self.body, textvariable=textvariable, values=values, state="readonly")
        combo.grid(row=row, column=1, sticky="ew", pady=4)
        return combo

    def add_checkbutton(self, row: int, text: str, variable):
        checkbox = ttk.Checkbutton(self.body, text=text, variable=variable)
        checkbox.grid(row=row, column=1, sticky="w", pady=4)
        return checkbox

    def add_text(self, row: int, height: int = 4):
        text = tk.Text(self.body, width=40, height=height, wrap="word")
        text.grid(row=row, column=1, sticky="ew", pady=4)
        return text

    def build_form(self) -> None:
        raise NotImplementedError

    def get_payload(self) -> dict:
        raise NotImplementedError

    def on_save(self) -> None:
        try:
            self.submit_callback(self.get_payload())
        except Exception as error:  # GUI boundary
            messagebox.showerror("Ошибка", str(error), parent=self)
            return
        self.destroy()
