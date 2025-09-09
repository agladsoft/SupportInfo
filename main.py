from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
import logging

from app.services import XMLRiverService, ClickHouseService, DadataService, SystemMonitoringService
from app.models import BalanceResponse, DatabaseInfo, DadataInfo, SystemInfo, AllServicesResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Support Info Balance Server")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

xmlriver_service = XMLRiverService()
clickhouse_service = ClickHouseService()
dadata_service = DadataService()
system_service = SystemMonitoringService()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница с информацией о всех сервисах"""
    xmlriver_info = xmlriver_service.get_balance_info()
    database_info = clickhouse_service.get_database_info()
    dadata_info = dadata_service.get_dadata_info()
    system_info = system_service.get_system_info()
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request, 
            "xmlriver_info": xmlriver_info,
            "database_info": database_info,
            "dadata_info": dadata_info,
            "system_info": system_info,
        }
    )


@app.get("/api/balance", response_model=BalanceResponse)
async def get_balance():
    """API эндпоинт для получения информации о балансе XMLRiver"""
    balance_info = xmlriver_service.get_balance_info()
    return BalanceResponse(**balance_info.model_dump())


@app.get("/api/database", response_model=DatabaseInfo)
async def get_database_status():
    """API эндпоинт для получения статуса базы данных"""
    return clickhouse_service.get_database_info()


@app.get("/api/dadata", response_model=DadataInfo)
async def get_dadata_status():
    """API эндпоинт для получения информации о DaData"""
    return dadata_service.get_dadata_info()


@app.get("/api/system", response_model=SystemInfo)
async def get_system_status():
    """API эндпоинт для получения системной информации"""
    return system_service.get_system_info()




@app.get("/api/all", response_model=AllServicesResponse)
async def get_all_services():
    """API эндпоинт для получения информации обо всех сервисах"""
    xmlriver_info = xmlriver_service.get_balance_info()
    database_info = clickhouse_service.get_database_info()
    dadata_info = dadata_service.get_dadata_info()
    system_info = system_service.get_system_info()
    
    return AllServicesResponse(
        xmlriver=BalanceResponse(**xmlriver_info.model_dump()),
        database=database_info,
        dadata=dadata_info,
        system=system_info,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
