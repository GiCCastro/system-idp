from fastapi import APIRouter,HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config import security
from app.models.evaluation.evaluation import Evaluation
from app.models.evaluation.form_question import FormQuestion
from app.models.evaluation.evaluation_question import EvaluationQuestion
from app.schemas.evaluation.evaluation_question import EvaluationQuestionCreate, EvaluationQuestionCreateResponse, EvaluationQuestionDetailResponse, EvaluationQuestionResponse

router = APIRouter(prefix="/evaluation_question", tags=["Evaluation_Question"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=EvaluationQuestionCreateResponse,
    summary="Cria uma nova relação entre avaliação e questão de formulário."
)

def create_evaluation_question(
    evaluation_question: EvaluationQuestionCreate,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    
    roles_permitted = ["Recursos Humanos", "Gestor"]
    
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Acesso negado. Apenas membros do RH podem criar uma relação entre avaliação e questão de formulário."
        )
        
    existing_evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_question.evaluation_id).first()
    
    if not existing_evaluation:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "A avaliação informada não existe no sistema."
        )

    existing_question = db.query(FormQuestion).filter(FormQuestion.id == evaluation_question.question_id).first()
    
    if not existing_question:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "A questão do formulário informada não existe no sistema."
        )
        
    existing_relation = db.query(EvaluationQuestion).filter(
            EvaluationQuestion.evaluation_id == evaluation_question.evaluation_id,
            EvaluationQuestion.question_id == evaluation_question.question_id
        ).first() 
        
    if existing_relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A relação entre esta avaliação e questão de formulário já foi criada."        
        )
        
    new_evaluation_question = EvaluationQuestion(
        evaluation_id = evaluation_question.evaluation_id,
        question_id = evaluation_question.question_id
    )
    
    try:
        db.add(new_evaluation_question)
        db.commit()
        db.refresh(new_evaluation_question)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Erro ao criar a relação entre avaliação e questão de formulário: {str(e)}"
        )
        
    return EvaluationQuestionCreateResponse(
        message = "Relação entre avaliação e questão de formulário criada com sucesso!",
        evaluation_question = EvaluationQuestionResponse(
            evaluation_id=new_evaluation_question.evaluation_id,
            question_id=new_evaluation_question.question_id
        )
    )
    
@router.get(
    "/{evaluation_id}",
    response_model=list[EvaluationQuestionDetailResponse],
    summary="Lista as perguntas vinculadas a uma avaliação específica"
)

def list_evaluation_questions(
    evaluation_id: int,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user),
):
    
    existing_evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not existing_evaluation:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada."
        )
            
    is_evaluator = (existing_evaluation.evaluator_id == user_logged["user_id"])

    if user_logged['role'] == 'Colaborador' or user_logged['role'] == 'Gestor':
        if not (is_evaluator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar o formulário desta avaliação"
            )
                
    records = db.query(EvaluationQuestion).filter(
        EvaluationQuestion.evaluation_id == evaluation_id
        ).all()  
    
    return records  
    
