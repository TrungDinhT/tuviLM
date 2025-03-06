from typing import Literal
from pydantic import BaseModel

from src.tuvi.element.sao import Sao
from src.tuvi.element.types import ROLE_TYPE, TYPE_DIA_CHI

# TODO : could having nhi hop
RELATION_TYPE = Literal['cung', 'tam phuong', 'tu chinh']


# TODO : should have multiples types of combo : stars only, stars with role, star with position, etc
# TODO : add condition  : do not have
# TODO : add role cung Than
class ElementComposition(BaseModel):

    name : str

    description : str | None = None

    target_position : TYPE_DIA_CHI | None = None

    role : ROLE_TYPE | None = None

    # Should we use a element here or just the name
    list_elements : set[str]

    relation : RELATION_TYPE
