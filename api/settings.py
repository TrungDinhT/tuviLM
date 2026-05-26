from __future__ import annotations

import os


class ApiSettings:
    def __init__(self) -> None:
        self.mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
        self.mongodb_db = os.environ.get("MONGODB_DB", "tuvilm")


def get_settings() -> ApiSettings:
    return ApiSettings()
