import requests
import math
import logging
import os
import time
from datetime import datetime
from .models import BalanceInfo, ServiceStatus, DatabaseInfo, DadataInfo, DadataAccountInfo
from dotenv import load_dotenv
from dadata.sync import DadataClient
import clickhouse_connect

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
                status=ServiceStatus.SUCCESS
            )
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к API: {e}")
            return BalanceInfo(
                balance="Ошибка",
                cost_per_request="Ошибка",
                rows_available="Ошибка",
                status=ServiceStatus.ERROR,
                error="Не удалось получить ответ от API"
            )
        except ValueError as e:
            logger.error(f"Ошибка при обработке данных API: {e}")
            return BalanceInfo(
                balance="Ошибка",
                cost_per_request="Ошибка",
                rows_available="Ошибка",
                status=ServiceStatus.ERROR,
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


class ClickHouseService:
    def __init__(self):
        self.host = os.getenv("CLICKHOUSE_HOST", "localhost")
        self.port = os.getenv("CLICKHOUSE_PORT", "8123")
        self.database = os.getenv("CLICKHOUSE_DATABASE", "default")
        self.username = os.getenv("CLICKHOUSE_USERNAME", "default")
        self.password = os.getenv("CLICKHOUSE_PASSWORD", "")
        self.timeout = 30
    
    def get_database_info(self) -> DatabaseInfo:
        """Получить информацию о подключении к ClickHouse и количестве уникальных компаний"""
        try:
            # Проверка базового подключения
            start_time = time.time()
            response = requests.get(
                f"http://{self.host}:{self.port}",
                timeout=self.timeout
            )
            response_time = round((time.time() - start_time) * 1000, 2)
            response.raise_for_status()
            
            if "Ok" not in response.text:
                return DatabaseInfo(
                    connection_status="Подключение к базе отсутствует",
                    status=ServiceStatus.ERROR,
                    error="Неожиданный ответ от сервера"
                )
            
            # Получение количества уникальных компаний
            unique_companies_count = self._get_unique_companies_count()
            
            return DatabaseInfo(
                connection_status="Подключение к базе стабильно",
                response_time=f"{response_time}ms",
                unique_companies_count=unique_companies_count,
                status=ServiceStatus.SUCCESS
            )
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при подключении к ClickHouse: {e}")
            return DatabaseInfo(
                connection_status="Подключение к базе отсутствует",
                status=ServiceStatus.ERROR,
                error="Не удалось получить ответ от сервера"
            )
        except Exception as e:
            logger.error(f"Общая ошибка ClickHouse сервиса: {e}")
            return DatabaseInfo(
                connection_status="Ошибка при получении данных",
                status=ServiceStatus.ERROR,
                error=str(e)
            )
    
    def _get_unique_companies_count(self) -> int:
        """Получить количество уникальных компаний из ClickHouse"""
        try:
            client = clickhouse_connect.get_client(
                host=self.host,
                port=int(self.port) if self.port != "8123" else 8123,
                database=self.database,
                username=self.username,
                password=self.password
            )
            
            query = """
            SELECT COUNT(company_name) 
            FROM (
                SELECT company_name_unified, company_inn, company_name, 
                       COUNT(DISTINCT company_inn) OVER (PARTITION BY company_name_unified) AS inn_count 
                FROM reference_inn 
                WHERE is_fts_found = FALSE
            ) 
            WHERE inn_count > 1 
            AND company_inn IS NOT NULL 
            AND company_name_unified IS NOT NULL
            """
            
            result = client.query(query)
            if result.result_rows and len(result.result_rows) > 0:
                return int(result.result_rows[0][0])
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к ClickHouse: {e}")
            return None


class DadataService:
    def __init__(self):
        self.accounts = [
            {
                "token": os.getenv("DADATA_TOKEN_1", ""),
                "secret": os.getenv("DADATA_SECRET_1", ""),
                "name": "ACCOUNT_1"
            },
            {
                "token": os.getenv("DADATA_TOKEN_2", ""),
                "secret": os.getenv("DADATA_SECRET_2", ""),
                "name": "ACCOUNT_2"
            }
        ]
    
    def get_dadata_info(self) -> DadataInfo:
        """Получить информацию об остатках запросов DaData"""
        try:
            accounts_info = []
            
            for account in self.accounts:
                if not account["token"] or not account["secret"]:
                    continue
                    
                try:
                    dadata_client = DadataClient(
                        token=account["token"], 
                        secret=account["secret"]
                    )
                    stats = dadata_client.get_daily_stats(datetime.now().date())
                    
                    accounts_info.append(DadataAccountInfo(
                        account_name=account["name"],
                        date=stats["date"],
                        remaining_requests=stats["remaining"]["suggestions"]
                    ))
                except Exception as e:
                    logger.error(f"Ошибка при получении статистики {account['name']}: {e}")
                    accounts_info.append(DadataAccountInfo(
                        account_name=account["name"],
                        date=str(datetime.now().date()),
                        remaining_requests=0
                    ))
            
            return DadataInfo(
                accounts=accounts_info,
                status=ServiceStatus.SUCCESS
            )
        except Exception as e:
            logger.error(f"Ошибка при получении информации DaData: {e}")
            return DadataInfo(
                accounts=[],
                status=ServiceStatus.ERROR,
                error="Не удалось получить статистику DaData"
            )


