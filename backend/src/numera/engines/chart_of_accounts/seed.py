from numera.domain.accounting.models import ChartAccount

# Initial operational subset of the Spanish Plan General de Contabilidad.
# The model is deliberately richer than a code/name dictionary so reporting
# and future AI features can reason over accounting semantics.
DEFAULT_PGC_ACCOUNTS = (
    ChartAccount(code="400000", name="Proveedores", group=4, category="liability", normal_balance="credit", financial_statement="balance_sheet", vat_behavior="none", reconcilable=True),
    ChartAccount(code="410000", name="Acreedores por prestaciones de servicios", group=4, category="liability", normal_balance="credit", financial_statement="balance_sheet", vat_behavior="none", reconcilable=True),
    ChartAccount(code="430000", name="Clientes", group=4, category="asset", normal_balance="debit", financial_statement="balance_sheet", vat_behavior="none", reconcilable=True),
    ChartAccount(code="472000", name="Hacienda Pública, IVA soportado", group=4, category="asset", normal_balance="debit", financial_statement="balance_sheet", vat_behavior="deductible", reconcilable=False),
    ChartAccount(code="477000", name="Hacienda Pública, IVA repercutido", group=4, category="liability", normal_balance="credit", financial_statement="balance_sheet", vat_behavior="collected", reconcilable=False),
    ChartAccount(code="570000", name="Caja, euros", group=5, category="asset", normal_balance="debit", financial_statement="balance_sheet", vat_behavior="none", reconcilable=True),
    ChartAccount(code="572000", name="Bancos e instituciones de crédito c/c vista, euros", group=5, category="asset", normal_balance="debit", financial_statement="balance_sheet", vat_behavior="none", reconcilable=True),
    ChartAccount(code="600000", name="Compras de mercaderías", group=6, category="expense", normal_balance="debit", financial_statement="profit_and_loss", vat_behavior="deductible", reconcilable=False),
    ChartAccount(code="621000", name="Arrendamientos y cánones", group=6, category="expense", normal_balance="debit", financial_statement="profit_and_loss", vat_behavior="deductible", reconcilable=False),
    ChartAccount(code="622000", name="Reparaciones y conservación", group=6, category="expense", normal_balance="debit", financial_statement="profit_and_loss", vat_behavior="deductible", reconcilable=False),
    ChartAccount(code="623000", name="Servicios de profesionales independientes", group=6, category="expense", normal_balance="debit", financial_statement="profit_and_loss", vat_behavior="deductible", reconcilable=False),
    ChartAccount(code="624000", name="Transportes", group=6, category="expense", normal_balance="debit", financial_statement="profit_and_loss", vat_behavior="deductible", reconcilable=False),
    ChartAccount(code="625000", name="Primas de seguros", group=6, category="expense", normal_balance="debit", financial_statement="profit_and_loss", vat_behavior="exempt", reconcilable=False),
    ChartAccount(code="626000", name="Servicios bancarios y similares", group=6, category="expense", normal_balance="debit", financial_statement="profit_and_loss", vat_behavior="exempt", reconcilable=False),
    ChartAccount(code="628000", name="Suministros", group=6, category="expense", normal_balance="debit", financial_statement="profit_and_loss", vat_behavior="deductible", reconcilable=False),
    ChartAccount(code="629000", name="Otros servicios", group=6, category="expense", normal_balance="debit", financial_statement="profit_and_loss", vat_behavior="deductible", reconcilable=False),
    ChartAccount(code="700000", name="Ventas de mercaderías", group=7, category="income", normal_balance="credit", financial_statement="profit_and_loss", vat_behavior="collected", reconcilable=False),
    ChartAccount(code="705000", name="Prestaciones de servicios", group=7, category="income", normal_balance="credit", financial_statement="profit_and_loss", vat_behavior="collected", reconcilable=False),
)
