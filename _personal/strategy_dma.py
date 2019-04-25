# -*- coding: utf-8 -*-

"""
Strategy Name: DMA - doubling moving average
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
Account.strategy_name = 'user_admin_portfolio_admin_dma'

# define the MACD_BBANDS strategy
def DMA(dataframe, SHORT=13, LONG=34):
    """
    1. 短周期为30，长周期为60
    2. 当短期均线由上向下穿越长期均线时做空，
    3. 当短期均线由下向上穿越长期均线时做多，每次开仓前先平掉所持仓位，再开仓。
    """
    CLOSE = dataframe.close
    # print(len(CLOSE))
    
    fast_avg = talib.SMA(CLOSE, SHORT)
    slow_avg = talib.SMA(CLOSE, LONG)

    cross_up = QA.CROSS(fast_avg, slow_avg)
    cross_down = QA.CROSS(slow_avg, fast_avg)

    return pd.DataFrame({'FAST': fast_avg, 'SLOW': slow_avg,
                         'cross_up': cross_up, 'cross_down': cross_down})


# get data from mongodb
data = QA.QA_fetch_stock_day_adv(code_list, start_date, end_date)
data = data.to_qfq()

# add indicator
ind = data.add_func(DMA)
# ind.xs('000001',level=1)['2018-01'].plot()

# data_forbacktest=data.select_time('2018-01-01','2018-05-20')
data_forbacktest = data

for items in data_forbacktest.panel_gen:
    for item in items.security_gen:
        daily_ind = ind.loc[item.index]
        
        # Buy
        if daily_ind.cross_up.iloc[0] > 0:
            order = Account.send_order(
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
        elif daily_ind.cross_down.iloc[0] > 0:
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
