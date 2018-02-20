#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 19:55:41 2018
@author: admin
"""

import urllib.request as req
import pandas as pd
import numpy as np
import datetime as dt
from bs4 import BeautifulSoup

cash = 10000000

now = dt.datetime.now()

equities = ('AAPL','AMZN','A','FB')

menu = ['Trade','Show Blotter','Show P/L','Quit']

blotter = pd.DataFrame(columns=[
        'Action',
        'Ticker',
        'Shares',
        'Price per Share',
        'Trade Timestap',
        'Money In/Out']
        )

pl = pd.DataFrame(columns=[
        'Ticker',
        'Current Market Price',
        'Position',
        'VWAP',
        'UPL',
        'RPL'
        ])


def display_menu(menu):
    print('\nMain Menu\n')
    for m in menu:
        print(str(menu.index(m) +1) + " - " + m)
    #print('Choose an option:')

def Trade(equities):
    print('\n'.join(equities))
        #print(str(equities.index(e) +1) + " - " + e)
    #print('Choose an option:')  

def buy(symbol):
    quote_page = 'https://finance.yahoo.com/quote/'+ symbol
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'D(ib)'})
    name = name_box.text.strip() 
    price_box = soup.find('td', attrs={'data-test': 'ASK-value'})
    price = price_box.text
    price = price.replace(',', '')
    price = price.split('x', 1)[0]
    blotter.loc[tradenum] = (['Buy', symbol, int(shares), float(price), pd.to_datetime('now'), round(float(price)*float(shares),2)])

def sell(symbol):
    quote_page = 'https://finance.yahoo.com/quote/'+ symbol
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'D(ib)'})
    name = name_box.text.strip() 
    price_box = soup.find('td', attrs={'data-test': 'BID-value'})
    price = price_box.text
    price = price.replace(',', '')
    price = price.split('x', 1)[0]
    blotter.loc[tradenum] = (['Sell', symbol, int(shares), float(price), pd.to_datetime('now'), round(float(price)*float(shares),2)])

def pl_buy(symbol):
    quote_page = 'https://finance.yahoo.com/quote/'+ symbol
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'D(ib)'})
    name = name_box.text.strip() 
    price_box = soup.find('td', attrs={'data-test': 'BID-value'})
    price = price_box.text
    price = price.replace(',', '')
    price = price.split('x', 1)[0]
    
    price_buy = pd.DataFrame([[symbol,price]])
    price_buy.columns = ['Ticker', 'Market Price']
    
    position = blotter.groupby(['Ticker'])[['Shares']].sum() # use as dataframe and join to vwap 
    #position = pd.DataFrame(position).reset_index()
    #position.columns = ['Ticker', 'Position']
    
    wap = blotter.groupby(['Ticker']).apply(lambda x: np.average(x[['Price per Share']], weights=x[['Shares']]))
    wap = pd.DataFrame(wap).reset_index()
    wap.columns = ['Ticker', 'WAP']
    
    #price_position = pd.merge(price_buy, position, on='Ticker')
    
    #pw = pd.merge(price_position, wap, on='Ticker')
    
    url = float(pw['Market Price'])*float(pw['Position'])
    
    #url_profit = pd.DataFrame([[symbol,url,'0']])
    #url_profit.columns = ['Ticker', 'URL','RPL']
    
    #pl_buy = pd.merge(pw, url_profit, on='Ticker')
    
    pl.loc[plnum] = (symbol,price,position,wap['WAP'],url,'0')
    
    
 
tradenum=0
plnum = 0

done = True

while done:
    display_menu(menu)
    selected = int(input('\nEnter your choice [1-4]: '))
    if selected == 1:
        print('\nTrade Menu')
        trade = input('Buy or Sell?: ')
        
        if trade == 'Buy':
            print('\nStocks: ')
            Trade(equities)
            symbol = input('\nPick your stock symbol: ')
            shares = int(input('\nEnter Number of shares: '))
            buy_confirm = input('\nBuy %s shares of %s? (Y/N): ' % (shares, symbol))
            if buy_confirm == 'Y':
                tradenum += 1
                buy(symbol)
                print('\nBlotter\n')
                print(blotter)
                plnum += 1 
                pl_buy(symbol)
            if buy_confirm == 'N':
                display_menu(menu)
        if trade == 'Sell':
            print('\nStocks: ')
            Trade(equities)
            symbol = input('\nPick your stock symbol: ')
            shares = int(input('\nEnter Number of shares: '))
            sell_confirm = input('\n Sell %s shares of %s? (Y/N): ' % (shares, symbol))
            if sell_confirm == 'Y':
                tradenum += 1
                sell(symbol)
                print('\nBlotter\n')
                print(blotter)
            if sell_confirm == 'N':
                display_menu(menu)
    
    elif selected == 2:
        print('\nBlotter\n')
        print(blotter)             
   
    elif selected == 3:
        print('\nP/L\n')
        print(pl)
        
        
        
        
  
       
    elif selected == 4:
        print('\nThanks')
        done = False
        
    elif selected >4 or selected<1:
        print('\nPlease enter a valid choice')
        #display_menu(menu)
