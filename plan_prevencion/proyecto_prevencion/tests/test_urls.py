import pytest
import sys
import os
import django
from django.http import HttpResponse
from django.urls import reverse
from django.test import Client

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plan_prevencion.settings")
django.setup()

from django.core.asgi import get_asgi_application


@pytest.mark.django_db
def test_home_page_accessible(mocker):
    mock_render = mocker.patch("proyecto_prevencion.views.render")
    mock_render.return_value = HttpResponse("Home Page", status=200)

    client = Client()
    url = reverse("home")
    response = client.get(url)

    mock_render.assert_called_once()
    assert response.status_code == 200
    assert response.content == b"Home Page"


@pytest.mark.django_db
class TestURLs:
    def setup_method(self):
        self.client = Client()

    def test_home_page_accessible(self):
        """Verifica que la página de inicio sea accesible."""
        response = self.client.get(reverse("home"))
        assert response.status_code == 200

    def test_logout_redirect(self):
        """Verifica que la vista de logout redirige correctamente."""
        response = self.client.get(reverse("admin_logout"))
        assert response.status_code in [302, 200]

    def test_api_docs_accessible(self):
        """Verifica que la documentación Swagger es accesible."""
        response = self.client.get(reverse("swagger-ui"))
        assert response.status_code == 200

    def test_api_schema_accessible(self):
        """Verifica que el esquema de la API es accesible."""
        response = self.client.get(reverse("schema"))
        assert response.status_code == 200

    def test_token_obtain(self):
        """Verifica que la ruta para obtener tokens JWT esté configurada."""
        response = self.client.post(
            reverse("token_obtain_pair"),
            data={"username": "user", "password": "password"},
        )
        assert response.status_code == 401

    def test_token_refresh(self):
        """Verifica que la ruta para refrescar tokens JWT esté configurada."""
        response = self.client.post(
            reverse("token_refresh"), data={"refresh": "invalid_token"}
        )
        assert response.status_code == 401

    def test_invalid_url(self):
        """Verifica que una URL inexistente devuelve 404."""
        response = self.client.get("/invalid-url/")
        assert response.status_code == 404


def test_asgi_import():
    """Verifica que el archivo asgi.py se pueda importar correctamente."""
    try:
        from plan_prevencion.asgi import application
    except Exception as e:
        pytest.fail(f"Error al importar el archivo asgi.py: {e}")


def test_asgi_application_instance():
    """Verifica que `application` sea una instancia válida de ASGI."""
    from plan_prevencion.asgi import application

    assert isinstance(
        application, type(get_asgi_application())
    ), "El objeto `application` no es válido."


def test_django_settings_environment_variable():
    """Verifica que la variable de entorno DJANGO_SETTINGS_MODULE esté configurada correctamente."""
    from plan_prevencion.asgi import application 
    assert os.getenv('DJANGO_SETTINGS_MODULE') == 'plan_prevencion.settings', (
        "La variable de entorno DJANGO_SETTINGS_MODULE no está configurada correctamente."
    )
