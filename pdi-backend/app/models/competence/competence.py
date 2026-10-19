from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class Competence(Base):
    __tablename__ = "competence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(300), nullable=True)
    enterprise_id = Column(Integer, ForeignKey("enterprise.id"), nullable=False)

    enterprise = relationship("Enterprise")
