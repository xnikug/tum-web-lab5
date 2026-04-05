import socket
import ssl
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import hashlib, json, os, time

from .models import HttpResponse


USER_AGENT = "go2web/1.0 (+lab5)"
DEFAULT_TIMEOUT = 15
MAX_REDIRECTS = 5
CACHE_DIR = os.path.expanduser("~/.go2web_cache")
CACHE_TTL = 300  # seconds

class HttpClient:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout

    def _cache_path(self, url):
        key = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(CACHE_DIR, key)

    def _load_cache(self, url):
        path = self._cache_path(url)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            data = json.loads(f.read())
        if time.time() - data["ts"] > CACHE_TTL:
            return None
        r = data["response"]
        return HttpResponse(r["status_code"], r["reason"], r["headers"], bytes(r["body"]), r["url"])

    def _save_cache(self, url, response):
        os.makedirs(CACHE_DIR, exist_ok=True)
        data = {"ts": time.time(), "response": {
            "status_code": response.status_code, "reason": response.reason,
            "headers": response.headers, "body": list(response.body), "url": response.url
        }}
        with open(self._cache_path(url), "wb") as f:
            f.write(json.dumps(data).encode())

    def get(
        self,
        url: str,
        accept: str = "text/html,application/json",
        redirects: int = MAX_REDIRECTS,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> HttpResponse:
        cached = self._load_cache(url)
        if cached:
            return cached

        if redirects < 0:
            raise RuntimeError("Too many redirects")

        if not urlparse(url).scheme:
            url = f"https://{url}"

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only http and https URLs are supported")

        host = parsed.hostname
        if not host:
            raise ValueError("Invalid URL: missing hostname")

        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"

        header_lines = [
            f"GET {path} HTTP/1.1",
            f"Host: {host}",
            f"User-Agent: {USER_AGENT}",
            f"Accept: {accept}",
            "Connection: close",
        ]
        if extra_headers:
            for key, value in extra_headers.items():
                header_lines.append(f"{key}: {value}")

        request = ("\r\n".join(header_lines) + "\r\n\r\n").encode("utf-8")

        raw = self._send_request(host=host, port=port, use_ssl=(parsed.scheme == "https"), request=request)
        status_code, reason, headers, body = self._parse_http_response(raw)

        if status_code in {301, 302, 303, 307, 308}:
            location = headers.get("location")
            if not location:
                raise RuntimeError("Redirect response missing Location header")
            next_url = urljoin(url, location)
            return self.get(next_url, accept=accept, redirects=redirects - 1, extra_headers=extra_headers)

        response = HttpResponse(status_code=status_code, reason=reason, headers=headers, body=body, url=url)
        self._save_cache(url, response)
        return response

    def _send_request(self, host: str, port: int, use_ssl: bool, request: bytes) -> bytes:
        with socket.create_connection((host, port), timeout=self.timeout) as sock:
            conn: socket.socket | ssl.SSLSocket
            conn = sock
            if use_ssl:
                context = ssl.create_default_context()
                conn = context.wrap_socket(sock, server_hostname=host)
            conn.sendall(request)
            chunks: List[bytes] = []
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                chunks.append(data)
            return b"".join(chunks)

    def _parse_http_response(self, raw: bytes) -> Tuple[int, str, Dict[str, str], bytes]:
        header_blob, _, body = raw.partition(b"\r\n\r\n")
        header_lines = header_blob.split(b"\r\n")
        if not header_lines:
            raise RuntimeError("Invalid HTTP response")

        status_line = header_lines[0].decode("iso-8859-1", errors="replace")
        parts = status_line.split(" ", 2)
        if len(parts) < 2:
            raise RuntimeError(f"Malformed status line: {status_line}")

        status_code = int(parts[1])
        reason = parts[2] if len(parts) > 2 else ""

        headers: Dict[str, str] = {}
        for line in header_lines[1:]:
            decoded = line.decode("iso-8859-1", errors="replace")
            if ":" not in decoded:
                continue
            key, value = decoded.split(":", 1)
            headers[key.strip().lower()] = value.strip()

        if headers.get("transfer-encoding", "").lower() == "chunked":
            body = self._decode_chunked(body)

        content_encoding = headers.get("content-encoding", "").lower()
        if content_encoding == "gzip":
            import gzip

            body = gzip.decompress(body)

        return status_code, reason, headers, body

    @staticmethod
    def _decode_chunked(body: bytes) -> bytes:
        index = 0
        decoded = bytearray()

        while True:
            line_end = body.find(b"\r\n", index)
            if line_end == -1:
                break
            size_line = body[index:line_end].split(b";", 1)[0]
            chunk_size = int(size_line, 16)
            index = line_end + 2
            if chunk_size == 0:
                break
            decoded.extend(body[index:index + chunk_size])
            index += chunk_size + 2

        return bytes(decoded)
