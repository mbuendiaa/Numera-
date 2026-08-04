import re

INVOICE_NUMBER_CANDIDATE_PATTERNS = [
    re.compile(r"FACTURA\s*:\s*(?:\n|\s)*([A-Z0-9]+[\/\-][0-9]+)", re.IGNORECASE),
    re.compile(r"(?:factura|invoice)\s*(?:n[ºo°]|no\.?|#)?[^\n]{0,30}?((?:[A-Z]{1,5}\s+)?[A-Z0-9]+[\/\-][0-9]+)", re.IGNORECASE),
    re.compile(r"\b([0-9]{5,}\/[A-Z][0-9])\b", re.IGNORECASE),
    re.compile(r"\b([A-Z][0-9]\/[0-9]{4,})\b", re.IGNORECASE),
    re.compile(r"\b([A-Z]{1,3}[0-9]?[\/\-][0-9]{4,})\b", re.IGNORECASE),
    re.compile(r"#\s*([0-9]{4,})", re.IGNORECASE),
]

DATE_PATTERNS = [
    re.compile(r"FECHA\s+(\d{1,2}[.\/\-]\d{1,2}[.\/\-]\d{2,4})", re.IGNORECASE),
    re.compile(r"(?:fecha|date)[^0-9]*(\d{1,2}[.\/\-]\d{1,2}[.\/\-]\d{2,4})", re.IGNORECASE),
    re.compile(r"(\d{1,2}[.\/\-]\d{1,2}[.\/\-]\d{2,4})"),
]

TAX_ID_PATTERNS = [
    re.compile(r"DNI\/CIF\s+([A-Z]?\d{8}[A-Z]?)", re.IGNORECASE),
    re.compile(r"\b([A-Z]\d{7,8})\b"),
    re.compile(r"\b(\d{8}[A-Z])\b"),
]

BASE_PATTERNS = [
    re.compile(r"BASES\s+IVA\s+%?\s*IVA\s+CUOTA\s+IVA\s+(\d{1,3}(?:\.\d{3})*,\d{2}|\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"Base\s+de\s+Incid[eê]ncia[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2}|\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"base\s+imponible[^0-9]*(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"subtotal[^0-9]*(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"TOTAL\s+BRUTO[^0-9]*(\d+[.,]\d{2})", re.IGNORECASE),
]

TAX_PATTERNS = [
    re.compile(r"BASES\s+IVA\s+%?\s*IVA\s+CUOTA\s+IVA\s+\d{1,3}(?:\.\d{3})*[.,]\d{2}\s+\d+[.,]\d{2}\s+(\d{1,3}(?:\.\d{3})*[.,]\d{2})", re.IGNORECASE),
    re.compile(r"(?:Taxa\s+Base\s+de\s+Incid[eê]ncia\s+Valor\s+I\.V\.A)[\s\S]{0,80}?\d+(?:[.,]\d+)?%?\s+\d{1,3}(?:\.\d{3})*,\d{2}\s+(\d{1,3}(?:\.\d{3})*,\d{2})", re.IGNORECASE),
    re.compile(r"Total\s+Impuestos\s+(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"(?:iva|vat)[^0-9]*(\d+[.,]\d{2})", re.IGNORECASE),
]

TOTAL_PATTERNS = [
    re.compile(r"TOTAL\s+LIQUIDO\s+(\d{1,3}(?:\.\d{3})*,\d{2}|\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"Total\s+do\s+documento(?:\s+EUR)?[^0-9]*(\d{1,3}(?:\.\d{3})*,\d{2}|\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"TOTAL\s+L[IÍ]QUIDO\s+(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"total[^0-9]*(\d+[.,]\d{2})", re.IGNORECASE),
]

CUSTOMER_NUMBER_PATTERNS = [
    re.compile(r"CLIENTE\s+(\d{2,})", re.IGNORECASE),
    re.compile(r"(?:N[ÚU]MERO|N[ºO])\s+CLIENTE[^0-9]*(\d{2,})", re.IGNORECASE),
]

DUE_DATE_PATTERNS = [
    re.compile(r"(?:VENCIMIENTO|VTO\.?)\s*[:\-]?\s*(\d{1,2}[.\/\-]\d{1,2}[.\/\-]\d{2,4})", re.IGNORECASE),
    re.compile(r"FORMA\s+DE\s+PAGO[\s\S]{0,120}?(\d{1,2}[.\/\-]\d{1,2}[.\/\-]\d{2,4})", re.IGNORECASE),
]

PAYMENT_METHOD_PATTERNS = [
    re.compile(r"FORMA\s+DE\s+PAGO\s+([A-ZÁÉÍÓÚÜÑ ]{3,40})", re.IGNORECASE),
]

VAT_RATE_PATTERNS = [
    re.compile(r"BASES\s+IVA\s+%?\s*IVA\s+CUOTA\s+IVA\s+\d+[.,]\d{2}\s+(\d+[.,]\d{2})", re.IGNORECASE),
    re.compile(r"(?:IVA|VAT)\s*(\d{1,2}(?:[.,]\d{1,2})?)\s*%", re.IGNORECASE),
]
