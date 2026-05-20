from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_api_env(path: Path = Path("api/.env")) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True, slots=True)
class ApiSettings:
    mongodb_uri: str
    mongodb_db: str
    mongodb_timeout_ms: int = 3000
    book_root: str = "./data/tuvitanbien_chunking_compact/part_2"
    model_name: str = "openai:gpt-5.4-mini"

    @classmethod
    def from_env(cls) -> "ApiSettings":
        load_api_env()
        return cls(
            mongodb_uri=os.getenv(
                "MONGODB_URI",
                "mongodb://localhost:27017/?replicaSet=rs0&directConnection=true",
            ),
            mongodb_db=os.getenv("MONGODB_DB", "tuvilm"),
            mongodb_timeout_ms=int(os.getenv("MONGODB_TIMEOUT_MS", "3000")),
            book_root=os.getenv(
                "TUVI_BOOK_ROOT", "./data/tuvitanbien_chunking_compact/part_2"
            ),
            model_name=os.getenv("TUVI_MODEL", "openai:gpt-5.4-mini"),
        )
