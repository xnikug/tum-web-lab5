from dataclasses import dataclass
from typing import Dict


@dataclass
class HttpResponse:
    status_code: int
    reason: str
    headers: Dict[str, str]
    body: bytes
    url: str
