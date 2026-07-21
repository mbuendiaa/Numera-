from numera.domain.accounting.models import ChartAccount

DEFAULT_SPANISH_CHART = {
    "400000": ChartAccount(code="400000", name="Proveedores", type="liability"),
    "430000": ChartAccount(code="430000", name="Clientes", type="asset"),
    "472000": ChartAccount(code="472000", name="Hacienda Pública, IVA soportado", type="asset"),
    "477000": ChartAccount(code="477000", name="Hacienda Pública, IVA repercutido", type="liability"),
    "600000": ChartAccount(code="600000", name="Compras de mercaderías", type="expense"),
    "700000": ChartAccount(code="700000", name="Ventas de mercaderías", type="income"),
    "572000": ChartAccount(code="572000", name="Bancos", type="asset"),
}


class ChartOfAccounts:
    def __init__(self, accounts: dict[str, ChartAccount] | None = None):
        self.accounts = accounts or DEFAULT_SPANISH_CHART

    def get(self, code: str) -> ChartAccount:
        if code not in self.accounts:
            raise KeyError(f"Account {code} not found in chart of accounts.")
        return self.accounts[code]
