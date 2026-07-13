import pytest

from app.core.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(kubernetes_kubeconfig="/tmp/config", kubernetes_context="kind")
