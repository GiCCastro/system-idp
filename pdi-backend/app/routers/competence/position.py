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
    summary="Cadastra um novo cargo no sistema para a empresa do usuário logado"
)
def create_position(
    position: PositionCreate,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso Negado. Apenas membros do RH podem cadastrar novos cargos."
        )

    enterprise_id = user_logged.get("enterprise_id")
    if not enterprise_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário logado não possui empresa vinculada."
        )
        
    existing_position = db.query(Position).filter(
        Position.name.ilike(position.name),
        Position.enterprise_id == enterprise_id
    ).first()

    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este cargo já está cadastrado para a sua empresa."
        )
        
    new_position = Position(
        name=position.name,
        description=position.description,
        enterprise_id=enterprise_id
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
    response_model=PaginatedResponse[PositionResponse],
    summary="Lista todos os cargos da empresa cadastrados com paginação"    
)
def list_position(
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=10, ge=1, le=100, description="Quantidade por página"),
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    query = db.query(Position)
    if user_logged.get("enterprise_id"):
        query = query.filter(Position.enterprise_id == user_logged["enterprise_id"])
    return paginate(query, page=page, limit=limit)
