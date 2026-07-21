from fastapi import FastAPI

from numera.api.routes import accounts, cognitive, companies, documents, events, health, invoices, journal, suppliers
from numera.infrastructure.database.session import create_database

app = FastAPI(title="Numera Core Platform", version="1.0.0")


@app.on_event("startup")
def startup():
    create_database()


app.include_router(health.router, tags=["Health"])
app.include_router(companies.router, prefix="/companies", tags=["Companies"])
app.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
app.include_router(accounts.router, prefix="/accounts", tags=["Chart of Accounts"])
app.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
app.include_router(cognitive.router, prefix="/cognitive", tags=["Cognitive System"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(journal.router, prefix="/journal", tags=["Journal"])
app.include_router(events.router, prefix="/events", tags=["Business Events"])
