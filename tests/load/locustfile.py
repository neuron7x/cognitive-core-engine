from locust import HttpUser, between, task


class ApiUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def health(self):
        self.client.get("/api/health")

    @task(1)
    def dot(self):
        self.client.post("/api/dot", json={"a": [1, 2, 3], "b": [4, 5, 6]})
