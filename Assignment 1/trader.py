#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 19:55:41 2018
@author: admin
"""

from flask import Flask
import urllib.request as req
import pandas as pd
from pandas import DataFrame as df
import numpy as np
import datetime as dt
from bs4 import BeautifulSoup

app = Flask(__name__)

tradenum=0
plnum =0 
cash = 10000000

now = dt.datetime.now()

equities = ('AAPL','AMZN','INTC','MSFT','SNAP')

menu = ['Trade','Show Blotter','Show P/L','Quit']

blotter = pd.DataFrame(columns=[
        'Action',
        'Ticker',
        'Shares',
        'Price per Share',
        'Trade Timestap',
        'Money In/Out']
        )

plb = pd.DataFrame(columns=[
        'Ticker',
        'Current Market Price',
        'Position',
        'VWAP',
        'UPL',
        'RPL',
        'As Of'
        ])

pls = pd.DataFrame(columns=[
        'Ticker',
        'Current Market Price',
        'Position',
        'VWAP',
        'UPL',
        'RPL',
        'As Of'
        ])


plt = pd.DataFrame(columns=[
        'Ticker',
        'Current Market Price',
        'Position',
        'VWAP',
        'UPL',
        'RPL',
        ])

def display_menu(menu):
    print('\nMain Menu\n')
    for m in menu:
        print(str(menu.index(m) +1) + " - " + m)
    
def Trade(equities):
    print('\n'.join(equities))

def buy_check(symbol):
    quote_page = 'https://finance.yahoo.com/quote/'+ symbol
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'D(ib)'})
    name = name_box.text.strip() 
    price_box = soup.find('td', attrs={'data-test': 'ASK-value'})
    price = price_box.text
    price = price.replace(',', '')
    price = price.split('x', 1)[0]
    return price

def sell_check(symbol):
    quote_page = 'https://finance.yahoo.com/quote/'+ symbol
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'D(ib)'})
    name = name_box.text.strip() 
    price_box = soup.find('td', attrs={'data-test': 'BID-value'})
    price = price_box.text
    price = price.replace(',', '')
    price = price.split('x', 1)[0]

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

def wavg(group, avg_name, weight_name):
    d = group[avg_name]
    w = group[weight_name]
    try:
        return (d * w).sum() / w.sum()
    except ZeroDivisionError:
        return d.mean()

def pl_buy(symbol):
    global plb
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
    
    position = blotter[blotter['Action'] == 'Buy'].groupby(['Ticker'])[['Shares']].sum() # use as dataframe and join to vwap 
    position = pd.DataFrame(position).reset_index()
    position.columns = ['Ticker', 'Position']
    
    wap = blotter.groupby('Ticker').apply(wavg, 'Price per Share', 'Shares')
    #wap = blotter.groupby(['Ticker']).apply(lambda x: np.average(x[['Price per Share']], weights=x[['Shares']]))
    wap = pd.DataFrame(wap).reset_index()
    wap.columns = ['Ticker', 'WAP']
    
    price_position = pd.merge(price_buy, position, on='Ticker')
    
    pw = pd.merge(price_position, wap, on='Ticker')
    
    url = float(pw['Market Price'])*float(pw['Position'])
    
    url_profit = pd.DataFrame([[symbol,url,'0',pd.to_datetime('now')]])
    url_profit.columns = ['Ticker', 'URL','RPL','As Of']
    
    pl_buy = pd.merge(pw, url_profit, on='Ticker')
     
    #pl = pl_buy.append(pl_buy)
    plb = np.vstack((plb,pl_buy)) 
    plb = df(plb)
    plb.columns=['Ticker','Current Price','Position','VWAP','URL','RPL','As Of']
    
    plb = plb.sort_values(by='As Of')
    plb = plb.drop_duplicates('Ticker', keep='last').values
    plb = df(plb)
    plb.columns=['Ticker','Current Price','Position','VWAP','URL','RPL','As Of']
 
def pl_sell(symbol):
    global pls
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
    
    position = blotter[blotter['Action'] == 'Sell'].groupby(['Ticker'])[['Shares']].sum() # use as dataframe and join to vwap 
    position = pd.DataFrame(position).reset_index()
    position.columns = ['Ticker', 'Position']
    
    wap = blotter.groupby('Ticker').apply(wavg, 'Price per Share', 'Shares')
    #wap = blotter.groupby(['Ticker']).apply(lambda x: np.average(x[['Price per Share']], weights=x[['Shares']]))
    wap = pd.DataFrame(wap).reset_index()
    wap.columns = ['Ticker', 'WAP']
    
    price_position = pd.merge(price_buy, position, on='Ticker')
    
    pw = pd.merge(price_position, wap, on='Ticker')
    
    rpl = float(pw['Market Price'])*float(pw['Position'])
    
    url_profit = pd.DataFrame([[symbol,'0',rpl,pd.to_datetime('now')]])
    url_profit.columns = ['Ticker', 'URL','RPL','As Of']
    
    pl_sell = pd.merge(pw, url_profit, on='Ticker')
     
    #pl = pl_buy.append(pl_buy)
    pls = np.vstack((pls,pl_sell)) 
    pls = df(pls)
    pls.columns=['Ticker','Current Price','Position','VWAP','URL','RPL','As Of']
    
    pls = pls.sort_values(by='As Of')
    pls = pls.drop_duplicates('Ticker', keep='last').values
    pls = df(pls)
    pls.columns=['Ticker','Current Price','Position','VWAP','URL','RPL','As Of']

def pl_tot(symbol):
    global plt
    quote_page = 'https://finance.yahoo.com/quote/'+ symbol
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'D(ib)'})
    name = name_box.text.strip() 
    price_box = soup.find('td', attrs={'data-test': 'BID-value'})
    price = price_box.text
    price = price.replace(',', '')
    price = price.split('x', 1)[0]
    
    if (symbol in plb[['Ticker']].values) == True and (symbol in pls[['Ticker']].values) ==True:
        plt = df([[symbol, 
                   price, 
                   float(plb['Position'])-float(pls['Position']),
                   float(plb['VWAP']), 
                   float(plb['URL'])-float(pls['RPL']),
                   float(pls['RPL'])
                   ]])
        plt.columns=['Ticker','Current Price','Position','VWAP','URL','RPL']
        
    elif (symbol in pls[['Ticker']].values) ==False:
        plt = plb[['Ticker','Current Price', 'Position', 'VWAP', 'URL', 'RPL']]
 
 
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
            quote_page = 'https://finance.yahoo.com/quote/'+ symbol
            page = req.urlopen(quote_page)
            soup = BeautifulSoup(page, 'html.parser')
            price_box = soup.find('td', attrs={'data-test': 'ASK-value'})
            price = price_box.text
            price = price.replace(',', '')
            price = price.split('x', 1)[0]
            total_price = float(price)*float(shares)
            buy_confirm = input('\nBuy %s shares of %s at $%s for $%s? (Y/N): ' % (shares, symbol, price, round(total_price,2)))
            if buy_confirm == 'Y' and total_price > cash:
                print('\nNot enough money to buy %s \n' %(symbol))
                print('\nTotal Cost: ')
                print(total_price)
                print('\nRemaining Cash: ')
                print(cash)
            if buy_confirm == 'Y' and total_price <= cash:
                tradenum += 1
                buy(symbol)
                cash = cash - blotter[blotter['Action'] == 'Buy']['Money In/Out'].sum()
                print('\nBlotter\n')
                print(blotter)
                print('\nRemaining Cash:\n')
                print(cash)
                pl_buy(symbol)
            if buy_confirm == 'N':
                print('\nDid not buy %s' %(symbol))
        elif trade == 'Sell':
            print('\nStocks: ')
            Trade(equities)
            symbol = input('\nPick your stock symbol: ')
            shares = int(input('\nEnter Number of shares: '))
            quote_page = 'https://finance.yahoo.com/quote/'+ symbol
            page = req.urlopen(quote_page)
            soup = BeautifulSoup(page, 'html.parser')
            price_box = soup.find('td', attrs={'data-test': 'ASK-value'})
            price = price_box.text
            price = price.replace(',', '')
            price = price.split('x', 1)[0]
            total_price = float(price)*float(shares)
            sell_confirm = input('\nSell %s shares of %s at $%s for $%s? (Y/N): ' % (shares, symbol, price, round(total_price,2)))
            if sell_confirm == 'Y' and (symbol in blotter[['Ticker']].values)==True:
                tradenum += 1
                sell(symbol)
                cash = cash + blotter[blotter['Action'] == 'Sell']['Money In/Out'].sum()
                print('\nBlotter\n')
                print(blotter)
                print('\nRemaining Cash:\n')
                print(cash)
                pl_sell(symbol)
            if sell_confirm == 'Y' and (symbol in plb[['Ticker']].values)==False:
                print('\nThere is no %s to sell\n' % (symbol))
            if sell_confirm == 'N':
                print('\nDid not sell %s' %(symbol))
    
    elif selected == 2:
        print('\nBlotter\n')
        print(blotter)             
   
    elif selected == 3:
        if len(plt) == 0:
            print('\nNo P and L yet\n')
        if len(plt) > 0:
            plnum=+1
            print('\nP/L\n')
            pl_tot(symbol)
            print(plt)
        
    elif selected == 4:
        print('\nThanks')
        done = False
        
    elif selected >4 or selected<1:
        print('\nPlease enter a valid choice')

if __name__ == "__main__":
    app.run(host='0.0.0.0') # host='0.0.0.0' needed for docker
