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

#Initialize tradenum to count the number of trades made (Buy or Sell) during the session 
#Will be used to place trades in the blotter
tradenum=0

#Initialize pl to have a line for each ticker's profit and loss during the session 
#Will be used in the P/L tracking
plnum =0 

#Initialize the user with $10M
cash = 10000000

#Get the current date and time for use in the blotter. 
#Will show the date and time for each trade in the blotter
now = dt.datetime.now()

#List of tickers to show in the trade menu
equities = ('AAPL','AMZN','INTC','MSFT','SNAP')

#Menu items
menu = ['Trade','Show Blotter','Show P/L','Quit']

#Make a data frame for the blotter that has nothing but columns  
blotter = pd.DataFrame(columns=[
        'Action',
        'Ticker',
        'Shares',
        'Price per Share',
        'Trade Timestap',
        'Money In/Out']
        )

#Make a data frame for the buy section of the session. This will be used to see the unrealized profit/loss
plb = pd.DataFrame(columns=[
        'Ticker',
        'Current Market Price',
        'Position',
        'VWAP',
        'UPL',
        'RPL',
        'As Of'
        ])

#Make a data frame for the sell section of the session. This will be used to see the realized profit/loss
pls = pd.DataFrame(columns=[
        'Ticker',
        'Current Market Price',
        'Position',
        'VWAP',
        'UPL',
        'RPL',
        'As Of'
        ])

#Used a merge between the buy and the sell to see both unrealized and realized profit/loss
'''
pltot = pd.DataFrame(columns=[
        'Ticker',
        'Current Market Price',
        'Position',
        'VWAP',
        'UPL',
        'RPL',
        ])
'''

#Function to number the menu items 1-4 and display them
def display_menu(menu):
    print('\nMain Menu\n')
    for m in menu:
        print(str(menu.index(m) +1) + " - " + m)

#Function to show the tickers  
def Trade(equities):
    print('\n'.join(equities))

#Function to check the ASK and BID prices of the ticker and add to the blotter for each confirmed Buy or Sell
def get_quote(symbol):
    quote_page = 'https://finance.yahoo.com/quote/'+ symbol
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'D(ib)'})
    name = name_box.text.strip() 
    buy_box = soup.find('td', attrs={'data-test': 'ASK-value'})
    buy = buy_box.text
    buy = buy.replace(',', '')
    buy = buy.split('x', 1)[0]
    sell_box = soup.find('td', attrs={'data-test': 'BID-value'})
    sell = sell_box.text
    sell = sell.replace(',', '')
    sell = sell.split('x', 1)[0]
    if trade =='Buy':
        blotter.loc[tradenum] = (['Buy', symbol, int(shares), float(price), pd.to_datetime('now'), round(float(price)*float(shares),2)])
    if trade == 'Sell':
        blotter.loc[tradenum] = (['Sell', symbol, int(shares), float(price), pd.to_datetime('now'), round(float(price)*float(shares),2)])

#Function to calculate the weighted average price for the ticker
#Using the price per share and the number of shares the weighted average is calculated 
#A regular average is displayed if there are no shares
def wavg(group, avg_name, weight_name):
    d = group[avg_name]
    w = group[weight_name]
    try:
        return (d * w).sum() / w.sum()
    except ZeroDivisionError:
        return d.mean()

#Function ran to add the unrealized profit/loss for each buy
#Use bid value (current price) to calculate unrealized profit/loss
def pl_buy(symbol):
    plb = [
        'Ticker',
        'Current Market Price',
        'Position',
        'VWAP',
        'UPL',
        'RPL',
        'Total P/L',
        'As Of'
        ]
    quote_page = 'https://finance.yahoo.com/quote/'+ symbol
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'D(ib)'})
    name = name_box.text.strip() 
    price_box = soup.find('td', attrs={'data-test': 'BID-value'})
    price = price_box.text
    price = price.replace(',', '')
    price = price.split('x', 1)[0]
    
    #Put symbol and price in a data frame to later be use a join to another data frame
    #The idea is to have SQL like tables and join them using the symbol to get all data on a row
    price_buy = pd.DataFrame([[symbol,price]])
    price_buy.columns = ['Ticker', 'Market Price']
    
    #Group by the ticker to get the total number of shares
    #If another buy of the same ticker happens we want to have the total number of shares
    position = blotter[blotter['Action'] == 'Buy'].groupby(['Ticker'])[['Shares']].sum() # use as dataframe and join to vwap 
    position = pd.DataFrame(position).reset_index()
    position.columns = ['Ticker', 'Position']
    
    #Use the wavg function to get the wegihted average by ticker
    #Put ticker and weighted average price in a data frame
    wap = blotter.groupby('Ticker').apply(wavg, 'Price per Share', 'Shares')
    #Weighted avg could also be calculated with numpy using:
    #wap = blotter.groupby(['Ticker']).apply(lambda x: np.average(x[['Price per Share']], weights=x[['Shares']]))
    wap = pd.DataFrame(wap).reset_index()
    wap.columns = ['Ticker', 'WAP']
    
    #Merge the price data frame to the position data frame and place in a new data frame
    price_position = pd.merge(price_buy, position, on='Ticker')
    
    #Merge the price and position data frame to the weighted average data frame and place in a new data frame
    pw = pd.merge(price_position, wap, on='Ticker')
    
    #Calculate the uneralized profit/loss using the position and market price
    url = float(pw['Market Price'])*float(pw['Position'])
    
    #Put ticker, unrealized profit/loss, and realized profit/loss as 0 in a data frame
    url_profit = pd.DataFrame([[symbol,url,'0', url, pd.to_datetime('now')]])
    url_profit.columns = ['Ticker', 'URL','RPL', 'Total P/L','As Of']
    
    #Merge the price data frame with the unrealized profit/loss data frame
    pl_buy = pd.merge(pw, url_profit, on='Ticker')
    
    #Make a profit loss data frame 
    #plb = np.vstack((plb,pl_buy)) 
    plb = df(pl_buy)
    plb.columns=['Ticker','Current Price','Position','VWAP','URL','RPL', 'Total P/L', 'As Of']
    
    #Sort profit and loss by most to least and take the most recent line per ticker
    plb = plb.sort_values(by='As Of')
    plb = plb.drop_duplicates('Ticker', keep='last').values
    plb = df(plb)
    plb.columns=['Ticker','Current Market Price','Position','VWAP','URL','RPL', 'Total P/L','As Of']
    return(plb)

#Run the same function as pl_buy but makes a data frame with realized profit and loss and unrealized = 0
def pl_sell(symbol):
    pls = [
        'Ticker',
        'Current Market Price',
        'Position',
        'VWAP',
        'UPL',
        'RPL',
        'Total P/L',
        'As Of'
        ]
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
    if position.empty==True:
        pls = plb
        return(pls)
    if position.empty==False:
        position = pd.DataFrame(position).reset_index()
        position.columns = ['Ticker', 'Position']
        
        wap = blotter.groupby('Ticker').apply(wavg, 'Price per Share', 'Shares')
        #Weighted avg could also be calculated with numpy using:
        #wap = blotter.groupby(['Ticker']).apply(lambda x: np.average(x[['Price per Share']], weights=x[['Shares']]))
        wap = pd.DataFrame(wap).reset_index()
        wap.columns = ['Ticker', 'WAP']
        
        price_position = pd.merge(price_buy, position, on='Ticker')
        
        pw = pd.merge(price_position, wap, on='Ticker')
        
        rpl = float(pw['Market Price'])*float(pw['Position']) 
        
        url_profit = pd.DataFrame([[symbol,'0',rpl, '0', pd.to_datetime('now')]])
        url_profit.columns = ['Ticker', 'URL','RPL','Total P/L', 'As Of']
        
        pl_sell = pd.merge(pw, url_profit, on='Ticker')
         
        #pls = np.vstack((pls,pl_sell)) 
        pls = df(pl_sell)
        pls.columns=['Ticker','Current Market Price','Position','VWAP','URL','RPL','Total P/L','As Of']
        
        pls = pls.sort_values(by='As Of')
        pls = pls.drop_duplicates('Ticker', keep='last').values
        pls = df(pls)
        pls.columns=['Ticker','Current Market Price','Position','VWAP','URL','RPL','Total P/L','As Of']
        return(pls)

#Merge the pl_buy and pl_sell data frames to get the total unrealized and realized profit/loss
def pl_tot(symbol):
    plb = pl_buy(symbol)
    pls = pl_sell(symbol)
    quote_page = 'https://finance.yahoo.com/quote/'+ symbol
    page = req.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('h1', attrs={'class':'D(ib)'})
    name = name_box.text.strip() 
    price_box = soup.find('td', attrs={'data-test': 'BID-value'})
    price = price_box.text
    price = price.replace(',', '')
    price = price.split('x', 1)[0]
    
    
    #Check if the ticker has been sold and calculate the URL and RPL
    if (symbol in plb[['Ticker']].values) == True and (symbol in pls[['Ticker']].values) ==True:   
        pltot = df([[symbol, 
                   price, 
                   float(plb['Position'])-float(pls['Position']),
                   float(plb['VWAP']), 
                   float(plb['URL'])-float(pls['RPL']),
                   float(pls['RPL']),
                   float(plb['URL'])+float(pls['RPL'])
                   ]])
        pltot.columns=['Ticker','Current Market Price','Position','VWAP','URL','RPL','Total P/L']
        return(pltot)
    #If the ticker has not been sold then use the plb as the totl profit/loss 
    elif (symbol in pls[['Ticker']].values) ==False and (symbol in plb[['Ticker']].values) ==True:
        pltot = plb[['Ticker','Current Market Price', 'Position', 'VWAP', 'URL', 'RPL','Total P/L']]
        return(pltot)

#Start program
done = True

#Program will exit when done = False 
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
            #Check to see if the user has enough cash to buy selected number of shares at ask price
            if buy_confirm == 'Y' and total_price > cash:
                print('\nNot enough money to buy %s \n' %(symbol))
                print('\nTotal Cost: ')
                print(total_price)
                print('\nRemaining Cash: ')
                print(cash)
            if buy_confirm == 'Y' and total_price <= cash:
                tradenum += 1
                #Add the buy to the blotter
                get_quote(symbol)
                #Add the buy to the profit/loss
                pl_buy(symbol)
                #pl_tot(symbol)
                #Remove the total buy from the user's cash
                cash = cash - blotter[blotter['Action'] == 'Buy']['Money In/Out'].sum()
                print('\nBlotter\n')
                print(blotter)
                print('\nRemaining Cash:\n')
                print(round(cash,2))

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
                get_quote(symbol)
                #Add the sell to the profit/loss
                #pl_buy(symbol)
                pl_sell(symbol)
                cash = cash + blotter[blotter['Action'] == 'Sell']['Money In/Out'].sum()
                print('\nBlotter\n')
                print(blotter)
                print('\nRemaining Cash:\n')
                print(round(cash,2))
            if sell_confirm == 'N':
                print('\nDid not sell %s' %(symbol))
    
    elif selected == 2:
        #Show blotter
        print('\nBlotter\n')
        print(blotter)             
   
    elif selected == 3:
        if pltot.empty == False:
            #Run the P/L
            plnum=+1
            pltot = pl_tot(symbol)
            x = pltot['Position'].sum() / pltot['Position']
            prctshare = pd.DataFrame([[symbol,x]])
            prctshare.columns = ['Ticker', '% of Total Shares']
            pltot = pd.merge(pltot, prctshare, on='Ticker')
            print('\nP/L\n')
            print(pltot)
        else:
            #If there's nothing in the P/L 
            print('\nNo P and L yet\n')

        
    elif selected == 4:
        #Exit program
        print('\nThanks')
        done = False
        
    elif selected >4 or selected<1:
        #Only allow users to eneter between 1 and 4
        print('\nPlease enter a valid choice')

'''
            if sell_confirm == 'Y' and (symbol in plb[['Ticker']].values)==False:
                #Checks to see if there is any of the ticker to sell
                print('\nThere is no %s to sell\n' % (symbol))
'''
