from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import or_

from sqlalchemy.orm import Session
from app.config.database import get_db
from app.config import security
from app.models.auth.role import Role
from app.models.auth.user import User
from app.models.evaluation.evaluation import Evaluation
from app.models.auth.enterprise import Enterprise
from app.schemas.evaluation.evaluation import EvaluationCreate, EvaluationCreateResponse, EvaluationDetailResponse, EvaluationResponse

    
router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

@router.post(
    "/create", 
    status_code=status.HTTP_201_CREATED, 
    response_model=EvaluationCreateResponse,
    summary="Cria uma nova avaliação."
)

def create_evaluation(
    evaluation: EvaluationCreate,
    db:Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Gestor", "Recursos Humanos"]
    
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas Gestores e membros do RH podem criar uma nova avaliação."
        )
        
    
    existing_user = db.query(User).filter(User.id == evaluation.user_id).first()
    existing_evaluator = db.query(User).filter(User.id == evaluation.evaluator_id).first()
    
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O(a) colaborador(a) informado(a) não existe no sistema."
        )
        
    if not existing_evaluator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O(a) avaliador(a) informado(a) não existe no sistema."
        )
    
    if evaluation.type == "SELF":
        if existing_user.id != existing_evaluator.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A autoavaliação deve ser feita pelo próprio colaborador."
            )
    
    elif evaluation.type == "MANAGER":
        if existing_user.id == existing_evaluator.id: 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A avaliação do tipo MANAGER não pode ser realizada pelo próprio colaborador."
            )
            
            
        if existing_user.manager_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O(a) colaborador(a) informado(a) não possui um gestor direto vinculado no seu cadastro."
            )
            
        if existing_evaluator.id != existing_user.manager_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Acesso negado. Apenas o gestor direto (ID: {existing_user.manager_id}) pode avaliar este colaborador."
            )
        role_evaluator = db.query(Role).filter(Role.id == existing_evaluator.role_id).first()
        if not role_evaluator or role_evaluator.name != "Gestor":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O avaliador informado deve possuir o perfil de Gestor."
                )
    else: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O tipo de avaliação informado é inválido. Os tipos válidos são: 'SELF' ou 'MANAGER'."
        )
    
            
    existing_enterprise = db.query(Enterprise).filter(Enterprise.id == evaluation.enterprise_id).first()
    
    if not existing_enterprise:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A empresa informada não existe no sistema."
        )
        
    new_evaluation = Evaluation(
        user_id = evaluation.user_id,
        evaluator_id = evaluation.evaluator_id,
        enterprise_id = evaluation.enterprise_id,
        type = evaluation.type
    )
    
    try:
        db.add(new_evaluation)
        db.commit()
        db.refresh(new_evaluation)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar a avaliação: {str(e)}"
        )
        
    return EvaluationCreateResponse(
        message = "Avaliação criada com sucesso!",
        evaluation = EvaluationResponse(
            id=new_evaluation.id,
            user_id=new_evaluation.user_id,
            evaluator_id=new_evaluation.evaluator_id,
            enterprise_id=new_evaluation.enterprise_id,
            type=new_evaluation.type,
            created_at=str(new_evaluation.created_at)
        )
    )
    
@router.get(
    "/list",
    response_model=list[EvaluationDetailResponse],
    summary="Lista todas as avaliações cadastradas."
)

def list_evaluations(
    db:Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    
    if user_logged["role"] not in roles_permitted:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Acesso negado. Apenas membros do RH podem listar todas as avaliações"
            )

    return db.query(Evaluation).all()


@router.get(
    "/{user_id}",
    response_model=list[EvaluationDetailResponse],
    summary="Lista todas as avaliações de um usuário específico."
)

def list_evaluation_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    
    existing_user = db.query(User).filter(User.id == user_id).first()
    is_user = (existing_user.id == user_logged["user_id"])
    
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )
        

    if user_logged['role'] == 'Colaborador':
        
        if not (is_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Você não tem permissão para acessar a avaliação deste usuário"
                )
        
        records = db.query(Evaluation).filter(
                Evaluation.user_id == user_id, Evaluation.type == 'SELF'
         ).all()  
        
    
    if user_logged["role"] == 'Gestor':
        
        if user_logged["user_id"] != existing_user.manager_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Apenas o gestor direto (ID: {existing_user.manager_id}) pode acessar esta avaliação."
            )

        
        records = db.query(Evaluation).filter(
                        Evaluation.user_id == user_id, Evaluation.type == 'MANAGER'
                 ).all() 
        
    if user_logged["role"] == 'Recursos Humanos':
        
        records = db.query(Evaluation).filter(
                            Evaluation.user_id == user_id
                     ).all() 
    
    return records
