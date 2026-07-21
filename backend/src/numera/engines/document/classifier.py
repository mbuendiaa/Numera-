class DocumentClassifier:
    def classify(self, text: str, filename: str) -> tuple[str, list[str]]:
        lower = f"{filename}\n{text}".lower()

        if any(k in lower for k in ["factura", "invoice", "iva", "vat", "total", "base imponible"]):
            return "invoice", ["Invoice-related keywords detected."]

        if any(k in lower for k in ["extracto", "statement", "saldo", "iban", "movimiento"]):
            return "bank_statement", ["Bank statement keywords detected."]

        if any(k in lower for k in ["nómina", "nomina", "payroll", "salario"]):
            return "payroll", ["Payroll keywords detected."]

        if any(k in lower for k in ["contrato", "contract", "agreement"]):
            return "contract", ["Contract keywords detected."]

        return "unknown", ["No strong document pattern detected."]
