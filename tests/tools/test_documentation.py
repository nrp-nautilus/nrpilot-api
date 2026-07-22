from app.models.documentation.models import DocumentationPage
from app.services.documentation.service import DocumentationService
from app.tools.documentation import build_documentation_tools


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


def test_documentation_tool_returns_source_url_and_excerpt() -> None:
    service = DocumentationService(FakeDocumentationRepository())
    tool = build_documentation_tools(service)[0]

    result = tool.invoke({"query": "How do I request a GPU?"})

    assert '"title":"GPU pods"' in result
    assert '"url":"https://nrp.ai/documentation/gpu/"' in result
