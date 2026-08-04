import re
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


        customer_number = self._extract_customer_number(lines, normalized)
        if customer_number:
            result.customer_number = ExtractedField(value=customer_number, confidence=0.92, source="regex:customer_number")
            explanation.append("Customer number extracted from invoice header.")

        invoice_number = self._extract_invoice_number(normalized)
        if invoice_number:
            result.invoice_number = ExtractedField(value=invoice_number, confidence=0.93, source="candidate_scoring:invoice_number")
            explanation.append("Invoice number extracted with candidate scoring.")

        date = _first_match(patterns.DATE_PATTERNS, normalized)
        if date:
            result.invoice_date = ExtractedField(value=date, confidence=0.85, source="regex:invoice_date")
            explanation.append("Invoice date extracted with regex.")


        due_date = _first_match(patterns.DUE_DATE_PATTERNS, normalized)
        if due_date:
            result.due_date = ExtractedField(value=due_date, confidence=0.82, source="regex:due_date")
            explanation.append("Payment due date extracted.")

        payment_method = _first_match(patterns.PAYMENT_METHOD_PATTERNS, normalized)
        if payment_method:
            payment_method = payment_method.strip().splitlines()[0].strip()
            result.payment_method = ExtractedField(value=payment_method, confidence=0.80, source="regex:payment_method")
            explanation.append("Payment method extracted.")

        base = _to_float(_first_match(patterns.BASE_PATTERNS, normalized))
        if base is not None:
            result.base_amount = ExtractedField(value=base, confidence=0.88, source="regex:base_amount")
            explanation.append("Base amount extracted with invoice totals regex.")


        vat_rate = _to_float(_first_match(patterns.VAT_RATE_PATTERNS, normalized))
        if vat_rate is not None:
            result.vat_rate = ExtractedField(value=vat_rate, confidence=0.90, source="regex:vat_rate")
            explanation.append("VAT rate extracted.")

        tax = _to_float(_first_match(patterns.TAX_PATTERNS, normalized))
        if tax is not None:
            result.tax_amount = ExtractedField(value=tax, confidence=0.88, source="regex:tax_amount")
            explanation.append("Tax amount extracted with invoice totals regex.")

        total = _to_float(_first_match(patterns.TOTAL_PATTERNS, normalized))
        if total is not None:
            result.total_amount = ExtractedField(value=total, confidence=0.92, source="regex:total_liquido")
            result.currency = ExtractedField(value="EUR", confidence=0.80, source="heuristic:spanish_invoice_currency")
            explanation.append("Total amount extracted from TOTAL LIQUIDO.")


        line_items = self._extract_line_items(lines, normalized)
        if line_items:
            result.line_items = ExtractedField(value=line_items, confidence=0.86, source="regex:invoice_lines")
            explanation.append(f"{len(line_items)} invoice line item(s) extracted.")

        result.global_confidence = self._confidence(result)
        if not explanation:
            explanation.append("No invoice fields extracted.")
        return result.model_dump(exclude_none=True), explanation


    def _extract_customer_number(self, lines: list[str], text: str) -> str | None:
        direct = _first_match(patterns.CUSTOMER_NUMBER_PATTERNS, text)
        # Reject dates accidentally captured after a standalone CLIENTE label.
        if direct and len(direct) >= 3:
            return direct
        header = lines[:10]
        for index, line in enumerate(header):
            if line.upper().startswith("FACTURA"):
                for candidate in reversed(header[:index]):
                    if re.fullmatch(r"\d{3,10}", candidate):
                        return candidate
        for candidate in header:
            if re.fullmatch(r"\d{3,10}", candidate):
                return candidate
        return direct

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


    def _extract_line_items(self, lines: list[str], text: str) -> list[dict]:
        """Extract invoice rows without creating synthetic/demo products.

        Supports the Spanish wholesale layout used by SELPROMAR and a common
        Portuguese seafood layout where quantities and prices include explicit
        KG tokens. The catalog service only persists rows returned here.
        """
        items: list[dict] = []
        seen: set[tuple[str, str, float | None]] = set()

        spanish_row = re.compile(
            r"^(?P<reference>\d{4,})\s+(?P<description>.+?)\s+(?P<boxes>\d+(?:[.,]\d+)?)\s+"
            r"(?P<quantity>\d+(?:[.,]\d+)?)\s+(?P<unit_price>\d+(?:[.,]\d+)?)\s+"
            r"(?P<amount>\d+(?:[.,]\d{2}))$"
        )
        portuguese_row = re.compile(
            r"^(?P<reference>\d{4,})\s+(?P<description>.+?)\s+(?P<boxes>\d+)\s+"
            r"(?P<gross_qty>\d+(?:[.,]\d+)?)\s+KG\s+"
            r"(?P<net_qty>\d+(?:[.,]\d+)?)\s+KG\s+"
            r"(?P<gross_price>\d+(?:[.,]\d+)?)\s+KG\s+"
            r"(?P<net_price>\d+(?:[.,]\d+)?)\s+KG\s+"
            r"(?P<discount>\d+(?:[.,]\d+)?)\s+"
            r"(?P<amount>\d{1,3}(?:\.\d{3})*(?:,\d{2})|\d+(?:,\d{2}))\s+\d+(?:[.,]\d+)?$",
            re.IGNORECASE,
        )

        for line in lines:
            match = spanish_row.match(line)
            if match:
                data = match.groupdict()
                row = {
                    "supplier_reference": data["reference"],
                    "description": data["description"].strip(),
                    "package_quantity": _to_float(data["boxes"]),
                    "quantity": _to_float(data["quantity"]),
                    "unit_price": _to_float(data["unit_price"]),
                    "net_amount": _to_float(data["amount"]),
                    "purchase_unit": "kg",
                    "package_unit": "box",
                    "lot_number": self._nearby_value(text, data["reference"], r"Lote\s*:?\s*([A-Z0-9\-]+)"),
                    "expiry_date": self._nearby_value(text, data["reference"], r"(?:Val\.|Cad\.|Caducidad)\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"),
                    "delivery_note_number": self._first_group(text, r"Alb:\s*([A-Z0-9/\-]+)"),
                }
                key = (row["supplier_reference"], row["description"], row["unit_price"])
                if key not in seen:
                    items.append(row)
                    seen.add(key)
                continue

            match = portuguese_row.match(line)
            if match:
                data = match.groupdict()
                # The invoiced amount is gross quantity × discounted PL/UN price.
                row = {
                    "supplier_reference": data["reference"],
                    "description": data["description"].strip(),
                    "package_quantity": _to_float(data["boxes"]),
                    "quantity": _to_float(data["gross_qty"]),
                    "net_quantity": _to_float(data["net_qty"]),
                    "unit_price": _to_float(data["gross_price"]),
                    "net_amount": _to_float(data["amount"]),
                    "discount_percent": _to_float(data["discount"]),
                    "purchase_unit": "kg",
                    "package_unit": "box",
                    "lot_number": self._nearby_value(text, data["reference"], r"Lote\s*:?\s*([A-Z0-9\-]+)"),
                    "expiry_date": self._nearby_value(text, data["reference"], r"Val\.\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"),
                    "delivery_note_number": self._first_group(text, r"Guia:\s*([A-Z0-9 /\-]+)"),
                }
                key = (row["supplier_reference"], row["description"], row["unit_price"])
                if key not in seen:
                    items.append(row)
                    seen.add(key)

        # Portuguese layouts often split description and numeric columns over
        # separate PDF text lines. Join the product header with the following
        # numeric row instead of treating either line as a separate product.
        metrics_re = re.compile(
            r"^(?P<boxes>\d+)\s+(?P<gross_qty>\d+(?:[.,]\d+)?)\s+KG\s+"
            r"(?P<net_qty>\d+(?:[.,]\d+)?)\s+KG\s+"
            r"(?P<gross_price>\d+(?:[.,]\d+)?)\s+KG\s+"
            r"(?P<net_price>\d+(?:[.,]\d+)?)\s+KG\s+"
            r"(?P<discount>\d+(?:[.,]\d+)?)\s+"
            r"(?P<amount>\d{1,3}(?:\.\d{3})*(?:,\d{2})|\d+(?:,\d{2}))\s+\d+(?:[.,]\d+)?$",
            re.IGNORECASE,
        )
        header_re = re.compile(r"^(?P<reference>\d{4,})\s+(?P<description>.+)$")
        for index, line in enumerate(lines):
            header = header_re.match(line)
            if not header:
                continue
            for offset in range(1, 5):
                if index + offset >= len(lines):
                    break
                metrics = metrics_re.match(lines[index + offset])
                if not metrics:
                    continue
                description_parts = [header.group("description").strip()]
                for part in lines[index + 1:index + offset]:
                    if not re.match(r"^(?:Lote|Valor|Desc\.|Flete|Base|Total|Taxa)", part, re.IGNORECASE):
                        description_parts.append(part.strip())
                data = metrics.groupdict()
                reference = header.group("reference")
                row = {
                    "supplier_reference": reference,
                    "description": " ".join(description_parts).strip(),
                    "package_quantity": _to_float(data["boxes"]),
                    "quantity": _to_float(data["gross_qty"]),
                    "net_quantity": _to_float(data["net_qty"]),
                    "unit_price": _to_float(data["gross_price"]),
                    "net_amount": _to_float(data["amount"]),
                    "discount_percent": _to_float(data["discount"]),
                    "purchase_unit": "kg",
                    "package_unit": "box",
                    "lot_number": self._nearby_value(text, reference, r"Lote\s*:?\s*([A-Z0-9\-]+)"),
                    "expiry_date": self._nearby_value(text, reference, r"Val\.\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})"),
                    "delivery_note_number": self._first_group(text, r"Guia:\s*([A-Z0-9 /\-]+)"),
                }
                key = (row["supplier_reference"], row["description"], row["unit_price"])
                if key not in seen:
                    items.append(row)
                    seen.add(key)
                break

        return items

    def _first_group(self, text: str, pattern: str) -> str | None:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _nearby_value(self, text: str, anchor: str, pattern: str) -> str | None:
        position = text.find(anchor)
        fragment = text[position:position + 400] if position >= 0 else text
        return self._first_group(fragment, pattern)

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
