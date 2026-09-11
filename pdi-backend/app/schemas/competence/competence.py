
from pydantic import BaseModel


class CompetenceCreate(BaseModel):
    name: str
    description: str


class CompetenceResponse(CompetenceCreate):
    id: int

    class Config:
        from_attributes = True


class CompetenceCreateResponse(BaseModel):
    message: str
    competence: CompetenceResponse