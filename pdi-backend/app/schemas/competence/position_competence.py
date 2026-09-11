from pydantic import BaseModel

from app.schemas.competence.competence import CompetenceResponse
from app.schemas.competence.position import PositionResponse

class PositionCompetenceCreate(BaseModel):
    position_id: int
    competence_id: int
    expected_level: int
    
class PositionCompetenceResponse(PositionCompetenceCreate):
    
    class Config:
        from_attributes = True
        
class PositionCompetenceDetailResponse(BaseModel):
    
    position: PositionResponse
    competence: CompetenceResponse
    expected_level: int
    
class PositionCompetenceCreateResponse(BaseModel):
    message: str
    position_competence: PositionCompetenceResponse