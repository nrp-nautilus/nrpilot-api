class KubernetesError(Exception):
    """Base Kubernetes adapter error."""


class KubernetesConnectionError(KubernetesError):
    """Unable to communicate with the Kubernetes API."""


class NamespaceNotFoundError(KubernetesError):
    """Namespace does not exist."""


class PodNotFoundError(KubernetesError):
    """Pod does not exist."""


class DeploymentNotFoundError(KubernetesError):
    """Deployment does not exist."""
