from unittest.mock import MagicMock, patch

from app.adapters.kubernetes.config import load_kubernetes_config
from app.core.settings import Settings


@patch("app.adapters.kubernetes.config.config.load_kube_config")
def test_load_local(mock_loader: MagicMock) -> None:
    settings = Settings(kubernetes_kubeconfig="test-config", kubernetes_context="kind")
    load_kubernetes_config(settings)

    mock_loader.assert_called_once_with(config_file="test-config", context="kind")
