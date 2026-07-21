import re

INVOICE_NUMBER_CANDIDATE_PATTERNS = [
    re.compile(r"FACTURA\s*:\s*(?:\n|\s)*([A-Z0-9]+[\/\-][0-9]+)", re.IGNORECASE),
    re.compile(r"(?:factura|invoice)[^\n]{0,80}?([A-Z0-9]+[\/\-][0-9]+)", re.IGNORECASE),
    re.compile(r"\b([0-9]{5,}\/[A-Z][0-9])\b", re.IGNORECASE),
    re.compile(r"\b([A-Z][0-9]\/[0-9]{4,})\b", re.IGNORECASE),
    re.compile(r"\b([A-Z]{1,3}[0-9]?[\/\-][0-9]{4,})\b", re.IGNORECASE),
    re.compile(r"#\s*([0-9]{4,})", re.IGNORECASE),
]

DATE_PATTERNS = [
    re.compile(r"FECHA\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", re.IGNORECASE),
    re.compile(r"(?:fecha|date)[^0-9]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", re.IGNORECASE),
    re.compile(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"),
]

TAX_ID_PATTERNS = [
    re.compile(r"DNI\/CIF\s+([A-Z]?\d{8}[A-Z]?)", re.IGNORECASE),
    re.compile(r"\b([A-Z]\d{7,8})\b"),
    re.compile(r"\b(\d{8}[A-Z])\b"),
]

BASE_PATTERNS = [
    re.compile(r"BASES\s+IVA\s+%?\s*IVA\s+CUOTA\s+IVA\s+(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"base\s+imponible[^0-9]*(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"subtotal[^0-9]*(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"TOTAL\s+BRUTO[^0-9]*(\d+[.,]\d{2})", re.IGNORECASE),
]

TAX_PATTERNS = [
    re.compile(r"BASES\s+IVA\s+%?\s*IVA\s+CUOTA\s+IVA\s+\d+[.,]\d{2}\s+\d+[.,]\d{2}\s+(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"Total\s+Impuestos\s+(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"(?:iva|vat)[^0-9]*(\d+[.,]\d{2})", re.IGNORECASE),
]

TOTAL_PATTERNS = [
    re.compile(r"TOTAL\s+LIQUIDO\s+(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"TOTAL\s+L[IÍ]QUIDO\s+(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"total[^0-9]*(\d+[.,]\d{2})", re.IGNORECASE),
]
