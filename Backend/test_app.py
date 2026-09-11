import unittest
import json
import uuid
from main import app

class FlaskAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "SecurePassword123!"
        self.test_phone = "1234567890"

    def test_01_root_endpoint(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")

    def test_02_register_success(self):
        response = self.app.post(
            "/api/register",
            data=json.dumps({
                "email": self.test_email,
                "password": self.test_password,
                "phonenum": self.test_phone
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("user_id", data)
        self.assertEqual(data["user"]["email"], self.test_email)

    def test_03_register_duplicate(self):
        # First register
        self.app.post(
            "/api/register",
            data=json.dumps({
                "email": self.test_email,
                "password": self.test_password,
                "phonenum": self.test_phone
            }),
            content_type="application/json"
        )
        # Attempt second register with same email
        response = self.app.post(
            "/api/register",
            data=json.dumps({
                "email": self.test_email,
                "password": "AnotherPassword123",
                "phonenum": self.test_phone
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("detail", data)

    def test_04_login_success(self):
        # Register user
        self.app.post(
            "/api/register",
            data=json.dumps({
                "email": self.test_email,
                "password": self.test_password,
                "phonenum": self.test_phone
            }),
            content_type="application/json"
        )
        # Login
        response = self.app.post(
            "/api/login",
            data=json.dumps({
                "email": self.test_email,
                "password": self.test_password
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["email"], self.test_email)

        # Verify /api/me with token
        token = data["access_token"]
        me_response = self.app.get(
            "/api/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(me_response.status_code, 200)
        me_data = me_response.get_json()
        self.assertEqual(me_data["email"], self.test_email)

    def test_05_login_invalid_password(self):
        # Register user
        self.app.post(
            "/api/register",
            data=json.dumps({
                "email": self.test_email,
                "password": self.test_password
            }),
            content_type="application/json"
        )
        # Login with wrong password
        response = self.app.post(
            "/api/login",
            data=json.dumps({
                "email": self.test_email,
                "password": "WrongPassword999!"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    unittest.main()
