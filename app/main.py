from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.config import get_settings
from app.gui.login_window import LoginWindow
from app.gui.main_window import MainWindow
from app.services.auth_service import AuthService
from app.services.contract_service import ContractService
from app.services.flower_service import FlowerService
from app.services.purchase_order_service import PurchaseOrderService
from app.services.report_service import ReportService
from app.services.supplier_service import SupplierService


def build_services() -> dict:
    return {
        "supplier_service": SupplierService(),
        "flower_service": FlowerService(),
        "contract_service": ContractService(),
        "purchase_order_service": PurchaseOrderService(),
        "report_service": ReportService(),
    }


def main() -> None:
    settings = get_settings()
    auth_service = AuthService(settings)
    services = build_services()

    root = tk.Tk()
    root.title(settings.app_title)
    root.geometry("1280x760")
    root.minsize(1100, 700)

    style = ttk.Style(root)
    try:
        style.theme_use("vista")
    except tk.TclError:
        pass

    def open_main_window(user) -> None:
        for child in root.winfo_children():
            child.destroy()
        root.title(f"{settings.app_title} | {user.role_label}")
        main_window = MainWindow(root, user, auth_service, services)
        main_window.pack(fill="both", expand=True)

    login = LoginWindow(root, auth_service, open_main_window)
    login.pack(fill="both", expand=True)
    root.mainloop()
