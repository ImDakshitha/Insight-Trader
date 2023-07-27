import time
import os
import do_not_share
import json
import hmac
import hashlib
import requests
import pandas as pd
from urllib.parse import urljoin, urlencode
import datetime
import pprint
import numpy as np




PATH = '/v1/open-interest-history'

# put the path you want to save the csv in your computer

pathtocsv='D:\\Codes\\Backtesting\\Coinalyze\\Collected Data'

# save your coinalyze api key at a separate do_not_share.py file
headers = {
    'X-MBX-APIKEY': do_not_share.API_KEY
}



BASE_URL = 'https://api.coinalyze.net'

# this grabs the futures data from BTCUSDT_PERP.A
symbol= "BTCUSDT_PERP.A"
# change if you want a data in a different time interval 
interval="5min"
# ***** coinalyze holds only the last 30 days data****
# so this st and et shold be within one month from the date execute this code
st=(datetime.datetime(2023, 6, 17, 0, 0))
et=(datetime.datetime(2023, 7, 16, 0, 0))

startTime=str(int(st.timestamp()))
endTime=str(int(et.timestamp()))



exchanges=requests.get(' https://api.coinalyze.net/v1/exchanges',headers={'api_key': do_not_share.API_KEY})
markets=requests.get(' https://api.coinalyze.net/v1/future-markets',headers={'api_key': do_not_share.API_KEY})
oi=requests.get(f"https://api.coinalyze.net/v1/open-interest-history?symbols={symbol}&interval={interval}&from={startTime}&to={endTime}",headers={'api_key': do_not_share.API_KEY})
funding=requests.get(f"https://api.coinalyze.net/v1/predicted-funding-rate-history?symbols={symbol}&interval={interval}&from={startTime}&to={endTime}",headers={'api_key': do_not_share.API_KEY})
ohlc=requests.get(f"https://api.coinalyze.net/v1/ohlcv-history?symbols={symbol}&interval={interval}&from={startTime}&to={endTime}",headers={'api_key': do_not_share.API_KEY})
liquidation=requests.get(f"https://api.coinalyze.net/v1/liquidation-history?symbols={symbol}&interval={interval}&from={startTime}&to={endTime}",headers={'api_key': do_not_share.API_KEY})

fundinghistory=funding.json()
exchangeslist=exchanges.json()
BTCmarkets=markets.json()



oihistory=oi.json()[0]
oihistory=oihistory['history']
ohlchistory=ohlc.json()[0]
ohlchistory=ohlchistory['history']
fundinghistory=funding.json()[0]
fundinghistory=fundinghistory['history']
liquidationhistory=liquidation.json()[0]
liquidationhistory=liquidationhistory['history']


oi_data=pd.DataFrame.from_dict(oihistory)
ohlc_data=pd.DataFrame.from_dict(ohlchistory)
funding_data=pd.DataFrame.from_dict(fundinghistory)
liquidation_data=pd.DataFrame.from_dict(liquidationhistory)

oi_data=oi_data.set_index('t')
ohlc_data=ohlc_data.set_index('t')
funding_data=funding_data.set_index('t')
liquidation_data=liquidation_data.set_index('t')

oi_data.columns=['OIOpen','OIHigh','OILow','OIClose']
ohlc_data.columns=['open','high','low','close','Volume','bv','tx','btx']
funding_data.columns=['PFopen','PFhigh','PFlow','PFclose']
liquidation_data.columns=['LL','LS']
df_merged=oi_data.merge(ohlc_data, how='outer',left_index=True, right_index=True).fillna('0')
df_merged2=df_merged.merge(funding_data, how='outer',left_index=True, right_index=True).fillna('0')
df_merged3=df_merged2.merge(liquidation_data, how='outer',left_index=True, right_index=True).fillna('0')


# adding the datetime as index of the dataframe
df_merged3.index = pd.to_datetime(df_merged3.index, unit='s')
file_name=str(f"{symbol} Futures data from {st.strftime('%Y-%m-%d %H.%M.%S')} to {et.strftime('%Y-%m-%d %H.%M.%S')}.csv")

##csv file saving to a specfic path
df_merged3.to_csv(os.path.join(pathtocsv,file_name))

#print(exchangeslist)
# print(BTCmarkets)
# for d in exchangeslist:
#     if d['name']=="Binance":
#         print(d)
##pprint.pprint(BTCmarkets)
# fig = make_subplots(rows=2, cols=1,shared_xaxes=True,vertical_spacing=0.02)

# fig.add_trace(go.Candlestick(x=df_merged3.index,
#                              open=df_merged3['OIOpen'],
#                              high=df_merged3['OIHigh'],
#                              low=df_merged3['OILow'],
#                              close=df_merged3['OIClose']),
#                              row=2,col=1)

# fig.add_trace(go.Candlestick(x=df_merged3.index,
#             open=df_merged3['open'],
#             high=df_merged3['high'],
#             low=df_merged3['low'],
#             close=df_merged3['close']),
#             row=1,col=1,
#             )

# # fig.append_trace(go.Scatter(x=oi_data["timestamp"], y=df_merged3["high"]*oi_data["Increase"],    mode='markers', marker_symbol='triangle-up',marker_color='green', marker_size=12),row=1,col=1)
# fig.update_xaxes(row=1, col=1, rangeslider_visible=False)
# fig.update_layout(height=800, width=1200,title_text="Open Interest with Price")
# fig.show()