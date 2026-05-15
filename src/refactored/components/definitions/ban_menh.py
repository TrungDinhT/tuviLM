from __future__ import annotations

from src.refactored.components.definitions.elementary import ComponentBase
from src.refactored.model.elementary import NguHanh


class BanMenh(ComponentBase):
    model_config = {"frozen": True}

    ngu_hanh: NguHanh
    description: str
