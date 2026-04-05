from html.parser import HTMLParser
from typing import List, Optional, Tuple


class ReadableTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._chunks: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if not self._skip_depth and tag in {"br", "p", "div", "li", "section", "article", "h1", "h2", "h3"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1
        if not self._skip_depth and tag in {"p", "div", "li", "section", "article"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if text:
            self._chunks.append(text + " ")

    def get_text(self) -> str:
        text = "".join(self._chunks)
        lines = [" ".join(line.split()) for line in text.splitlines()]
        cleaned = [line for line in lines if line]
        return "\n".join(cleaned)


class SearchResultsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: List[Tuple[str, str]] = []
        self._capture = False
        self._current_href: Optional[str] = None
        self._current_text: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag != "a":
            return
        attrs_map = dict(attrs)
        href = attrs_map.get("href")
        class_name = attrs_map.get("class") or ""
        if href and ("result__a" in class_name or "result-link" in class_name):
            self._capture = True
            self._current_href = href
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            stripped = data.strip()
            if stripped:
                self._current_text.append(stripped)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._capture:
            return
        title = " ".join(self._current_text).strip()
        if self._current_href and title:
            self.results.append((title, self._current_href))
        self._capture = False
        self._current_href = None
        self._current_text = []
