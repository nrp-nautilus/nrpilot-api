import re
from collections.abc import Sequence
from html.parser import HTMLParser
from time import perf_counter
from typing import Final
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from app.core.logging import get_logger
from app.domain.documentation.exceptions import DocumentationUnavailableError
from app.domain.documentation.ports import DocumentationRepository
from app.models.documentation.models import DocumentationPage

logger = get_logger(__name__)

_USER_AGENT: Final = "NRPilot/0.1 documentation retrieval"
_MAX_EXCERPT_LENGTH: Final = 2_000


class NRPDocumentationClient(DocumentationRepository):
    """Read-only retrieval client for the official NRP documentation site."""

    def __init__(
        self,
        documentation_url: str,
        timeout_seconds: float,
        max_results: int,
    ) -> None:
        self._documentation_url = _canonical_url(documentation_url)
        self._timeout_seconds = timeout_seconds
        self._max_results = max_results
        self._documentation_origin = _origin(self._documentation_url)
        self._documentation_path = urlsplit(self._documentation_url).path.rstrip("/")

    def search(self, query: str) -> Sequence[DocumentationPage]:
        started_at = perf_counter()
        logger.debug(
            "nrp_documentation_search_started",
            query_length=len(query),
            max_results=self._max_results,
        )
        links = self._documentation_links()
        candidates = _rank_links(links, query, self._max_results)
        logger.debug(
            "nrp_documentation_links_ranked",
            query_term_count=len(_query_terms(query)),
            candidates=[
                {"url": url, "score": _link_score(title, url, query)}
                for title, url in candidates
            ],
        )
        pages: list[DocumentationPage] = []

        for title, url in candidates:
            page_title, content = self._get_page(url)
            if content:
                pages.append(
                    DocumentationPage(
                        title=page_title or title,
                        url=url,
                        excerpt=content[:_MAX_EXCERPT_LENGTH],
                    )
                )
        logger.debug(
            "nrp_documentation_search_completed",
            result_count=len(pages),
            duration_seconds=perf_counter() - started_at,
        )
        return pages

    def _documentation_links(self) -> list[tuple[str, str]]:
        _, html = self._fetch(self._documentation_url)
        parser = _PageParser()
        parser.feed(html)

        links = [(parser.title or "NRP documentation", self._documentation_url)]
        for title, href in parser.links:
            url = _canonical_url(urljoin(self._documentation_url, href))
            if self._is_documentation_url(url):
                links.append((title, url))
        unique_links = list(dict.fromkeys(links))
        logger.debug(
            "nrp_documentation_links_discovered",
            documentation_url=self._documentation_url,
            link_count=len(unique_links),
        )
        return unique_links

    def _get_page(self, url: str) -> tuple[str, str]:
        _, html = self._fetch(url)
        parser = _PageParser()
        parser.feed(html)
        logger.debug(
            "nrp_documentation_page_parsed",
            url=url,
            title=parser.title,
            content_length=len(parser.content),
        )
        return parser.title, parser.content

    def _fetch(self, url: str) -> tuple[str, str]:
        request = Request(url, headers={"User-Agent": _USER_AGENT})
        started_at = perf_counter()
        logger.debug("nrp_documentation_fetch_started", url=url)
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:  # noqa: S310
                charset = response.headers.get_content_charset() or "utf-8"
                body = response.read()
                final_url = response.geturl()
                logger.debug(
                    "nrp_documentation_fetch_completed",
                    url=url,
                    final_url=final_url,
                    status_code=response.getcode(),
                    response_bytes=len(body),
                    duration_seconds=perf_counter() - started_at,
                )
                return final_url, body.decode(charset, errors="replace")
        except OSError as exc:
            logger.warning("nrp_documentation_request_failed", url=url)
            raise DocumentationUnavailableError(
                "NRP documentation is currently unavailable"
            ) from exc

    def _is_documentation_url(self, url: str) -> bool:
        parts = urlsplit(url)
        return _origin(url) == self._documentation_origin and parts.path.startswith(
            self._documentation_path
        )


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.links: list[tuple[str, str]] = []
        self.content = ""
        self._in_title = False
        self._in_main = False
        self._current_link: str | None = None
        self._current_link_text: list[str] = []
        self._content_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "main":
            self._in_main = True
        elif tag == "a" and (href := attributes.get("href")):
            self._current_link = href
            self._current_link_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "main":
            self._in_main = False
            self.content = " ".join(self._content_parts).strip()
        elif tag == "a" and self._current_link:
            text = " ".join(self._current_link_text).strip()
            if text:
                self.links.append((text, self._current_link))
            self._current_link = None
            self._current_link_text = []

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self._in_title:
            self.title = f"{self.title} {text}".strip()
        if self._current_link is not None:
            self._current_link_text.append(text)
        if self._in_main:
            self._content_parts.append(text)


def _rank_links(
    links: Sequence[tuple[str, str]], query: str, max_results: int
) -> list[tuple[str, str]]:
    ranked = sorted(
        links,
        key=lambda link: (
            -_link_score(link[0], link[1], query),
            link[0],
        ),
    )
    return ranked[:max_results]


def _link_score(title: str, url: str, query: str) -> int:
    searchable_text = f"{title} {url}".lower()
    return sum(term in searchable_text for term in _query_terms(query))


def _query_terms(query: str) -> set[str]:
    return {
        term.lower() for term in re.findall(r"[A-Za-z0-9]+", query) if len(term) > 1
    }


def _canonical_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"
