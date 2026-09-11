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
    
    