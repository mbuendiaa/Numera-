import re

def _to_number(raw: str) -> float | None:
    if not raw:
        return None
    cleaned = raw.replace("€", "").replace(" ", "").strip()
    cleaned = cleaned.replace(".", "").replace(",", ".") if "," in cleaned else cleaned
    try:
        return float(cleaned)
    except ValueError:
        return None

def _field(value, confidence: float, source: str):
    return {"value": value, "confidence": confidence, "source": source}

class InvoiceParser:
    def parse(self, text: str) -> tuple[dict, list[str]]:
        explanation = []
        fields = {}

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        if lines:
            fields["supplier_name"] = _field(lines[0], 0.55, "heuristic:first_non_empty_line")
            explanation.append("Supplier candidate extracted from first non-empty OCR line.")

        invoice_match = re.search(r"(factura|invoice)[^\n#]*[#:\s]+([A-Z0-9\\-\\/]+)", clean_text, re.IGNORECASE)
        if invoice_match:
            fields["invoice_number"] = _field(invoice_match.group(2), 0.80, "regex:invoice_number")
            explanation.append("Invoice number extracted with regex.")

        date_match = re.search(r"(fecha|date)[^0-9]*(\\d{1,2}[\\/\\-]\\d{1,2}[\\/\\-]\\d{2,4})", clean_text, re.IGNORECASE)
        if date_match:
            fields["issue_date"] = _field(date_match.group(2), 0.75, "regex:date")
            explanation.append("Issue date extracted with regex.")

        total_matches = re.findall(r"total[^0-9]*(\\d+[\\.,]?\\d*)", clean_text, re.IGNORECASE)
        if total_matches:
            total = _to_number(total_matches[-1])
            fields["total_amount"] = _field(total, 0.85, "regex:last_total")
            explanation.append("Total amount extracted with regex.")

        base_match = re.search(r"base\\s+imponible[^0-9]*(\\d+[\\.,]?\\d*)", clean_text, re.IGNORECASE)
        if base_match:
            fields["base_amount"] = _field(_to_number(base_match.group(1)), 0.80, "regex:base_imponible")
            explanation.append("Base amount extracted with regex.")

        iva_match = re.search(r"(iva|vat)[^0-9]*(\\d+[\\.,]?\\d*)", clean_text, re.IGNORECASE)
        if iva_match:
            fields["tax_amount"] = _field(_to_number(iva_match.group(2)), 0.75, "regex:iva")
            explanation.append("Tax amount extracted with regex.")

        if not fields:
            explanation.append("No invoice fields extracted.")
        return fields, explanation
