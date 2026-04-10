from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class MemoryEntry:
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict) -> "MemoryEntry":
        return cls(
            title=payload["title"],
            content=payload["content"],
            tags=list(payload.get("tags", [])),
            entry_id=payload["entry_id"],
            created_at=payload["created_at"],
            updated_at=payload["updated_at"],
        )
