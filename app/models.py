from pydantic import BaseModel
from enum import Enum


class BalanceStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class BalanceInfo(BaseModel):
    balance: str
    cost_per_request: str
    rows_available: str
    status: BalanceStatus
    error: str | None = None


class BalanceResponse(BaseModel):
    balance: str
    cost_per_request: str
    rows_available: str
    status: BalanceStatus
    error: str | None = None