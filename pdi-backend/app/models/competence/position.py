from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class Position(Base):
    __tablename__ = "position"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(300), nullable=True)
    enterprise_id = Column(Integer, ForeignKey("enterprise.id"), nullable=False)

    enterprise = relationship("Enterprise")