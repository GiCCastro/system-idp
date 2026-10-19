from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config import security
from app.models.competence.competence import Competence
from app.models.competence.position import Position
from app.schemas.competence.position_competence import PositionCompetenceCreate, PositionCompetenceDetailResponse, PositionCompetenceResponse, PositionCompetenceCreateResponse
from app.models.competence.position_competence import PositionCompetence
from app.utils.pagination import PaginatedResponse, paginate

router = APIRouter(prefix="/position_competence", tags=["Position_Competence"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=PositionCompetenceCreateResponse,
    summary="Define níveis esperados por cargo para a empresa do usuário logado."
)
def create_relation_position_competence(
    position_competence: PositionCompetenceCreate,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso Negado. Apenas membros do RH podem definir níveis esperados por cargo."
        )

    enterprise_id = user_logged.get("enterprise_id")
    if not enterprise_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário logado não possui empresa vinculada."
        )
    
    existing_position = db.query(Position).filter(Position.id == position_competence.position_id).first()
    if not existing_position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O cargo informado não existe no sistema."
        )

    if existing_position.enterprise_id != enterprise_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. O cargo informado pertence a outra empresa."
        )
        
    existing_competence = db.query(Competence).filter(Competence.id == position_competence.competence_id).first()
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
        
    existing_relation = db.query(PositionCompetence).filter(
        PositionCompetence.position_id == position_competence.position_id,
        PositionCompetence.competence_id == position_competence.competence_id
    ).first()
    
    if existing_relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nível esperado para esta competência já foi definido para este cargo."        
        )
        
    if position_competence.expected_level < 1 or position_competence.expected_level > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nível esperado deve ser numa escala de 1 a 5"    
        )    
        
    new_relation = PositionCompetence(
        position_id = position_competence.position_id,
        competence_id = position_competence.competence_id,
        expected_level = position_competence.expected_level
    )
    
    try:
        db.add(new_relation)
        db.commit()
        db.refresh(new_relation)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao definir nível esperado para esta competência {str(e)}"
        )
        
    return {
        "message": "Nível esperado para competência definido com sucesso!",
        "position_competence": {
            "position_id": new_relation.position_id,
            "competence_id": new_relation.competence_id,
            "expected_level": new_relation.expected_level
        }
    }
    
@router.get(
    "/list",
    response_model=PaginatedResponse[PositionCompetenceDetailResponse],
    summary="Lista todos os níveis esperados por cargo da empresa com paginação."
)
def list_position_competence(
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=10, ge=1, le=100, description="Quantidade por página"),
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    query = (
        db.query(PositionCompetence)
        .join(Position, PositionCompetence.position_id == Position.id)
    )
    if user_logged.get("enterprise_id"):
        query = query.filter(Position.enterprise_id == user_logged["enterprise_id"])
    return paginate(query, page=page, limit=limit)
