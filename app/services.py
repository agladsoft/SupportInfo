import requests
import math
import logging
import os
from .models import BalanceInfo, BalanceStatus
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class XMLRiverService:
    def __init__(self):
        self.user = os.getenv("USER_XML_RIVER", "")
        self.key = os.getenv("KEY_XML_RIVER", "")
        self.base_url = "https://xmlriver.com/api"
        self.timeout = 120
    
    def get_balance_info(self) -> BalanceInfo:
        """Получить информацию о балансе с xmlriver API"""
        try:
            balance_response = self._get_balance()
            cost_response = self._get_cost()
            
            balance = float(balance_response)
            cost_per_1000 = float(cost_response)
            count_ability_handle_rows = math.floor(balance / (cost_per_1000 / 1000))
            cost_per_request_kopecks = round(cost_per_1000 / 10)
            
            return BalanceInfo(
                balance=f"{balance:.2f}",
                cost_per_request=f"{cost_per_request_kopecks}",
                rows_available=f"{count_ability_handle_rows}",
                status=BalanceStatus.SUCCESS
            )
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к API: {e}")
            return BalanceInfo(
                balance="Ошибка",
                cost_per_request="Ошибка",
                rows_available="Ошибка",
                status=BalanceStatus.ERROR,
                error="Не удалось получить ответ от API"
            )
        except ValueError as e:
            logger.error(f"Ошибка при обработке данных API: {e}")
            return BalanceInfo(
                balance="Ошибка",
                cost_per_request="Ошибка",
                rows_available="Ошибка",
                status=BalanceStatus.ERROR,
                error="Неверный формат данных от API"
            )
    
    def _get_balance(self) -> str:
        """Получить баланс с API"""
        response = requests.get(
            f"{self.base_url}/get_balance/yandex/",
            params={"user": self.user, "key": self.key},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.text
    
    def _get_cost(self) -> str:
        """Получить стоимость с API"""
        response = requests.get(
            f"{self.base_url}/get_cost/yandex/",
            params={"user": self.user, "key": self.key},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.text