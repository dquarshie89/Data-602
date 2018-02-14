# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 15:10:48 2018

@author: dquarshie
"""

import urllib.request as req
from bs4 import BeautifulSoup

equities = ('AAPL','AMZN','Main Menu')
menu = ['Buy','Sell','Show P/L','Show Blotter','Quit']
blotter = [[]]

def display_menu(menu):
    for m in menu:
        print(str(menu.index(m) +1) + " - " + m)
    #print('Choose an option:')

def buy(equities):
    for e in equities:
         print(str(equities.index(e) +1) + " - " + e)
    #print('Pick a stock:')

done = True
while done:
    display_menu(menu)
    selected = input("Enter your choice [1-5]: ")
    if selected == "1" or selected == "Buy":
        print('Buy Menu')
        buy(equities)
        stock = input("Pick a stock: ")
        
    elif selected == "5" or selected == "Quit":
        done = False
        print('Thanks')
        
       
    
        
        


