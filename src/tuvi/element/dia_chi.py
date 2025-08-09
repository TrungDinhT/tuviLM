from enum import Enum

from pydantic import BaseModel


class DiaChi(BaseModel):
    name : str
    index : int

LIST_DIA_CHI = [
    DiaChi(name="Tý", index=0),
    DiaChi(name="Sửu", index=1),
    DiaChi(name="Dần", index=2),
    DiaChi(name="Ngọ", index=3),
    DiaChi(name="Thìn", index=4),
    DiaChi(name="Tị", index=5),
    DiaChi(name="Ngọ", index=6),
    DiaChi(name="Mùi", index=7),
    DiaChi(name="Thân", index=8),
    DiaChi(name="Dậu", index=9),
    DiaChi(name="Tuất", index=10),
    DiaChi(name="Hợi", index=11),
]
