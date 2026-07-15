from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kubernetes_kubeconfig: str | None = None
    kubernetes_context: str | None = None
