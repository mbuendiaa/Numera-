from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from numera.api.routes import (
    accounting,
    accounts,
    auth,
    cognitive,
    companies,
    documents,
    events,
    health,
    invoices,
    intelligence,
    journal,
    purchases,
    products,
    suppliers,
    tax,
    tenancy,
)
from numera.infrastructure.database.session import create_database

app = FastAPI(title="Numera Core Platform", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000","http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    create_database()


app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(auth.users_router, prefix="/users", tags=["Users"])
app.include_router(tenancy.router, prefix="/companies", tags=["Companies & Access"])
app.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
app.include_router(products.router, prefix="/products", tags=["Products & Supplier Catalog"])
app.include_router(accounts.router, prefix="/accounts", tags=["Chart of Accounts"])
app.include_router(accounting.router, prefix="/accounting", tags=["Accounting Engine"])
app.include_router(intelligence.router, prefix="/intelligence", tags=["Accounting Intelligence"])
app.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
app.include_router(cognitive.router, prefix="/cognitive", tags=["Cognitive System"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(journal.router, prefix="/journal", tags=["Journal"])
app.include_router(events.router, prefix="/events", tags=["Business Events"])

app.include_router(purchases.router, prefix="/purchases", tags=["Purchases"])
app.include_router(tax.router, prefix="/tax", tags=["Tax & VAT"])
