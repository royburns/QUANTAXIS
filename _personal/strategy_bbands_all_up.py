# -*- coding: utf-8 -*-

"""
Strategy Name: BBANDS_ALL_UP
    1. Bolling BANDS
    2. All bands up
"""

import QUANTAXIS as QA
from QUANTAXIS.QAUtil.QAParameter import MARKET_TYPE
import numpy as np
import pandas as pd
import talib
import math
import datetime
st1=datetime.datetime.now()


# code_list = ['000793', '300059', '600885', '600079',
#              '601899', '601808']
# code_list = QA.QA_fetch_stock_block_adv().code[0:50]
code_list = ['601899']
start_date = '2017-01-01'
end_date = '2018-09-21'

# create account
Account = QA.QA_Account()
Broker = QA.QA_BacktestBroker()

Account.reset_assets(1000000)

Account.user_cookie = 'user_admin'
Account.portfolio_cookie = 'user_admin_portfolio'
Account.account_cookie = 'user_admin_portfolio_admin_account'
Account.strategy_name = 'user_admin_portfolio_admin_bbands_all_up'

# define the MACD_BBANDS strategy
def BBANDS_ALL_UP(dataframe, SHORT=12, LONG=26, M=9):
    """
    1. upper, middle, lower -- all up, then buy.
    2. upper, middle, lower -- all down, then sell.
    """
    CLOSE = dataframe.close

    upper, middle, lower = talib.BBANDS(CLOSE, timeperiod=22, nbdevup=2, nbdevdn=2, matype=0)
    # print(upper)
    # print(dataframe.close.iloc[-1])

    # all_up = upper[-1] > upper[-2] and upper[-2] > upper[-3] \
    #             and middle[-1] > middle[-2] and middle[-2] > middle[-3] \
    #             and lower[-1] > lower[-2] and lower[-2] > lower[-3] \
    #             and CLOSE > middle[-1]
    # all_down = lower[-1] < lower[-2] \
    #             and middle[-1] < middle[-2] \
    #             and upper[-1] < upper[-2] \
    #             or CLOSE < middle[-1]
                
    # all_up = upper[-1] > upper[-2] and upper[-2] > upper[-3] \
    all_down = upper[-1] > upper[-2] and upper[-2] > upper[-3] \
                and middle[-1] > middle[-2] and middle[-2] > middle[-3] \
                and CLOSE > middle[-1]
                
    # all_down = upper[-1] < upper[-2] and middle[-1] < middle[-2] and lower[-1] < lower[-2] \
    all_up = lower[-1] < lower[-2] \
                and middle[-1] < middle[-2] \
                and upper[-1] < upper[-2] \
                or CLOSE < middle[-1]

    # print('all_up', all_up, 'all_down', all_down)

    return pd.DataFrame({'upper': upper, 'middle': middle, 'lower': lower, 'close': CLOSE, 
                         'all_up': all_up, 'all_down': all_down})


# get data from mongodb
data = QA.QA_fetch_stock_day_adv(code_list, start_date, end_date)
data = data.to_qfq()

# add indicator
ind = data.add_func(BBANDS_ALL_UP)

# data_forbacktest=data.select_time('2018-01-01','2018-05-20')
data_forbacktest = data

for items in data_forbacktest.panel_gen:
    for item in items.security_gen:
        daily_ind = ind.loc[item.index]
        
        # Buy
        # daily_ind.cross_mid_up.iloc[0]
        # print(daily_ind.upper)
        # print(daily_ind.upper.iloc)
        if daily_ind.all_up.iloc[0] == True:
            if Account.sell_available.get(item.code[0], 0) <= 0:
                order = Account.send_order(
                    code=item.code[0], 
                    time=item.date[0], 
                    # amount=1000,
                    money=math.floor(Account.init_cash / (len(code_list) + 1)),
                    towards=QA.ORDER_DIRECTION.BUY,
                    # price=0,
                    price=daily_ind.close.iloc[0],
                    order_model=QA.ORDER_MODEL.CLOSE,
                    # amount_model=QA.AMOUNT_MODEL.BY_AMOUNT
                    amount_model=QA.AMOUNT_MODEL.BY_MONEY
                    )
                if order:
                    Broker.receive_order(QA.QA_Event(order=order,market_data=item))
                    trade_mes=Broker.query_orders(Account.account_cookie,'filled')
                    res=trade_mes.loc[order.account_cookie,order.realorder_id]
                    order.trade(res.trade_id,res.trade_price,res.trade_amount,res.trade_time)
        # Sell
        elif daily_ind.all_down.iloc[0] == True:
            if Account.sell_available.get(item.code[0], 0) > 0:
                order = Account.send_order(
                    code=item.code[0], 
                    time=item.date[0], 
                    amount=Account.sell_available.get(item.code[0], 0),
                    towards=QA.ORDER_DIRECTION.SELL,
                    price=0,
                    order_model=QA.ORDER_MODEL.MARKET,
                    amount_model=QA.AMOUNT_MODEL.BY_AMOUNT
                    )
                if order:
                    Broker.receive_order(QA.QA_Event(order=order,market_data=item))
                    trade_mes=Broker.query_orders(Account.account_cookie,'filled')
                    res=trade_mes.loc[order.account_cookie,order.realorder_id]
                    order.trade(res.trade_id,res.trade_price,res.trade_amount,res.trade_time)
    Account.settle()

print('TIME -- {}'.format(datetime.datetime.now()-st1))
# print(Account.history)
# print(Account.history_table)
# print(Account.daily_hold)

# create Risk analysis
Risk = QA.QA_Risk(Account, benchmark_code='601899', benchmark_type=MARKET_TYPE.STOCK_CN)
# print(Risk.message)
# print(Risk.assets)
Risk.plot_assets_curve()
plt=Risk.plot_dailyhold()
plt.show()
plt1=Risk.plot_signal()
# plt.show()

performance=QA.QA_Performance(Account)
plt=performance.plot_pnlmoney(performance.pnl_fifo)
# plt.show()
# Risk.assets.plot()
# Risk.benchmark_assets.plot()

# save result
Account.save()
Risk.save()
QA.QA_SU_save_strategy(Account.strategy_name, account_cookie=Account.account_cookie)


account_info = QA.QA_fetch_account({'account_cookie': Account.account_cookie})
account = QA.QA_Account().from_message(account_info[0])
print(account)
