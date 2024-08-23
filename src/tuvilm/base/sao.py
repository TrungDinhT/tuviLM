import abc

from tuvilm.base.birthtime import BirthTime


class Sao:
    name : str

    @abc.abstractmethod
    def get_position(self, birth_time : BirthTime):
        pass
