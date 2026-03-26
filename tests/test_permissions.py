from __future__ import annotations

from app.services.auth_service import AuthService


def test_role_permissions_matrix():
    service = AuthService()

    assert service.can_write("purchase_manager", "suppliers") is True
    assert service.can_write("purchase_manager", "contracts") is False
    assert service.can_read("sales_manager", "flowers") is True
    assert service.can_write("sales_manager", "purchase_orders") is True
    assert service.can_read("warehouse_manager", "suppliers") is False
    assert service.can_read("analyst", "reports") is True
    assert service.can_write("analyst", "reports") is False


def test_authenticate_demo_user():
    service = AuthService()
    user = service.authenticate("purchase_manager", "purchase123")

    assert user is not None
    assert user.role == "purchase_manager"
