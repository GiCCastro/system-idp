from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config import security
from app.schemas.competence.competence import CompetenceCreate, CompetenceCreateResponse, CompetenceResponse
from app.models.competence.competence import Competence
from app.utils.pagination import PaginatedResponse, paginate

router = APIRouter(prefix="/competences", tags=["Competences"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=CompetenceCreateResponse,
    summary="Cadastra uma nova competência no sistema para a empresa do usuário logado"
)
def create_competence(
    competence: CompetenceCreate,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso Negado. Apenas membros do RH podem cadastrar novas competências."
        )

    enterprise_id = user_logged.get("enterprise_id")
    if not enterprise_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário logado não possui empresa vinculada."
        )
        
    existing_competence = db.query(Competence).filter(
        Competence.name.ilike(competence.name),
        Competence.enterprise_id == enterprise_id
    ).first()

    if existing_competence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta competência já está cadastrada para a sua empresa."
        )
        
    new_competence = Competence(
        name=competence.name,
        description=competence.description,
        enterprise_id=enterprise_id
    )
    
    try:
        db.add(new_competence)
        db.commit()
        db.refresh(new_competence)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao cadastrar competência {str(e)}."
        )
        
    return CompetenceCreateResponse(
        message="Competência cadastrada com sucesso!",
        competence=CompetenceResponse(
            id=new_competence.id,
            name=new_competence.name,
            description=new_competence.description
        )
    )
    
@router.get(
    "/list",
    response_model=PaginatedResponse[CompetenceResponse],
    summary="Lista todas as competências da empresa cadastradas com paginação"
)
def list_competences(
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=10, ge=1, le=100, description="Quantidade por página"),
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    query = db.query(Competence)
    if user_logged.get("enterprise_id"):
        query = query.filter(Competence.enterprise_id == user_logged["enterprise_id"])
    return paginate(query, page=page, limit=limit)
