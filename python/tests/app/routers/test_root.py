import time
import unittest

from fastapi.testclient import TestClient

from greenbids.tailor.core.app import app


class TestRoot(unittest.TestCase):
    def setUp(self) -> None:

        self.client = self.enterContext(TestClient(app))
        while self.client.get("/healthz/readiness").status_code != 200:
            time.sleep(0.001)
        return super().setUp()

    def test_predict_empty(self):
        response = self.client.put("/", json=[])
        self.assertListEqual(response.json(), [])
        self.assertEqual(response.status_code, 200)
