from kubernetes import config

from app.core.settings import Settings


def load_kubernetes_config(settings: Settings) -> None:
    """
    Configure the Kubernetes Python client.

    Loads the user's kubeconfig.
    """
    config.load_kube_config(
        config_file=settings.kubernetes_kubeconfig, context=settings.kubernetes_context
    )
