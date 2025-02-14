from typing import Literal
from pydantic import BaseModel

from src.tuvi.sao import Sao
from src.tuvi.element.types import ROLE_TYPE

# TODO : could having nhi hop
RELATION_TYPE = Literal['tam phuong', 'tu chinh']

class StarComposition(BaseModel):

    role : ROLE_TYPE | None = None

    list_sao : list[Sao]

    relation : RELATION_TYPE
