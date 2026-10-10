from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
from sqlalchemy import or_

from sqlalchemy.orm import Session
from app.config.database import get_db
from app.config import security
from app.models.auth.role import Role
from app.models.auth.user import User
from app.models.competence.position import Position
from app.models.evaluation.evaluation import Evaluation
from app.models.evaluation.evaluation_question import EvaluationQuestion
from app.models.evaluation.form_question import FormQuestion
from app.models.auth.enterprise import Enterprise
from app.models.competence.position_competence import PositionCompetence
from app.schemas.evaluation.evaluation import EvaluationCreate, EvaluationCreateResponse, EvaluationDetailResponse, EvaluationResponse
from app.services.gemini_service import generate_form_questions_ai
from app.services.email_service import send_evaluation_notification
    
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
    
    if evaluation.target_position_id is not None:
        existing_position = db.query(Position).filter(Position.id == evaluation.target_position_id).first()
        if not existing_position:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O cargo informado para a avaliação não existe no sistema."
            )
    
    if evaluation.type == "SELF":
        if existing_user.id != existing_evaluator.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A autoavaliação deve ser feita pelo próprio colaborador."
            )
            
        existing_cycle = db.query(Evaluation).filter(
            Evaluation.user_id == evaluation.user_id,
            Evaluation.type == "SELF",
            Evaluation.cycle == evaluation.cycle
        ).first()
        
        if existing_cycle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe uma autoavaliação (SELF) cadastrada para este colaborador no ciclo '{evaluation.cycle}'."
            )
    
    elif evaluation.type == "MANAGER":
        if existing_user.id == existing_evaluator.id: 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A avaliação do tipo MANAGER não pode ser realizada pelo próprio colaborador."
            )
            
        existing_cycle = db.query(Evaluation).filter(
                    Evaluation.user_id == evaluation.user_id,
                    Evaluation.type == "MANAGER",
                    Evaluation.cycle == evaluation.cycle
                ).first()
                
        if existing_cycle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe uma avaliação (MANAGER) cadastrada para este colaborador no ciclo '{evaluation.cycle}'."
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
        target_position_id = evaluation.target_position_id,
        enterprise_id = evaluation.enterprise_id,
        type = evaluation.type,
        cycle = evaluation.cycle
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
            target_position_id=new_evaluation.target_position_id,
            enterprise_id=new_evaluation.enterprise_id,
            type=new_evaluation.type,
            cycle=new_evaluation.cycle,
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

@router.post(
    "/{evaluation_id}/generate-questions",
    status_code=status.HTTP_201_CREATED,
    summary="IA: Gera perguntas para o ciclo completo (Autoavaliação e Avaliação do Gestor)"
)
def generate_questions_for_evaluation(
    evaluation_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_logged: dict = Depends(security.get_logged_in_user)
):
    roles_permitted = ["Recursos Humanos"]
    if user_logged["role"] not in roles_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas membros do RH podem gerar perguntas via IA."
        )
        
    existing_evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not existing_evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada."
        )
    
    # 1. Recupera o colaborador avaliado de forma segura
    user = db.query(User).filter(User.id == existing_evaluation.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador associado à avaliação não foi encontrado."
        )

    # 2. Determina o cargo avaliado (target_position_id ou cargo atual do colaborador)
    user_pos_id = (
        existing_evaluation.target_position_id 
        or getattr(user, "id_position", None) 
        or getattr(user, "position_id", None)
    )
    if not user_pos_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O colaborador avaliado não possui um cargo definido."
        )

    position = db.query(Position).filter(Position.id == user_pos_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cargo associado à avaliação não foi encontrado no banco."
        )

    # 3. VALIDAÇÃO: Assegura que o ciclo possui AMBAS as avaliações (SELF e MANAGER)
    self_evaluation = db.query(Evaluation).filter(
        Evaluation.user_id == user.id,
        Evaluation.cycle == existing_evaluation.cycle,
        or_(Evaluation.target_position_id == position.id, Evaluation.target_position_id.is_(None)),
        Evaluation.type == "SELF"
    ).order_by(Evaluation.created_at.desc()).first()

    manager_evaluation = db.query(Evaluation).filter(
        Evaluation.user_id == user.id,
        Evaluation.cycle == existing_evaluation.cycle,
        or_(Evaluation.target_position_id == position.id, Evaluation.target_position_id.is_(None)),
        Evaluation.type == "MANAGER"
    ).order_by(Evaluation.created_at.desc()).first()

    if not self_evaluation or not manager_evaluation:
        missing = []
        if not self_evaluation:
            missing.append("Autoavaliação (SELF)")
        if not manager_evaluation:
            missing.append("Avaliação do Gestor (MANAGER)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível gerar perguntas. O ciclo está incompleto para este cargo. Falta cadastrar: {', '.join(missing)}."
        )

    # 4. Busca competências do cargo
    position_competences = db.query(PositionCompetence).filter(
        PositionCompetence.position_id == position.id
    ).all()
    
    if not position_competences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Este cargo não possui competências vinculadas."
        )
        
    competences_payload = [
        {
            "competence_id": pc.competence_id,
            "name": pc.competence.name,
            "expected_level": pc.expected_level
        }
        for pc in position_competences
    ]

    # 5. Gera perguntas com IA
    try:
        questions = generate_form_questions_ai(
            position_name=position.name,
            competences=competences_payload
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Serviço de IA temporariamente indisponível. Detalhes: {str(e)}"
        )
    
    # 6. Salva as perguntas e VINCULA A AMBAS AS AVALIAÇÕES (SELF e MANAGER)
    evaluations_to_link = [self_evaluation, manager_evaluation]

    for question in questions:
        new_form_question = FormQuestion(
            competence_id=question["competence_id"],
            question_text=question["question_text"],
        )
        db.add(new_form_question)
        db.flush()
        
        for eval_inst in evaluations_to_link:
            existing_link = db.query(EvaluationQuestion).filter(
                EvaluationQuestion.evaluation_id == eval_inst.id,
                EvaluationQuestion.question_id == new_form_question.id
            ).first()

            if not existing_link:
                db.add(EvaluationQuestion(
                    evaluation_id=eval_inst.id,
                    question_id=new_form_question.id
                ))
        
    db.commit()

    # 7. Dispara e-mails para ambas as pontas
    # E-mail para o Colaborador (Autoavaliação)
    if user.email:
        background_tasks.add_task(
            send_evaluation_notification,
            to_email=user.email,
            recipient_name=user.name,
            evaluation_type="SELF",
            employee_name=user.name
        )

    # E-mail para o Gestor
    manager_user = db.query(User).filter(User.id == manager_evaluation.evaluator_id).first()
    if manager_user and manager_user.email:
        background_tasks.add_task(
            send_evaluation_notification,
            to_email=manager_user.email,
            recipient_name=manager_user.name,
            evaluation_type="MANAGER",
            employee_name=user.name
        )

    return {
        "message": "Perguntas criadas pela IA com sucesso e notificações enviadas para colaborador e gestor!", 
        "total": len(questions),
        "linked_evaluations": {
            "self_evaluation_id": self_evaluation.id,
            "manager_evaluation_id": manager_evaluation.id
        }
    }