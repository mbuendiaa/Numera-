from numera.domain.accounting.models import ChartAccount
from numera.engines.chart_of_accounts.seed import DEFAULT_PGC_ACCOUNTS

DEFAULT_SPANISH_CHART = {account.code: account for account in DEFAULT_PGC_ACCOUNTS}


class ChartOfAccounts:
    """In-memory chart used by unit tests and standalone engine execution."""

    def __init__(self, accounts: dict[str, ChartAccount] | None = None):
        self.accounts = accounts or DEFAULT_SPANISH_CHART

    def get(self, company_id_or_code: str, code: str | None = None) -> ChartAccount:
        account_code = code or company_id_or_code
        if account_code not in self.accounts:
            raise KeyError(f"Account {account_code} not found in chart of accounts.")
        return self.accounts[account_code]
