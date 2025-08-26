from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
import logging

from app.services import XMLRiverService
from app.models import BalanceResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Support Info Balance Server")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

xmlriver_service = XMLRiverService()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница с информацией о балансе"""
    balance_info = xmlriver_service.get_balance_info()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "balance_info": balance_info}
    )


@app.get("/api/balance", response_model=BalanceResponse)
async def get_balance():
    """API эндпоинт для получения информации о балансе"""
    balance_info = xmlriver_service.get_balance_info()
    return BalanceResponse(**balance_info.model_dump())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
