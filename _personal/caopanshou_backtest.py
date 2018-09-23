# coding=utf-8
#
# The MIT License (MIT)
#
# Copyright (c) 2016-2018 yutiansut/QUANTAXIS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from QUANTAXIS.QAARP.QARisk import QA_Risk
from QUANTAXIS.QAARP.QAUser import QA_User
from QUANTAXIS.QAARP.QAAccount import QA_Account
from QUANTAXIS.QABacktest.QABacktest import QA_Backtest
from QUANTAXIS.QAUtil.QALogs import QA_util_log_info
from QUANTAXIS.QAUtil.QAParameter import FREQUENCE, MARKET_TYPE
from test_backtest.minstrategy import MAMINStrategy
from test_backtest.caopanshou import CaoPanShouStrategy


class Backtest(QA_Backtest):

    def __init__(self, market_type, frequence, start, end, code_list, commission_fee):
        super().__init__(market_type,  frequence, start, end, code_list, commission_fee)

        cpsstrategy = CaoPanShouStrategy()
        self.user = QA_User(user_cookie='user_admin')
        self.portfolio = self.user.new_portfolio('folio_admin_caopanshou')
        # self.account = self.portfolio.new_account()
        # self.portfolio, self.account = self.user.register_account(cpsstrategy, portfolio_cookie='folio_admin')
        self.portfolio, self.account = self.user.register_account(cpsstrategy)
        # account = QA_Account(user_cookie='user_admin',
        #                      portfolio_cookie='portfolio_admin',
        #                      account_cookie='account_admin')
        # self.user = QA_User.register_account(account)
        # self.portfolio, self.account = self.user.register_account(cpsstrategy)


    def after_success(self):
        QA_util_log_info(self.account.history_table)
        risk = QA_Risk(self.account, benchmark_code='000300',
                       benchmark_type=MARKET_TYPE.INDEX_CN)

        print(risk().T)

        self.account.save()
        risk.save()


def run_daybacktest():
    # import QUANTAXIS as QA
    backtest = Backtest(
        code_list=[300059, 601225],
        market_type=MARKET_TYPE.STOCK_CN,
        # frequence=FREQUENCE.FIFTEEN_MIN,
        frequence=FREQUENCE.DAY,
        start='2018-01-01',
        end='2018-02-05',
        # code_list=QA.QA_fetch_stock_block_adv().code[0:50],
        commission_fee=0.00015)
    backtest.start_market()

    backtest.run()
    backtest.stop()


if __name__ == '__main__':
    run_daybacktest()
    # backtest._settle()
    # backtest.run()
