import pytest
import sys
import os
import django

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plan_prevencion.settings")
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from proyecto_prevencion.apis.views.medida import (
    api_medida_list,
    api_medida_create,
    api_medida_update,
    api_medida_delete,
)
from proyecto_prevencion.models import Medida, Usuario


@pytest.mark.django_db
def test_api_medida_permission_denied_for_non_superuser(mocker):
    factory = APIRequestFactory()
    user = mocker.Mock(spec=Usuario, is_authenticated=True, is_superuser=False)
    endpoints = [
        ("get", api_medida_list, (), {}),
        ("post", api_medida_create, (), {"tipo_medida": 1, "organismo": 1}),
        ("put", api_medida_update, (1,), {"nombre_corto": "Test"}),
        ("delete", api_medida_delete, (1,), {}),
    ]
    for method, view_func, args, data in endpoints:
        request = (
            getattr(factory, method)("/api/medidas/", data, format="json")
            if method in ["post", "put"]
            else getattr(factory, method)("/api/medidas/")
        )
        force_authenticate(request, user=user)
        response = view_func(request, *args)
        assert response.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        )


@pytest.mark.django_db
def test_api_medida_delete_referenced_sets_inactive(mocker):
    factory = APIRequestFactory()
    user = mocker.Mock(spec=Usuario, is_authenticated=True, is_superuser=True)
    request = factory.delete("/api/medidas/1/")
    force_authenticate(request, user=user)

    medida_obj = mocker.Mock(spec=Medida, id=1, activo=True)
    mock_get_object = mocker.patch(
        "proyecto_prevencion.apis.views.medida.get_object_or_404",
        return_value=medida_obj,
    )

    def delete_side_effect():
        from django.db import IntegrityError

        raise IntegrityError()

    medida_obj.delete.side_effect = delete_side_effect

    response = api_medida_delete(request, pk=1)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.data["success"] is False
    assert "desactivó" in response.data["message"]
    assert medida_obj.save.called
    mock_get_object.assert_called_once_with(Medida, pk=1)
