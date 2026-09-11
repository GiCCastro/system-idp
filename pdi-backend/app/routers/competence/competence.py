from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config import security
from app.schemas.competence.competence import CompetenceCreate, CompetenceCreateResponse, CompetenceResponse
from app.models.competence.competence import Competence

router = APIRouter(prefix="/competences", tags=["Competences"])

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=CompetenceCreateResponse,
    summary="Cadastra um nova competência no sistema"
)

def create_competence(
    competence: CompetenceCreate,
    db:Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    
    roles_permitted = ["Recursos Humanos"]
    
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso Negado. Apenas membros do RH podem cadastrar novas competências."
        )
        
    existing_competence = db.query(Competence).filter(Competence.name.ilike(competence.name)).first()
    if existing_competence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta competência já está cadastrada no sistema"
        )
        
    new_competence = Competence(
        name=competence.name,
        description=competence.description
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
    response_model=list[CompetenceResponse],
    summary="Lista todas as competências cadastradas"
)
    
def list_competences(
    db:Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
        
    return db.query(Competence).all()