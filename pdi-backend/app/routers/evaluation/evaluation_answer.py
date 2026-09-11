from fastapi import APIRouter,HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config import security
from app.models.evaluation.evaluation import Evaluation
from app.models.evaluation.evaluation_answer import EvaluationAnswer
from app.models.evaluation.form_question import FormQuestion
from app.schemas.evaluation.evaluation_answer import EvaluationAnswerCreate, EvaluationAnswerCreateResponse, EvaluationAnswerDetailResponse, EvaluationAnswerResponse

router = APIRouter(prefix="/evaluation_answer", tags=["Evaluation_Answer"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=EvaluationAnswerCreateResponse,
    summary="Responde questão"
)

def create_evaluation_answer(
    evaluation_answer: EvaluationAnswerCreate,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    
    existing_evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_answer.evaluation_id).first()
    
    if not existing_evaluation:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail= "A avaliação informada não existe no sistema."
        )
        
    new_answers_to_add = []
    
    for item in evaluation_answer.answers:
        
        existing_question = db.query(FormQuestion).filter(
            FormQuestion.id == item.question_id).first()
        
        if not existing_question:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"A questão com ID {item.question_id} não existe no sistema."
            ) 
            
            
        existing_relation = db.query(EvaluationAnswer).filter(
                    EvaluationAnswer.evaluation_id == evaluation_answer.evaluation_id,
                    EvaluationAnswer.question_id == item.question_id
                ).first() 
                
        if existing_relation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A questão com ID {item.question_id} já foi respondida para esta avaliação."        
            )
            
        if item.score < 1 or item.score > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O score deve ser numa escala de 1 a 5"    
            )   
            
            
        new_evaluation_answer = EvaluationAnswer(
            evaluation_id = evaluation_answer.evaluation_id,
            question_id = item.question_id,
            answer_text = item.answer_text,
            score = item.score
        )
        
        new_answers_to_add.append(new_evaluation_answer)
    
    try:
        db.add_all(new_answers_to_add)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Erro ao responder: {str(e)}"
        )

    return EvaluationAnswerCreateResponse(
        message = "Respostas salvas com sucesso!",
        evaluation_question = EvaluationAnswerResponse(
            evaluation_id=new_evaluation_answer.evaluation_id,
            answers=evaluation_answer.answers
        )
    )
    
@router.get(
    "/list",
    response_model=list[EvaluationAnswerDetailResponse],
    summary="Lista todas as questões respondidas."
)

def list_evaluation_questions(
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    
    return db.query(EvaluationAnswer).all()