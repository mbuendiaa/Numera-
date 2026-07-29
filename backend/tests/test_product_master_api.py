from fastapi.testclient import TestClient
from sqlalchemy import delete

from numera.infrastructure.database.session import SessionLocal, create_database
from numera.infrastructure.persistence.models import (
    AuthTokenORM,
    CompanyMembershipORM,
    ProductORM,
    ProductPriceHistoryORM,
    SupplierORM,
    SupplierProductORM,
    UserORM,
)
from numera.main import app

client = TestClient(app)


def setup_function():
    create_database()
    with SessionLocal() as db:
        db.execute(delete(ProductPriceHistoryORM))
        db.execute(delete(SupplierProductORM))
        db.execute(delete(ProductORM))
        db.execute(delete(SupplierORM))
        db.execute(delete(AuthTokenORM))
        db.execute(delete(CompanyMembershipORM))
        db.execute(delete(UserORM))
        db.commit()


def onboarding(email="products@numera.test"):
    assert client.post("/auth/register", json={
        "email": email, "password": "StrongPass123!", "name": "Product Owner"
    }).status_code == 201
    tokens = client.post("/auth/login", json={
        "email": email, "password": "StrongPass123!"
    }).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    company = client.post("/companies/", headers=headers, json={
        "name": "Congelados CientoCinco", "country": "ES", "currency": "EUR"
    }).json()
    return headers, company["id"]


def create_supplier(company_id: str, name: str, tax_id: str):
    response = client.post("/suppliers/", json={
        "company_id": company_id,
        "name": name,
        "tax_id": tax_id,
        "country": "ES",
        "default_account": "400000",
    })
    assert response.status_code == 201
    return response.json()


def test_product_supplier_catalog_price_history_and_comparison():
    headers, company_id = onboarding()
    supplier_one = create_supplier(company_id, "CONGELADOS LA RED 2000, S.L.", "B41993478")
    supplier_two = create_supplier(company_id, "OTRO PROVEEDOR DE PESCADO, S.L.", "B00000001")

    product = client.post("/products/", headers=headers, json={
        "name": "Boquerón eviscerado y harinado 8x5",
        "category": "Pescado congelado",
        "base_unit": "kg",
        "default_vat_rate": "10.00",
        "internal_sku": "BOQ-EH-8X5",
    })
    assert product.status_code == 201
    product_id = product.json()["id"]

    red_link = client.post(f"/products/suppliers/{supplier_one['id']}", headers=headers, json={
        "product_id": product_id,
        "supplier_reference": "700453",
        "supplier_description": "X BOQUERON EVISC. Y HARINADO 8X5",
        "purchase_unit": "kg",
        "package_unit": "box",
        "currency": "EUR",
        "default_vat_rate": "10.00",
    })
    assert red_link.status_code == 201

    other_link = client.post(f"/products/suppliers/{supplier_two['id']}", headers=headers, json={
        "product_id": product_id,
        "supplier_reference": "BQ-0085",
        "supplier_description": "BOQUERON HARINADO FORMATO 8X5",
        "purchase_unit": "kg",
        "currency": "EUR",
        "default_vat_rate": "10.00",
    })
    assert other_link.status_code == 201

    observed = client.post(
        f"/products/supplier-products/{red_link.json()['id']}/prices",
        headers=headers,
        json={
            "unit_price": "6.450000",
            "observed_at": "2026-04-21",
            "quantity": "48.0000",
            "package_quantity": "12",
            "net_amount": "309.60",
            "vat_rate": "10.00",
            "currency": "EUR",
            "invoice_number": "V1/2604047",
            "lot_number": "150126BO",
            "delivery_note_number": "A1/437142",
        },
    )
    assert observed.status_code == 201
    assert observed.json()["supplier_reference"] == "700453"

    cheaper = client.post(
        f"/products/supplier-products/{other_link.json()['id']}/prices",
        headers=headers,
        json={"unit_price": "6.20", "observed_at": "2026-04-22", "currency": "EUR"},
    )
    assert cheaper.status_code == 201

    catalog = client.get(
        f"/products/suppliers/{supplier_one['id']}/catalog", headers=headers
    )
    assert catalog.status_code == 200
    assert catalog.json()[0]["supplier_reference"] == "700453"
    assert catalog.json()[0]["latest_price"] == "6.450000"

    history = client.get(f"/products/{product_id}/price-history", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) == 2
    assert {row["supplier_name"] for row in history.json()} == {
        "CONGELADOS LA RED 2000, S.L.", "OTRO PROVEEDOR DE PESCADO, S.L."
    }

    offers = client.get(f"/products/{product_id}/supplier-offers", headers=headers)
    assert offers.status_code == 200
    assert [offer["supplier_name"] for offer in offers.json()] == [
        "OTRO PROVEEDOR DE PESCADO, S.L.", "CONGELADOS LA RED 2000, S.L."
    ]


def test_product_data_is_scoped_to_active_company():
    first_headers, _ = onboarding("first@numera.test")
    product = client.post("/products/", headers=first_headers, json={
        "name": "Producto privado", "base_unit": "unit"
    })
    assert product.status_code == 201

    second_headers, _ = onboarding("second@numera.test")
    hidden = client.get(f"/products/{product.json()['id']}", headers=second_headers)
    assert hidden.status_code == 404


def test_product_routes_are_exposed_in_openapi():
    paths = client.get("/openapi.json").json()["paths"]
    expected = {
        "/products/",
        "/products/{product_id}",
        "/products/{product_id}/supplier-offers",
        "/products/{product_id}/price-history",
        "/products/suppliers/{supplier_id}",
        "/products/suppliers/{supplier_id}/catalog",
        "/products/supplier-products/{supplier_product_id}",
        "/products/supplier-products/{supplier_product_id}/prices",
    }
    assert expected <= set(paths)
