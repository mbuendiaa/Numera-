from numera.engines.document.extractor import InvoiceExtractor


def test_invoice_number_prefers_invoice_over_delivery_note():
    text = """
CONGELADOS LA RED 2000,SL
CONGELADOS CIENTOCINCO S.L.2604047/V1
1856
FACTURA:
CLIENTE
21/04/2026
Alb:A1/437142 de21/04/2026 Ref.:
TOTAL LIQUIDO 340,56
"""
    fields, _ = InvoiceExtractor().extract(text)
    assert fields["invoice_number"]["value"] == "V1/2604047"
