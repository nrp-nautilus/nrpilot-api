from app.adapters.kubernetes.config import load_kubernetes_config
from app.core.settings import Settings


def test_load_local(settings: Settings) -> None:
    api_client = load_kubernetes_config(settings)

    assert api_client.configuration.api_key == {"BearerToken": "Bearer qwertyuiop"}
    assert api_client.configuration.host == "http://localhost"
