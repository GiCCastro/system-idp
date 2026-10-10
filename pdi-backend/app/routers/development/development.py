from fastapi import APIRouter,HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.config import security
from app.config.database import get_db
from app.models.development.development import Development, DevelopmentStatusEnum
from app.models.competence.position import Position
from app.models.auth.user import User
from app.schemas.development.development import DevelopmentCreate, DevelopmentCreateResponse, DevelopmentDetailResponse, DevelopmentResponse


router = APIRouter(prefix="/development", tags=["development"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=DevelopmentCreateResponse,
    summary="Cria desenvolvimento"
)

def create_development(
    development: DevelopmentCreate,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    
    existing_user = db.query(User).filter(User.id == development.user_id).first()
    existing_position = db.query(Position).filter(Position.id == development.position_id).first()
    existing_relation = db.query(Development).filter(
        Development.user_id == development.user_id,
        Development.position_id == development.position_id
    ).first()
    
    
    if user_logged["role"] not in roles_permitted:
         raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Acesso negado. Apenas membros do RH podem criar um desenvolvimento."
        )
    
    if not existing_user:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="O usuário informado não existe no sistema."
        )
        
    if not existing_position:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="A posição informada não existe no sistema."
        )
        
    if existing_relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este desenvolvimento já foi criado ao usuário."        
        )
        
    new_development = Development(
        user_id = development.user_id,
        position_id = development.position_id,
        title = development.title,
        status=development.status or DevelopmentStatusEnum.PENDING,
    )
    
    try:
        db.add(new_development)
        db.commit()
        db.refresh(new_development)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar a desenvolvimento: {str(e)}"
        )
        
    return DevelopmentCreateResponse(
        message= "Desenvolvimento criado com sucesso!",
        development= DevelopmentResponse(
            id=new_development.id,
            user_id=new_development.user_id,
            position_id=new_development.position_id,
            title=new_development.title,
            status=new_development.status,
            created_at=str(new_development.created_at)
        )
    )
         
@router.get(
    "/{user_id}",
    response_model=list[DevelopmentDetailResponse],
    summary="Lista o desenvolvimento do usuário"
)
            
def list_development_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail = "Acesso negado. Apenas membros do RH podem listar todas os desenvolvimentos"
        )
    
    existing_user = db.query(User).filter(User.id == user_id).first()
    
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )
        
    records = db.query(Development).filter(
        Development.user_id == user_id
    ).all()
    
    return records
    
    


from app.models.evaluation.evaluation import Evaluation
from app.models.evaluation.evaluation_answer import EvaluationAnswer
from app.models.evaluation.evaluation_question import EvaluationQuestion
from app.models.development.development_plan import DevelopmentPlan, PlanStatusEnum
from app.services.gap_service import calculate_calibrated_gaps
from app.services.gemini_service import generate_pdi_suggestions_ai

@router.post(
    "/generate-from-evaluation/{evaluation_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Calcula Gaps e gera o PDI 70-20-10 automaticamente"
)

def generate_development_from_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)        
):
    roles_permitted = ["Recursos Humanos"]
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas membros do RH podem gerar o desenvolvimento a partir da avaliação."
        )
    
    existing_evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not existing_evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A avaliação informada não existe no sistema."
        )
        
    user_id = existing_evaluation.user_id
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O usuário associado à avaliação não existe no sistema."
        )
        
    position_id = existing_evaluation.target_position_id or existing_user.position_id
    existing_position = db.query(Position).filter(Position.id == position_id).first()
    if not existing_position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A posição associada à avaliação não existe no sistema."
        )
        
    target_cycle = existing_evaluation.cycle
    self_evaluation = db.query(Evaluation).filter(
        Evaluation.user_id == user_id,
        Evaluation.type == "SELF",
        Evaluation.cycle == target_cycle
    ).first()
    
    manager_evaluation = db.query(Evaluation).filter(
        Evaluation.user_id == user_id,
        Evaluation.type == "MANAGER",
        Evaluation.cycle == target_cycle
    ).first()
    
    if not self_evaluation or not manager_evaluation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível gerar o PDI. O ciclo '{target_cycle}' está incompleto (deve conter SELF e MANAGER cadastradas)."
        )

    total_self_questions = db.query(EvaluationQuestion).filter(
        EvaluationQuestion.evaluation_id == self_evaluation.id
    ).count()

    total_manager_questions = db.query(EvaluationQuestion).filter(
        EvaluationQuestion.evaluation_id == manager_evaluation.id
    ).count()
        
    self_answers_count = (
        db.query(EvaluationAnswer.id)
        .join(Evaluation, EvaluationAnswer.evaluation_id == Evaluation.id)
        .filter(
            Evaluation.user_id == user_id,
            Evaluation.type == "SELF",
            Evaluation.cycle == target_cycle
        )
        .count()
    )
    
    manager_answers_count = (
        db.query(EvaluationAnswer.id)
        .join(Evaluation, EvaluationAnswer.evaluation_id == Evaluation.id)
        .filter(
            Evaluation.user_id == user_id,
            Evaluation.type == "MANAGER",
            Evaluation.cycle == target_cycle
        )
        .count()
    )
    
    if (total_self_questions > 0 and self_answers_count < total_self_questions) or (total_manager_questions > 0 and manager_answers_count < total_manager_questions) or self_answers_count == 0 or manager_answers_count == 0:
        pending = []
        if self_answers_count == 0 or (total_self_questions > 0 and self_answers_count < total_self_questions):
            pending.append(f"Autoavaliação ({self_answers_count}/{total_self_questions} respondidas)")
        if manager_answers_count == 0 or (total_manager_questions > 0 and manager_answers_count < total_manager_questions):
            pending.append(f"Avaliação do Gestor ({manager_answers_count}/{total_manager_questions} respondidas)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível gerar o PDI. Faltam respostas para: {', '.join(pending)}."
        )
        
    existing_development = db.query(Development).filter(
        Development.user_id == existing_user.id,
        Development.position_id == position_id
    ).first()
    
    if existing_development:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um Plano de Desenvolvimento (PDI) gerado para este colaborador nesta posição."
        )

    gaps = calculate_calibrated_gaps(
        db=db, 
        user_id=existing_user.id, 
        cycle=target_cycle,
        target_position_id=position_id,
        enterprise_id=existing_user.enterprise_id
    )
    
    if not gaps:
        return {
            "message": "Nenhum gap negativo identificado. O colaborador atingiu ou superou os requisitos do cargo!",
            "plans_created": 0
        }
        
    try:
        ai_suggestions = generate_pdi_suggestions_ai(
            position_name=existing_position.name,
            gaps=gaps,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de IA temporariamente indisponível. Tente novamente em instantes."
        ) from exc

    new_development = Development(
        user_id=user_id,
        position_id=position_id,
        title=f"PDI - Plano de Desenvolvimento ({existing_position.name})",
        status=DevelopmentStatusEnum.PENDING
    )
    
    db.add(new_development)
    db.flush()
        
        
    gap_map = {gap["competence_id"]: gap["gap"] for gap in gaps}
        
    for suggestion in ai_suggestions:
        competence_id = suggestion.get("competence_id")
            
        full_action_text = (
        f"[Prática 70%]: {suggestion.get('action_70', '')}\n\n"
        f"[Mentoria/Troca 20%]: {suggestion.get('action_20', '')}\n\n"
        f"[Educação Formal 10%]: {suggestion.get('action_10', '')}"
    )
        
        existing_plan = db.query(DevelopmentPlan).filter(
            DevelopmentPlan.development_id == new_development.id,
            DevelopmentPlan.competence_id == competence_id
        ).first()
        
        if existing_plan:
            existing_plan.gap = gap_map.get(competence_id, existing_plan.gap)
            existing_plan.action = full_action_text
        else:
            new_plan = DevelopmentPlan(
                development_id=new_development.id,
                competence_id=competence_id,
                gap=gap_map.get(competence_id, 0.0),
                action=full_action_text,
                status=PlanStatusEnum.PENDING
            )
            db.add(new_plan)
    
    db.commit()
    
    return {
        "message": "PDI gerado e persistido com sucesso!",
        "development_id": new_development.id,
        "total_competences_addressed": len(ai_suggestions)
    }