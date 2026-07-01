from pydantic import BaseModel


class Memory(BaseModel):
    memory_id: str
    company_id: str
    category: str
    description: str
    confidence: float
    status: str = "active"
