from numera.engines.document import patterns
from numera.engines.document.models import ExtractedField, InvoiceExtraction


def _to_float(raw: str | None) -> float | None:
    if raw is None:
        return None
    cleaned = raw.replace("€", "").replace(" ", "").strip()
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _first_match(regex_list, text: str):
    for regex in regex_list:
        match = regex.search(text)
        if match:
            return match.group(1)
    return None


def _clean_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


class InvoiceExtractor:
    def extract(self, text: str) -> tuple[dict, list[str]]:
        explanation = []
        lines = _clean_lines(text)
        normalized = "\n".join(lines)
        result = InvoiceExtraction()

        supplier = self._extract_supplier(lines)
        if supplier:
            result.supplier_name = ExtractedField(value=supplier, confidence=0.80, source="heuristic:supplier_header")
            explanation.append("Supplier name extracted from invoice header.")

        tax_id = _first_match(patterns.TAX_ID_PATTERNS, normalized)
        if tax_id:
            result.supplier_tax_id = ExtractedField(value=tax_id, confidence=0.80, source="regex:tax_id")
            explanation.append("Tax ID extracted with regex.")

        invoice_number = self._extract_invoice_number(normalized)
        if invoice_number:
            result.invoice_number = ExtractedField(value=invoice_number, confidence=0.93, source="candidate_scoring:invoice_number")
            explanation.append("Invoice number extracted with candidate scoring.")

        date = _first_match(patterns.DATE_PATTERNS, normalized)
        if date:
            result.invoice_date = ExtractedField(value=date, confidence=0.85, source="regex:invoice_date")
            explanation.append("Invoice date extracted with regex.")

        base = _to_float(_first_match(patterns.BASE_PATTERNS, normalized))
        if base is not None:
            result.base_amount = ExtractedField(value=base, confidence=0.88, source="regex:base_amount")
            explanation.append("Base amount extracted with invoice totals regex.")

        tax = _to_float(_first_match(patterns.TAX_PATTERNS, normalized))
        if tax is not None:
            result.tax_amount = ExtractedField(value=tax, confidence=0.88, source="regex:tax_amount")
            explanation.append("Tax amount extracted with invoice totals regex.")

        total = _to_float(_first_match(patterns.TOTAL_PATTERNS, normalized))
        if total is not None:
            result.total_amount = ExtractedField(value=total, confidence=0.92, source="regex:total_liquido")
            result.currency = ExtractedField(value="EUR", confidence=0.80, source="heuristic:spanish_invoice_currency")
            explanation.append("Total amount extracted from TOTAL LIQUIDO.")

        result.global_confidence = self._confidence(result)
        if not explanation:
            explanation.append("No invoice fields extracted.")
        return result.model_dump(exclude_none=True), explanation

    def _extract_invoice_number(self, text: str) -> str | None:
        candidates = []
        for regex in patterns.INVOICE_NUMBER_CANDIDATE_PATTERNS:
            for match in regex.finditer(text):
                raw = match.group(1).strip()
                normalized = self._normalize_invoice_candidate(raw)
                score = self._score_invoice_candidate(normalized, text, match.start())
                candidates.append((normalized, score))
        if not candidates:
            return None
        return sorted(candidates, key=lambda item: item[1], reverse=True)[0][0]

    def _normalize_invoice_candidate(self, value: str) -> str:
        value = value.strip().replace(" ", "").upper()
        if "/" in value:
            left, right = value.split("/", 1)
            if left.isdigit() and len(left) >= 5 and len(right) <= 3 and right[0].isalpha():
                return f"{right}/{left}"
        return value

    def _score_invoice_candidate(self, candidate: str, text: str, position: int) -> int:
        score = 0
        before = text[max(0, position - 100):position].lower()
        after = text[position:position + 100].lower()

        if "factura" in before or "factura" in after:
            score += 80
        if "alb:" in before or "albaran" in before or "albarán" in before:
            score -= 90
        if "ref" in before or "n/ref" in before:
            score -= 30
        if candidate.startswith("A1/"):
            score -= 90
        if candidate.startswith("V"):
            score += 50
        if "/" in candidate:
            score += 25
        digits = "".join(ch for ch in candidate if ch.isdigit())
        if len(digits) >= 5:
            score += 25
        if position < max(250, len(text) * 0.25):
            score += 35
        return score

    def _extract_supplier(self, lines: list[str]) -> str | None:
        for line in lines[:8]:
            clean = line.strip()
            lower = clean.lower()
            if len(clean) < 3:
                continue
            if any(token in lower for token in ["factura", "cliente", "fecha", "hoja", "dni/cif"]):
                continue
            if clean.replace(".", "").replace(",", "").isdigit():
                continue
            if any(token in lower for token in ["s.l", "sl", "s.a", "sa", ",sl", "2000"]):
                return clean

        for line in lines[:8]:
            clean = line.strip()
            lower = clean.lower()
            if len(clean) >= 3 and not any(token in lower for token in ["factura", "cliente", "fecha", "hoja"]):
                return clean
        return None

    def _confidence(self, result: InvoiceExtraction) -> float:
        fields = [
            result.supplier_name,
            result.supplier_tax_id,
            result.invoice_number,
            result.invoice_date,
            result.base_amount,
            result.tax_amount,
            result.total_amount,
        ]
        present = [field.confidence for field in fields if field is not None]
        if not present:
            return 0.0
        return round(sum(present) / len(present), 2)
