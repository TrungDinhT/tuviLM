import pydantic

from src.tuvi.types import NGU_HANH, STAR_STATUS


class Sao(pydantic.BaseModel):

    name : str

    description : str | None = None

    elemental : NGU_HANH

    def get_status(position : str) -> STAR_STATUS:
        return None


class ChinhTinh(Sao):

    pass

class PhuTinh(Sao):

    pass
