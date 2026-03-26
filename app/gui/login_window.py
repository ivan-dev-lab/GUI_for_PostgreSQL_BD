from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class LoginWindow(ttk.Frame):
    def __init__(self, parent, auth_service, on_success):
        super().__init__(parent, padding=24)
        self.auth_service = auth_service
        self.on_success = on_success
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.role_var = tk.StringVar(value="Роль: не определена")
        self._build()

    def _build(self) -> None:
        card = ttk.LabelFrame(self, text="Вход в систему", padding=20)
        card.pack(expand=True)

        ttk.Label(card, text="Логин").grid(row=0, column=0, sticky="w", pady=6, padx=(0, 12))
        username_entry = ttk.Entry(card, textvariable=self.username_var, width=28)
        username_entry.grid(row=0, column=1, pady=6)

        ttk.Label(card, text="Пароль").grid(row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        password_entry = ttk.Entry(card, textvariable=self.password_var, width=28, show="*")
        password_entry.grid(row=1, column=1, pady=6)

        ttk.Button(card, text="Войти", command=self._login).grid(row=2, column=0, columnspan=2, pady=(10, 8))
        ttk.Label(card, textvariable=self.role_var).grid(row=3, column=0, columnspan=2, sticky="w")

        username_entry.focus_set()
        self.bind_all("<Return>", lambda _event: self._login())

    def _login(self) -> None:
        user = self.auth_service.authenticate(self.username_var.get(), self.password_var.get())
        if user is None:
            messagebox.showerror("Ошибка входа", "Неверный логин или пароль.", parent=self)
            return
        self.role_var.set(f"Роль: {user.role_label}")
        self.on_success(user)
