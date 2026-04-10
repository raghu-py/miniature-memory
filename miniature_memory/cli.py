from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from miniature_memory.config import build_config, ensure_app_dir
from miniature_memory.crypto import CryptoManager, MissingPassphraseError
from miniature_memory.models import MemoryEntry
from miniature_memory.store import MemoryStore


def build_store() -> MemoryStore:
    config = build_config()
    ensure_app_dir(config.base_dir)
    passphrase = os.getenv("MINI_MEMORY_PASSPHRASE", "")
    crypto = CryptoManager(config.salt_file, passphrase)
    store = MemoryStore(config.db_file, crypto)
    store.initialize()
    return store


def cmd_init(args: argparse.Namespace) -> int:
    _ = args
    store = build_store()
    print(f"Initialized encrypted store at: {store.db_file}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    store = build_store()
    entry = MemoryEntry(
        title=args.title,
        content=args.content,
        tags=args.tags or [],
    )
    store.add(entry)
    print(json.dumps(entry.to_dict(), indent=2))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    _ = args
    store = build_store()
    entries = store.list_entries()
    print(json.dumps([entry.to_dict() for entry in entries], indent=2))
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    store = build_store()
    entry = store.get(args.id)
    if entry is None:
        print("Entry not found.", file=sys.stderr)
        return 1
    print(json.dumps(entry.to_dict(), indent=2))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    store = build_store()
    entries = store.search(args.query)
    print(json.dumps([entry.to_dict() for entry in entries], indent=2))
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    store = build_store()
    deleted = store.delete(args.id)
    if not deleted:
        print("Entry not found.", file=sys.stderr)
        return 1
    print(f"Deleted entry: {args.id}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    store = build_store()
    output_path = Path(args.output).expanduser().resolve()
    store.export_plaintext(output_path)
    print(f"Exported plaintext JSON to: {output_path}")
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Encrypted miniature memory CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize the encrypted store")
    init_parser.set_defaults(func=cmd_init)

    add_parser = subparsers.add_parser("add", help="Add a memory entry")
    add_parser.add_argument("--title", required=True, help="Entry title")
    add_parser.add_argument("--content", required=True, help="Entry content")
    add_parser.add_argument("--tags", nargs="*", default=[], help="Optional tags")
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list", help="List memory entries")
    list_parser.set_defaults(func=cmd_list)

    get_parser = subparsers.add_parser("get", help="Get one entry by ID")
    get_parser.add_argument("--id", required=True, help="Entry ID")
    get_parser.set_defaults(func=cmd_get)

    search_parser = subparsers.add_parser("search", help="Search memory entries")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.set_defaults(func=cmd_search)

    delete_parser = subparsers.add_parser("delete", help="Delete one entry by ID")
    delete_parser.add_argument("--id", required=True, help="Entry ID")
    delete_parser.set_defaults(func=cmd_delete)

    export_parser = subparsers.add_parser("export", help="Export plaintext JSON")
    export_parser.add_argument("--output", required=True, help="Output path for JSON export")
    export_parser.set_defaults(func=cmd_export)

    return parser


def main() -> int:
    parser = make_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except MissingPassphraseError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
