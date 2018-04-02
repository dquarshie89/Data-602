# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 10:47:29 2018

@author: dquarshie
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import json
#from bs4 import BeautifulSoup 
from bson import json_util
from pymongo import MongoClient

tradenum=0
plnum =0 
cash = 10000000

now = dt.datetime.now()

client = MongoClient()
db = client.blotter_database
collection = db.blotter_collection
trades = db.trades

menu = ['Crypto Info', 'Trade','Show Blotter','Show P/L','Quit']

blotter = pd.DataFrame(columns=[
        'Action',
        'Currency',
        'Quantity',
        'Price per Share',
        'Trade Timestap',
        'Money In/Out',
        'Cash']
        )

#rec_cur ='USD'

def display_menu(menu):
    print('\nMain Menu\n')
    for m in menu:
        print(str(menu.index(m) +1) + " - " + m)

def get_quote(give_cur,rec_cur):
    price = requests.get("https://min-api.cryptocompare.com/data/pricemultifull?fsyms="+give_cur+"&tsyms="+rec_cur)
    price_data = price.json()
    
    price_data = price_data["RAW"]
    price_data = json.dumps(price_data)
    price_data = json.loads(price_data)
    
    price_data = price_data[give_cur]
    price_data = json.dumps(price_data)
    price_data = json.loads(price_data)
    
    price_data = price_data[rec_cur]
    price_data = json.dumps(price_data)
    price_data = json.loads(price_data)
    
    history_data = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym="+give_cur+"&tsym="+rec_cur+"&limit=100")
    history_data = history_data.json()
    hist_df = pd.DataFrame(history_data["Data"])
    hist_df['time'] = pd.to_datetime(hist_df['time'], unit='s')
    
    price = price_data["PRICE"]
    maxprice = price_data["HIGH24HOUR"]
    minprice = price_data["LOW24HOUR"]
    stdprice= round(np.std(hist_df['close']),2)
    
    return (price, maxprice, minprice, stdprice, hist_df['time'] ,hist_df['close'])

def action(trade):
    x = get_quote(give_cur,rec_cur)
    if trade =='Buy':
        blotter.loc[tradenum] = (['Buy', give_cur, float(shares), float(x[1]), pd.to_datetime('now'), round(float(x[1])*float(shares),2),cash-round(float(x[1])*float(shares),2)])
    if trade == 'Sell':
        blotter.loc[tradenum] = (['Sell', give_cur, float(shares), float(x[1]), pd.to_datetime('now'), round(float(x[1])*float(shares),2),cash+round(float(x[1])*float(shares),2)])
   
        
def get_graph(give_cur,rec_cur):  
    quote = get_quote(give_cur,rec_cur)
    plt.plot(quote[4] ,quote[5] )
    plt.gcf().autofmt_xdate()
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Price of '+give_cur+' in '+rec_cur+' over 100 Days')
    plt.show(block=False)

def mavg(give_cur,rec_cur):
    quote = get_quote(give_cur,rec_cur)
    ret = np.cumsum(quote[5].values.tolist(), dtype=float)
    c = ret[20:] = ret[20:] - ret[:-20]
    c = ret[20 - 1:] / 20
    c = pd.DataFrame(c)
    plt.plot(c,'r-')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.title('Moving 20 Day Avg Price of '+give_cur+' in '+rec_cur)
    plt.show(block=False)
    
def wavg(group, avg_name, weight_name):
    d = group[avg_name]
    w = group[weight_name]
    try:
        return (d * w).sum() / w.sum()
    except ZeroDivisionError:
        return d.mean()
    


       
done = True

while done:
    display_menu(menu)
    selected = int(input('\nEnter your choice [1-5]: '))
    if selected == 1:
        print('\nCrypto Info')
        give_cur = input('\nPick crypto to look up: ') 
        rec_cur = input('\nPick currency to receive: ') 
        get_graph(give_cur,rec_cur)
        mavg(give_cur,rec_cur)
        q = get_quote(give_cur,rec_cur)
        print('\nCurrent Price: %s' %(q[0]))
        print('\nMax Price in the Last 24hrs: %s' %(q[1]))
        print('\nMin Price in the Last 24hrs: %s' %(q[2]))
        print('\nStd Dev of Price in the Last 24hrs: %s' %(q[3]))
    if selected == 2:
        print('\nTrade Menu')
        trade = input('Buy or Sell?: ')
        if trade == 'Buy':
            give_cur = input('\nPick your currency to buy: ')
            rec_cur = input('\nPick your currency to sell: ')
            shares = float(input('\nEnter Quantity: '))
            get_graph(give_cur,rec_cur)
            x = get_quote(give_cur,rec_cur)
            buy_confirm = input('\nBuy %s of %s for %s at %s for %s? (Y/N): ' % (shares, give_cur, rec_cur, x[1], round(float(x[1])*float(shares),2)))
            #Check to see if the user has enough cash to buy selected number of shares at ask price
            if buy_confirm == 'Y' and float(x[1])*float(shares) > cash:
                print('\nNot enough money to buy %s \n' %(give_cur))
                print('\nTotal Cost: ')
                print(float(x[1])*float(shares))
                print('\nRemaining Cash: ')
                print(cash)
            if buy_confirm == 'Y' and float(x[1])*float(shares) <= cash:
                tradenum += 1
                #Add the buy to the blotter
                act = action(trade)
                #Remove the total buy from the user's cash
                cash = cash - blotter[blotter['Action'] == 'Buy']['Money In/Out'].sum()
                print('\nBlotter\n')
                print(blotter)
                print('\nRemaining Cash:\n')
                print(cash)
                blot = blotter.to_json(orient='records')[1:-1].replace('},{', '} {')
                blot = json_util.loads(blot)
                result = trades.insert_one(blot)
                #Add the buy to the profit/loss
                #pl_buy(symbol)
                #pl_tot(symbol)
            if buy_confirm == 'N':
                print('\nDid not buy %s' %(give_cur))
        elif trade == 'Sell':
            give_cur = input('\nPick your currency to sell: ')
            rec_cur = input('\nPick your currency to buy: ')
            shares = float(input('\nEnter Quantity: '))
            get_graph(give_cur,rec_cur)
            x = get_quote(give_cur,rec_cur)
            sell_confirm = input('\nSell %s of %s for %s at %s for %s? (Y/N): ' % (shares, give_cur, rec_cur, x[1], round(float(x[1])*float(shares),2)))
            if sell_confirm == 'Y' and (give_cur in blotter[['Currency']].values)==True:
                tradenum += 1
                act = action(trade)
                cash = cash + blotter[blotter['Action'] == 'Sell']['Money In/Out'].sum()
                print('\nBlotter\n')
                print(blotter)
                print('\nRemaining Cash:\n')
                print(cash)
                blot = blotter.to_json(orient='records')[1:-1].replace('},{', '} {')
                blot = json_util.loads(blot)
                result = trades.insert_one(blot)
                #Add the sell to the profit/loss
                #pl_sell(symbol)
            #if sell_confirm == 'Y' and (symbol in plb[['Ticker']].values)==False:
                #Checks to see if there is any of the ticker to sell
                #print('\nThere is no %s to sell\n' % (symbol))
            if sell_confirm == 'N':
                print('\nDid not sell %s' %(give_cur))
    
            
        
            
    elif selected == 3:
        #Show blotter
        print('\nBlotter\n')
        print(blotter) 
    
    elif selected == 5:
        print('\nThanks')
        done = False
        
    elif selected >5 or selected<1:
        print('\nPlease enter a valid choice')
    
