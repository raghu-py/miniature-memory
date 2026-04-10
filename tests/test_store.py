from __future__ import annotations

from pathlib import Path

from miniature_memory.crypto import CryptoManager
from miniature_memory.models import MemoryEntry
from miniature_memory.store import MemoryStore


def test_add_get_search_delete(tmp_path: Path) -> None:
    salt_file = tmp_path / "salt.bin"
    db_file = tmp_path / "memory.db.enc"
    crypto = CryptoManager(salt_file=salt_file, passphrase="unit-test-passphrase")
    store = MemoryStore(db_file=db_file, crypto=crypto)
    store.initialize()

    entry = MemoryEntry(
        title="XSS Lab",
        content="Teach stored and reflected XSS with output encoding examples.",
        tags=["security", "teaching", "xss"],
    )

    store.add(entry)

    fetched = store.get(entry.entry_id)
    assert fetched is not None
    assert fetched.title == "XSS Lab"

    results = store.search("output encoding")
    assert len(results) == 1
    assert results[0].entry_id == entry.entry_id

    deleted = store.delete(entry.entry_id)
    assert deleted is True
    assert store.get(entry.entry_id) is None
