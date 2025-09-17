import os
from typing import Optional

from locust import HttpUser, between, events, task


@events.init_command_line_parser.add_listener
def _(parser) -> None:
    """Expose an --api-key option and LOCUST_API_KEY env var for the load test."""

    parser.add_argument(
        "--api-key",
        default=None,
        env_var="LOCUST_API_KEY",
        help="API key used for the X-API-Key header",
    )


class ApiUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def _resolve_api_key(self) -> Optional[str]:
        """Return the API key from the environment or Locust options."""

        api_key = os.getenv("COG_API_KEY")
        if api_key:
            return api_key

        parsed_options = getattr(self.environment, "parsed_options", None)
        if parsed_options is not None:
            return getattr(parsed_options, "api_key", None)

        return None

    def on_start(self) -> None:
        api_key = self._resolve_api_key()
        if not api_key:
            raise RuntimeError(
                "COG_API_KEY environment variable or Locust --api-key option must be provided"
            )

        self.client.headers.update({"X-API-Key": api_key})

    @task(3)
    def health(self):
        self.client.get("/api/health")

    @task(1)
    def dot(self):
        self.client.post("/api/dot", json={"a": [1, 2, 3], "b": [4, 5, 6]})
