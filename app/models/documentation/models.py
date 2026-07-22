from pydantic import BaseModel


class DocumentationPage(BaseModel):
    """A relevant excerpt from an official NRP documentation page."""

    title: str
    url: str
    excerpt: str
