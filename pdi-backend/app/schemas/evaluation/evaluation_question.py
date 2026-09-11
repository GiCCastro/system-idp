from pydantic import BaseModel

from app.schemas.evaluation.evaluation import EvaluationResponse
from app.schemas.evaluation.form_question import FormQuestionResponse

class EvaluationQuestionCreate(BaseModel):
    evaluation_id: int
    question_id: int

class EvaluationQuestionResponse(EvaluationQuestionCreate):
    class Config:
        from_attributes = True
        
        
class EvaluationQuestionDetailResponse(BaseModel):
    evaluation:  EvaluationResponse
    question: FormQuestionResponse     

    class Config:
        from_attributes = True
        
class EvaluationQuestionCreateResponse(BaseModel):
    message: str
    evaluation_question: EvaluationQuestionResponse