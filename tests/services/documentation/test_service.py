from app.models.documentation.models import DocumentationPage
from app.services.documentation.service import DocumentationService


class FakeDocumentationRepository:
    def search(self, query: str) -> list[DocumentationPage]:
        assert query == "How do I request a GPU?"
        return [
            DocumentationPage(
                title="GPU pods",
                url="https://nrp.ai/documentation/gpu/",
                excerpt="Request GPU resources in a pod spec.",
            )
        ]


def test_documentation_service_delegates_to_repository() -> None:
    service = DocumentationService(FakeDocumentationRepository())

    pages = service.search("How do I request a GPU?")

    assert pages[0].title == "GPU pods"
