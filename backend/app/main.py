from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import transactions

app = FastAPI(title="Smart Financial Coach API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(transactions.router, prefix="/api")
