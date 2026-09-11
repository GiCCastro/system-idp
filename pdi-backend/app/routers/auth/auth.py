from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import or_ 
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config import security
from app.models.competence.position import Position
from app.schemas.auth.user import UserCreate, UserLogin, UserCreateResponse, Token, UserResponse
from app.models.auth.user import User
from app.models.auth.enterprise import Enterprise
from app.models.auth.role import Role

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register", 
    status_code=status.HTTP_201_CREATED, 
    response_model=UserCreateResponse, 
    summary="Cadastra um novo usuário no banco de dados"
)
def register_user(
    user: UserCreate, 
    db: Session = Depends(get_db), 
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas membros do RH podem cadastrar novos usuários."
        )

    # Verificações de duplicidade
    if db.query(User).filter(User.cpf == user.cpf).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este CPF já está cadastrado no sistema."
        )
        
    if db.query(User).filter(User.np == user.np).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este NP já está cadastrado no sistema."
        )
    
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está cadastrado no sistema."
        )
    
    # Validações relacionais
    existing_role = db.query(Role).filter(Role.id == user.role_id).first()
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A role informada não existe no sistema."
        )
    
    existing_enterprise = db.query(Enterprise).filter(Enterprise.id == user.enterprise_id).first()
    if not existing_enterprise:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A empresa informada não existe no sistema."
        )
        
    existing_position = db.query(Position).filter(Position.id == user.position_id).first()
    if not existing_position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O cargo informado não existe no sistema."
        )    
    
    # Validação do Gestor com tratamento seguro para nulos
    manager_name = None
    if user.manager_id:
        existing_manager = db.query(User).filter(User.id == user.manager_id).first()
        if not existing_manager:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O usuário informado como gestor não existe no sistema."
            )
            
        manager_role = db.query(Role).filter(Role.id == existing_manager.role_id).first()
        if not manager_role or manager_role.name != "Gestor":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O superior vinculado deve ter o perfil de Gestor."
            )
        manager_name = existing_manager.name
    
    password_hash = security.get_encrypted_password(user.password)

    new_user = User(
        cpf=user.cpf,
        name=user.name,
        email=user.email,
        password=password_hash,
        np=user.np,
        role_id=user.role_id,
        position_id=user.position_id,
        manager_id=user.manager_id,
        enterprise_id=user.enterprise_id,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao cadastrar usuário {str(e)}."
        )
    
    return UserCreateResponse( 
        message="Usuário cadastrado com sucesso!",
        user=UserResponse(
            id=new_user.id,
            cpf=new_user.cpf,
            name=new_user.name,
            email=new_user.email,
            np=new_user.np,
            role=existing_role.name,
            manager=manager_name,
            enterprise=existing_enterprise.name,
            position=existing_position.name
        )
    ) 

@router.post(
    "/login", 
    status_code=status.HTTP_200_OK, 
    response_model=Token, 
    summary="Autentica o usuário e devolve o Token JWT com a Role"
)
def login(
    credentials: UserLogin, 
    db: Session = Depends(get_db)
):
    user_db = db.query(User).filter(
        or_(User.email == credentials.email, User.np == credentials.np)
    ).first()

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou NP incorreto."
        )
    
    validate_password = security.verify_password(credentials.password, user_db.password)
    if not validate_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta."
        )
    
    role_user = db.query(Role).filter(Role.id == user_db.role_id).first()
    position_user = db.query(Position).filter(Position.id == user_db.position_id).first()
    enterprise_user = db.query(Enterprise).filter(Enterprise.id == user_db.enterprise_id).first()
    
    # Tratamento seguro da busca do gestor no Login
    manager_name = None
    if user_db.manager_id:
        manager_user = db.query(User).filter(User.id == user_db.manager_id).first()
        if manager_user:
            manager_name = manager_user.name

    token_jwt = security.create_access_token(data={
        "sub": str(user_db.id),
        "user_id": user_db.id,
        "role": role_user.name if role_user else None,
        "enterprise_id": user_db.enterprise_id
    })

    return Token(
        access_token=token_jwt,
        token_type="bearer",
        user=UserResponse(
            id=user_db.id,
            cpf=user_db.cpf,
            name=user_db.name,
            email=user_db.email,
            np=user_db.np,
            role=role_user.name if role_user else "",
            manager=manager_name,
            position=position_user.name if position_user else "",
            enterprise=enterprise_user.name if enterprise_user else ""
        )
    )