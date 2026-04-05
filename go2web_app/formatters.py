import json
from html import unescape

from .models import HttpResponse
from .parsers import ReadableTextParser


def decode_body(response: HttpResponse) -> str:
    content_type = response.headers.get("content-type", "").lower()

    charset = "utf-8"
    for part in content_type.split(";"):
        part = part.strip()
        if part.startswith("charset="):
            charset = part.split("=", 1)[1].strip()
            break

    text = response.body.decode(charset, errors="replace")

    if "application/json" in content_type or text.lstrip().startswith(("{", "[")):
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            return text

    parser = ReadableTextParser()
    parser.feed(text)
    output = parser.get_text()
    return unescape(output) if output else text
