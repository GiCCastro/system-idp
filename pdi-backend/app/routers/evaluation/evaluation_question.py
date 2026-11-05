from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config import security
from app.models.development.development import Development
from app.models.evaluation.evaluation import Evaluation
from app.models.evaluation.evaluation_answer import EvaluationAnswer
from app.models.evaluation.form_question import FormQuestion
from app.models.evaluation.evaluation_question import EvaluationQuestion
from app.schemas.evaluation.evaluation_question import (
    EvaluationQuestionCreate,
    EvaluationQuestionCreateResponse,
    EvaluationQuestionDetailResponse,
    EvaluationQuestionResponse,
)

router = APIRouter(prefix="/evaluation_question", tags=["Evaluation_Question"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=EvaluationQuestionCreateResponse,
    summary="Vincula uma questão de formulário ao ciclo completo (Autoavaliação e Avaliação do Gestor)."
)

def create_evaluation_question(
    evaluation_question: EvaluationQuestionCreate,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    
    roles_permitted = ["Recursos Humanos"]
    
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Acesso negado. Apenas membros do RH podem vincular questões de formulário ao ciclo de avaliação."
        )
        
    existing_evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_question.evaluation_id).first()
    
    if not existing_evaluation:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "A avaliação informada não existe no sistema."
        )

    if user_logged.get("enterprise_id") and existing_evaluation.user and existing_evaluation.user.enterprise_id != user_logged["enterprise_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Esta avaliação pertence a outra empresa."
        )

    existing_question = db.query(FormQuestion).filter(FormQuestion.id == evaluation_question.question_id).first()
    
    if not existing_question:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "A questão do formulário informada não existe no sistema."
        )

    # Busca ambas as avaliações (SELF e MANAGER) do mesmo colaborador e ciclo
    self_evaluation = db.query(Evaluation).filter(
        Evaluation.user_id == existing_evaluation.user_id,
        Evaluation.cycle == existing_evaluation.cycle,
        Evaluation.type == "SELF"
    ).order_by(Evaluation.created_at.desc()).first()

    manager_evaluation = db.query(Evaluation).filter(
        Evaluation.user_id == existing_evaluation.user_id,
        Evaluation.cycle == existing_evaluation.cycle,
        Evaluation.type == "MANAGER"
    ).order_by(Evaluation.created_at.desc()).first()

    if not self_evaluation or not manager_evaluation:
        missing = []
        if not self_evaluation:
            missing.append("Autoavaliação (SELF)")
        if not manager_evaluation:
            missing.append("Avaliação do Gestor (MANAGER)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível vincular a questão. O ciclo '{existing_evaluation.cycle}' está incompleto. Falta cadastrar: {', '.join(missing)}."
        )

    # Trava: Impede adicionar questões se o ciclo já tiver respostas registradas ou PDI gerado
    position_id = existing_evaluation.target_position_id or (
        existing_evaluation.user.position_id if existing_evaluation.user else None
    )
    if position_id:
        existing_dev = db.query(Development).filter(
            Development.user_id == existing_evaluation.user_id,
            Development.position_id == position_id
        ).first()
        if existing_dev:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível adicionar novas questões. Os gaps e o PDI para este colaborador já foram gerados."
            )

    existing_answers_count = db.query(EvaluationAnswer).filter(
        EvaluationAnswer.evaluation_id.in_([self_evaluation.id, manager_evaluation.id])
    ).count()

    if existing_answers_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível adicionar novas questões. Este ciclo de avaliação já possui respostas registradas."
        )

    evaluations_to_link = [self_evaluation, manager_evaluation]
    created_links = []

    for eval_inst in evaluations_to_link:
        existing_relation = db.query(EvaluationQuestion).filter(
            EvaluationQuestion.evaluation_id == eval_inst.id,
            EvaluationQuestion.question_id == evaluation_question.question_id
        ).first()

        if not existing_relation:
            new_link = EvaluationQuestion(
                evaluation_id=eval_inst.id,
                question_id=evaluation_question.question_id
            )
            db.add(new_link)
            created_links.append(new_link)

    if not created_links:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta questão já está vinculada a ambas as avaliações (SELF e MANAGER) deste ciclo."
        )

    try:
        db.commit()
        for link in created_links:
            db.refresh(link)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Erro ao vincular questão ao ciclo de avaliação: {str(e)}"
        )
        
    return EvaluationQuestionCreateResponse(
        message = "Questão vinculada com sucesso ao ciclo completo (Autoavaliação e Avaliação do Gestor)!",
        evaluation_question = EvaluationQuestionResponse(
            evaluation_id=existing_evaluation.id,
            question_id=evaluation_question.question_id
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

    if user_logged.get("enterprise_id") and existing_evaluation.user and existing_evaluation.user.enterprise_id != user_logged["enterprise_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Esta avaliação pertence a outra empresa."
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
