import json
from datetime import datetime, timedelta
from enum import Enum
import traceback
from typing import List, Dict
from dataclasses import dataclass, asdict
import pandas as pd
from .UseCaseBacktestTimeLine import BacktestTimeLine
from .infra import HttpHelper
from .log import error_log
import vectorbt as vbt

import numpy as np

from typing import Union



@dataclass
class OrdersDay:
    order_date: str
    k_line: Union[any, None]
    # calculate after
    index: Union[any, None]
    action: str

@dataclass
class createBacktestObjectCaseObject:
    period_init: str
    period_end: str
    period_frequency: str
    strategy: Union[any, None]
    time_line_order_days: List[OrdersDay]

    # calculate after
    signals_index: Union[any, None]
    backtest_profit: float
    backtest_stats: Union[any, None]
    backtest_total_return: Union[any, None]
    backtest_orders_records: Union[any, None]

@dataclass
class backtestProfitUseCaseResponse:
    data: createBacktestObjectCaseObject
    success: bool


class BacktestProfit(BacktestTimeLine):
    """Class BacktestProfit
        BacktestTimeLine-> receive backtestTimeLine
    """

    def __init__(self, backtestTimeLine: BacktestTimeLine,url_k_lines:str, headers: dict ) -> None:
        super().__init__(
            period_init=backtestTimeLine._period_init,
            period_end=backtestTimeLine._period_end,
            period_frequency=backtestTimeLine._period_frequency,
            strategy_code=backtestTimeLine._strategy)
        super().execute(url_k_lines=url_k_lines, headers=headers)
        self._signals_index: float = None
        self._backtest_profit: float = None
        self._backtest_stats: any = None
        self._total_return: any = None
        self._backtest_orders: any = None
        self._backtest_: any = None


    def executeProfit(self):
        """Get period with init and end, use frequency to create 'actions' in period"""
        try:

            apply_strategy = self._requestApplyStrategy()
            if (apply_strategy["success"] == False):
                raise Exception("Problem to apply strategy")

            calculate_profit = self._calculateProfit()
            if (calculate_profit["success"] == False):
                raise Exception("Problem to apply strategy")
            response = self.toJsonProfit()


        # TODO: implementar a resposta dos k-lines de cada dia estipulado
            return {"data": response, "success": True, "message":"OK"}

        except Exception as e:
            error_log(message_err=f"{e}",
                      traceback=f"{traceback.format_exc()}")
            return {"data": None, "success": False, "message": f"{e}"}

    def toJsonProfit(self)-> backtestProfitUseCaseResponse:
        """return a json"""
        response = backtestProfitUseCaseResponse(
                    data=createBacktestObjectCaseObject(
                        period_init=self._period_init,
                        period_end=self._period_end,
                        period_frequency=self._period_frequency,
                        strategy=self._strategy,
                        time_line_order_days=self._time_line_order_days,
                        backtest_profit=self._backtest_profit,
                        backtest_stats=self._backtest_stats,
                        signals_index=self._signals_index,
                        backtest_total_return=self._total_return,
                        backtest_orders_records=self._backtest_orders_records,
                    ),
                    success=True
                    )
        return asdict(response)

    def _requestApplyStrategy(self):
        try:
            # TODO:ALTERAR AQUI (MOCK)
            request = {
                "data": [
                      {
                        "date": "2024-02-01",
                        "action": "buy",
                        "strategy": {
                            "create oiafhjiasffsbia":"iuahfuifusa"
                        },
                        "index":{
                            "SMA": 1.0,
                            "TLA":110,
                            "example":11
                        },
                        "price_close": 100,
                        "k-lines": {
                                    "date": "2024-02-01",
                                    "min_low": 100,
                                    "max_high": 150,
                                    "total_volume": 200001,
                                    "candle_count": 10,
                                    "avg_close": 1899.30
                                }
                      },
                      {
                        "date": "2024-02-02",
                        "action": "sell",
                        "strategy": {
                            "create oiafhjiasffsbia":"iuahfuifusa"
                        },
                        "index":{
                            "SMA": 1.0,
                            "TLA":110,
                            "example":11
                        },
                        "price_close": 160,
                        "k-lines": {
                                    "date": "2024-02-01",
                                    "min_low": 100,
                                    "max_high": 150,
                                    "total_volume": 200001,
                                    "candle_count": 10,
                                    "avg_close": 1899.30
                                }
                      },
                      {
                        "date": "2024-02-03",
                        "action": "buy",
                        "strategy": {
                            "create oiafhjiasffsbia":"iuahfuifusa"
                        },
                        "index":{
                            "SMA": 1.0,
                            "TLA":110,
                            "example":11
                        },
                        "price_close": 106,
                        "k-lines": {
                                    "date": "2024-02-01",
                                    "min_low": 100,
                                    "max_high": 150,
                                    "total_volume": 200001,
                                    "candle_count": 10,
                                    "avg_close": 1899.30
                                }
                      },
                      {
                        "date": "2024-02-04",
                        "action": "sell",
                        "strategy": {
                            "create oiafhjiasffsbia":"iuahfuifusa"
                        },
                        "index":{
                            "SMA": 1.0,
                            "TLA":110,
                            "example":11
                        },
                        "price_close": 47,
                        "k-lines": {
                                    "date": "2024-02-01",
                                    "min_low": 100,
                                    "max_high": 150,
                                    "total_volume": 200001,
                                    "candle_count": 10,
                                    "avg_close": 1899.30
                                }
                      },
                ]
            }
            self._signals_index = request["data"]
            return {"data": request["data"], "success": True, "message":"OK"}

        except Exception as e:
            error_log(message_err=f"{e}",
                      traceback=f"{traceback.format_exc()}")
            return {"data": None, "success": False, "message": f"{e}"}



    def _calculateProfit(self) -> List[Dict[str, str]]:
        """atraves de uma lista de actions
            actions = [
                {"order_day": "2024-02-01", "action": "buy"},
                {"order_day": "2024-02-02", "action": "sell"},
                {"order_day": "2024-02-03", "action": "buy"},
                {"order_day": "2024-02-04", "action": "sell"},
            ]
            transofrmar isso em:
                # Criar um DataFrame com os sinais
                df = pd.DataFrame(actions)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df.set_index("timestamp", inplace=True)

            # Criar Series booleanas para entradas e saídas
                entries = df["action"] == "buy"
                exits = df["action"] == "sell"

            Utilizar precos de fechamento do dia:
            # Simulação de preços fictícios
                price_data = pd.Series([100, 102, 101, 103], index=df.index)

            # Criar um backtest com vectorbt
            pf = vbt.IndicatorFactory.from_pandas(price_data).as_indicator()
            portfolio = vbt.IndicatorFactory.from_pandas(price_data).as_indicator().run(entries=entries, exits=exits)

            # Analisar o resultado
            print(portfolio.performance())
            """
        try:
            if(self._signals_index == None):
                raise Exception("Don't have actions")

            df = pd.DataFrame(self._signals_index)

            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            entries = df["action"] == "buy"
            exits = df["action"] == "sell"

            price_data = df["price_close"]
            portfolio = vbt.Portfolio.from_signals(close=price_data,
                                                   entries=entries,
                                                   exits=exits,
                                                   init_cash=1000,
                                                   accumulate=True,
                                                   size=1)
            self._backtest_stats = {key: self._convert_to_serializable(value) for key, value in portfolio.stats().items()}
            self._total_return = portfolio.total_return()
            self._backtest_profit = portfolio.total_profit()
            self._backtest_orders_records = json.loads(
                portfolio.orders.records_readable.to_json(orient="records", date_format="iso"))

            response = {
                "stats": self._backtest_stats,
                "performance": self._total_return,
                "profit": self._backtest_profit,
                "orders_record": self._backtest_orders_records
            }


            return {"data": response, "success": True, "message":"OK"}

        except Exception as e:
            error_log(message_err=f"{e}",
                      traceback=f"{traceback.format_exc()}")
            return {"data": None, "success": False, "message": f"{e}"}

    def _convert_to_serializable(self, obj):
            if isinstance(obj, pd.Timestamp):  # Converter Timestamp para string ISO
                return obj.isoformat()
            elif isinstance(obj, pd.Timedelta):  # Converter Timedelta para string legível
                return str(obj)
            elif pd.isna(obj) or obj is pd.NaT or obj == np.inf or obj == -np.inf:  # Converter NaN e NaT para None
                return None
            elif isinstance(obj, (np.int64, np.int32)):  # Converter NumPy int para Python int
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32)):  # Converter NumPy float para Python float
                return float(obj)
            elif obj == np.inf:  # Tratar infinito positivo
                return "Infinity"
            elif obj == -np.inf:  # Tratar infinito negativo
                return "-Infinity"
            return obj  # Manter os outros tipos
