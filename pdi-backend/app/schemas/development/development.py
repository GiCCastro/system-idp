from datetime import date

from pydantic import BaseModel

from app.models.development.development import DevelopmentStatusEnum
from app.schemas.competence.position import PositionResponse
from app.schemas.auth.user import UserSimpleResponse

class DevelopmentCreate(BaseModel):
    user_id: int
    position_id: int
    title: str
    status: DevelopmentStatusEnum = DevelopmentStatusEnum.PENDING
    
class DevelopmentResponse(DevelopmentCreate):
    id: int
    created_at: date
    
    class Config:
        from_attributes = True
        
class DevelopmentDetailResponse(BaseModel):
    user: UserSimpleResponse
    position: PositionResponse
    title: str
    status: DevelopmentStatusEnum = DevelopmentStatusEnum.PENDING
    
    class Config: 
        from_attributes = True
        
class DevelopmentCreateResponse(BaseModel):
    message: str
    development: DevelopmentResponse