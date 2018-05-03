#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  2 19:59:29 2018

@author: admin
"""

from fbprophet import Prophet
import datetime as dt
from datetime import timedelta

start_date =  dt.datetime.now()
end_date = start_date + timedelta(days=1)

bitcoin_market_info = pd.read_html("https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20170101&end="+time.strftime("%Y%m%d"))[0]
# convert the date string to the correct date format
bitcoin_market_info = bitcoin_market_info.assign(Date=pd.to_datetime(bitcoin_market_info['Date']))
bitcoin_market_info['Volume'] = bitcoin_market_info['Volume'].astype('int64')
bitcoin_market_info.columns = ['Date','bt_Open','bt_High','bt_Low','bt_Close','bt_Volume','bt_MarketCap']

#bitcoin_market_info['ds'] = bitcoin_market_info.index
bitcoin_market_info['ds'] = bitcoin_market_info['Date']
bitcoin_market_info['y'] = bitcoin_market_info['bt_Close']

forecast_data = bitcoin_market_info[['ds', 'y']].copy()
#forecast_data.reset_index(inplace=True)
#del forecast_data['Date']


# Create the Prophet model and fit the data

m = Prophet()
m.fit(forecast_data)

future = m.make_future_dataframe(periods=96, freq='H')
future.tail()

forecast = m.predict(future)
#print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())



forecast[(forecast['ds'] >= start_date) & (forecast['ds'] <= end_date)].head()[['ds','yhat']]
