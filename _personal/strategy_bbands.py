# -*- coding: utf-8 -*-

"""
Strategy Name: BBANDS
    1. Bolling BANDS
"""

import QUANTAXIS as QA
import numpy as np
import pandas as pd
import talib
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import talib

code_list = ['000001', '000002', '000004', '600000',
             '600536', '000936', '002023', '600332',
             '600398', '300498', '603609', '300673']
# code_list = QA.QA_fetch_stock_block_adv().code[0:50]
# code_list = ['600789']
start_date = '2018-01-01'
end_date = '2018-05-25'


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


# create account
Account = QA.QA_Account()
Broker = QA.QA_BacktestBroker()

Account.reset_assets(1000000)
Account.account_cookie = 'user_admin_bbands'

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
                code=item.data.index.levels[1][0],
                time=item.data.index.levels[0][0],
                # code=item.data['code'][0],
                # time=item.data['date'][0],
                amount=1000,
                towards=QA.ORDER_DIRECTION.BUY,
                price=0,
                order_model=QA.ORDER_MODEL.CLOSE,
                amount_model=QA.AMOUNT_MODEL.BY_AMOUNT
                )
            Account.receive_deal(Broker.receive_order(QA.QA_Event(order=order, market_data=item)))
        # Sell
        # elif daily_ind.CROSS_SC.iloc[0] > 0:
        elif daily_ind.cross_mid_down.iloc[0] > 0:
            if Account.sell_available.get(item.code[0], 0) > 0:
                order = Account.send_order(
                    code=item.data.index.levels[1][0],
                    time=item.data.index.levels[0][0],
                    # code=item.data['code'][0],
                    # time=item.data['date'][0],
                    amount=Account.sell_available.get(item.code[0], 0),
                    towards=QA.ORDER_DIRECTION.SELL,
                    price=0,
                    order_model=QA.ORDER_MODEL.MARKET,
                    amount_model=QA.AMOUNT_MODEL.BY_AMOUNT
                    )
                Account.receive_deal(Broker.receive_order(QA.QA_Event(order=order, market_data=item)))
    Account.settle()

print(Account.history)
print(Account.history_table)
print(Account.daily_hold)

# create Risk analysis
Risk = QA.QA_Risk(Account)
print(Risk.message)
print(Risk.assets)

# Risk.assets.plot()
# Risk.benchmark_assets.plot()
Risk.plot_assets_curve()
Risk.plot_dailyhold()
Risk.plot_signal()

# plt.style.use('ggplot')
# f, ax = plt.subplots(figsize=(20, 8))
# ax.set_title('SIGNAL TABLE --ACCOUNT: {}'.format(Account.account_cookie))
# ax.set_xlabel('Code')
# ax.set_ylabel('DATETIME', rotation=90)
# import matplotlib.patches as mpatches
# # x2 = Risk.benchmark_assets.x
#
# patch_assert = mpatches.Patch(color='red', label='assert')
# patch_benchmark = mpatches.Patch(label='benchmark')
# plt.legend(handles=[patch_assert, patch_benchmark], loc=0)
# plt.title('Assert and Benchmark')
#
#
# cmap = sns.cubehelix_palette(start=1, rot=3, gamma=0.8, as_cmap=True)
# ht = sns.heatmap(Account.trade.head(55), cmap=cmap, linewidths=0.05, ax=ax)
# # sns.heatmap(Account.trade.head(55), cmap="YlGnBu",linewidths = 0.05, ax = ax)
# # ht.set_xticklabels(rotation=90)
# # ht.set_yticklabels(rotation=90)
# plt.show()

# # save result
# Account.save()
# Risk.save()
#
# account_info=QA.QA_fetch_account({'account_cookie':'user_admin_macd'})
# account=QA.QA_Account().from_message(account_info[0])
# print(account)
