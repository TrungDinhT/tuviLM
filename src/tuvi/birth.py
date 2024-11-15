import datetime as dt

import pydantic

from src.tuvi.types import TYPE_DIA_CHI, TYPE_GENDER, TYPE_THIEN_CAN

class BirthTime(pydantic.BaseModel):

    hour : TYPE_DIA_CHI

    date : int

    month : int

    thien_can : TYPE_THIEN_CAN

    dia_chi : TYPE_DIA_CHI

    gender : TYPE_GENDER

    @classmethod
    def from_solar_day(cls, time : dt.datetime):
        raise NotImplementedError
