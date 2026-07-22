from collections.abc import Sequence

from app.domain.documentation.ports import DocumentationRepository
from app.models.documentation.models import DocumentationPage


class DocumentationService:
    """Application service for answering questions from NRP documentation."""

    def __init__(self, repository: DocumentationRepository) -> None:
        self._repository = repository

    def search(self, query: str) -> Sequence[DocumentationPage]:
        return self._repository.search(query)
