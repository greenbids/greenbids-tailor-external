import locust


class Probes(locust.HttpUser):
    """Health check probes testing.
    There are 3 different probes (liveness, readiness, and startup
    see https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/).
    They should return a JSON payload on GET request.
    """

    wait_time = locust.between(10, 15)
    fixed_count = 1

    @locust.task
    def test_startup(self):
        self.client.get("/healthz/startup")

    @locust.task
    def test_readiness(self):
        self.client.get("/healthz/readiness")

    @locust.task
    def test_liveness(self):
        self.client.get("/healthz/liveness")
