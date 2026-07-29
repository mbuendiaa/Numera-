import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from numera.api.dependencies import get_current_user, require_company_roles
from numera.api.schemas.auth import Message
from numera.api.schemas.tenancy import (
    ActiveCompanyRead,
    AuditLogRead,
    CompanyWithRole,
    MemberAdd,
    MemberRead,
    MembershipRead,
    MemberRoleUpdate,
)
from numera.domain.schemas import CompanyCreate, CompanyRead
from numera.infrastructure.database.session import get_db
from numera.infrastructure.persistence.models import (
    AuditLogORM,
    CompanyMembershipORM,
    CompanyORM,
    UserORM,
)

router = APIRouter()


def _audit(db: Session, *, user_id: str, company_id: str | None, action: str,
           entity_type: str, entity_id: str | None = None, details: dict | None = None) -> None:
    db.add(AuditLogORM(
        user_id=user_id,
        company_id=company_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details_json=json.dumps(details or {}, ensure_ascii=False),
    ))


def _membership(db: Session, user_id: str, company_id: str) -> CompanyMembershipORM | None:
    return db.scalar(select(CompanyMembershipORM).where(
        CompanyMembershipORM.user_id == user_id,
        CompanyMembershipORM.company_id == company_id,
        CompanyMembershipORM.is_active.is_(True),
    ))


@router.post("/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreate,
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = CompanyORM(**payload.model_dump())
    db.add(company)
    db.flush()
    db.add(CompanyMembershipORM(
        user_id=user.id,
        company_id=company.id,
        role="owner",
        created_by=user.id,
    ))
    # A newly created company becomes active immediately. This makes the
    # onboarding flow atomic: create company -> owner membership -> active
    # company, with no separate activation step required.
    user.company_id = company.id
    user.role = "owner"
    _audit(db, user_id=user.id, company_id=company.id, action="company.created",
           entity_type="company", entity_id=company.id)
    db.commit()
    db.refresh(company)
    return company


@router.get("/my", response_model=list[CompanyWithRole])
def my_companies(
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(CompanyORM, CompanyMembershipORM)
        .join(CompanyMembershipORM, CompanyMembershipORM.company_id == CompanyORM.id)
        .filter(CompanyMembershipORM.user_id == user.id)
        .order_by(CompanyORM.created_at.desc())
        .all()
    )
    return [CompanyWithRole(
        id=company.id,
        name=company.name,
        country=company.country,
        currency=company.currency,
        role=membership.role,
        is_active=membership.is_active,
        selected=user.company_id == company.id,
    ) for company, membership in rows]


@router.post("/{company_id}/activate", response_model=ActiveCompanyRead)
def activate_company(
    company_id: str,
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = _membership(db, user.id, company_id)
    if membership is None:
        raise HTTPException(status_code=403, detail="You do not have access to this company")
    company = db.get(CompanyORM, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    user.company_id = company_id
    user.role = membership.role
    _audit(db, user_id=user.id, company_id=company_id, action="company.activated",
           entity_type="company", entity_id=company_id)
    db.commit()
    return ActiveCompanyRead(company_id=company.id, company_name=company.name, role=membership.role)


@router.get("/{company_id}/members", response_model=list[MemberRead])
def list_members(
    company_id: str,
    _: CompanyMembershipORM = Depends(require_company_roles("owner", "admin", "accountant")),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.company_id != company_id:
        raise HTTPException(status_code=409, detail="Select this company as active first")
    rows = (
        db.query(CompanyMembershipORM, UserORM)
        .join(UserORM, UserORM.id == CompanyMembershipORM.user_id)
        .filter(CompanyMembershipORM.company_id == company_id)
        .order_by(UserORM.name.asc())
        .all()
    )
    return [MemberRead(
        id=m.id, user_id=m.user_id, company_id=m.company_id, role=m.role,
        is_active=m.is_active, created_at=m.created_at, created_by=m.created_by,
        email=u.email, name=u.name,
    ) for m, u in rows]


@router.post("/{company_id}/members", response_model=MembershipRead, status_code=status.HTTP_201_CREATED)
def add_member(
    company_id: str,
    payload: MemberAdd,
    _: CompanyMembershipORM = Depends(require_company_roles("owner", "admin")),
    actor: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if actor.company_id != company_id:
        raise HTTPException(status_code=409, detail="Select this company as active first")
    target = db.scalar(select(UserORM).where(UserORM.email == payload.email))
    if target is None:
        raise HTTPException(status_code=404, detail="User not found; the user must register first")
    existing = db.scalar(select(CompanyMembershipORM).where(
        CompanyMembershipORM.user_id == target.id,
        CompanyMembershipORM.company_id == company_id,
    ))
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=409, detail="User is already a company member")
        existing.is_active = True
        existing.role = payload.role.value
        membership = existing
    else:
        membership = CompanyMembershipORM(
            user_id=target.id, company_id=company_id, role=payload.role.value, created_by=actor.id
        )
        db.add(membership)
    _audit(db, user_id=actor.id, company_id=company_id, action="member.added",
           entity_type="membership", details={"target_user_id": target.id, "role": payload.role.value})
    db.commit()
    db.refresh(membership)
    return membership


@router.patch("/{company_id}/members/{user_id}", response_model=MembershipRead)
def update_member_role(
    company_id: str,
    user_id: str,
    payload: MemberRoleUpdate,
    _: CompanyMembershipORM = Depends(require_company_roles("owner", "admin")),
    actor: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if actor.company_id != company_id:
        raise HTTPException(status_code=409, detail="Select this company as active first")
    membership = _membership(db, user_id, company_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    if membership.role == "owner" and payload.role.value != "owner":
        owners = db.query(CompanyMembershipORM).filter(
            CompanyMembershipORM.company_id == company_id,
            CompanyMembershipORM.role == "owner",
            CompanyMembershipORM.is_active.is_(True),
        ).count()
        if owners <= 1:
            raise HTTPException(status_code=409, detail="A company must keep at least one owner")
    membership.role = payload.role.value
    if actor.id == user_id:
        actor.role = membership.role
    _audit(db, user_id=actor.id, company_id=company_id, action="member.role_updated",
           entity_type="membership", entity_id=membership.id, details={"role": membership.role})
    db.commit()
    db.refresh(membership)
    return membership


@router.delete("/{company_id}/members/{user_id}", response_model=Message)
def remove_member(
    company_id: str,
    user_id: str,
    _: CompanyMembershipORM = Depends(require_company_roles("owner", "admin")),
    actor: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if actor.company_id != company_id:
        raise HTTPException(status_code=409, detail="Select this company as active first")
    if actor.id == user_id:
        raise HTTPException(status_code=409, detail="You cannot remove yourself from the active company")
    membership = _membership(db, user_id, company_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    if membership.role == "owner":
        owners = db.query(CompanyMembershipORM).filter(
            CompanyMembershipORM.company_id == company_id,
            CompanyMembershipORM.role == "owner",
            CompanyMembershipORM.is_active.is_(True),
        ).count()
        if owners <= 1:
            raise HTTPException(status_code=409, detail="A company must keep at least one owner")
    membership.is_active = False
    target = db.get(UserORM, user_id)
    if target and target.company_id == company_id:
        target.company_id = None
    _audit(db, user_id=actor.id, company_id=company_id, action="member.removed",
           entity_type="membership", entity_id=membership.id, details={"target_user_id": user_id})
    db.commit()
    return Message(detail="Member removed successfully")


@router.get("/{company_id}/audit", response_model=list[AuditLogRead])
def audit_log(
    company_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    _: CompanyMembershipORM = Depends(require_company_roles("owner", "admin", "accountant")),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.company_id != company_id:
        raise HTTPException(status_code=409, detail="Select this company as active first")
    return (
        db.query(AuditLogORM)
        .filter(AuditLogORM.company_id == company_id)
        .order_by(AuditLogORM.created_at.desc())
        .limit(limit)
        .all()
    )
