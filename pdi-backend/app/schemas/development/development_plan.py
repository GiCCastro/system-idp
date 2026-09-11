from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.models.development.development_plan import PlanStatusEnum
from app.schemas.competence.competence import CompetenceResponse
from app.schemas.development.development import DevelopmentResponse


class DevelopmentPlanCreate(BaseModel):
    development_id: int
    competence_id: int
    gap: int
    action: str
    status: PlanStatusEnum = PlanStatusEnum.PENDING
    
class DevelopmentPlanResponse(DevelopmentPlanCreate):
    id: int
    created_at: date
    
    class Config:
        from_attributes = True
        
class DevelopmentPlanDetailResponse(BaseModel):
    development: DevelopmentResponse
    competence: CompetenceResponse
    gap: int
    action: str
    status: PlanStatusEnum = PlanStatusEnum.PENDING 
    
    class Config: 
        from_attributes = True
        
class DevelopmentPlanCreateResponse(BaseModel):
    message: str
    development_plan: DevelopmentPlanResponse