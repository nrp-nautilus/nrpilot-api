from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kubernetes_host: str | None = None
    kubernetes_api_key: SecretStr | None = None
    nrp_llm_token: SecretStr | None = None
    nrp_llm_base_url: str | None = None
    model: str = "qwen3-small"
    nrp_documentation_url: str = "https://nrp.ai/documentation/"
    nrp_documentation_timeout_seconds: float = 10.0
    nrp_documentation_max_results: int = 3
    log_level: str = "INFO"
