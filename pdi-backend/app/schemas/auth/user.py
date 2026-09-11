from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    cpf: str
    name: str
    email: EmailStr
    password: str
    np: str
    role_id: int
    manager_id: Optional[int] = None
    position_id: int
    enterprise_id: int
    
class UserResponse(BaseModel):
    id: int
    cpf: str
    name: str
    email: EmailStr
    np: str
    role: str
    manager: Optional[str] = None
    position: str
    enterprise: str
    
    class Config:
            from_attributes = True
            
class UserSimpleResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    np: str

    class Config:
        from_attributes = True
    
class UserCreateResponse(BaseModel):
    message: str
    user: UserResponse

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    np: Optional[str] = None
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

