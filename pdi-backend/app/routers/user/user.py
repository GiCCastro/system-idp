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


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Busca os detalhes de um usuário específico por ID."
)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    if user_logged.get("enterprise_id") and user.enterprise_id != user_logged["enterprise_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Este colaborador pertence a outra empresa."
        )

    is_self = (user.id == user_logged["user_id"])
    is_manager = (user.manager_id == user_logged["user_id"])
    is_hr = (user_logged["role"] == "Recursos Humanos")

    if not (is_self or is_manager or is_hr):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para visualizar os dados deste usuário."
        )

    return user
