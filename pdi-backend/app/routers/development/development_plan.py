from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.config import security
from app.config.database import get_db
from app.models.competence.competence import Competence
from app.models.development.development import Development, DevelopmentStatusEnum
from app.models.development.development_plan import DevelopmentPlan, PlanStatusEnum
from app.models.auth.user import User
from app.schemas.development.development_plan import (
    DevelopmentPlanCreate,
    DevelopmentPlanCreateResponse,
    DevelopmentPlanDetailResponse,
    DevelopmentPlanResponse,
    DevelopmentPlanStatusUpdate,
    DevelopmentPlanStatusUpdateResponse,
)

router = APIRouter(prefix="/development_plan", tags=["development_plan"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=DevelopmentPlanCreateResponse,
    summary="Cria o plano de ação para o desenvolvimento"
)
def create_development_plan(
    development_plan: DevelopmentPlanCreate,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    
    existing_development = db.query(Development).filter(Development.id == development_plan.development_id).first()
    existing_competence = db.query(Competence).filter(Competence.id == development_plan.competence_id).first()
    existing_relation = db.query(DevelopmentPlan).filter(
        DevelopmentPlan.development_id == development_plan.development_id,
        DevelopmentPlan.competence_id == development_plan.competence_id
    ).first()
    
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas membros do RH podem criar um plano de desenvolvimento."
        )
         
    if not existing_development:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O desenvolvimento informado não existe no sistema"
        )

    if user_logged.get("enterprise_id") and existing_development.user and existing_development.user.enterprise_id != user_logged["enterprise_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Este desenvolvimento pertence a outra empresa."
        )
        
    if not existing_competence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A competência informada não existe no sistema."
        )
        
    if existing_relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este plano de ação já foi criado ao desenvolvimento."        
        )
            
    new_development_plan = DevelopmentPlan(
        development_id=development_plan.development_id,
        competence_id=development_plan.competence_id,
        gap=development_plan.gap,
        action=development_plan.action,
        status=development_plan.status or PlanStatusEnum.PENDING,
    )
    
    try:
        db.add(new_development_plan)
        db.commit()
        db.refresh(new_development_plan)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar o plano de ação: {str(e)}"
        )
        
    return DevelopmentPlanCreateResponse(
        message="Desenvolvimento criado com sucesso!",
        development_plan=DevelopmentPlanResponse(
            id=new_development_plan.id,
            development_id=new_development_plan.development_id,
            competence_id=new_development_plan.competence_id,
            gap=new_development_plan.gap,
            action=new_development_plan.action,
            status=new_development_plan.status,
            created_at=new_development_plan.created_at
        )
    )
    
@router.get(
    "/{development_id}",
    response_model=list[DevelopmentPlanDetailResponse],
    summary="Lista o plano de ação para o desenvolvimento"
)
def list_development_user(
    development_id: int,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas membros do RH podem listar todos os planos de desenvolvimento"
        )
    
    existing_development = db.query(Development).filter(Development.id == development_id).first()
    
    if not existing_development:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desenvolvimento não encontrado."
        )

    if user_logged.get("enterprise_id") and existing_development.user and existing_development.user.enterprise_id != user_logged["enterprise_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Este desenvolvimento pertence a outra empresa."
        )
        
    records = db.query(DevelopmentPlan).filter(
        DevelopmentPlan.development_id == development_id
    ).all()
    
    return records


@router.patch(
    "/{plan_id}/status",
    response_model=DevelopmentPlanStatusUpdateResponse,
    summary="Atualiza o status de uma ação específica do plano de desenvolvimento e recalcula o status do desenvolvimento pai."
)
def update_development_plan_status(
    plan_id: int,
    status_update: DevelopmentPlanStatusUpdate,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    plan = db.query(DevelopmentPlan).filter(DevelopmentPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano de ação não encontrado."
        )

    development = db.query(Development).filter(Development.id == plan.development_id).first()
    if not development:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desenvolvimento associado não encontrado."
        )

    dev_user = db.query(User).filter(User.id == development.user_id).first()
    if user_logged.get("enterprise_id") and dev_user and dev_user.enterprise_id != user_logged["enterprise_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Este plano de desenvolvimento pertence a outra empresa."
        )

    is_owner = (development.user_id == user_logged["user_id"])
    is_manager = (dev_user and dev_user.manager_id == user_logged["user_id"])
    is_hr = (user_logged["role"] == "Recursos Humanos")

    if not (is_owner or is_manager or is_hr):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para alterar o status desta ação."
        )

    plan.status = status_update.status
    db.flush()

    # Verifica se todas as ações deste desenvolvimento foram concluídas
    all_plans = db.query(DevelopmentPlan).filter(DevelopmentPlan.development_id == development.id).all()
    all_completed = len(all_plans) > 0 and all(p.status == PlanStatusEnum.COMPLETE for p in all_plans)

    if all_completed:
        development.status = DevelopmentStatusEnum.COMPLETE
    else:
        development.status = DevelopmentStatusEnum.IN_PROGRESS

    db.commit()
    db.refresh(plan)
    db.refresh(development)

    return DevelopmentPlanStatusUpdateResponse(
        message=f"Status da ação atualizado para {plan.status.value} com sucesso!",
        development_plan=plan,
        development_status=development.status.value
    )
