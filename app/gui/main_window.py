from __future__ import annotations

from tkinter import messagebox, ttk

from app.gui.contracts_frame import ContractsFrame
from app.gui.flowers_frame import FlowersFrame
from app.gui.purchase_orders_frame import PurchaseOrdersFrame
from app.gui.reports_frame import ReportsFrame
from app.gui.suppliers_frame import SuppliersFrame


class MainWindow(ttk.Frame):
    def __init__(self, parent, user, auth_service, services: dict):
        super().__init__(parent, padding=8)
        self.parent = parent
        self.user = user
        self.auth_service = auth_service
        self.services = services
        self._build()

    def _build(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 8))
        ttk.Label(
            header,
            text=f"Пользователь: {self.user.display_name} | Роль: {self.user.role_label}",
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left")
        ttk.Button(header, text="Выход", command=self._exit_app).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        if self.auth_service.can_read(self.user.role, "suppliers"):
            notebook.add(
                SuppliersFrame(
                    notebook,
                    supplier_service=self.services["supplier_service"],
                    can_write=self.auth_service.can_write(self.user.role, "suppliers"),
                ),
                text="Поставщики",
            )

        if self.auth_service.can_read(self.user.role, "flowers"):
            notebook.add(
                FlowersFrame(
                    notebook,
                    flower_service=self.services["flower_service"],
                    supplier_service=self.services["supplier_service"],
                    can_write=self.auth_service.can_write(self.user.role, "flowers"),
                ),
                text="Цветы",
            )

        if self.auth_service.can_read(self.user.role, "contracts"):
            notebook.add(
                ContractsFrame(
                    notebook,
                    contract_service=self.services["contract_service"],
                    can_write=self.auth_service.can_write(self.user.role, "contracts"),
                ),
                text="Договоры",
            )

        if self.auth_service.can_read(self.user.role, "purchase_orders"):
            notebook.add(
                PurchaseOrdersFrame(
                    notebook,
                    purchase_order_service=self.services["purchase_order_service"],
                    contract_service=self.services["contract_service"],
                    flower_service=self.services["flower_service"],
                    can_write=self.auth_service.can_write(self.user.role, "purchase_orders"),
                ),
                text="Заказы",
            )

        if self.auth_service.can_read(self.user.role, "reports"):
            notebook.add(
                ReportsFrame(
                    notebook,
                    report_service=self.services["report_service"],
                ),
                text="Отчеты",
            )

    def _exit_app(self) -> None:
        if messagebox.askyesno("Выход", "Завершить работу приложения?", parent=self):
            self.parent.destroy()
