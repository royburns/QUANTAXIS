# -*- coding: utf-8 -*-

"""
Strategy Name: BBANDS
    1. Bolling BANDS
"""

import QUANTAXIS as QA
import numpy as np
import pandas as pd
import talib
import datetime
st1=datetime.datetime.now()


code_list = ['000793', '300059', '600885', '600079',
             '601899', '601808']
# code_list = QA.QA_fetch_stock_block_adv().code[0:50]
# code_list = ['600789']
start_date = '2018-01-01'
end_date = '2018-09-21'

# create account
Account = QA.QA_Account()
Broker = QA.QA_BacktestBroker()

Account.reset_assets(1000000)

Account.user_cookie = 'user_admin'
Account.portfolio_cookie = 'user_admin_portfolio'
Account.account_cookie = 'user_admin_portfolio_admin_account'
Account.strategy_name = 'user_admin_portfolio_admin_bbands'

# define the MACD_BBANDS strategy
def BBANDS(dataframe, SHORT=12, LONG=26, M=9):
    """
    1.DIF向上突破DEA，买入信号参考。
    2.DIF向下跌破DEA，卖出信号参考。
    """
    CLOSE = dataframe.close
    # print(len(CLOSE))
    DIFF = QA.EMA(CLOSE, SHORT) - QA.EMA(CLOSE, LONG)
    DEA = QA.EMA(DIFF, M)
    MACD = 2*(DIFF-DEA)

    CROSS_JC = QA.CROSS(DIFF, DEA)
    CROSS_SC = QA.CROSS(DEA, DIFF)
    ZERO = 0

    upper, middle, lower = talib.BBANDS(CLOSE, timeperiod=20, nbdevup=2, nbdevdn=1.4, matype=0)
    # print(dataframe.close.iloc[-1])

    cross_upper_up = QA.CROSS(CLOSE, upper)
    cross_upper_down = QA.CROSS(upper, CLOSE)
    cross_mid_up = QA.CROSS(CLOSE, middle)
    cross_mid_down = QA.CROSS(middle, CLOSE)
    cross_lower_up = QA.CROSS(CLOSE, lower)
    cross_lower_down = QA.CROSS(lower, CLOSE)

    return pd.DataFrame({'DIFF': DIFF, 'DEA': DEA, 'MACD': MACD,
                         'CROSS_JC': CROSS_JC, 'CROSS_SC': CROSS_SC, 'ZERO': ZERO,
                         'upper': upper, 'middle': middle, 'lower': lower,
                         'cross_upper_up': cross_upper_up, 'cross_upper_down': cross_upper_down,
                         'cross_mid_up': cross_mid_up, 'cross_mid_down': cross_mid_down,
                         'cross_lower_up': cross_lower_up, 'cross_lower_down': cross_lower_down})


# get data from mongodb
# data = QA.QA_fetch_stock_day_adv('600789', start_date, end_date)
data = QA.QA_fetch_stock_day_adv(code_list, start_date, end_date)
data = data.to_qfq()

# add indicator
ind = data.add_func(BBANDS)
# ind.xs('000001',level=1)['2018-01'].plot()

# data_forbacktest=data.select_time('2018-01-01','2018-05-20')
data_forbacktest = data

for items in data_forbacktest.panel_gen:
    for item in items.security_gen:
        daily_ind = ind.loc[item.index]

        '''
        MultiIndex(levels=[[2018-01-31 00:00:00], ['000001']],
                    labels=[[0], [0]],
                    names=['date', 'code'])
        [[2018-01-30 00:00:00], ['603609']]
        2018-01-31 00:00:00
        000001
        <pandas.core.indexing._iLocIndexer object at 0x000002908ED90A48>
        open        1.335000e+01
        high        1.393000e+01
        low         1.332000e+01
        close       1.370000e+01
        volume      2.081592e+06
        amount      2.856544e+09
        preclose             NaN
        adj         1.000000e+00
        Name: (2018-01-02 00:00:00, 000001), dtype: float64
        1.335000e+01
        '''
        # print(item.data.index)
        # print(item.data.index.levels)
        # print(item.data.index.levels[0][0])
        # print(item.data.index.levels[1][0])
        # print(item.data.iloc)
        # print(item.data.iloc[0])
        # print(item.data.iloc[0]['open'])
        
        # Buy
        # if daily_ind.CROSS_JC.iloc[0] > 0:
        if daily_ind.cross_mid_up.iloc[0] > 0:
            order = Account.send_order(
                # code=item.data.index.levels[1][0],
                # time=item.data.index.levels[0][0],
                code=item.code[0], 
                time=item.date[0], 
                amount=1000,
                towards=QA.ORDER_DIRECTION.BUY,
                price=0,
                order_model=QA.ORDER_MODEL.CLOSE,
                amount_model=QA.AMOUNT_MODEL.BY_AMOUNT
                )
            Broker.receive_order(QA.QA_Event(order=order,market_data=item))
            trade_mes=Broker.query_orders(Account.account_cookie,'filled')
            res=trade_mes.loc[order.account_cookie,order.realorder_id]
            order.trade(res.trade_id,res.trade_price,res.trade_amount,res.trade_time)
        # Sell
        # elif daily_ind.CROSS_SC.iloc[0] > 0:
        elif daily_ind.cross_mid_down.iloc[0] > 0:
            if Account.sell_available.get(item.code[0], 0) > 0:
                order = Account.send_order(
                    # code=item.data.index.levels[1][0],
                    # time=item.data.index.levels[0][0],
                    code=item.code[0], 
                    time=item.date[0], 
                    amount=Account.sell_available.get(item.code[0], 0),
                    towards=QA.ORDER_DIRECTION.SELL,
                    price=0,
                    order_model=QA.ORDER_MODEL.MARKET,
                    amount_model=QA.AMOUNT_MODEL.BY_AMOUNT
                    )
                Broker.receive_order(QA.QA_Event(order=order,market_data=item))
                trade_mes=Broker.query_orders(Account.account_cookie,'filled')
                res=trade_mes.loc[order.account_cookie,order.realorder_id]
                order.trade(res.trade_id,res.trade_price,res.trade_amount,res.trade_time)
    Account.settle()

print('TIME -- {}'.format(datetime.datetime.now()-st1))
print(Account.history)
print(Account.history_table)
print(Account.daily_hold)

# create Risk analysis
Risk = QA.QA_Risk(Account)
print(Risk.message)
print(Risk.assets)
Risk.plot_assets_curve()
plt=Risk.plot_dailyhold()
plt.show()
plt1=Risk.plot_signal()
plt.show()

performance=QA.QA_Performance(Account)
plt=performance.plot_pnlmoney(performance.pnl_fifo)
plt.show()
# Risk.assets.plot()
# Risk.benchmark_assets.plot()

# save result
Account.save()
Risk.save()
QA.QA_SU_save_strategy('bbands', account_cookie=Account.account_cookie)


account_info = QA.QA_fetch_account({'account_cookie': Account.account_cookie})
account = QA.QA_Account().from_message(account_info[0])
print(account)
