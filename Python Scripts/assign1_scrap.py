#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 19:55:41 2018

@author: admin
"""

import urllib.request as req
import pandas as pd
from bs4 import BeautifulSoup

equities = ('AAPL','AMZN','A')

menu = ['Trade','Show Blotter','Show P/L','Quit']

blotter = pd.DataFrame(columns=[
        'Action',
        'Company',
        'Price per Share',
        'Shares',
        'Total Equity']
        )

def display_menu(menu):
    for m in menu:
        print(str(menu.index(m) +1) + " - " + m)
    #print('Choose an option:')

def Trade(equities):
    #for e in equities:
    print('\n'.join(equities))
        #print(str(equities.index(e) +1) + " - " + e)
    #print('Choose an option:')  

def buy(symbol):
    quote_page = 'https://www.bloomberg.com/quote/'+ symbol +':US'
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'companyName__99a4824b'})
    name = name_box.text.strip() 
    price_box = soup.find('span', attrs={'class':"priceText__1853e8a5"})
    price = price_box.text
    price = price.replace(',', '')
    blotter.loc[tradenum] = (['Buy', name, float(price), int(shares), round(float(price)*float(shares),2)])

def sell(symbol):
    quote_page = 'https://www.bloomberg.com/quote/'+ symbol +':US'
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'companyName__99a4824b'})
    name = name_box.text.strip() 
    price_box = soup.find('span', attrs={'class':"priceText__1853e8a5"})
    price = price_box.text
    price = price.replace(',', '')
    blotter.loc[tradenum] = (['Sell', name, float(price), int(shares), round(float(price)*float(shares),2)])

   
tradenum=0

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
            buy_confirm = input('\n Buy %s shares of %s? (Y/N): ' % (shares, symbol))
            if buy_confirm == 'Y':
                tradenum += 1
                buy(symbol)
                print(blotter)
        if trade == 'Sell':
            print('\nStocks: ')
            Trade(equities)
            symbol = input('\nPick your stock symbol: ')
            shares = int(input('\nEnter Number of shares: '))
            sell_confirm = input('\n Sell %s shares of %s? (Y/N): ' % (shares, symbol))
            if sell_confirm == 'Y':
                tradenum += 1
                sell(symbol)
                print(blotter)
                
        
        
    elif selected == 3:
        print(blotter)
       
    elif selected == 4:
        print('\nThanks')
        done = False
        
    elif selected >4 or selected<1:
        print('\nPlease enter a valid choice')
        #display_menu(menu)
