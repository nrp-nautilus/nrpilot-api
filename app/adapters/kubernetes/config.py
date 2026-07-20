from kubernetes.client import ApiClient, Configuration

from app.core.settings import Settings


def load_kubernetes_config(settings: Settings) -> ApiClient:

    configuration = Configuration(host=settings.kubernetes_host)
    configuration.api_key["BearerToken"] = f"Bearer {settings.kubernetes_api_key}"

    return ApiClient(configuration)
