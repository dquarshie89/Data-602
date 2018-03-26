#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 10 16:59:34 2018

@author: admin
"""

from flask import Flask
import urllib.request as req
import requests
import pandas as pd
#from pandas import DataFrame as df
import numpy as np
import datetime as dt
import time 
from bs4 import BeautifulSoup

give_cur = 'BTC'
rec_cur = 'USD'

price = requests.get("https://min-api.cryptocompare.com/data/price?fsym="+give_cur+"&tsyms="+rec_cur)
history = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym="+give_cur+"&tsym="+rec_cur+"&limit=100")

price_data = price.json()
history_data = history.json()

print(price_data[rec_cur])
hist_df = pd.DataFrame(history_data["Data"])

hist_df['time'] = pd.to_datetime(hist_df['time'])
print(hist_df['time'])
time_close = hist_df[['time','close']].copy()
print(time_close)
time_close.plot()
#print (time.strftime("%Z - %Y/%m/%d, %H:%M:%S", time.localtime(float(hist_df['time']))))
