from __future__ import annotations

from dataclasses import dataclass

from src.tuvi.element.tuhoa import TypeTuHoa


@dataclass(frozen=True)
class TuHoaDefinition:
    name: str
    description: str | None = None


TUHOA_REGISTRY: dict[str, TuHoaDefinition] = {
    "Hóa Lộc": TuHoaDefinition(name="Hóa Lộc"),
    "Hóa Quyền": TuHoaDefinition(name="Hóa Quyền"),
    "Hóa Khoa": TuHoaDefinition(name="Hóa Khoa"),
    "Hóa Kỵ": TuHoaDefinition(name="Hóa Kỵ"),
}


def make_tuhoa(name: str) -> TypeTuHoa:
    if name not in TUHOA_REGISTRY:
        raise KeyError(f"TuHoa '{name}' is not registered")

    tuhoa_definition = TUHOA_REGISTRY[name]
    return TypeTuHoa(name=tuhoa_definition.name)
