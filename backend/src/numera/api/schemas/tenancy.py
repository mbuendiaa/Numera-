from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from numera.api.schemas.auth import UserRole


class CompanyWithRole(BaseModel):
    id: str
    name: str
    country: str
    currency: str
    role: UserRole
    is_active: bool
    selected: bool


class MembershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    company_id: str
    role: UserRole
    is_active: bool
    created_at: datetime
    created_by: str | None = None


class MemberRead(MembershipRead):
    email: str
    name: str


class MemberAdd(BaseModel):
    email: str
    role: UserRole = UserRole.readonly

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value:
            raise ValueError("Invalid email address")
        return value


class MemberRoleUpdate(BaseModel):
    role: UserRole


class ActiveCompanyRead(BaseModel):
    company_id: str
    company_name: str
    role: UserRole


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str | None
    user_id: str | None
    action: str
    entity_type: str
    entity_id: str | None
    details_json: str
    created_at: datetime
