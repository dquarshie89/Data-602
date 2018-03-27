# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 10:47:29 2018

@author: dquarshie
"""

from flask import Flask
import urllib.request as req
import requests
import pandas as pd
import matplotlib.pyplot as plt
#from pandas import DataFrame as df
import numpy as np
import datetime as dt
import time 
from bs4 import BeautifulSoup 

tradenum=0
plnum =0 
cash = 10000000

now = dt.datetime.now()

menu = ['Trade','Show Blotter','Show P/L','Quit']

blotter = pd.DataFrame(columns=[
        'Action',
        'Ticker',
        'Shares',
        'Price per Share',
        'Trade Timestap',
        'Money In/Out']
        )

rec_cur ='USD'

def display_menu(menu):
    print('\nMain Menu\n')
    for m in menu:
        print(str(menu.index(m) +1) + " - " + m)

def get_quote(give_cur,rec_cur):
    price = requests.get("https://min-api.cryptocompare.com/data/price?fsym="+give_cur+"&tsyms="+rec_cur)
    price_data = price.json()
    price_data = price_data[rec_cur]
    
    history_data = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym="+give_cur+"&tsym="+rec_cur+"&limit=100")
    history_data = history_data.json()
    hist_df = pd.DataFrame(history_data["Data"])
    hist_df['time'] = pd.to_datetime(hist_df['time'], unit='s')
    time_close = hist_df[['time','close']].copy()
    plt.plot(hist_df['time'] ,hist_df['close'] )
    plt.gcf().autofmt_xdate()
    plt.show(block=True)
    
    if trade =='Buy':
        blotter.loc[tradenum] = (['Buy', give_cur, float(shares), float(price_data), pd.to_datetime('now'), round(float(price_data)*float(shares),2)])
    if trade == 'Sell':
        blotter.loc[tradenum] = (['Sell', give_cur, float(shares), float(price_data), pd.to_datetime('now'), round(float(price_data)*float(shares),2)])
    print(price_data)


    

done = True

while done:
    display_menu(menu)
    selected = int(input('\nEnter your choice [1-4]: '))
    if selected == 1:
        print('\nTrade Menu')
        trade = input('Buy or Sell?: ')
        if trade == 'Buy':
            give_cur = input('\nPick your cyrpto to buy: ')
            shares = float(input('\nEnter Quantity: '))
            get_quote(give_cur,rec_cur)
            #history(give_cur,rec_cur)
            #print(price_data)
            #print(give_cur+" = $"+str(price_data)+"Shares:"+shares)
        
            
    elif selected == 4:
        print('\nThanks')
        done = False
        
    elif selected >4 or selected<1:
        print('\nPlease enter a valid choice')
    