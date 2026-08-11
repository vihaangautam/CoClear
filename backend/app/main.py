from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import properties, tenancies, condition_reports, payments, dashboard, uploads, tickets, tenant_portal, auth

app = FastAPI(
    title="PGPal API",
    description="Deposit dispute prevention infrastructure for PG operators",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(properties.router, prefix="/api/v1", tags=["Properties"])
app.include_router(tenancies.router, prefix="/api/v1", tags=["Tenancies"])
app.include_router(condition_reports.router, prefix="/api/v1", tags=["Condition Reports"])
app.include_router(payments.router, prefix="/api/v1", tags=["Payments"])
app.include_router(uploads.router, prefix="/api/v1", tags=["Uploads"])
app.include_router(tickets.router, prefix="/api/v1", tags=["Tickets"])
app.include_router(tenant_portal.router, prefix="/api/v1", tags=["Tenant Portal"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "pgpal-api"}
