import locust


class Connectivity(locust.FastHttpUser):
    """Connectivity testing."""

    weight = 0.001

    @locust.task
    def test_ping(self):
        self.client.get("/ping")
