from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kubernetes_host: str | None = None
    kubernetes_api_key: str | None = None
    nrp_llm_token: str | None = None
    nrp_llm_base_url: str | None = None
    model: str = "qwen3-small"
