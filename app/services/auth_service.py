from __future__ import annotations

from dataclasses import dataclass

from app.config import AppSettings, get_settings
from app.constants import PERMISSIONS, ROLE_LABELS


@dataclass(frozen=True)
class UserSession:
    username: str
    display_name: str
    role: str

    @property
    def role_label(self) -> str:
        return ROLE_LABELS.get(self.role, self.role)


class AuthService:
    def __init__(self, settings: AppSettings | None = None):
        self.settings = settings or get_settings()

    def authenticate(self, username: str, password: str) -> UserSession | None:
        user = self.settings.users.get(username.strip())
        if not user or user.password != password:
            return None
        return UserSession(username=user.username, display_name=user.display_name, role=user.role)

    def get_permission(self, role: str, section: str) -> str:
        return PERMISSIONS.get(role, {}).get(section, "none")

    def can_read(self, role: str, section: str) -> bool:
        return self.get_permission(role, section) in {"read", "crud"}

    def can_write(self, role: str, section: str) -> bool:
        return self.get_permission(role, section) == "crud"

    def visible_sections(self, role: str) -> list[str]:
        return [section for section, access in PERMISSIONS.get(role, {}).items() if access != "none"]
