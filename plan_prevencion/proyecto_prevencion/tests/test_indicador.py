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

from proyecto_prevencion.apis.views.indicador import api_rechazar_indicador, api_indicadores_list, api_aprobar_indicador
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


@pytest.mark.django_db
def test_api_indicadores_list_returns_ordered_list_for_superuser(mocker):
    factory = APIRequestFactory()
    user = mocker.Mock(spec=Usuario, is_authenticated=True, is_superuser=True)
    request = factory.get("/api/indicadores/")
    force_authenticate(request, user=user)

    mock_indicador_qs = mocker.Mock()
    mock_indicador_qs.order_by.return_value = mock_indicador_qs
    mock_select_related = mocker.Mock(return_value=mock_indicador_qs)
    mock_prefetch_related = mocker.Mock(return_value=mock_indicador_qs)
    mock_indicador_manager = mocker.patch(
        "proyecto_prevencion.models.Indicador.objects"
    )
    mock_indicador_manager.select_related.return_value = mock_indicador_qs
    mock_indicador_qs.prefetch_related = mock_prefetch_related
    mock_indicador_qs.order_by = mock_indicador_qs.order_by

    mock_serializer_instance = mocker.Mock()
    mock_serializer_instance.data = [
        {"id": 2, "calculo_indicador": 10.0, "fecha_reporte": "2024-06-01T12:00:00Z"},
        {"id": 1, "calculo_indicador": 5.0, "fecha_reporte": "2024-05-01T12:00:00Z"},
    ]
    mock_serializer = mocker.patch(
        "proyecto_prevencion.apis.views.indicador.IndicadorSerializer",
        return_value=mock_serializer_instance
    )

    response = api_indicadores_list(request)

    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["data"] == mock_serializer_instance.data
    mock_indicador_manager.select_related.assert_called_once_with('medida', 'usuario')
    mock_indicador_qs.prefetch_related.assert_called_once_with('documentos_subidos')
    mock_indicador_qs.order_by.assert_called_once_with('-fecha_reporte')
    mock_serializer.assert_called_once_with(mock_indicador_qs, many=True)


@pytest.mark.django_db
def test_api_aprobar_indicador_updates_status_and_medida(mocker):
    factory = APIRequestFactory()
    user = mocker.Mock(spec=Usuario, is_authenticated=True, is_superuser=True)
    request = factory.post("/api/indicadores/1/aprobar/")
    force_authenticate(request, user=user)

    from datetime import datetime, timedelta
    import pytz
    now = datetime(2024, 6, 10, 12, 0, 0, tzinfo=pytz.UTC)
    mock_timezone_now = mocker.patch("proyecto_prevencion.apis.views.indicador.timezone.now", return_value=now)

    mock_medida = mocker.Mock()
    mock_medida.frecuencia = 'anual'
    mock_medida.proxima_fecha_carga = None

    mock_indicador = mocker.Mock()
    mock_indicador.medida = mock_medida
    mock_indicador.cumple_requisitos = False
    mock_indicador.fecha_aprobacion = None
    mock_indicador.fecha_rechazo = now - timedelta(days=1)
    mock_indicador.motivo_rechazo = "Some reason"
    mock_indicador.save = mocker.Mock()

    mocker.patch("proyecto_prevencion.apis.views.indicador.get_object_or_404", return_value=mock_indicador)

    mock_medida.save = mocker.Mock()

    response = api_aprobar_indicador(request, pk=1)

    assert response.status_code == 200
    assert response.data["success"] is True
    assert "aprobado" in response.data["message"].lower()

    assert mock_indicador.cumple_requisitos is True
    assert mock_indicador.fecha_aprobacion == now
    assert mock_indicador.fecha_rechazo is None
    assert mock_indicador.motivo_rechazo == ""
    mock_indicador.save.assert_called_once()

    assert mock_medida.proxima_fecha_carga == now.date().replace(year=now.date().year + 1)
    mock_medida.save.assert_called_once()


@pytest.mark.django_db
def test_api_rechazar_indicador_with_valid_motivo(mocker):
    factory = APIRequestFactory()
    user = mocker.Mock(spec=Usuario, is_authenticated=True, is_superuser=True)
    motivo = "Falta documento firmado por la autoridad"
    request = factory.post("/api/indicadores/1/rechazar/", data={"motivo": motivo}, format="json")
    force_authenticate(request, user=user)

    from datetime import datetime
    import pytz
    now = datetime(2024, 6, 10, 12, 0, 0, tzinfo=pytz.UTC)
    mocker.patch("proyecto_prevencion.apis.views.indicador.timezone.now", return_value=now)

    mock_indicador = mocker.Mock()
    mock_indicador.cumple_requisitos = True
    mock_indicador.fecha_aprobacion = now
    mock_indicador.fecha_rechazo = None
    mock_indicador.motivo_rechazo = ""
    mock_indicador.save = mocker.Mock()

    mocker.patch("proyecto_prevencion.apis.views.indicador.get_object_or_404", return_value=mock_indicador)

    response = api_rechazar_indicador(request, pk=1)

    assert response.status_code == 200
    assert response.data["success"] is True
    assert "rechazado" in response.data["message"].lower()

    assert mock_indicador.cumple_requisitos is False
    assert mock_indicador.fecha_aprobacion is None
    assert mock_indicador.fecha_rechazo == now
    assert mock_indicador.motivo_rechazo == motivo
    mock_indicador.save.assert_called_once()


@pytest.mark.django_db
def test_api_indicador_approval_or_rejection_server_error_returns_500(mocker):
    factory = APIRequestFactory()
    user = mocker.Mock(spec=Usuario, is_authenticated=True, is_superuser=True)

    request_approve = factory.post("/api/indicadores/1/aprobar/")
    force_authenticate(request_approve, user=user)
    mocker.patch(
        "proyecto_prevencion.apis.views.indicador.get_object_or_404",
        side_effect=Exception("Unexpected DB error"),
    )

    response_approve = api_aprobar_indicador(request_approve, pk=1)
    assert response_approve.status_code == 500
    assert response_approve.data["success"] is False
    assert "Unexpected DB error" in response_approve.data["error"]

    motivo = "Motivo válido"
    request_reject = factory.post("/api/indicadores/1/rechazar/", data={"motivo": motivo}, format="json")
    force_authenticate(request_reject, user=user)
    mocker.patch(
        "proyecto_prevencion.apis.views.indicador.get_object_or_404",
        side_effect=Exception("Unexpected DB error"),
    )

    response_reject = api_rechazar_indicador(request_reject, pk=1)
    assert response_reject.status_code == 500
    assert response_reject.data["success"] is False
    assert "Unexpected DB error" in response_reject.data["error"]