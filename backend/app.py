
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.positions import router as portfolio_router
from routes.instruments import router as instruments_router
from routes.trades import router as trades_router
from routes.transactions import router as transactions_router
from routes.accounts import router as accounts_router
from routes.prices import router as prices_router

app = FastAPI(title="Investment Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio_router, prefix="/portfolio")
app.include_router(instruments_router, prefix="/instruments")
app.include_router(prices_router, prefix="/prices", tags=["Prices"])
app.include_router(trades_router, prefix="/trades", tags=["Trades"])
app.include_router(transactions_router, prefix="/transactions", tags=["Transactions"])
app.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])
