from typing import TypeVar
from unittest.mock import Mock

import pytest
from kubernetes.client import ApiException

from app.adapters.kubernetes.client import KubernetesClient
from app.adapters.kubernetes.exceptions import (
    DeploymentNotFoundError,
    KubernetesConnectionError,
    NamespaceNotFoundError,
    PodNotFoundError,
)
from app.core.settings import Settings
from tests.adapters.kubernetes.conftest import KubernetesMocks

E = TypeVar("E", bound=BaseException, default=BaseException)


def test_initializes_clients(
    settings: Settings, mock_k8s_clients: KubernetesMocks
) -> None:
    KubernetesClient(settings)

    mock_k8s_clients.config.assert_called_once_with(settings)
    mock_k8s_clients.core.assert_called_once()
    mock_k8s_clients.apps.assert_called_once()


def test_list_namespaces(
    kubernetes_client: KubernetesClient, mock_k8s_clients: KubernetesMocks
) -> None:
    namespaces = [Mock(), Mock()]

    core = mock_k8s_clients.core.return_value

    core.list_namespace.return_value.items = namespaces

    result = kubernetes_client.list_namespaces()

    assert result == namespaces

    core.list_namespace.assert_called_once_with()


def test_list_pods(
    kubernetes_client: KubernetesClient, mock_k8s_clients: KubernetesMocks
) -> None:
    pods = [Mock()]

    core = mock_k8s_clients.core.return_value

    core.list_namespaced_pod.return_value.items = pods

    result = kubernetes_client.list_pods("default")

    assert result == pods

    core.list_namespaced_pod.assert_called_once_with("default")


def test_describe_pod(
    kubernetes_client: KubernetesClient, mock_k8s_clients: KubernetesMocks
) -> None:
    pod = Mock()

    core = mock_k8s_clients.core.return_value

    core.read_namespaced_pod.return_value = pod

    result = kubernetes_client.describe_pod("default", "api")

    assert result is pod

    core.read_namespaced_pod.assert_called_once_with(name="api", namespace="default")


def test_get_logs(
    kubernetes_client: KubernetesClient, mock_k8s_clients: KubernetesMocks
) -> None:
    core = mock_k8s_clients.core.return_value

    core.read_namespaced_pod_log.return_value = "hello"

    logs = kubernetes_client.get_pod_logs("default", "api", tail_lines=50)

    assert logs == "hello"

    core.read_namespaced_pod_log.assert_called_once_with(
        name="api", namespace="default", tail_lines=50
    )


def test_list_deployments(
    kubernetes_client: KubernetesClient, mock_k8s_clients: KubernetesMocks
) -> None:
    deployments = [Mock()]

    apps = mock_k8s_clients.apps.return_value

    apps.list_namespaced_deployment.return_value.items = deployments

    result = kubernetes_client.list_deployments("default")

    assert result == deployments

    apps.list_namespaced_deployment.assert_called_once_with("default")


@pytest.mark.parametrize(
    ("resource", "exception"),
    [
        ("namespace", NamespaceNotFoundError),
        ("pod", PodNotFoundError),
        ("deployment", DeploymentNotFoundError),
    ],
)
def test_translate_404(resource: str, exception: type[E]) -> None:
    exc = ApiException(status=404)

    with pytest.raises(exception):
        KubernetesClient._translate_exception(exc, resource)


def test_translate_connection_error() -> None:
    exc = ApiException(status=500)

    with pytest.raises(KubernetesConnectionError):
        KubernetesClient._translate_exception(exc, "pod")
