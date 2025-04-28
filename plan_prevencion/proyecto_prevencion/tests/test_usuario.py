import os
import sys
import django
import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from proyecto_prevencion.apis.views.usuario import api_register, api_dashboard
from proyecto_prevencion.models import Usuario

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plan_prevencion.settings")
django.setup()


@pytest.mark.django_db
def test_api_register_success(mocker):
    factory = APIRequestFactory()
    valid_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123",
        "first_name": "Test",
        "last_name": "User",
        "rut_usuario": "12345678-9",
        "organismo": 1,
    }
    request = factory.post("/api/usuario/register/", data=valid_data, format="json")

    mock_serializer_cls = mocker.patch(
        "proyecto_prevencion.apis.views.usuario.UsuarioRegistrationSerializer"
    )
    mock_serializer = mocker.Mock()
    mock_serializer.is_valid.return_value = True
    mock_serializer.save.return_value = None
    mock_serializer.errors = {}
    mock_serializer_cls.return_value = mock_serializer

    response = api_register(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert (
        response.data["message"]
        == "Registro exitoso. Se le avisará cuando su cuenta sea validada."
    )
    mock_serializer.is_valid.assert_called_once()
    mock_serializer.save.assert_called_once()


@pytest.mark.django_db
def test_api_dashboard_success(mocker):
    factory = APIRequestFactory()
    user = mocker.Mock(
        spec=Usuario,
        is_authenticated=True,
        is_superuser=False,
        aprobado=True,
        organismo=mocker.Mock(id=1),
    )
    request = factory.get("/api/usuario/dashboard/")
    force_authenticate(request, user=user)

    medida1 = mocker.Mock(id=1, organismo=user.organismo, activo=True)
    medida2 = mocker.Mock(id=2, organismo=user.organismo, activo=True)
    medidas_qs = [medida1, medida2]
    mock_medida_manager = mocker.patch(
        "proyecto_prevencion.apis.views.usuario.Medida.objects"
    )
    mock_prefetch = mocker.Mock()
    mock_prefetch.__iter__ = lambda self: iter(medidas_qs)
    mock_medida_manager.filter.return_value.prefetch_related.return_value = (
        mock_prefetch
    )

    mock_medida_serializer = mocker.patch(
        "proyecto_prevencion.apis.views.usuario.MedidaSerializer"
    )
    mock_medida_serializer.side_effect = lambda medida: mocker.Mock(
        data={"id": medida.id, "nombre_corto": f"Medida {medida.id}"}
    )

    indicador_aprobado = mocker.Mock(
        id=10,
        cumple_requisitos=True,
        fecha_reporte="2024-06-01T12:00:00Z",
        fecha_rechazo=None,
    )
    indicador_rechazado = mocker.Mock(
        id=11,
        cumple_requisitos=False,
        fecha_reporte="2024-06-02T12:00:00Z",
        fecha_rechazo="2024-06-03T12:00:00Z",
    )

    def indicador_filter_side_effect(*args, **kwargs):
        if kwargs.get("medida") == medida1:
            return mocker.Mock(
                order_by=lambda *a, **k: mocker.Mock(first=lambda: indicador_aprobado)
            )
        elif kwargs.get("medida") == medida2:
            return mocker.Mock(order_by=lambda *a, **k: mocker.Mock(first=lambda: None))
        return mocker.Mock(order_by=lambda *a, **k: mocker.Mock(first=lambda: None))

    mock_indicador_manager = mocker.patch(
        "proyecto_prevencion.apis.views.usuario.Indicador.objects"
    )
    mock_indicador_manager.filter.side_effect = indicador_filter_side_effect

    response = api_dashboard(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    data = response.data["data"]
    assert data["approved"] == [
        {
            "medida": {"id": medida1.id, "nombre_corto": f"Medida {medida1.id}"},
            "indicador_id": indicador_aprobado.id,
            "cumple_requisitos": True,
            "fecha_reporte": indicador_aprobado.fecha_reporte,
        }
    ]
    assert data["pending_completion"] == [
        {"medida": {"id": medida2.id, "nombre_corto": f"Medida {medida2.id}"}}
    ]
    assert data["pending_review"] == []
    assert data["rejected"] == []


@pytest.mark.django_db
def test_api_register_validation_errors(mocker):
    factory = APIRequestFactory()
    invalid_data = {
        "username": "",
        "email": "",
        "password": "short",
        "first_name": "",
        "last_name": "",
        "rut_usuario": "",
        "organismo": "",
    }
    request = factory.post("/api/usuario/register/", data=invalid_data, format="json")

    mock_serializer_cls = mocker.patch(
        "proyecto_prevencion.apis.views.usuario.UsuarioRegistrationSerializer"
    )
    mock_serializer = mocker.Mock()
    mock_serializer.is_valid.return_value = False
    mock_serializer.errors = {
        "email": ["Este campo es obligatorio."],
        "password": ["Debe tener al menos 8 caracteres."],
    }
    mock_serializer_cls.return_value = mock_serializer

    response = api_register(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert "errors" in response.data
    assert response.data["errors"] == {
        "email": ["Este campo es obligatorio."],
        "password": ["Debe tener al menos 8 caracteres."],
    }
    mock_serializer.is_valid.assert_called_once()
    mock_serializer.save.assert_not_called()
