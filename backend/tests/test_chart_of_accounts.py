from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from numera.domain.accounting.models import ChartAccount
from numera.engines.chart_of_accounts.engine import ChartOfAccountsEngine
from numera.infrastructure.database.base import Base
from numera.infrastructure.repositories import AccountRepository


def make_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    return ChartOfAccountsEngine(AccountRepository(db))


def test_seed_and_query_default_pgc_accounts():
    chart = make_engine()
    assert chart.seed_defaults("company_test") >= 10
    account = chart.get("company_test", "600000")
    assert account.name == "Compras de mercaderías"
    assert account.category == "expense"
    assert account.financial_statement == "profit_and_loss"


def test_seed_is_idempotent():
    chart = make_engine()
    first = chart.seed_defaults("company_test")
    second = chart.seed_defaults("company_test")
    assert first > 0
    assert second == 0


def test_create_custom_account():
    chart = make_engine()
    created = chart.create(
        "company_test",
        ChartAccount(
            code="600100",
            name="Compras de pescado",
            group=6,
            category="expense",
            normal_balance="debit",
            financial_statement="profit_and_loss",
            vat_behavior="deductible",
        ),
    )
    assert created.code == "600100"
    assert chart.get("company_test", "600100").name == "Compras de pescado"
