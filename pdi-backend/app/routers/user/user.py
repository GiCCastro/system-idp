from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config import security
from app.models.auth.user import User
from app.schemas.auth.user import UserDetailResponse
from app.utils.pagination import PaginatedResponse, paginate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/list",
    response_model=PaginatedResponse[UserDetailResponse],
    summary="Lista todos os usuários cadastrados no sistema com paginação."
)
def list_users(
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=10, ge=1, le=100, description="Quantidade por página"),
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas membros do RH podem listar colaboradores."
        )

    query = db.query(User)
    if user_logged.get("enterprise_id"):
        query = query.filter(User.enterprise_id == user_logged["enterprise_id"])

    return paginate(query, page=page, limit=limit)