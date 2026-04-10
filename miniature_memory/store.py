from __future__ import annotations

import json
import os
from pathlib import Path

from miniature_memory.crypto import CryptoManager
from miniature_memory.models import MemoryEntry


class MemoryStore:
    def __init__(self, db_file: Path, crypto: CryptoManager) -> None:
        self.db_file = db_file
        self.crypto = crypto

    def initialize(self) -> None:
        if not self.db_file.exists():
            self._write_payload([])
            try:
                os.chmod(self.db_file, 0o600)
            except PermissionError:
                pass

    def _read_payload(self) -> list[dict]:
        if not self.db_file.exists():
            return []
        encrypted = self.db_file.read_bytes()
        if not encrypted:
            return []
        raw = self.crypto.decrypt(encrypted)
        return json.loads(raw.decode("utf-8"))

    def _write_payload(self, payload: list[dict]) -> None:
        serialized = json.dumps(payload, indent=2).encode("utf-8")
        encrypted = self.crypto.encrypt(serialized)
        self.db_file.write_bytes(encrypted)

    def add(self, entry: MemoryEntry) -> MemoryEntry:
        payload = self._read_payload()
        payload.append(entry.to_dict())
        self._write_payload(payload)
        return entry

    def list_entries(self) -> list[MemoryEntry]:
        payload = self._read_payload()
        return [MemoryEntry.from_dict(item) for item in payload]

    def get(self, entry_id: str) -> MemoryEntry | None:
        for entry in self.list_entries():
            if entry.entry_id == entry_id:
                return entry
        return None

    def delete(self, entry_id: str) -> bool:
        payload = self._read_payload()
        original_count = len(payload)
        payload = [item for item in payload if item["entry_id"] != entry_id]
        if len(payload) == original_count:
            return False
        self._write_payload(payload)
        return True

    def search(self, query: str) -> list[MemoryEntry]:
        needle = query.casefold().strip()
        scored: list[tuple[int, MemoryEntry]] = []

        for entry in self.list_entries():
            score = self._score_entry(entry, needle)
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda item: (-item[0], item[1].created_at))
        return [entry for _, entry in scored]

    def export_plaintext(self, output_file: Path) -> Path:
        entries = [entry.to_dict() for entry in self.list_entries()]
        output_file.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        return output_file

    @staticmethod
    def _score_entry(entry: MemoryEntry, needle: str) -> int:
        if not needle:
            return 0
        hay_title = entry.title.casefold()
        hay_content = entry.content.casefold()
        hay_tags = " ".join(entry.tags).casefold()

        score = 0
        if needle in hay_title:
            score += 5
        if needle in hay_tags:
            score += 3
        if needle in hay_content:
            score += 2

        for token in needle.split():
            if token in hay_title:
                score += 2
            if token in hay_tags:
                score += 1
            if token in hay_content:
                score += 1
        return score
