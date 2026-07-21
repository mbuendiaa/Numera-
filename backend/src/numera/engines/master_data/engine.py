import re
import unicodedata

from numera.domain.schemas import SupplierCreate
from numera.infrastructure.repositories import SupplierRepository


LEGAL_SUFFIXES = {
    "SL",
    "S L",
    "SA",
    "S A",
    "SLU",
    "S L U",
    "SOCIEDAD LIMITADA",
    "SOCIEDAD ANONIMA",
}


def normalize_party_name(value: str) -> str:
    """Return a stable comparison key for supplier/customer names."""
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.upper().replace("&", " Y ")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    tokens = [token for token in text.split() if token]

    while tokens:
        suffix_removed = False
        for suffix in sorted(LEGAL_SUFFIXES, key=len, reverse=True):
            suffix_tokens = suffix.split()
            if tokens[-len(suffix_tokens) :] == suffix_tokens:
                tokens = tokens[: -len(suffix_tokens)]
                suffix_removed = True
                break
        if not suffix_removed:
            break

    return " ".join(tokens)


class MasterDataEngine:
    """Resolve business parties before transactional engines use them."""

    def __init__(self, suppliers: SupplierRepository):
        self.suppliers = suppliers

    def resolve_supplier(self, company_id: str, name: str | None):
        if not name or not name.strip():
            return None

        normalized_name = normalize_party_name(name)
        if not normalized_name:
            return None

        supplier = self.suppliers.find_by_normalized_name(company_id, normalized_name)
        if supplier is not None:
            return supplier

        return self.suppliers.create(
            SupplierCreate(
                company_id=company_id,
                name=name.strip(),
                country="ES",
                default_account="400000",
            )
        )
