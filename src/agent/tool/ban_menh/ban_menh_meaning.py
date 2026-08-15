from __future__ import annotations

from dataclasses import dataclass

from src.refactored.model.menh_cuc_relation import MenhCucRelationType


@dataclass(frozen=True)
class BanMenhMeaning:
    name: str
    symbol: str
    keywords: tuple[str, ...]
    nature: str
    reading_hint: str
    aliases: tuple[str, ...] = ()

    def as_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "symbol": self.symbol,
            "keywords": list(self.keywords),
            "nature": self.nature,
            "reading_hint": self.reading_hint,
        }
        if self.aliases:
            payload["aliases"] = list(self.aliases)
        return payload


_RELATION_LENS: dict[MenhCucRelationType, dict[str, str]] = {
    MenhCucRelationType.SINH_XUAT: {
        "relation": "Mệnh sinh Cục",
        "meaning": (
            "Người phải tự mình nỗ lực, tiên phong hành động trước khi hoàn "
            "cảnh biến đổi theo ý mình."
        ),
    },
    MenhCucRelationType.SINH_NHAP: {
        "relation": "Cục sinh Mệnh",
        "meaning": "Người gặp nhiều may mắn, được hoàn cảnh hỗ trợ và ưu đãi.",
    },
    MenhCucRelationType.KHAC_XUAT: {
        "relation": "Mệnh khắc Cục",
        "meaning": ("Người có khả năng thay đổi, cải cách môi trường xung quanh mình."),
    },
    MenhCucRelationType.KHAC_NHAP: {
        "relation": "Cục khắc Mệnh",
        "meaning": (
            "Hoàn cảnh gây khó khăn, cản trở hoặc buộc bản tính cá nhân phải "
            "thay đổi để thích nghi."
        ),
    },
    MenhCucRelationType.BINH_HOA: {
        "relation": "Mệnh Cục Bình Hòa",
        "meaning": "Mệnh và môi trường ngang hàng, ít có sự chi phối lẫn nhau.",
    },
}


def build_menh_cuc_lens(
    relation_type: MenhCucRelationType,
) -> dict[str, object]:
    relation_lens = _RELATION_LENS[relation_type]
    return {
        "relation": relation_lens["relation"],
        "meaning": relation_lens["meaning"],
    }
