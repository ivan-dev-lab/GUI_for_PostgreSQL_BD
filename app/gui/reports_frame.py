from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.constants import REPORT_OPTIONS
from app.utils.exporters import export_to_csv, export_to_xlsx


class ReportsFrame(ttk.Frame):
    def __init__(self, parent, report_service):
        super().__init__(parent, padding=12)
        self.report_service = report_service
        self.current_report = None
        self.report_var = tk.StringVar(value=REPORT_OPTIONS["orders_period"])
        self.date_from_var = tk.StringVar()
        self.date_to_var = tk.StringVar()
        self.report_map = {label: key for key, label in REPORT_OPTIONS.items()}

        title_label = ttk.Label(self, text="Отчеты", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))

        controls = ttk.LabelFrame(self, text="Параметры отчета", padding=10)
        controls.pack(fill="x", pady=(0, 8))
        ttk.Label(controls, text="Отчет").grid(row=0, column=0, sticky="w")
        report_combo = ttk.Combobox(
            controls,
            textvariable=self.report_var,
            values=list(self.report_map.keys()),
            state="readonly",
            width=36,
        )
        report_combo.grid(row=0, column=1, padx=(6, 12), pady=4, sticky="w")
        ttk.Label(controls, text="Дата с").grid(row=0, column=2, sticky="w")
        ttk.Entry(controls, textvariable=self.date_from_var, width=16).grid(row=0, column=3, padx=(6, 12), pady=4, sticky="w")
        ttk.Label(controls, text="Дата по").grid(row=0, column=4, sticky="w")
        ttk.Entry(controls, textvariable=self.date_to_var, width=16).grid(row=0, column=5, padx=(6, 12), pady=4, sticky="w")
        ttk.Button(controls, text="Сформировать", command=self.generate_report).grid(row=0, column=6, pady=4)

        tree_container = ttk.Frame(self)
        tree_container.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_container, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll_y.set)

        export_frame = ttk.Frame(self)
        export_frame.pack(fill="x", pady=(8, 0))
        ttk.Button(export_frame, text="Экспорт CSV", command=self.export_csv).pack(side="left")
        ttk.Button(export_frame, text="Экспорт XLSX", command=self.export_xlsx).pack(side="left", padx=(6, 0))

    def _configure_columns(self, headers: list[str]) -> None:
        column_ids = [f"c{index}" for index, _ in enumerate(headers)]
        self.tree["columns"] = column_ids
        for column_id, header in zip(column_ids, headers):
            self.tree.heading(column_id, text=header)
            self.tree.column(column_id, width=150, stretch=True)

    def generate_report(self) -> None:
        report_key = self.report_map[self.report_var.get()]
        self.current_report = self.report_service.generate_report(
            report_key,
            date_from=self.date_from_var.get(),
            date_to=self.date_to_var.get(),
        )
        self._configure_columns(self.current_report.headers)
        self.tree.delete(*self.tree.get_children())
        for index, row in enumerate(self.current_report.rows, start=1):
            self.tree.insert("", "end", iid=str(index), values=row)

    def export_csv(self) -> None:
        if self.current_report is None:
            messagebox.showwarning("Экспорт", "Сначала сформируйте отчет.", parent=self)
            return
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Сохранить CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not file_path:
            return
        export_to_csv(file_path, self.current_report.headers, self.current_report.rows)
        messagebox.showinfo("Экспорт", "CSV-файл успешно сохранен.", parent=self)

    def export_xlsx(self) -> None:
        if self.current_report is None:
            messagebox.showwarning("Экспорт", "Сначала сформируйте отчет.", parent=self)
            return
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Сохранить XLSX",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
        )
        if not file_path:
            return
        export_to_xlsx(file_path, self.current_report.title, self.current_report.headers, self.current_report.rows)
        messagebox.showinfo("Экспорт", "XLSX-файл успешно сохранен.", parent=self)
