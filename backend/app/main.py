from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import transactions

app = FastAPI(title="Financial Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Backend is running!"}
