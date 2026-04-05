from urllib.parse import parse_qs, quote_plus, unquote, urlparse

from .formatters import decode_body
from .http_client import HttpClient
from .parsers import SearchResultsParser


SEARCH_HEADERS = {
    "Accept-Encoding": "identity",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Referer": "https://duckduckgo.com/",
    "Cookie": "kl=en-us; s=l; ss=-1",
}


def run_url_mode(url: str) -> int:
    client = HttpClient()
    try:
        response = client.get(url)
    except Exception as exc:
        print(f"Request failed: {exc}")
        return 1

    print(f"HTTP {response.status_code} {response.reason}".strip())
    print(f"URL: {response.url}")
    print()
    print(decode_body(response))
    return 0


def normalize_search_link(link: str) -> str:
    if link.startswith("//"):
        link = f"https:{link}"
    elif link.startswith("/"):
        link = f"https://duckduckgo.com{link}"

    parsed_link = urlparse(link)
    query_params = parse_qs(parsed_link.query)
    if "uddg" in query_params and query_params["uddg"]:
        return unquote(query_params["uddg"][0])

    return link


def run_search_mode(search_terms: list[str]) -> int:
    query = " ".join(search_terms).strip()
    if not query:
        print("Search term is required")
        return 1

    search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    client = HttpClient()

    try:
        response = client.get(search_url, accept="text/html", extra_headers=SEARCH_HEADERS)
    except Exception as exc:
        print(f"Search failed: {exc}")
        return 1

    html = response.body.decode("utf-8", errors="replace")
    parser = SearchResultsParser()
    parser.feed(html)

    if not parser.results:
        try:
            retry_response = client.get(search_url, accept="text/html", extra_headers=SEARCH_HEADERS)
            retry_html = retry_response.body.decode("utf-8", errors="replace")
            parser.feed(retry_html)
        except Exception:
            pass

    if not parser.results:
        print("No search results found")
        return 0

    normalized_results: list[tuple[str, str]] = []
    seen_links: set[str] = set()
    for title, link in parser.results:
        direct_link = normalize_search_link(link)
        if not direct_link.startswith("http"):
            continue
        if direct_link in seen_links:
            continue
        seen_links.add(direct_link)
        normalized_results.append((title, direct_link))

    if not normalized_results:
        print("No search results found")
        return 0

    print(f"Top results for: {query}")
    print()
    for index, (title, direct_link) in enumerate(normalized_results[:10], start=1):
        print(f"{index}. {title}")
        print(f"   {direct_link}")

    return 0
