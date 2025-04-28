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

from proyecto_prevencion.apis.views.indicador import api_rechazar_indicador
from proyecto_prevencion.models import Usuario


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
