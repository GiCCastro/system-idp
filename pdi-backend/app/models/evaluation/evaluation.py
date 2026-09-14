import enum
from datetime import date
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Date, ForeignKey, Enum as SQLEnum

from app.config.database import Base 

class EvaluationTypeEnum(str, enum.Enum):
    SELF = "SELF"
    MANAGER = "MANAGER"

class Evaluation(Base):
    __tablename__ = "evaluation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    evaluator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    target_position_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    enterprise_id = Column(Integer, ForeignKey("enterprise.id"), nullable=True)
    created_at = Column(Date, default=date.today, nullable=False)
    user = relationship("User", foreign_keys=[user_id])
    evaluator = relationship("User", foreign_keys=[evaluator_id])
    target_position = relationship("Position", foreign_keys=[target_position_id])
    enterprise = relationship("Enterprise")
    type = Column(SQLEnum(EvaluationTypeEnum), nullable=False)