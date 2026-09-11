from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.config.database import Base  

class EvaluationQuestion(Base):
    __tablename__ = "evaluation_question"
    
    evaluation_id = Column(Integer, ForeignKey("evaluation.id"), primary_key=True, nullable=False)
    question_id = Column(Integer, ForeignKey("form_question.id"), primary_key=True, nullable=False)
    
    evaluation = relationship("Evaluation")
    question = relationship("FormQuestion")