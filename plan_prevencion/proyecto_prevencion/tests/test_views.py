import pytest
import sys
import os
import django

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plan_prevencion.settings")
django.setup()
from django.db import IntegrityError
from rest_framework.test import APIRequestFactory, force_authenticate
from proyecto_prevencion.apis.views.organismos import api_organismo_list
from proyecto_prevencion.apis.views.indicador import api_rechazar_indicador
from proyecto_prevencion.apis.views.comuna_plan import api_comuna_create
from proyecto_prevencion.apis.views.tipos_medida import api_tipomedida_delete
from proyecto_prevencion.models import Usuario


@pytest.mark.django_db
def test_api_organismo_list_success(mocker):

    factory = APIRequestFactory()
    request = factory.get("/api/organismos/")

    user = mocker.Mock(is_authenticated=True, is_superuser=True)
    force_authenticate(request, user=user)

    organismo1 = mocker.Mock(id=1, nombre="Organismo 1", activo=True)
    organismo2 = mocker.Mock(id=2, nombre="Organismo 2", activo=True)

    mock_filter = mocker.patch(
        "proyecto_prevencion.models.OrganismoPublico.objects.filter"
    )
    mock_filter.return_value = [organismo1, organismo2]

    mock_serializer = mocker.patch(
        "proyecto_prevencion.apis.serializers.OrganismoPublicoSerializer"
    )
    mock_serializer.return_value.data = [
        {"id": 1, "nombre": "Organismo 1"},
        {"id": 2, "nombre": "Organismo 2"},
    ]

    response = api_organismo_list(request)

    assert response.status_code == 200
    assert response.data["success"] is True
    assert len(response.data["data"]) == 2


@pytest.mark.django_db
def test_rechazar_indicador_without_motivo_returns_400(mocker):
    factory = APIRequestFactory()
    user = mocker.Mock(spec=Usuario, is_authenticated=True, is_superuser=True)
    request = factory.post("/api/indicadores/1/rechazar/", data={}, format="json")
    force_authenticate(request, user=user)

    mock_get_object = mocker.patch(
        "proyecto_prevencion.apis.views.indicador.get_object_or_404"
    )

    response = api_rechazar_indicador(request, pk=1)

    assert response.status_code == 400
    assert response.data["success"] is False
    assert "motivo" in response.data["error"].lower()
    mock_get_object.assert_not_called()


@pytest.mark.django_db
def test_api_comuna_create_success(mocker):
    factory = APIRequestFactory()
    user = mocker.Mock(is_authenticated=True, is_superuser=True)
    data = {"nombre_comuna": "Nueva Comuna", "activo": True}
    request = factory.post("/api/comunas/", data=data, format="json")
    force_authenticate(request, user=user)

    mock_serializer_cls = mocker.patch(
        "proyecto_prevencion.apis.views.comuna_plan.ComunaPlanSerializer"
    )
    mock_serializer = mock_serializer_cls.return_value
    mock_serializer.is_valid.return_value = True
    mock_serializer.data = {"id": 1, "nombre_comuna": "Nueva Comuna", "activo": True}
    mock_serializer.save.return_value = None

    response = api_comuna_create(request)

    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["data"] == {
        "id": 1,
        "nombre_comuna": "Nueva Comuna",
        "activo": True,
    }
    mock_serializer.is_valid.assert_called_once()
    mock_serializer.save.assert_called_once()


@pytest.mark.django_db
def test_delete_tipo_medida_integrity_error(mocker):

    factory = APIRequestFactory()
    user = mocker.Mock(is_authenticated=True, is_superuser=True)
    request = factory.delete("/api/tipos-medida/1/")
    force_authenticate(request, user=user)

    mock_medida = mocker.Mock()
    mock_get_object = mocker.patch(
        "proyecto_prevencion.apis.views.tipos_medida.get_object_or_404",
        return_value=mock_medida,
    )

    mock_medida.delete.side_effect = IntegrityError

    response = api_tipomedida_delete(request, pk=1)

    assert response.status_code == 409
    assert response.data["success"] is False
    assert "referenciado" in response.data["message"]
    assert mock_medida.activo is False
    mock_medida.save.assert_called_once()
