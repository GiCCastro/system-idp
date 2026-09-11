from pydantic import BaseModel

from app.schemas.evaluation.evaluation import EvaluationResponse
from app.schemas.evaluation.form_question import FormQuestionResponse

class EvaluationAnswerItem(BaseModel):
    question_id: int
    answer_text: str
    score: int
    

class EvaluationAnswerCreate(BaseModel):
    evaluation_id: int
    answers: list[EvaluationAnswerItem]

class EvaluationAnswerResponse(EvaluationAnswerCreate):
    class Config:
        from_attributes = True
        
         
class EvaluationAnswerDetailResponse(BaseModel):
    evaluation:  EvaluationResponse
    question: FormQuestionResponse     
    answer_text: str
    score: int

    class Config:
        from_attributes = True
        
class EvaluationAnswerCreateResponse(BaseModel):
    message: str
    evaluation_question: EvaluationAnswerResponse