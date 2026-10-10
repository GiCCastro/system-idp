from collections import defaultdict
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.evaluation.evaluation_answer import EvaluationAnswer
from app.models.evaluation.form_question import FormQuestion
from app.models.evaluation.evaluation import Evaluation
from app.models.competence.position_competence import PositionCompetence
from app.models.competence.position import Position
from app.models.auth.user import User

def get_average_scores_by_type(
    db: Session,
    user_id: int,
    evaluation_type: str,
    cycle: str
) -> tuple[dict[int, float], dict[int, list[str]]]:
    
    query = (
        db.query(EvaluationAnswer.score, EvaluationAnswer.answer_text, FormQuestion.competence_id)
        .join(FormQuestion, EvaluationAnswer.question_id == FormQuestion.id)
        .join(Evaluation, EvaluationAnswer.evaluation_id == Evaluation.id)
        .filter(Evaluation.user_id == user_id, Evaluation.type == evaluation_type)
    )
    
    query = query.filter(Evaluation.cycle == cycle)
    
    records = query.all()
    
    grouped_scores = defaultdict(list)
    grouped_answers = defaultdict(list)
    
    for score, text, competence_id in records:
        grouped_scores[competence_id].append(score)
        if text and text.strip():
            grouped_answers[competence_id].append(text.strip())
        
    for competence_id, scores in grouped_scores.items():
        grouped_scores[competence_id] = sum(scores) / len(scores)
    
    return grouped_scores, grouped_answers

def find_mentors_for_competence(
    db: Session,
    competence_id: int,
    enterprise_id: int,
    exclude_user_id: int,
    cycle: str | None = None,
    min_score: float = 4.0
) -> list[dict]:
    query = (
        db.query(
            User.id,
            User.name.label("user_name"),
            Position.name.label("position_name"),
            Evaluation.type,
            EvaluationAnswer.score,
        )
        .join(Position, User.position_id == Position.id)
        .join(Evaluation, Evaluation.user_id == User.id)
        .join(EvaluationAnswer, EvaluationAnswer.evaluation_id == Evaluation.id)
        .join(FormQuestion, EvaluationAnswer.question_id == FormQuestion.id)
        .filter(
            User.enterprise_id == enterprise_id,
            User.id != exclude_user_id,
            FormQuestion.competence_id == competence_id,
        )
    )

    if cycle:
        query = query.filter(Evaluation.cycle == cycle)

    records = query.all()

    scores_by_user = defaultdict(lambda: {"SELF": [], "MANAGER": []})
    user_info = {}

    for user_id, user_name, position_name, eval_type, score in records:
        val_str = str(eval_type.value if hasattr(eval_type, "value") else eval_type).upper()
        
        if "SELF" in val_str:
            clean_type = "SELF"
        elif "MANAGER" in val_str:
            clean_type = "MANAGER"
        else:
            continue

        scores_by_user[user_id][clean_type].append(score)
        user_info[user_id] = {"user_name": user_name, "position_name": position_name}

    mentors = []
    for user_id, type_dict in scores_by_user.items():
        self_list = type_dict.get("SELF", [])
        manager_list = type_dict.get("MANAGER", [])

        if not self_list or not manager_list:
            continue

        avg_self = sum(self_list) / len(self_list)
        avg_manager = sum(manager_list) / len(manager_list)

        calibrated_score = (avg_manager * 0.7) + (avg_self * 0.3)

        if calibrated_score >= min_score:
            mentors.append({
                "user_name": user_info[user_id]["user_name"],
                "position_name": user_info[user_id]["position_name"],
                "score_in_competence": round(calibrated_score, 2)
            })
            
    mentors.sort(key=lambda m: m["score_in_competence"], reverse=True)
    return mentors[:2]

def calculate_calibrated_gaps(
    db: Session,
    user_id: int,
    cycle: str,
    target_position_id: int | None = None,
    enterprise_id: int | None = None,
) -> list[dict]:

    self_scores, self_answers = get_average_scores_by_type(db, user_id, "SELF", cycle=cycle)
    manager_scores, manager_answers = get_average_scores_by_type(db, user_id, "MANAGER", cycle=cycle)

    if not self_scores or not manager_scores:
        return []

    position_competences = db.query(PositionCompetence).filter(PositionCompetence.position_id == target_position_id).all()
    
    gaps_deficit = []
    for position_competence in position_competences:
        competence_id = position_competence.competence_id
        self_score = self_scores.get(competence_id)
        manager_score = manager_scores.get(competence_id)
        
        if self_score is None or manager_score is None:
            continue
        
        final_score = (manager_score * 0.7) + (self_score * 0.3)
        gap = round(final_score - position_competence.expected_level, 2)
        
        comments = []
        if competence_id in self_answers:
            comments.extend([f"Autoavaliação: {comment}" for comment in self_answers[competence_id]])
        if competence_id in manager_answers:
            comments.extend([f"Avaliação do Gestor: {comment}" for comment in manager_answers[competence_id]])
        
        if gap < 0:
            
            suggested_mentors = []
            if enterprise_id:
                suggested_mentors = find_mentors_for_competence(
                    db=db,
                    competence_id=competence_id,
                    enterprise_id=enterprise_id,
                    exclude_user_id=user_id,
                    cycle=cycle
                )
            
            gaps_deficit.append({
                "competence_id": competence_id,
                "competence_name": position_competence.competence.name,
                "expected_level": position_competence.expected_level,
                "actual_score": round(final_score, 2),
                "self_score": round(self_score, 2) if self_score else None,
                "manager_score": round(manager_score, 2) if manager_score else None,
                "gap": gap,
                "comments": comments,
                "suggested_mentors": suggested_mentors
            })
        
    return gaps_deficit
