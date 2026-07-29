from pathlib import Path

from numera.engines.document.extractor import InvoiceExtractor


def test_extracts_realistic_wholesale_invoice_fields():
    text = Path("uploads/company_baedae9f7050/CONGELADOS CIENTOCINCO_V1 _2604047.pdf")
    # Test the parser with the text layout commonly returned by pypdf.
    sample = """CONGELADOS LA RED 2000,SL
FACTURA: V1/2604047
CLIENTE 1856
FECHA 21/04/2026
DNI/CIF B41993478
REFERENCIA DESCRIPCION CAJAS KG / UNID. PRECIO IMPORTE
700453 X BOQUERON ESVISC. Y HARINADO 8X5 12 48,000 6,450 309,60
N/Ref R871 Lote 150126BO
TOTAL BRUTO 309,60
Total Impuestos 30,96
TOTAL LIQUIDO 340,56
FORMA DE PAGO PAGARE
BASES IVA % IVA CUOTA IVA 309,60 10,00 30,96
21/05/2026 340,56
Alb:A1/437142 de21/04/2026
"""
    fields, _ = InvoiceExtractor().extract(sample)
    assert fields["invoice_number"]["value"] == "V1/2604047"
    assert fields["customer_number"]["value"] == "1856"
    assert fields["vat_rate"]["value"] == 10.0
    assert fields["line_items"]["value"][0]["supplier_reference"] == "700453"
    assert fields["line_items"]["value"][0]["unit_price"] == 6.45
