from collections.abc import Generator
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from app.adapters.kubernetes.client import KubernetesClient
from app.core.settings import Settings


@dataclass
class KubernetesMocks:
    config: MagicMock
    core: MagicMock
    apps: MagicMock


@pytest.fixture
def mock_k8s_clients() -> Generator[KubernetesMocks]:
    with (
        patch("app.adapters.kubernetes.client.load_kubernetes_config") as mock_config,
        patch("app.adapters.kubernetes.client.client.CoreV1Api") as mock_core,
        patch("app.adapters.kubernetes.client.client.AppsV1Api") as mock_apps,
    ):
        yield KubernetesMocks(config=mock_config, core=mock_core, apps=mock_apps)


@pytest.fixture
def kubernetes_client(
    settings: Settings, mock_k8s_clients: KubernetesMocks
) -> KubernetesClient:
    return KubernetesClient(settings)
