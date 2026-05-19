from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
import os, uuid, asyncpg

app = FastAPI(title="ShopKube Catalog API")
Instrumentator().instrument(app).expose(app)

class Product(BaseModel):
    name: str
    price: float
    category: str
    stock: int

@app.on_event("startup")
async def startup():
    app.state.db = await asyncpg.connect(os.getenv("DATABASE_URL"))
    await app.state.db.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price FLOAT NOT NULL,
            category TEXT NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()

@app.get("/health")
async def health():
    return {"status": "ok", "version": os.getenv("APP_VERSION", "v1")}

@app.get("/products")
async def list_products():
    rows = await app.state.db.fetch("SELECT * FROM products")
    return [dict(r) for r in rows]

@app.post("/products", status_code=201)
async def create_product(p: Product):
    pid = str(uuid.uuid4())
    await app.state.db.execute(
        "INSERT INTO products VALUES($1,$2,$3,$4,$5)",
        pid, p.name, p.price, p.category, p.stock
    )
    return {"id": pid, **p.model_dump()}

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    row = await app.state.db.fetchrow(
        "SELECT * FROM products WHERE id=$1", product_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    result = await app.state.db.execute(
        "DELETE FROM products WHERE id=$1", product_id
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Product not found")
    return {"deleted": product_id}
# ShopKube v1.0
