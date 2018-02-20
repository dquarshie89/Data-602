import urllib.request as req
import pandas as pd
import numpy as np
import datetime as dt
from bs4 import BeautifulSoup


pl = pd.DataFrame(columns=['Ticker','Current Price','Position','VWAP','URL','RPL'])

#pl = pl.set_index('Ticker')
'''
pl = []
pl.columns = ['Ticker', 'Market Price', 'Position', 'WAP', 'URL', 'RPL']
'''
symbol ='A'

def wavg(group, avg_name, weight_name):
    """ http://stackoverflow.com/questions/10951341/pandas-dataframe-aggregate-function-using-multiple-columns
    In rare instance, we may not have weights, so just return the mean
    """
    d = group[avg_name]
    w = group[weight_name]
    try:
        return (d * w).sum() / w.sum()
    except ZeroDivisionError:
        return d.mean()

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
#price_buy = price_buy.reset_index(level='Ticker')
price_buy = pd.DataFrame(price_buy).reset_index(drop=True) 
price_buy.columns = ['Ticker', 'Current Price']

'''
position = blotter.groupby(['Ticker'])[['Shares']].sum() # use as dataframe and join to vwap 
position = pd.DataFrame(position).reset_index()
position.columns = ['Ticker', 'Position']

wap = blotter.groupby('Ticker').apply(wavg, 'Price per Share', 'Shares')
#wap = blotter.groupby(['Ticker']).apply(lambda x: np.average(x[['Price per Share']], weights=x[['Shares']]))
wap = pd.DataFrame(wap).reset_index()
wap.columns = ['Ticker', 'VWAP']

price_position = pd.merge(price_buy, position, on='Ticker')

pw = pd.merge(price_position, wap, on='Ticker')

url = float(pw['Current Price'])*float(pw['Position'])

url_profit = pd.DataFrame([[symbol,url,'0']])
url_profit.columns = ['Ticker', 'URL','RPL']

plb = pd.merge(pw, url_profit, on='Ticker')
#plb = pd.DataFrame(plb).reset_index()
plb.columns=['Ticker','Current Price','Position','VWAP','URL','RPL']
'''
#plb = plb.set_index('Ticker')
#pl = pd.concat([pl, plb], axis=0)
print(price_buy)
#print(pl)
#print(plb)
#pl.loc[1] = ([plb])

#pl = ([plb])
# pd.DataFrame([[k[0], k[1], v.split()[1]] for k,v in d.items()], columns=['id','Name','Value'])
'''
ticker = pl_buy['Ticker']
mp = pl_buy['Market Price']
pos = pl_buy['Position']
vwap = pl_buy['WAP']
unreal = pl_buy['URL']
real = pl_buy['RPL']
'''
#print(pl_buy)

#pl = ('1',ticker,mp,pos,vwap,unreal,'0')
