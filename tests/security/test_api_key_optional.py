import importlib

import pytest

from cognitive_core import config
from cognitive_core.api import auth


@pytest.mark.integration
def test_health_without_api_key(api_client, monkeypatch):
    monkeypatch.delenv("COG_API_KEY", raising=False)
    importlib.reload(config)
    importlib.reload(auth)

    response = api_client.get("/api/health")
    assert response.status_code == 500
