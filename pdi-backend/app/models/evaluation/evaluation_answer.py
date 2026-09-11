from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.config.database import Base

class EvaluationAnswer(Base):
    __tablename__ = "evaluation_answer"
    
    evaluation_id = Column(Integer, ForeignKey("evaluation.id"), primary_key=True, nullable=False)
    question_id = Column(Integer, ForeignKey("form_question.id"), primary_key=True, nullable=False)
    answer_text = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)
        
    evaluation = relationship("Evaluation")
    question = relationship("FormQuestion")