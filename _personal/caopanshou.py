# utf-8
from QUANTAXIS.QAARP.QAStrategy import QA_Strategy
from QUANTAXIS.QAUtil.QAParameter import (AMOUNT_MODEL, MARKET_TYPE,
                                          FREQUENCE, ORDER_DIRECTION,
                                          ORDER_MODEL)
from QUANTAXIS.QAUtil.QALogs import QA_util_log_info
import time
import QUANTAXIS as QA
import pandas as pd


class CaoPanShouStrategy(QA_Strategy):
    '''
    操盘手

    啦啦啦
    '''
    def __init__(self):
        super().__init__()
        self.frequence = FREQUENCE.DAY
        self.market_type = MARKET_TYPE.STOCK_CN

    def on_bar(self, event):
        sellavailable=self.sell_available

        # data = QA.QA_fetch_stock_day_full_adv()

        try:
            for item in event.market_data.code:
                if sellavailable is None:

                    event.send_order(account_id=self.account_cookie,
                                     amount=100, amount_model=AMOUNT_MODEL.BY_AMOUNT,
                                     time=self.current_time, code=item, price=0,
                                     order_model=ORDER_MODEL.MARKET, towards=ORDER_DIRECTION.BUY,
                                     market_type=self.market_type, frequence=self.frequence,
                                     broker_name=self.broker)

                else:
                    if sellavailable.get(item, 0) > 0:
                        event.send_order(account_id=self.account_cookie,
                                         amount=sellavailable[item], amount_model=AMOUNT_MODEL.BY_AMOUNT,
                                         time=self.current_time, code=item, price=0,
                                         order_model=ORDER_MODEL.MARKET, towards=ORDER_DIRECTION.SELL,
                                         market_type=self.market_type, frequence=self.frequence,
                                         broker_name=self.broker
                                         )
                    else:
                        event.send_order(account_id=self.account_cookie,
                                         amount=100, amount_model=AMOUNT_MODEL.BY_AMOUNT,
                                         time=self.current_time, code=item, price=0,
                                         order_model=ORDER_MODEL.MARKET, towards=ORDER_DIRECTION.BUY,
                                         market_type=self.market_type, frequence=self.frequence,
                                         broker_name=self.broker)

        except:
            pass


def MACD_JCSC(dataframe, SHORT=12, LONG=26, M=9):
    '''
    1. DIF向上突破DEA，买入信号参考。
    2. DIF向下跌破DEA，卖出信号参考。
    '''

    CLOSE = dataframe.close
    DIF = QA.EMA(CLOSE, SHORT) - QA.EMA(CLOSE, LONG)
    DEA = QA.EMA(DIF, M)
    MACD = 2 * (DIF - DEA)

    CLOSE_JC = QA.CROSS(DIF, DEA)
    CLOSE_SC = QA.CROSS(DEA, DIF)
    ZERO = 0

    return pd.DataFrame({'DIF':DIF, 'DEA':DEA, 'MACD':MACD,
    'CLOSE_JC':CLOSE_JC, 'CLOSE_SC':CLOSE_SC, 'ZERO':ZERO})
    