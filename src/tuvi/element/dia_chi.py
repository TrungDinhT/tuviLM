from enum import Enum

from pydantic import BaseModel


class DiaChi(BaseModel):
    name : str
    index : int

LIST_DIA_CHI = [
    DiaChi(name="Ty", index=0),
    DiaChi(name="Suu", index=1),
    DiaChi(name="Dan", index=2),
    DiaChi(name="Ngo", index=3),
    DiaChi(name="Thin", index=4),
    DiaChi(name="Ti", index=5),
    DiaChi(name="Ngo", index=6),
    DiaChi(name="Mui", index=7),
    DiaChi(name="Than", index=8),
    DiaChi(name="Dau", index=9),
    DiaChi(name="Tuat", index=10),
    DiaChi(name="Hoi", index=11),
]
