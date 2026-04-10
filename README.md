# miniature-memory

A small, security-aware local memory store for notes, snippets, reminders, and teaching material.

This starter project is a practical fit for a Python developer and cybersecurity teacher:
- local-first storage
- encrypted data at rest with a passphrase
- simple CLI workflow
- metadata, tags, and keyword search
- clean project structure for future upgrades

## Features

- Add memory entries with title, content, and tags
- List all saved entries
- Search entries by keyword
- Read a single entry by ID
- Delete entries by ID
- Export decrypted entries to JSON
- Encrypt the on-disk database using `cryptography.Fernet`

## Project structure

```text
miniature-memory/
├── miniature_memory/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── crypto.py
│   ├── models.py
│   └── store.py
├── tests/
│   └── test_store.py
├── requirements.txt
└── README.md
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Set a passphrase once per shell session:

```bash
export MINI_MEMORY_PASSPHRASE="change-this-now"
```

Initialize the store:

```bash
python -m miniature_memory.cli init
```

Add a memory:

```bash
python -m miniature_memory.cli add \
  --title "SQL Injection lesson" \
  --content "Explain UNION-based injection, parameterized queries, and least privilege." \
  --tags python security teaching
```

List memories:

```bash
python -m miniature_memory.cli list
```

Search:

```bash
python -m miniature_memory.cli search --query injection
```

Get one entry:

```bash
python -m miniature_memory.cli get --id <ENTRY_ID>
```

Delete one entry:

```bash
python -m miniature_memory.cli delete --id <ENTRY_ID>
```

Export decrypted JSON:

```bash
python -m miniature_memory.cli export --output exported_memories.json
```

## Security notes

- The encryption key is derived from your passphrase using PBKDF2.
- The encrypted database is stored locally.
- The export command writes plaintext JSON, so handle exported files carefully.
- Use a strong passphrase and keep it out of shell history in production.
- This is a teaching-friendly starter, not a hardened secret manager.

## Next upgrades

- switch storage to SQLite
- add full-text search
- add password manager integration
- add audit logging
- add embeddings or semantic retrieval
- expose as FastAPI service
