
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.portfolio import router as portfolio_router
from routes.instruments import router as instruments_router

app = FastAPI(title="Investment Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio_router, prefix="/portfolio")
app.include_router(instruments_router, prefix="/instruments")
