from types import SimpleNamespace

from numera.engines.master_data.engine import MasterDataEngine, normalize_party_name


class FakeSupplierRepository:
    def __init__(self):
        self.items = []

    def list(self):
        return self.items

    def create(self, payload):
        supplier = SimpleNamespace(id=f"supplier_{len(self.items) + 1}", **payload.model_dump())
        self.items.append(supplier)
        return supplier


def test_normalize_party_name_ignores_punctuation_accents_and_legal_suffix():
    assert normalize_party_name("Congelados La Red 2000, S.L.") == "CONGELADOS LA RED 2000"
    assert normalize_party_name("CONGELADOS LA RED 2000 SL") == "CONGELADOS LA RED 2000"


def test_resolve_supplier_creates_once_and_reuses_normalized_match():
    repository = FakeSupplierRepository()
    engine = MasterDataEngine(repository)

    created = engine.resolve_supplier("company_1", "Congelados La Red 2000, S.L.")
    resolved = engine.resolve_supplier("company_1", "CONGELADOS LA RED 2000 SL")

    assert created.id == resolved.id
    assert created.default_account == "400000"
    assert len(repository.items) == 1


def test_resolve_supplier_is_isolated_by_company():
    repository = FakeSupplierRepository()
    engine = MasterDataEngine(repository)

    first = engine.resolve_supplier("company_1", "Proveedor Demo SL")
    second = engine.resolve_supplier("company_2", "Proveedor Demo S.L.")

    assert first.id != second.id
    assert len(repository.items) == 2


def test_resolve_supplier_returns_none_for_empty_name():
    repository = FakeSupplierRepository()
    engine = MasterDataEngine(repository)

    assert engine.resolve_supplier("company_1", None) is None
    assert engine.resolve_supplier("company_1", "   ") is None
    assert repository.items == []
