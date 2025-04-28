from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken
from .models import Usuario, OrganismoPublico

# Create your tests here.
class AdminUsuariosAPITest(APITestCase):
    def setUp(self):
        # Creamos el organismo
        self.org = OrganismoPublico.objects.create(nombre_organismo="Talento Futuro")

        # Creamos un superusuario con create_superuser
        self.admin = Usuario.objects.create_superuser(
            username="admin",
            email="admin@org.com",
            password="password123",
            rut_usuario="00000000-0",
            organismo=self.org,
            aprobado=True,
        )

        # Creamos un usuario aprobado
        self.approved_user = Usuario.objects.create_user(
            username="usuario1",
            email="user1@org.com",
            password="pass123",
            rut_usuario="15637908-1",
            organismo=self.org,
            aprobado=True,
        )

        # Y un usuario pendiente
        self.pending_user = Usuario.objects.create_user(
            username="usuario2",
            email="user2@org.com",
            password="pass123",
            rut_usuario="15637908-2",
            organismo=self.org,
            aprobado=False,
        )

        # Autenticamos al admin por JWT
        token = AccessToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_list_usuarios(self):
        url = reverse("api_admin_usuarios")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["success"])

        approved = resp.data["data"]["approved_users"]
        pending = resp.data["data"]["pending_users"]

        self.assertEqual(len(approved), 1)
        self.assertEqual(approved[0]["email"], self.approved_user.email)

        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["email"], self.pending_user.email)

    def test_aprobar_usuario(self):
        url = reverse("api_aprobar_usuario", kwargs={"user_id": self.pending_user.id})
        resp = self.client.post(url)

        self.pending_user.refresh_from_db()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["success"])
        self.assertTrue(self.pending_user.aprobado)

    def test_desactivar_usuario(self):
        url = reverse("api_desactivar_usuario", kwargs={"user_id": self.approved_user.id})
        resp = self.client.post(url)

        self.approved_user.refresh_from_db()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["success"])
        self.assertFalse(self.approved_user.aprobado)

    def test_permisos(self):
        url = reverse("api_admin_usuarios")

        # Sin token → 401
        self.client.credentials()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # Con usuario NO superuser → 403
        normal_token = AccessToken.for_user(self.approved_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {normal_token}")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
