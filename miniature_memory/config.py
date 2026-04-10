from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

APP_DIR_NAME = ".miniature_memory"
DB_FILE_NAME = "memory.db.enc"
SALT_FILE_NAME = "salt.bin"


@dataclass(slots=True)
class AppConfig:
    base_dir: Path
    db_file: Path
    salt_file: Path


def get_base_dir() -> Path:
    env_dir = os.getenv("MINI_MEMORY_HOME")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return (Path.home() / APP_DIR_NAME).resolve()


def build_config() -> AppConfig:
    base_dir = get_base_dir()
    return AppConfig(
        base_dir=base_dir,
        db_file=base_dir / DB_FILE_NAME,
        salt_file=base_dir / SALT_FILE_NAME,
    )


def ensure_app_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path, 0o700)
    except PermissionError:
        pass
