# -*- coding: utf-8 -*-
# Demo: Cao pan shou strategy
# src: ./test_backtest/caopanshou.py

import QUANTAXIS as QA
import numpy as np
import pandas as pd
import datetime
st1 = datetime.datetime.now()


def caopanshou(dataframe, SHORT=12, LONG=26, M=9):
    """
    1.DIF向上突破DEA，买入信号参考。
    2.DIF向下跌破DEA，卖出信号参考。
    """
    # DA:(3*CLOSE+OPEN+LOW+HIGH)/6,POINTDOT;
    # X2:(20*DA+19*REF(DA,1)+18*REF(DA,2)+17*REF(DA,3)+16*REF(DA,4)+15*REF(DA,5)+14*REF(DA,6)+13*REF(DA,7)+12*REF(DA,8)+11*REF(DA,9)+10*REF(DA,10)+9*REF(DA,11)+8*REF(DA,12)+7*REF(DA,13)+6*REF(DA,14)+5*REF(DA,15)+4*REF(DA,16)+3*REF(DA,17)+2*REF(DA,18)+REF(DA,20))/210,COLORF0F000;
    # X3:MA(X2,5),COLORYELLOW,LINETHICK1;
    # X1:=(C+L+H)/3;
    # 买:=CROSS(X2,X3);
    # 卖:=CROSS(X3,X2);
    OPEN = dataframe.open
    CLOSE = dataframe.close
    HIGH = dataframe.high
    LOW = dataframe.low

    DA = (OPEN + 3 * CLOSE + HIGH + LOW) / 6

    X2 = (20*DA + 19*QA.REF(DA,1) + 18*QA.REF(DA,2) + 17*QA.REF(DA,3) + 16*QA.REF(DA,4)
        + 15*QA.REF(DA,5) + 14*QA.REF(DA,6) + 13*QA.REF(DA,7) + 12*QA.REF(DA,8) + 11*QA.REF(DA,9)
        + 10*QA.REF(DA,10) + 9*QA.REF(DA,11) + 8*QA.REF(DA,12) + 7*QA.REF(DA,13) + 6*QA.REF(DA,14)
        + 5*QA.REF(DA,15) + 4*QA.REF(DA,16) + 3*QA.REF(DA,17) + 2*QA.REF(DA,18) + QA.REF(DA,20)) / 210
    X3 = QA.MA(X2,5)
    X1 = (OPEN + CLOSE + HIGH + LOW) / 4

    # Support and Resistance
    # 止盈价:HHV(MA(C,5),13),LINETHICK2,COLORYELLOW;{下穿，清仓观望；上穿，进场，根据上面的买卖指标}
    # 生命线:LLV(MA(C,5),13),LINETHICK2,COLORBLUE;{下穿、低于、沿着下行，空仓不做；上穿、高于，不做 OR 少仓位，根据上面的买卖指标}
    resistance = QA.HHV(QA.MA(CLOSE, 5), 13)
    support = QA.LLV(QA.MA(CLOSE, 5), 13)
    # print(resistance)

    cross_up_upper = QA.CROSS(CLOSE, resistance)
    cross_down_upper = QA.CROSS(resistance, CLOSE)
    cross_up_downer = QA.CROSS(CLOSE, support)
    cross_down_downer = QA.CROSS(support, CLOSE)

    return pd.DataFrame({'resistance': resistance, 'support': support, 'close': CLOSE})

    # CLOSE = dataframe.close
    # DIFF = QA.EMA(CLOSE, SHORT) - QA.EMA(CLOSE, LONG)
    # DEA = QA.EMA(DIFF, M)
    # MACD = 2*(DIFF-DEA)

    # CROSS_JC = QA.CROSS(DIFF, DEA)
    # CROSS_SC = QA.CROSS(DEA, DIFF)
    # ZERO = 0
    # return pd.DataFrame({'DIFF': DIFF, 'DEA': DEA, 'MACD': MACD, 'CROSS_JC': CROSS_JC, 'CROSS_SC': CROSS_SC, 'ZERO': ZERO})


date_start = '2016-06-01'
date_start_backtest = '2017-01-01'
date_end = '2019-04-26'
# create account
user = QA.QA_User(username='admin', password='admin')
portfolio = user.new_portfolio('portfolio_caopanshou')


Account = portfolio.new_account(account_cookie='account_baima_20190428', init_cash=1000000)
Account.end_ = date_end
Broker = QA.QA_BacktestBroker()


# QA.QA_SU_save_strategy('caopanshou', if_save=True)
QA.QA_SU_save_strategy('caopanshou', portfolio_cookie=portfolio.portfolio_cookie, account_cookie=Account.account_cookie ,if_save=True)
# get data from mongodb
data = QA.QA_fetch_stock_day_adv(
    # ['000001', '000002', '000004', '600000'], '2017-01-01', '2019-04-24')
    # ['600596', '002017'], date_start, date_end)
    # ['600737', '601228', '300094', '300383', '002340', '002256', '002027', '002366'], date_start, date_end)
    ['000651', '601155'], date_start, date_end) # 格力电器 000651， 新城控股 601155， 分众传媒 002027
data = data.to_qfq()

# add indicator
ind = data.add_func(caopanshou)
# ind.xs('000001',level=1)['2018-01'].plot()

data_forbacktest = data.select_time(date_start_backtest, date_end)


for items in data_forbacktest.panel_gen:
    for item in items.security_gen:
        daily_ind = ind.loc[item.index]

        if daily_ind.close.iloc[0] > daily_ind.resistance.iloc[0] and \
            Account.sell_available.get(item.code[0], 0) == 0: # 空仓，买，只买一次
            # 阻力位之上，买入并持有
            order = Account.send_order(
                code=item.code[0],
                time=item.date[0],
                amount=1000,
                towards=QA.ORDER_DIRECTION.BUY,
                price=item.close[0], # money need price
                money=490000,
                order_model=QA.ORDER_MODEL.CLOSE,
                # amount_model=QA.AMOUNT_MODEL.BY_AMOUNT
                amount_model=QA.AMOUNT_MODEL.BY_MONEY
            )
            # print(item.to_json()[0])
            Broker.receive_order(QA.QA_Event(order=order, market_data=item))
            trade_mes = Broker.query_orders(Account.account_cookie, 'filled')
            res = trade_mes.loc[order.account_cookie, order.realorder_id]
            order.trade(res.trade_id, res.trade_price,
                        res.trade_amount, res.trade_time)
        elif daily_ind.close.iloc[0] < daily_ind.resistance.iloc[0]:
            # 跌破支撑位，卖出并观望
            # print(item.code)
            print('\n')
            print(Account.hold_table())
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
                # print
                Broker.receive_order(QA.QA_Event(
                    order=order, market_data=item))
                trade_mes = Broker.query_orders(
                    Account.account_cookie, 'filled')
                res = trade_mes.loc[order.account_cookie, order.realorder_id]
                order.trade(res.trade_id, res.trade_price,
                            res.trade_amount, res.trade_time)
    Account.settle()

print('TIME -- {}'.format(datetime.datetime.now()-st1))
# print(Account.history)
# print(Account.history_table)
# print(Account.daily_hold)

# create Risk analysis
Risk = QA.QA_Risk(Account)

Account.save()
Risk.save()


# print(Risk.message)
# print(Risk.assets)
# Risk.plot_assets_curve()
# plt=Risk.plot_dailyhold()
# plt.show()
# plt1=Risk.plot_signal()
# plt.show()

# performance=QA.QA_Performance(Account)
# plt=performance.plot_pnlmoney(performance.pnl_fifo)
# plt.show()
# Risk.assets.plot()
# Risk.benchmark_assets.plot()

# save result

#account_info = QA.QA_fetch_account({'account_cookie': 'user_admin_macd'})
#account = QA.QA_Account().from_message(account_info[0])
# print(account)
