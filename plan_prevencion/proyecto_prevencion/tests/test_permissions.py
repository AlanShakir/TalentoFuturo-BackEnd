import pytest
import sys
import os
import django

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plan_prevencion.settings")

django.setup()


from proyecto_prevencion.apis.permissions import IsSuperUser, IsRegularApprovedUser


class DummyView:
    pass


@pytest.fixture
def mock_request(mocker):
    return mocker.Mock()


def test_is_superuser_allows_authenticated_superuser(mocker, mock_request):
    user = mocker.Mock()
    user.is_authenticated = True
    user.is_superuser = True
    mock_request.user = user
    perm = IsSuperUser()
    assert perm.has_permission(mock_request, DummyView()) is True


def test_is_regular_approved_user_allows_authenticated_approved_user(
    mocker, mock_request
):
    user = mocker.Mock()
    user.is_authenticated = True
    user.is_superuser = False
    user.aprobado = True
    mock_request.user = user
    perm = IsRegularApprovedUser()
    assert perm.has_permission(mock_request, DummyView()) is True


def test_is_regular_approved_user_denies_superuser(mocker, mock_request):
    user = mocker.Mock()
    user.is_authenticated = True
    user.is_superuser = True
    user.aprobado = True
    mock_request.user = user
    perm = IsRegularApprovedUser()
    assert perm.has_permission(mock_request, DummyView()) is False


def test_permissions_deny_unauthenticated_user(mocker, mock_request):
    user = mocker.Mock()
    user.is_authenticated = False
    user.is_superuser = False
    user.aprobado = False
    mock_request.user = user
    assert IsSuperUser().has_permission(mock_request, DummyView()) is False
    assert IsRegularApprovedUser().has_permission(mock_request, DummyView()) is False


def test_permissions_deny_none_user(mocker, mock_request):
    mock_request.user = None
    assert IsSuperUser().has_permission(mock_request, DummyView()) is False
    assert IsRegularApprovedUser().has_permission(mock_request, DummyView()) is False


def test_is_regular_approved_user_denies_unapproved_user(mocker, mock_request):
    user = mocker.Mock()
    user.is_authenticated = True
    user.is_superuser = False
    user.aprobado = False
    mock_request.user = user
    perm = IsRegularApprovedUser()
    assert perm.has_permission(mock_request, DummyView()) is False
