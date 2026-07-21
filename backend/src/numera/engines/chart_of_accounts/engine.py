from numera.domain.accounting.models import ChartAccount
from numera.engines.chart_of_accounts.seed import DEFAULT_PGC_ACCOUNTS


class ChartOfAccountsEngine:
    def __init__(self, repository):
        self.repository = repository

    def seed_defaults(self, company_id: str) -> int:
        created = 0
        for account in DEFAULT_PGC_ACCOUNTS:
            _, was_created = self.repository.upsert(company_id, account)
            created += int(was_created)
        return created

    def ensure_seeded(self, company_id: str) -> None:
        if not self.repository.exists_for_company(company_id):
            self.seed_defaults(company_id)

    def get(self, company_id: str, code: str):
        self.ensure_seeded(company_id)
        return self.repository.get(company_id, code)

    def list(self, company_id: str, *, category: str | None = None, active_only: bool = True, search: str | None = None):
        self.ensure_seeded(company_id)
        return self.repository.list(company_id, category=category, active_only=active_only, search=search)

    def create(self, company_id: str, account: ChartAccount):
        existing = self.repository.get(company_id, account.code)
        if existing:
            raise ValueError(f"Account {account.code} already exists for company {company_id}.")
        obj, _ = self.repository.upsert(company_id, account)
        return obj
