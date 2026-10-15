import unittest
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi.security import HTTPAuthorizationCredentials

from app.config import security


class EnterpriseIsolationSecurityTest(unittest.TestCase):
    def test_get_logged_in_user_extracts_enterprise_id(self):
        payload = {
            "sub": "42",
            "role": "Recursos Humanos",
            "enterprise_id": 99,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
        }
        token = jwt.encode(payload, security.SECRET_KEY, algorithm=security.ALGORITHM)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        logged_user = security.get_logged_in_user(credentials)

        self.assertEqual(logged_user["user_id"], 42)
        self.assertEqual(logged_user["role"], "Recursos Humanos")
        self.assertEqual(logged_user["enterprise_id"], 99)

    def test_create_access_token_preserves_enterprise_id(self):
        data = {
            "sub": "10",
            "user_id": 10,
            "role": "Gestor",
            "enterprise_id": 7
        }
        token = security.create_access_token(data)
        decoded = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])

        self.assertEqual(decoded["enterprise_id"], 7)
        self.assertEqual(decoded["sub"], "10")


if __name__ == "__main__":
    unittest.main()
