from collections.abc import Sequence
from typing import Protocol

from app.models.documentation.models import DocumentationPage


class DocumentationRepository(Protocol):
    """Provides relevant, authoritative NRP documentation pages."""

    def search(self, query: str) -> Sequence[DocumentationPage]: ...
