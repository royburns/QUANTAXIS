# utf-8

'''
stock-info-database.csv

    "Code","Symbol","Industry","Board"
    "000001.SZ","平安银行","Unknown","Unknown"
    "000002.SZ","万科Ａ","Unknown","Unknown"
    "000004.SZ","国农科技","Unknown","Unknown"
    "000005.SZ","世纪星源","Unknown","Unknown"
    "000006.SZ","深振业Ａ","Unknown","Unknown"
    "000007.SZ","零七股份","Unknown","Unknown"

stock-name-database.csv

    "Code","Name"
    "600846.SS","上海同济科技实业股份有限公司"
    "300216.SZ","湖南千山制药机械股份有限公司"
    "002409.SZ","江苏雅克科技股份有限公司"

user-defined-database.csv

    "Code","Symbol"
    "002056.PP","摸鱼科技"

'''
import time
import QUANTAXIS as QA
import pandas as pd


df = QA.QA_fetch_stock_list_adv()
df_stock_info = pd.DataFrame()
df_stock_info
# df_stock_info['Code'] = []
# df_stock_info['Symbol'] = []
# df_stock_info['Industry'] = []
# df_stock_info['Board'] = []
# df_stock_info.set_index('Code')

df_stock_name = pd.DataFrame()
# df_stock_name['Code'] = []
# df_stock_name['Name'] = []
# df_stock_name.set_index('Code')

# print(df['code'])
for index, row in df.iterrows():
    # print(row)
    # item1['Code'] = row['code'] + '.' + row['sse'].upper()
    # item1['Symbol'] = row['name']
    # item1['Industry'] = ['Unknown']
    # item1['Board'] = ['Unknown']
    if row['sse'] == 'sz':
        row['sse'] = 'SZ'
    else:
        row['sse'] = 'SS'
    item1 = pd.DataFrame([[row['code'] + '.' + row['sse'].upper(), row['name'], 
                        'Unknown', 'Unknown']], 
                        columns=['Code','Symbol','Industry','Board'])
    df_stock_info = df_stock_info.append(item1, ignore_index=True)

    # df_stock_name['Code'] = row['code'] + '.' + row['sse'].upper()
    # df_stock_name['Name'] = row['name']
    item2 = pd.DataFrame([[row['code'] + '.' + row['sse'].upper(), row['name']]], 
                        columns=['Code','Name'])
    df_stock_name = df_stock_name.append(item2, ignore_index=True)

df_stock_info.to_csv('E:\workspace\code\quantaxis\_personal\stock-info-database.csv', columns=['Code','Symbol','Industry','Board'], index=False)
df_stock_name.to_csv('E:\workspace\code\quantaxis\_personal\stock-name-database.csv', columns=['Code','Name'], index=False)
