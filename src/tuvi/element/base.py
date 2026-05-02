from pydantic import BaseModel


class Element(BaseModel):

    name : str

    short_names : list[str] | None = None
