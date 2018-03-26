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
#shares = int(input('\nEnter Number of shares: '))

'''
price = requests.get("https://min-api.cryptocompare.com/data/price?fsym="+give_cur+"&tsyms="+rec_cur)
price_data = price.json()
history = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym="+give_cur+"&tsym="+rec_cur+"&limit=100")
'''

def display_menu(menu):
    print('\nMain Menu\n')
    for m in menu:
        print(str(menu.index(m) +1) + " - " + m)

def get_quote(give_cur,rec_cur):
    price = requests.get("https://min-api.cryptocompare.com/data/price?fsym="+give_cur+"&tsyms="+rec_cur)
    price_data = price.json()
    history = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym="+give_cur+"&tsym="+rec_cur+"&limit=100")
    '''
    if trade =='Buy':
        blotter.loc[tradenum] = (['Buy', symbol, int(shares), float(price), pd.to_datetime('now'), round(float(price)*float(shares),2)])
    if trade == 'Sell':
        blotter.loc[tradenum] = (['Sell', symbol, int(shares), float(price), pd.to_datetime('now'), round(float(price)*float(shares),2)])
'''
    return(history)
done = True

while done:
    display_menu(menu)
    selected = int(input('\nEnter your choice [1-4]: '))
    if selected == 1:
        print('\nTrade Menu')
        trade = input('Buy or Sell?: ')
        if trade == 'Buy':
            give_cur = input('\nPick your cyrpto to buy: ')
            get_quote(give_cur,rec_cur)
            print(give_cur+" = $"+str(price_data[rec_cur]))
            
    elif selected == 4:
        print('\nThanks')
        done = False
        
    elif selected >4 or selected<1:
        print('\nPlease enter a valid choice')
    