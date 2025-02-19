"""ImperiumEngine test suite."""
import numpy as np
import pandas as pd
import pytest

from imperiumengine.backtest import BacktestProfit, BacktestTimeLine


class TestBacktest:
    @pytest.mark.backtest
    def test_backtest_time_line(self) -> None:
        """Dados de exemplo"""
        # INPUT
        period_init = "2024-02-01"
        period_end = "2024-02-28"
        period_frequency = "1d"
        strategy_code = {"meu teste":"sim"}
        # EXEC

        new_time_line = BacktestTimeLine(period_init=period_init,
                                       period_end=period_end,
                                       period_frequency=period_frequency,
                                       strategy_code=strategy_code)

        # EXPECT
        expect_response = new_time_line.execute(url_k_lines='teste',headers={})
        assert expect_response['success'] == True



if __name__ == "__main__":
    pytest.main([__file__])
