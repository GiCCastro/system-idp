from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config import security
from app.schemas.competence.position import PositionCreate, PositionResponse, PositionCreateResponse
from app.models.competence.position import Position

router = APIRouter(prefix="/position", tags=["Position"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=PositionCreateResponse,
    summary="Cadastra um novo cargo no sistema"
)

def create_position(
    position: PositionCreate,
    db:Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    
    roles_permitted = ["Recursos Humanos"]
    
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso Negado. Apenas membros do RH podem cadastrar novos cargos."
        )
        
    existing_position = db.query(Position).filter(Position.name.ilike(position.name)).first()
    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este cargo já está cadastrado no sistema"
        )
        
    new_position = Position(
        name=position.name,
        description=position.description
    )
    
    try:
        db.add(new_position)
        db.commit()
        db.refresh(new_position)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao cadastrar cargo {str(e)}."
        )
        
    return PositionCreateResponse(
        message="Cargo cadastrado com sucesso!",
        position=PositionResponse(
            id=new_position.id,
            name=new_position.name,
            description=new_position.description
        )
    )
    
@router.get(
    "/list",
    response_model=list[PositionResponse],
    summary="Lista todos os cargos cadastrados"    
)

def list_position(
    db:Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    
    return db.query(Position).all()
