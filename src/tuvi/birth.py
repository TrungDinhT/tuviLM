import datetime as dt
import pydantic

from src.external_lib.day_from_js import get_lunar_date
from src.tuvi.element.types import LIST_DIA_CHI, LIST_THIEN_CAN, TYPE_DIA_CHI, TYPE_GENDER, TYPE_THIEN_CAN

class TuviTime(pydantic.BaseModel):

    hour : TYPE_DIA_CHI

    date : int

    month : int

    thien_can : TYPE_THIEN_CAN

    dia_chi : TYPE_DIA_CHI

    gender : TYPE_GENDER

    @classmethod
    def from_solar_day(cls, time : dt.datetime, gender : TYPE_GENDER):

        is_tomorrow = False

        # Move to tomorrow if 23h
        if time.hour == 23 :
            time += dt.timedelta(days=1)
            is_tomorrow = True

        if is_tomorrow or time.hour == 0:
            hour = "Tý"
        else:
            hour = LIST_DIA_CHI[(time.hour + 1) // 2]

        lunar = get_lunar_date(time.day, time.month, time.year)

        dia_chi = LIST_DIA_CHI[(lunar.year + 8) % 12]
        thien_can = LIST_THIEN_CAN[(lunar.year + 6) % 10]

        return cls(
            hour=hour,
            date=lunar.day,
            month=lunar.month,
            thien_can=thien_can,
            dia_chi=dia_chi,
            gender=gender
        )
