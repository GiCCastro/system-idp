from fastapi import APIRouter,HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.config import security
from app.config.database import get_db
from app.models.competence.competence import Competence
from app.models.development.development import Development
from app.models.development.development_plan import DevelopmentPlan, PlanStatusEnum
from app.schemas.development.development_plan import DevelopmentPlanCreate, DevelopmentPlanCreateResponse, DevelopmentPlanDetailResponse, DevelopmentPlanResponse

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
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Acesso negado. Apenas membros do RH podem criar um plano de desenvolvimento."
        )
         
    if not existing_development:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O desenvolvimento informado não existe no sistema"
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
            development_id = development_plan.development_id,
            competence_id = development_plan.competence_id,
            gap = development_plan.gap,
            action = development_plan.action,
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
        message= "Desenvolvimento criado com sucesso!",
        development_plan= DevelopmentPlanResponse(
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
            status_code= status.HTTP_403_FORBIDDEN,
            detail = "Acesso negado. Apenas membros do RH podem listar todos os planos de desenvolvimento"
        )
    
    existing_development= db.query(Development).filter(Development.id == development_id).first()
    
    if not existing_development:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desenvolvimento não encontrado."
        )
        
    records = db.query(DevelopmentPlan).filter(
        DevelopmentPlan.development_id == development_id
    ).all()
    
    return records
