"""
Mock CRM API Server para testes
Execute com: uvicorn sample_api:app --port 8001
Atualizado: 2025-11-20
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import uuid

app = FastAPI(title="Mock CRM API", version="1.0.0")

# Dados em memória (simulação)
customers_db = {}
deals_db = {}


class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None


class CustomerResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    status: str = "active"


class DealCreate(BaseModel):
    title: str
    value: float
    customer_id: str
    stage: str = "qualification"
    probability: int = 10
    expected_close_date: Optional[str] = None


class DealResponse(BaseModel):
    id: str
    title: str
    value: float
    customer_id: str
    stage: str
    probability: int
    expected_close_date: Optional[str] = None


@app.get("/")
def root():
    """Health check."""
    return {"status": "ok", "message": "Mock CRM API is running"}


@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str):
    """Busca cliente por ID."""
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customers_db[customer_id]


@app.get("/customers")
def search_customers(
    query: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    limit: int = Query(10)
):
    """Busca clientes por filtros."""
    results = list(customers_db.values())
    
    if query:
        results = [
            c for c in results 
            if query.lower() in c["name"].lower() or 
               (c["company"] and query.lower() in c["company"].lower())
        ]
    
    if email:
        results = [c for c in results if c["email"] == email]
    
    return {"customers": results[:limit]}


@app.post("/customers", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate):
    """Cria novo cliente."""
    customer_id = str(uuid.uuid4())
    customer_data = {
        "id": customer_id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "company": customer.company,
        "status": "active"
    }
    customers_db[customer_id] = customer_data
    return customer_data


@app.get("/deals")
def get_deals(
    customer_id: Optional[str] = Query(None),
    stage: Optional[str] = Query(None)
):
    """Lista negociações."""
    results = list(deals_db.values())
    
    if customer_id:
        results = [d for d in results if d["customer_id"] == customer_id]
    
    if stage:
        results = [d for d in results if d["stage"] == stage]
    
    return {"deals": results}


@app.post("/deals", response_model=DealResponse)
def create_deal(deal: DealCreate):
    """Cria nova negociação."""
    # Verificar se cliente existe
    if deal.customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    deal_id = str(uuid.uuid4())
    deal_data = {
        "id": deal_id,
        "title": deal.title,
        "value": deal.value,
        "customer_id": deal.customer_id,
        "stage": deal.stage,
        "probability": deal.probability,
        "expected_close_date": deal.expected_close_date
    }
    deals_db[deal_id] = deal_data
    return deal_data


# Seed com dados de exemplo
@app.on_event("startup")
def seed_database():
    """Popula banco com dados de exemplo."""
    # Clientes
    customer1_id = str(uuid.uuid4())
    customers_db[customer1_id] = {
        "id": customer1_id,
        "name": "João Silva",
        "email": "joao@exemplo.com",
        "phone": "+5511999999999",
        "company": "Empresa XYZ",
        "status": "active"
    }
    
    customer2_id = str(uuid.uuid4())
    customers_db[customer2_id] = {
        "id": customer2_id,
        "name": "Maria Santos",
        "email": "maria@exemplo.com",
        "phone": "+5511888888888",
        "company": "Tech Corp",
        "status": "active"
    }
    
    # Deals
    deal1_id = str(uuid.uuid4())
    deals_db[deal1_id] = {
        "id": deal1_id,
        "title": "CRM Enterprise - Empresa XYZ",
        "value": 9960.0,  # R$ 199 x 50 users/month
        "customer_id": customer1_id,
        "stage": "negotiation",
        "probability": 70,
        "expected_close_date": "2025-12-15"
    }
    
    deal2_id = str(uuid.uuid4())
    deals_db[deal2_id] = {
        "id": deal2_id,
        "title": "AI Assistant - Tech Corp",
        "value": 499.0,
        "customer_id": customer2_id,
        "stage": "qualification",
        "probability": 30,
        "expected_close_date": None
    }
    
    print(f"✅ Database seeded with {len(customers_db)} customers and {len(deals_db)} deals")


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Mock CRM API on http://localhost:8001")
    print("📚 Docs available at http://localhost:8001/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)
