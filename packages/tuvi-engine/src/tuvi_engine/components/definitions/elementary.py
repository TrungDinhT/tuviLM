from pydantic import BaseModel, model_validator

from src.refactored.model.elementary import DiaChi, NguHanh, ThienCan


class ComponentBase(BaseModel):
    model_config = {"frozen": True}

    id: str
    name: str

    def __hash__(self) -> int:
        return hash(self.id)


class ThienCanEntity(ComponentBase):
    model_config = {"frozen": True}

    ngu_hanh: NguHanh
    value: ThienCan

    @model_validator(mode="before")
    @classmethod
    def _normalize_identity(cls, data: object):
        if not isinstance(data, dict):
            return data
        return {**data, "value": ThienCan(data["id"])}


class DiaChiEntity(ComponentBase):
    model_config = {"frozen": True}

    ngu_hanh: NguHanh
    value: DiaChi

    @model_validator(mode="before")
    @classmethod
    def _normalize_identity(cls, data: object):
        if not isinstance(data, dict):
            return data
        return {**data, "value": DiaChi(data["id"])}
