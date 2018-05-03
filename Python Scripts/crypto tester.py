# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 16:36:38 2018

@author: dquarshie
"""

import requests
import pandas as pd
from pandas import DataFrame as df
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import json

tradenum=0
cash = 10000000
give_cur='BTC'
rec_cur='USD'

now = dt.datetime.now()

menu = ['Crypto Info', 'Trade','Show Blotter','Show P/L','Quit']

blotter = pd.DataFrame(columns=[
        'Action',
        'Bought Currency',
        'Sold Currency',
        'Quantity',
        'Price per Share',
        'Trade Timestap',
        'Money In/Out',
        'Cash']
        ) 

col_names = ['Bought Currency','Current Market Price','Position','VWAP','UPL','RPL','Total P/L']
             #,'% of Total Shares']
pl =pd.DataFrame([['BTC',0,0,0,0,0,0]] ,columns=col_names)
eth =pd.DataFrame([['ETH',0,0,0,0,0,0]] ,columns=col_names)
pl = pl.append(eth, ignore_index=True)
pl = pl.set_index('Bought Currency')

#pos_pcts= pd.DataFrame(columns=['Bought Currency','Position'])

'''
df_pl = pd.DataFrame(columns=[
    'Bought Currency',
    'Current Market Price',
    'Position',
    'VWAP',
    'UPL',
    'RPL',
    'Total P/L',
    '% of Total Shares']
    )
'''

def display_menu(menu):
    print('\nMain Menu\n')
    for m in menu:
        print(str(menu.index(m) +1) + " - " + m)

def get_quote(give_cur,rec_cur):
    gdax = requests.get("https://api.gdax.com/products/"+give_cur+"-"+rec_cur+"/book")
    gdax = pd.read_json(gdax.text)

    ask = gdax.iloc[0]['asks'][0]
    bid = gdax.iloc[0]['bids'][0]
    
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
    
    maxprice = price_data["HIGH24HOUR"]
    minprice = price_data["LOW24HOUR"]
    stdprice= round(np.std(hist_df['close']),2)
    
    return (ask, bid, minprice, maxprice, stdprice, hist_df['time'] ,hist_df['close'])

def action(trade):
    x = get_quote(give_cur,rec_cur)
    if trade =='Buy':
        blotter.loc[tradenum] = (['Buy', give_cur, rec_cur, float(shares), float(x[1]), pd.to_datetime('now'), round(float(x[1])*float(shares),2),cash-round(float(x[1])*float(shares),2)])
    if trade == 'Sell':
        blotter.loc[tradenum] = (['Sell', give_cur, rec_cur, float(shares), float(x[1]), pd.to_datetime('now'), round(float(x[1])*float(shares),2),cash+round(float(x[1])*float(shares),2)])

def update_pl(pl, shares):
    if trade =='Buy': 
        x = get_quote(give_cur,rec_cur)
        current_qty = pl.at[give_cur,'Position']
        #current_vwap = pl.at[give_cur,'VWAP']
        new_vwap = blotter.groupby('Bought Currency').apply(wavg, 'Price per Share', 'Quantity')
        pl.at[give_cur,'Position'] = current_qty + shares
        pl.at[give_cur,'VWAP'] = round(new_vwap[0],2)
        pl.at[give_cur,'UPL'] = float(x[1])*float(shares)
        pl.at[give_cur,'Current Market Price'] =float(x[1])
        pl.at[give_cur,'Total P/L']=pl.at[give_cur,'UPL']+pl.at[give_cur,'RPL']
        
    elif trade =='Sell': 
        x = get_quote(give_cur,rec_cur)
        current_qty = pl.at[give_cur,'Position']
        current_upl = pl.at[give_cur,'UPL']
        new_vwap = blotter.groupby('Bought Currency').apply(wavg, 'Price per Share', 'Quantity')
        pl.at[give_cur,'Position'] = current_qty - shares
        pl.at[give_cur,'VWAP'] = round(new_vwap[0],2)
        pl.at[give_cur,'RPL'] = float(x[1])*float(shares)
        pl.at[give_cur,'Current Market Price'] =float(x[1])
        pl.at[give_cur,'UPL'] = current_upl - (float(x[1])*float(shares))
        pl.at[give_cur,'Total P/L']=pl.at[give_cur,'UPL']+pl.at[give_cur,'RPL']
        
    return pl

def pl_pct(pl):
    pos_pcts = pl.groupby(['Bought Currency']).agg({'Position': 'sum'})/pl.agg({'Position': 'sum'})
    pos_pcts = pd.DataFrame(pos_pcts).reset_index()
    pos_pcts.columns = ['Bought Currency','% of Total Shares']
    pl_pcts = pl.groupby(['Bought Currency']).agg({'Total P/L': 'sum'})/pl.agg({'Total P/L': 'sum'})
    pl_pcts= pl_pcts.reset_index()
    pl_pcts.columns = ['Bought Currency','% of Total P/L']
    pcts = pd.merge(pos_pcts,pl_pcts,on='Bought Currency')
    return pcts
    # pos_pcts, pl_pcts
    

def get_graph(give_cur,rec_cur):  
    quote = get_quote(give_cur,rec_cur)
    plt.plot(quote[5] ,quote[6])
    plt.gcf().autofmt_xdate()
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Price of '+give_cur+' in '+rec_cur+' over 100 Days')
    plt.show(block=False)

def mavg(give_cur,rec_cur):
    quote = get_quote(give_cur,rec_cur)
    ret = np.cumsum(quote[6].values.tolist(), dtype=float)
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

def view_pl(pl,pcts):
    print("P/L")
    print(pl)
    print(pcts)
    #print()


 
done = True   

while done:
    #df_pl=initialize_pl(give_cur,rec_cur)
    display_menu(menu)
    #df_pl=initialize_pl(give_cur,rec_cur)
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
    
    elif selected == 2:
        
        print('\nTrade Menu')
        trade = input('Buy or Sell?: ')
        if trade == 'Buy':
            give_cur = input('\nPick your currency to buy: ')
            #rec_cur = input('\nPick your currency to sell: ')
            shares = float(input('\nEnter Quantity: '))
            get_graph(give_cur,rec_cur)
            x = get_quote(give_cur,rec_cur)
            buy_confirm = input('\nBuy %s of %s for %s at %s for %s? (Y/N): ' % (shares, give_cur, rec_cur, x[0], round(float(x[0])*float(shares),2)))
            #Check to see if the user has enough cash to buy selected number of shares at ask price
            if buy_confirm == 'Y' and float(x[1])*float(shares) > cash:
                print('\nNot enough money to buy %s \n' %(give_cur))
                print('\nTotal Cost: ')
                print(float(x[1])*float(shares))
                print('\nRemaining Cash: ')
                print(round(cash,2))
            if buy_confirm == 'Y' and float(x[1])*float(shares) <= cash:
                tradenum += 1
                #Add the buy to the blotter
                action(trade)
                cash = cash - blotter[blotter['Action'] == 'Buy']['Money In/Out'].sum()
                #df_pl=initialize_pl(give_cur,rec_cur)
                update_pl(pl, shares)
                #pl_pct(pl)
                print('\nBlotter\n')
                print(blotter)
                print('\nRemaining Cash:\n')
                print(round(cash,2))
            if buy_confirm == 'N':
                print('\nDid not buy %s' %(give_cur))
        if trade == 'Sell':
            give_cur = input('\nPick your currency to sell: ')
            #rec_cur = input('\nPick your currency to buy: ')
            shares = float(input('\nEnter Quantity: '))
            get_graph(give_cur,rec_cur)
            x = get_quote(give_cur,rec_cur)
            sell_confirm = input('\nSell %s of %s for %s at %s for %s? (Y/N): ' % (shares, give_cur, rec_cur, x[0], round(float(x[0])*float(shares),2)))
            if sell_confirm == 'Y':
                tradenum += 1
                action(trade)
                cash = cash + blotter[blotter['Action'] == 'Sell']['Money In/Out'].sum()
                #df_pl=initialize_pl(give_cur,rec_cur)
                update_pl(pl, shares)
                #pl_pct(pl)
                print('\nBlotter\n')
                print(blotter)
                print('\nRemaining Cash:\n')
                print(round(cash,2))
            
    elif selected == 3:
        #Show blotter
        print('\nBlotter\n')
        print(blotter) 
    
    elif selected == 4:  
        pcts=pl_pct(pl)
        view_pl(pl,pcts)

    elif selected == 5:
        print('\nThanks')
        done = False
        
    elif selected >5 or selected<1:
        print('\nPlease enter a valid choice')
    

#client = MongoClient()
#db = client.blotter_database
#collection = db.blotter_collection
#trades = db.trades
