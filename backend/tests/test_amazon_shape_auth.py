import unittest
from starlette.testclient import TestClient
from app.main import app
from app.settings import settings


class TestAmazonShapeAuth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoints(self):
        r1 = self.client.get("/health")
        self.assertEqual(r1.status_code, 200)
        self.assertTrue(r1.json().get("ok"))

        r2 = self.client.get("/api/health")
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.json().get("ok"))

    def test_prm_discovery_endpoint(self):
        # RFC 9728 Protected Resource Metadata
        res = self.client.get("/.well-known/oauth-protected-resource")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("resource", data)
        self.assertIn("authorization_servers", data)
        self.assertIn("scopes_supported", data)

    def test_auth_server_metadata_endpoint(self):
        res = self.client.get("/.well-known/oauth-authorization-server")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("authorization_endpoint", data)
        self.assertIn("token_endpoint", data)
        self.assertIn("code_challenge_methods_supported", data)
        self.assertIn("S256", data["code_challenge_methods_supported"])

    def test_oauth_authorize_and_token(self):
        # 1. Authorize
        auth_res = self.client.get("/authorize?client_id=alexa-test&code_challenge=xyz&code_challenge_method=S256")
        self.assertEqual(auth_res.status_code, 200)
        code = auth_res.json().get("code")
        self.assertTrue(code)

        # 2. Token
        token_res = self.client.post("/token", json={"grant_type": "authorization_code", "code": code})
        self.assertEqual(token_res.status_code, 200)
        token_data = token_res.json()
        self.assertIn("access_token", token_data)
        self.assertEqual(token_data.get("token_type"), "Bearer")

    def test_mcp_unauthenticated_401_without_www_authenticate(self):
        # Test Alexa+ invariant: when auth is enabled, unauthenticated /mcp returns 401 without WWW-Authenticate
        original_auth = settings.auth_enabled
        try:
            settings.auth_enabled = True
            res = self.client.post("/mcp", content="{}")
            self.assertEqual(res.status_code, 401)
            # Must NOT include WWW-Authenticate header
            self.assertNotIn("www-authenticate", res.headers)

            # With valid bearer token, passes through auth middleware
            res_auth = self.client.post("/mcp", headers={"Authorization": "Bearer test_token"}, content="{}")
            self.assertNotEqual(res_auth.status_code, 401)
        finally:
            settings.auth_enabled = original_auth


if __name__ == "__main__":
    unittest.main()
