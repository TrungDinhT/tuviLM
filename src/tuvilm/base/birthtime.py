import datetime as dt

class BirthTime:
    """Thời điểm sinh theo ngày âm"""
    def __init__(
        self,
        cang : str,
        chi : str,
        month : int,
        day : int,
        hour : int
    ):
        self.cang = cang
        self.chi = chi
        self.month = month
        self.day = day
        self.hour = hour

    @classmethod
    def from_ngay_duong(cls, time_duong : dt.datetime):
        return
