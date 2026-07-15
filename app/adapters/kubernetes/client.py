from app.adapters.kubernetes.config import load_kubernetes_config
from app.core.settings import Settings


class KubernetesClient:
    def __init__(self, settings: Settings) -> None:
        load_kubernetes_config(settings)
