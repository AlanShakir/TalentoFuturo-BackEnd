import pytest
import sys
import os
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plan_prevencion.settings')

django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from proyecto_prevencion.apis.views.admins_usuarios import api_usuarios_list, api_aprobar_usuario
from proyecto_prevencion.models import Usuario

@pytest.mark.django_db
def test_api_usuarios_list_returns_grouped_users(mocker):
    factory = APIRequestFactory()
    user = mocker.Mock(spec=Usuario, is_authenticated=True, is_superuser=True)
    request = factory.get('/api/admin/usuarios/')
    force_authenticate(request, user=user)

    approved_user = mocker.Mock(spec=Usuario, id=1, email='usuario1@org.com', aprobado=True)
    pending_user = mocker.Mock(spec=Usuario, id=2, email='usuario2@org.com', aprobado=False)
    mock_filter = mocker.patch('proyecto_prevencion.models.Usuario.objects.filter')
    mock_filter.side_effect = [
        [approved_user], 
        [pending_user],  
    ]

    mock_serializer = mocker.patch('proyecto_prevencion.apis.views.admins_usuarios.UsuarioSerializer')
    mock_serializer.side_effect = lambda users, many: mocker.Mock(data=[
        {"id": u.id, "email": u.email, "aprobado": u.aprobado} for u in users
    ])

    response = api_usuarios_list(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert "data" in response.data
    assert response.data["data"]["approved_users"] == [
        {"id": 1, "email": "usuario1@org.com", "aprobado": True}
    ]
    assert response.data["data"]["pending_users"] == [
        {"id": 2, "email": "usuario2@org.com", "aprobado": False}
    ]


@pytest.mark.django_db
def test_api_aprobar_usuario_approves_and_sends_email(mocker):

    factory = APIRequestFactory()
    admin_user = mocker.Mock(spec=Usuario, is_authenticated=True, is_superuser=True)
    request = factory.post('/api/admin/usuarios/aprobar/1/')
    force_authenticate(request, user=admin_user)

    usuario_obj = mocker.Mock(spec=Usuario, id=1, email='usuario1@org.com', aprobado=False)
    mock_get_object_or_404 = mocker.patch(
        'proyecto_prevencion.apis.views.admins_usuarios.get_object_or_404',
        return_value=usuario_obj
    )

    mock_send_mail = mocker.patch(
        'proyecto_prevencion.apis.views.admins_usuarios.send_mail',
        return_value=1 
    )

    response = api_aprobar_usuario(request, user_id=1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert response.data["message"] == "Usuario aprobado correctamente."
    assert usuario_obj.aprobado is True
    assert usuario_obj.save.called
    mock_send_mail.assert_called_once_with(
        'Cuenta Aprobada',
        'Su cuenta ha sido aprobada y ya puede ingresar a la plataforma.',
        'grupo1@backend-python.com',
        [usuario_obj.email],
        fail_silently=False,
    )
