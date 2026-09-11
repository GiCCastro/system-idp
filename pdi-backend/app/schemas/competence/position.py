from pydantic import BaseModel

class PositionCreate(BaseModel):
    
    name: str
    description: str
    
class PositionResponse(PositionCreate):
    id: int
    
    class Config:
        from_attributes = True
        
class PositionCreateResponse(BaseModel):
    message: str
    position: PositionResponse