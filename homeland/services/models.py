from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(frozen=True)
class Service:
    container: str
    title: str
    description: str
    category: str
    icon: str = "📦"
    url: Optional[str] = None
    homepage: bool = True

    def to_dict(self) -> dict:
        return asdict(self)
