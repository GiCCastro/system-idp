from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.config.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    np = Column(String(10), unique=True, index=True, nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    enterprise_id = Column(Integer, ForeignKey("enterprise.id"), nullable=False)

