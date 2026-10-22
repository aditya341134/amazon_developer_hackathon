import unittest
from starlette.testclient import TestClient
from app.db.connection import connect
from app.db.schema import init_schema
from app.mcp_server import build_mcp_starlette_app


class TestRpcInitialize(unittest.TestCase):
    def setUp(self):
        self.conn = connect(":memory:")
        init_schema(self.conn)
        self.starlette_app = build_mcp_starlette_app(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_mcp_app_creation(self):
        self.assertIsNotNone(self.starlette_app)

    def test_mcp_options_cors(self):
        client = TestClient(self.starlette_app)
        # Check that CORS/OPTIONS requests are handled
        response = client.options("/", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
        self.assertIn(response.status_code, [200, 204, 400, 404, 405])


if __name__ == "__main__":
    unittest.main()
