from datetime import date

from pydantic import BaseModel, EmailStr  
from app.models.evaluation.evaluation import EvaluationTypeEnum
from app.schemas.auth.user import UserSimpleResponse
from app.schemas.competence.position import PositionResponse

class EvaluationCreate(BaseModel):
    user_id: int
    evaluator_id: int
    target_position_id: int
    enterprise_id: int
    type: EvaluationTypeEnum
    
class EvaluationResponse(EvaluationCreate):
    
    id: int
    created_at: date
    
    class Config:
        from_attributes = True
        
class EnterpriseResponse(BaseModel):
    id: int
    cnpj: str
    name: str
    email: EmailStr
    niche: str
        
class EvaluationDetailResponse(BaseModel):
    
    id: int
    created_at: date
    user: UserSimpleResponse
    evaluator: UserSimpleResponse
    enterprise: EnterpriseResponse
    target_position_id: PositionResponse
    type: EvaluationTypeEnum
    
        
class EvaluationCreateResponse(BaseModel):
    message: str
    evaluation: EvaluationResponse