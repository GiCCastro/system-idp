from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config import security
from app.models.competence.competence import Competence
from app.models.evaluation.form_question import FormQuestion
from app.schemas.evaluation.form_question import FormQuestionCreate, FormQuestionDetailResponse, FormQuestionResponse, FormQuestionCreateResponse
from app.utils.pagination import PaginatedResponse, paginate

router = APIRouter(prefix="/form_question", tags=["Form_Question"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=FormQuestionCreateResponse,
    summary="Cria uma nova questão de formulário para a empresa do usuário logado."
)
def create_form_question(
    form_question: FormQuestionCreate,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso Negado. Apenas membros do RH podem criar questões de formulário."
        )

    enterprise_id = user_logged.get("enterprise_id")
    if not enterprise_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário logado não possui empresa vinculada."
        )
        
    existing_competence = db.query(Competence).filter(Competence.id == form_question.competence_id).first()
    if not existing_competence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A competência informada não existe no sistema."
        )

    if existing_competence.enterprise_id != enterprise_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. A competência informada pertence a outra empresa."
        )
        
    new_form_question = FormQuestion(
        question_text = form_question.question_text,
        competence_id = form_question.competence_id,
        enterprise_id = enterprise_id
    )
    
    try:
        db.add(new_form_question)
        db.commit()
        db.refresh(new_form_question)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar a questão de formulário: {str(e)}"
        )
        
    return FormQuestionCreateResponse(
        message = "Questão de formulário criada com sucesso!",
        form_question = FormQuestionResponse(
            id=new_form_question.id,
            question_text=new_form_question.question_text,
            competence_id=new_form_question.competence_id,
        )
    )

@router.get(
    "/list",
    response_model=PaginatedResponse[FormQuestionDetailResponse],
    summary="Lista todas as questões de formulário da empresa cadastradas com paginação."
)
def list_form_questions(
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=10, ge=1, le=100, description="Quantidade por página"),
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    query = db.query(FormQuestion)
    if user_logged.get("enterprise_id"):
        query = query.filter(FormQuestion.enterprise_id == user_logged["enterprise_id"])
    return paginate(query, page=page, limit=limit)
