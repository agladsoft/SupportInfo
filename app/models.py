from pydantic import BaseModel
from enum import Enum
from typing import List, Dict


class ServiceStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class BalanceInfo(BaseModel):
    balance: str
    cost_per_request: str
    rows_available: str
    status: ServiceStatus
    error: str | None = None


class BalanceResponse(BaseModel):
    balance: str
    cost_per_request: str
    rows_available: str
    status: ServiceStatus
    error: str | None = None


class DatabaseInfo(BaseModel):
    connection_status: str
    response_time: str | None = None
    unique_companies_count: int | None = None
    status: ServiceStatus
    error: str | None = None


class DadataAccountInfo(BaseModel):
    account_name: str
    date: str
    remaining_requests: int


class DadataInfo(BaseModel):
    accounts: List[DadataAccountInfo]
    status: ServiceStatus
    error: str | None = None


class AllServicesResponse(BaseModel):
    xmlriver: BalanceResponse
    database: DatabaseInfo
    dadata: DadataInfo