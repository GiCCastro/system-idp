from pydantic import BaseModel

from app.schemas.competence.competence import CompetenceResponse

class FormQuestionCreate(BaseModel):
    
    question_text: str
    competence_id: int

class FormQuestionResponse(FormQuestionCreate):
    
    id: int
    
    class Config:
        from_attributes = True
        
class FormQuestionDetailResponse(BaseModel):
    
    id: int
    question_text: str
    competence: CompetenceResponse
    
    class Config:
        from_attributes = True
        
class FormQuestionCreateResponse(BaseModel):
    message: str
    form_question: FormQuestionResponse