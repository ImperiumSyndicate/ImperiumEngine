import json
from datetime import datetime, timedelta
from enum import Enum
import traceback
from typing import List, Dict
from dataclasses import dataclass, asdict

from .infra import HttpHelper
from .log import error_log

from typing import Union

@dataclass
class createTimeLineUseCaseObject:
    period_init: str
    period_end: str
    period_frequency: str
    strategy: Union[any, None]

    # calculate after
    time_line_period: Union[any, None]
    time_line_order_days: Union[any, None]
    time_line_number_orders: Union[int, None]
    k_lines_order_days: Union[any, None]
    k_lines: Union[any, None]

@dataclass
class createTimeLineUseCaseResponse:
    data: createTimeLineUseCaseObject
    success: bool

class Frequency(Enum):
    ONE_DAY = "1d"
    FIFTEEN_DAYS = "15d"
    TWENTY_DAYS = "20d"

    @staticmethod
    def from_str(freq: str) -> int:
        """Converte string da frequência para número de dias."""
        mapping = {
            "1d": 1,
            "15d": 15,
            "20d": 20
        }
        if freq not in mapping:
            raise ValueError(f"Frequência inválida: {freq}. Use 1d, 15d ou 20d.")
        return mapping[freq]


class BacktestTimeLine:
    """Class create time-line
        period_init: str-> date init period
        period_end: str-> date end period
        period_frequency: str-> frequency period
        strategy: str-> strategy to apply in the period
        currency_code: str-> Name of currency code to  use in request_k_lines
    """

    def __init__(self, period_init:str,
                       period_end:str,
                       period_frequency:str,
                       strategy_code: any,
                    #    TODO: inserir nome da moeda BTC padrao usada pelo gustavo
                       currency_code: str="BTC") -> None:
        self._strategy:any = strategy_code
        self._period_frequency: str = period_frequency
        self._period_end: str = period_end
        self._period_init: str = period_init
        self._currency_code: str = currency_code

        self._time_line_period: any = None
        self._time_line_order_days: any = None
        self._time_line_number_orders: int = None
        # filter with frequency
        self._k_lines: any = None
        self._k_lines_order_days: any = None


    def execute(self, url_k_lines: str, headers: dict) -> None:
        """Get period with init and end,
           use frequency to create 'actions' in period

        Args:
            url_k_lines (str): url to request and get k_lines
            headers (dict): possible headers in request

        Returns:
            dict: {"data": response, "success": True, "message":"OK"}
        """
        try:
            calculate_time_line = self._create_time_line()
            if (calculate_time_line["success"] == False):
                raise Exception("Problem to create Time Line")

            request_api_signals = self._requestKLines(url_k_lines=url_k_lines, headers=headers)
            if (request_api_signals["success"] == False):
                raise Exception("Problem in API Signals")

            filter_only_order_date = self._findOnlyDateInOrder()
            if (filter_only_order_date["success"] == False):
                raise Exception("Problem in filter orders")


            response = self.toJson()


        # TODO: implementar a resposta dos k-lines de cada dia estipulado
            return {"data": response, "success": True, "message":"OK"}

        except Exception as e:
            error_log(message_err=f"{e}",
                      traceback=f"{traceback.format_exc()}")
            return {"data": None, "success": False, "message": f"{e}"}

    def toJson(self)-> createTimeLineUseCaseResponse:
        """return a json"""


        response = createTimeLineUseCaseResponse(
                    data=createTimeLineUseCaseObject(
                        period_init=self._period_init,
                        period_end=self._period_end,
                        period_frequency=self._period_frequency,
                        strategy=self._strategy,
                        time_line_period=self._time_line_period,
                        time_line_number_orders=self._time_line_number_orders,
                        time_line_order_days=self._time_line_order_days,
                        k_lines=self._k_lines,
                        k_lines_order_days=self._k_lines_order_days
                    ),
                    success=True
                    )
        return asdict(response)


    def _create_time_line(self) -> List[Dict[str, str]]:
        """Divide um período em intervalos baseados na frequência especificada.

            A função recebe uma data inicial, uma data final e uma frequência (`1d`, `15d` ou `20d`).
            Ela divide o período em intervalos de acordo com a frequência e retorna um dicionário contendo:
            - A lista de períodos (`init_day`, `end_day`).
            - A lista de datas (`order_days`), onde a primeira é `init_period` e as demais são `end_day` dos períodos.
            - O número total de períodos gerados (`number_orders`).

            Args:
                init_period (str): Data inicial no formato "YYYY-MM-DD".
                end_period (str): Data final no formato "YYYY-MM-DD".
                frequency (str): Frequência da divisão, podendo ser "1d", "15d" ou "20d".

            Returns:
                Dict[str, Any]: Um dicionário contendo:
                    - "period" (List[Dict[str, str]]): Lista de períodos gerados, cada um com "init_day" e "end_day".
                    - "order_days" (List[str]): Lista de datas ordenadas, onde o primeiro é `init_period` e os demais são `end_day`.
                    - "number_orders" (int): Contagem total de períodos gerados.

            Raises:
                ValueError: Se a frequência for inválida ou se as datas não estiverem no formato correto.
            Example:
                _create_time_line("2024-01-01", "2024-01-31", "15d")
            """
        try:
            start_date = datetime.strptime(self._period_init, "%Y-%m-%d")
            end_date = datetime.strptime(self._period_end, "%Y-%m-%d")

            days_interval = Frequency.from_str(self._period_frequency)

            periods = []
            # order_days = [self._period_init]  # A primeira data sempre será init_period
            order_days = []  # A primeira data sempre será init_period
            current_start = start_date

            while current_start <= end_date:
                current_end = min(current_start + timedelta(days=days_interval - 1), end_date)

                periods.append({
                    "init_day": current_start.strftime("%Y-%m-%d"),
                    "end_day": current_end.strftime("%Y-%m-%d")
                })

                order_days.append(current_end.strftime("%Y-%m-%d"))
                current_start = current_end + timedelta(days=1)

            self._time_line_period: any = periods
            self._time_line_order_days: any = order_days
            self._time_line_number_orders: int = len(periods)

            response = {
                "period": periods,
                "order_days": order_days,
                "number_orders": len(periods)
            }

            return {"data": response, "success": True, "message":"OK"}

        except Exception as e:
            error_log(message_err=f"{e}",
                      traceback=f"{traceback.format_exc()}")
            return {"data": None, "success": False, "message": f"{e}"}

    def _requestKLines(self, url_k_lines: str,headers: dict = {}):
        """request to api Signals to get K-LINES

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        try:
            if (self._time_line_order_days == None):
                raise Exception("Don't have order day")
            # TODO: é aqui que vc insere o payload esperado pela API SCHEMA - ver payload e ajustar
            # httpHelper = HttpHelper()
            # body = {
            #     "start_time" : self._period_init,
            #     "end_time"  : self._period_end,
            #     "currency_code": self._currency_code
            # }
            # request = httpHelper.post(url=url_k_lines,headers=headers,body=body)
            # if (request["success"] == False):
            #     raise Exception("Problem in API Signals")
            # TODO: MOCK apagar depois que integrar
            request = {
                "data": [
                      {
                      "date": "2024-02-01",
                      "min_low": 100,
                      "max_high": 150,
                      "total_volume": 200001,
                      "candle_count": 10,
                      "avg_close": 1899.30
                      },
                      {
                      "date": "2024-02-02",
                      "min_low": 100,
                      "max_high": 150,
                      "total_volume": 200001,
                      "candle_count": 10,
                      "avg_close": 1899.30
                      },
                      {
                      "date": "2024-02-03",
                      "min_low": 100,
                      "max_high": 150,
                      "total_volume": 200001,
                      "candle_count": 10,
                      "avg_close": 1899.30
                      },
                      {
                      "date": "2024-02-04",
                      "min_low": 100,
                      "max_high": 166,
                      "total_volume": 200001,
                      "candle_count": 10,
                      "avg_close": 1899.30
                      },
                ]
            }
            self._k_lines = request["data"]
            return {"data": request["data"], "success": True, "message":"OK"}

        except Exception as e:
            error_log(message_err=f"{e}",
                      traceback=f"{traceback.format_exc()}")
            return {"data": None, "success": False, "message": f"{e}"}

    def _findOnlyDateInOrder(self):
        try:
            if (self._time_line_order_days == None):
                raise Exception("Don't have order day")

            self._k_lines_order_days = [item for item in self._k_lines if item["date"] in self._time_line_order_days]

            return {"data": self._k_lines_order_days, "success": True, "message":"OK"}

        except Exception as e:
            error_log(message_err=f"{e}",
                      traceback=f"{traceback.format_exc()}")
            return {"data": None, "success": False, "message": f"{e}"}
