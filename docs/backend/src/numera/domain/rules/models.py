from pydantic import BaseModel


class Rule(BaseModel):
    rule_id: str
    company_id: str
    category: str
    description: str
    severity: str
    status: str = "active"
