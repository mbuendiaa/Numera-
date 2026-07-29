import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    account_code: str
    confidence: float
    reason: str
    matched_value: str | None = None


def normalize_text(value: str | None) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"\s+", " ", value).strip().upper()
    return value


SUPPLIER_RULES = {
    "IBERDROLA": ("628000", 0.98),
    "ENDESA": ("628000", 0.98),
    "NATURGY": ("628000", 0.98),
    "REPSOL": ("628000", 0.94),
    "ORANGE": ("629000", 0.97),
    "VODAFONE": ("629000", 0.97),
    "TELEFONICA": ("629000", 0.97),
    "MOVISTAR": ("629000", 0.97),
}

KEYWORD_RULES = {
    "ELECTRICIDAD": ("628000", 0.90),
    "LUZ": ("628000", 0.88),
    "GAS": ("628000", 0.88),
    "TELEFONO": ("629000", 0.88),
    "INTERNET": ("629000", 0.90),
    "ALQUILER": ("621000", 0.90),
    "REPARACION": ("622000", 0.86),
    "MANTENIMIENTO": ("622000", 0.86),
    "SEGURO": ("625000", 0.90),
    "BANCO": ("626000", 0.82),
    "GESTORIA": ("623000", 0.86),
    "ASESORIA": ("623000", 0.86),
    "TRANSPORTE": ("624000", 0.86),
}


def classify_purchase(*, supplier_name: str | None, description: str | None, supplier_default_account: str | None = None) -> ClassificationResult:
    if supplier_default_account:
        return ClassificationResult(supplier_default_account, 0.99, "Supplier default account", supplier_default_account)

    supplier = normalize_text(supplier_name)
    text = normalize_text(description)
    for token, (account, confidence) in SUPPLIER_RULES.items():
        if token in supplier:
            return ClassificationResult(account, confidence, "Supplier rule", token)
    combined = f"{supplier} {text}".strip()
    for token, (account, confidence) in KEYWORD_RULES.items():
        if token in combined:
            return ClassificationResult(account, confidence, "Keyword rule", token)
    return ClassificationResult("600000", 0.65, "Default purchase account", None)
