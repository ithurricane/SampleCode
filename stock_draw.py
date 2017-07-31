#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***********************************************************************************
"""
Sample :
python stock_draw.py 6734 D:\Dev\stockdb\ipagp.ttf
"""
#twitter : @ithurricanept
#***********************************************************************************

from __future__ import unicode_literals
import time, os, sys, datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, MonthLocator, DayLocator, MONDAY
from matplotlib.finance import candlestick2_ochl, volume_overlay
from matplotlib import gridspec
from matplotlib.dates import num2date, IndexDateFormatter
from matplotlib.ticker import  IndexLocator, FuncFormatter
from matplotlib.font_manager import FontProperties
from matplotlib.dates import date2num, AutoDateFormatter, AutoDateLocator
from operator import itemgetter
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from urllib2 import urlopen
import urllib2
import pandas_datareader._utils as web
from pykdb.core import Stocks, KDBError
import datetime
import time
import matplotlib.dates as mdates


#MACD, MACD Signal and MACD difference
def MACD(df, n_fast, n_slow):
    #EMAfast = pd.Series(pd.ewma(df['Close'], span = n_fast, min_periods = n_slow - 1))
    EMAfast = pd.Series(df['Close']).ewm(ignore_na=False, span=n_fast, min_periods=n_slow - 1, adjust=True).mean()
    #EMAslow = pd.Series(pd.ewma(df['Close'], span = n_slow, min_periods = n_slow - 1))
    EMAslow = pd.Series(df['Close']).ewm(ignore_na=False, span=n_slow, min_periods=n_slow - 1, adjust=True).mean()
    MACD = pd.Series(EMAfast - EMAslow, name = 'MACD_' + str(n_fast) + '_' + str(n_slow))
    #MACDsign = pd.Series(pd.ewma(MACD, span = 9, min_periods = 8), name = 'MACDsign_' + str(n_fast) + '_' + str(n_slow))
    MACDsign = pd.Series(MACD, name='MACDsign_' + str(n_fast) + '_' + str(n_slow)).ewm(ignore_na=False, span=9, min_periods=8, adjust=True).mean()
    MACDdiff = pd.Series(MACD - MACDsign, name = 'MACDdiff_' + str(n_fast) + '_' + str(n_slow))
    df = df.join(MACD)
    df = df.join(MACDsign)
    df = df.join(MACDdiff)
    return df

#Relative Strength Index
def RSI(df, n):
    i = 0
    UpI = [0]
    DoI = [0]
    while i + 1 <= df.index[-1]:
        UpMove = df.get_value(i + 1, 'High') - df.get_value(i, 'High')
        DoMove = df.get_value(i, 'Low') - df.get_value(i + 1, 'Low')
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else: UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else: DoD = 0
        DoI.append(DoD)
        i = i + 1
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    #PosDI = pd.Series(pd.ewma(UpI, span = n, min_periods = n - 1))
    PosDI = pd.Series(UpI).ewm(adjust=True,ignore_na=False,min_periods=n-1,span=n).mean()
    #NegDI = pd.Series(pd.ewma(DoI, span = n, min_periods = n - 1))
    NegDI = pd.Series(DoI).ewm(adjust=True, ignore_na=False, min_periods=n-1, span=n).mean()
    RSI = pd.Series(PosDI / (PosDI + NegDI), name = 'RSI_' + str(n))
    df = df.join(RSI)
    return df

#True Strength Index
def TSI(df, r, s):
    M = pd.Series(df['Close'].diff(1))
    aM = abs(M)
    #EMA1 = pd.Series(pd.ewma(M, span = r, min_periods = r - 1))
    EMA1 = pd.Series(M).ewm(adjust=True,ignore_na=False,min_periods=r-1,span=r).mean()
    #aEMA1 = pd.Series(pd.ewma(aM, span = r, min_periods = r - 1))
    aEMA1 = pd.Series(aM).ewm(adjust=True,ignore_na=False,min_periods=r-1,span=r).mean()
    #EMA2 = pd.Series(pd.ewma(EMA1, span = s, min_periods = s - 1))
    EMA2 = pd.Series(EMA1).ewm(adjust=True,ignore_na=False,min_periods=s-1,span=s).mean()
    #aEMA2 = pd.Series(pd.ewma(aEMA1, span = s, min_periods = s - 1))
    aEMA2 = pd.Series(aEMA1).ewm(adjust=True,ignore_na=False,min_periods=s-1,span=s).mean()
    TSI = pd.Series(EMA2 / aEMA2, name = 'TSI_' + str(r) + '_' + str(s))
    df = df.join(TSI)
    return df

def get_quote_yahoojp(code, start=None, end=None, interval='d'):
    base = 'http://info.finance.yahoo.co.jp/history/?code={0}.T&{1}&{2}&tm={3}&p={4}'
    start, end = web._sanitize_dates(start, end)
    start = 'sy={0}&sm={1}&sd={2}'.format(start.year, start.month, start.day)
    end = 'ey={0}&em={1}&ed={2}'.format(end.year, end.month, end.day)
    p = 1
    results = []

    if interval not in ['d', 'w', 'm', 'v']:
        raise ValueError("Invalid interval: valid values are 'd', 'w', 'm' and 'v'")

    while True:
        url = base.format(code, start, end, interval, p)
        tables = pd.read_html(url, header=0)
        if len(tables) < 2 or len(tables[1]) == 0:
            break
        results.append(tables[1])
        p += 1
    result = pd.concat(results, ignore_index=True)
    result.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
    if interval == 'm':
        result['Date'] = pd.to_datetime(result['Date'], format='%Y年%m月')
    else:
        result['Date'] = pd.to_datetime(result['Date'], format='%Y年%m月%d日')
    #result = result.set_index('Date')
    #result = result.sort_index()
    result = result.sort_values(by=['Date'])
    return result

def get_stock_name(code, contry):
    name = code
    if contry == 'jp' or contry == 'japan':
        base = 'http://info.finance.yahoo.co.jp/history/?code={0}'
        url = base.format(code)
        tables = pd.read_html(url, header=0)
        name = tables[0].columns[0]
    elif contry == 'cn' or contry == 'china':
        if code[-2:] == 'ss':
            code2 = 'sh' + code[0:-3]
        elif code[-2:] == 'sz':
            code2 = 'sz' + code[0:-3]

        url = 'http://hq.sinajs.cn/?list=%s' % code2
        req = urllib2.Request(url)
        content = urlopen(req).read()
        str = content.decode('gbk')
        data = str.split('"')[1].split(',')
        name = "%-6s" % data[0]

    return name

def movavg(s, n):
    """
    returns an n period moving average for the time series s

    s is a list ordered from oldest (index 0) to most recent (index -1)
    n is an integer

        returns a numeric array of the moving average

    See also ema in this module for the exponential moving average.
    """
    s = np.array(s)
    c = np.cumsum(s)
    return (c[n-1:] - c[:-n+1]) / float(n-1)

def get_locator():

    """

    the axes cannot share the same locator, so this is a helper

    function to generate locators that have identical functionality

    """

    return IndexLocator(10, 1)


def millions(x, pos):

    'The two args are the value and tick position'

    return '%1.1fM' % (x*1e-6)



def thousands(x, pos):

    'The two args are the value and tick position'

    return '%1.1fK' % (x*1e-3)

def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
    x = np.asarray(x)
    if type == 'simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()

    a = np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a

def moving_average_convergence(x, nslow=26, nfast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = moving_average(x, nslow, type='exponential')
    emafast = moving_average(x, nfast, type='exponential')
    return emaslow, emafast, emafast - emaslow

if __name__ == '__main__':
    print sys.argv[:]

    if len(sys.argv) < 3 :
        print "Usage : python stock_draw.py code fontpath."
        print "eg : python stock_draw.py 6734 D:\Dev\stockdb\ipagp.ttf"
        raise SystemExit

    symbol = sys.argv[1]
    contry = 'jp'
    fontpath = sys.argv[2]

    # (Year, month, day) tuples suffice as args for quotes_historical_yahoo
    sd = datetime.datetime(2017, 4, 1)
    ed = datetime.date.today()
    start = '2017-02-01'

    inst = Stocks()

    #quotes = quotes_historical_yahoo_ochl(symbol, date1, date2)
    df = inst.price(sd, ed, symbol+'-T', '1d')

    if len(df) == 0:
        raise SystemExit

    opens = df[u'始値']
    closes = df[u'終値']
    highs = df[u'高値']
    lows = df[u'安値']
    volumes = df[u'出来高']

    #ds, opens, closes, highs, lows, volumes = zip(*quotes)

    days = len(closes)

    '''
    idx = pd.Index(closes)
    vales = np.arange(len(idx)).astype(float)
    s = Series(vales, index=idx)

    # SMA EMA
    sma5 = pd.rolling_mean(s, window=5)
    sma5 = sma5.dropna()
    ewma = pd.stats.moments.ewma
    ewma5 = ewma(s, span=5)
    ewma25 = ewma(s, span=25)

    #ewma25 = ewma25.dropna()
    #ax0.plot(pd.rolling_mean(s, window=25),'b.',label='SMA(p,25)')
    #plt.plot(ewma25,label="EMA25")
    #plt.setp( plt.gca().get_xticklabels(),rotation=90, horizontalalignment='left')
    # SMA5  SMA25
    # sma5 = pd.rolling_mean(stock_tse['Adj Close'], window=5)
    # ma5 = moving_average(closes2, 5, type='simple')
    # ma25 = moving_average(closes2, 25, type='simple')
   '''

    stockname = get_stock_name(symbol, contry)
    stockname = symbol + stockname

    stock_tse = get_quote_yahoojp(symbol, start=start)
    sma5 = pd.rolling_mean(stock_tse['Adj Close'], window=5)
    sma5 = sma5.dropna()
    ewma = pd.stats.moments.ewma
    ewma5 = ewma(stock_tse['Adj Close'], span=5)
    ewma25 = ewma(stock_tse['Adj Close'], span=25)
    ewma25 = ewma25.dropna()

    ma5 = np.array(ewma5).astype(float)
    ma25 = np.array(ewma25).astype(float)

    ma5 = ma5[-days:]
    ma25 = ma25[-days:]

    #fig = plt.figure(figsize=(8, 6))
    #fp = FontProperties(fname=r'D:\Dev\stockdb\ipagp.ttf')
    fp = FontProperties(fname=fontpath)

    fig = plt.figure()
    fig.subplots_adjust(bottom=0.15)
    fig.subplots_adjust(hspace=0)

    fig.suptitle(stockname, fontproperties=fp, fontsize=24, fontweight='bold')

    gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
    ax0 = plt.subplot(gs[0])

    candles = candlestick2_ochl(ax0, opens, closes, highs, lows, width=1, colorup='blue',colordown='r')
    textsize = 8        # size for axes text

    left, height, top = 0.025, 0.06, 0.9
    t1 = ax0.text(left, top, '%s daily'%symbol, fontsize=textsize,
                   transform=ax0.transAxes)
    t2 = ax0.text(left, top-height, 'EMA(5)', color='b', fontsize=textsize, transform=ax0.transAxes)
    t3 = ax0.text(left, top-2*height, 'EMA(25)', color='r', fontsize=textsize, transform=ax0.transAxes)

    s = '%s O:%1.2f H:%1.2f L:%1.2f C:%1.2f, V:%1.1fM Chg:%+1.2f' %(
        time.strftime('%d-%b-%Y'),
        opens[-1], highs[-1],
        lows[-1], closes[-1],
        volumes[-1]*1e-6,
        closes[-1]-opens[-1])
    t5 = ax0.text(0.4, top, s, fontsize=textsize, transform=ax0.transAxes)

    ax0.plot(ma5, color='b', lw=2)
    ax0.plot(ma25, color='r', lw=2)

    ax0.legend(loc='best')
    ax0.set_ylabel(u'株価', fontproperties = fp, fontsize=16)

    #ax0.xaxis_date()
    #ax0.autoscale_view()

    ax1 = plt.subplot(gs[1], sharex=ax0)

    #vc = volume_overlay3(ax1, quotes, colorup='k', colordown='r', width=4, alpha=1.0)
    #volume_overlay(ax1, opens, closes, volumes, colorup='g', alpha=0.5, width=1)
    #ax1.set_xticks(ds)

    vc = volume_overlay(ax1, opens, closes, volumes, colorup='g', alpha=0.5, width=1)
    ax1.add_collection(vc)

    inxval = mdates.date2num(closes.index.to_pydatetime())
    formatter = IndexDateFormatter(inxval, '%Y-%m-%d')
    millionformatter = FuncFormatter(millions)
    thousandformatter = FuncFormatter(thousands)

    ax1.xaxis.set_major_locator(get_locator())
    ax1.xaxis.set_major_formatter(formatter)
    ax1.yaxis.set_major_formatter(millionformatter)
    ax1.yaxis.tick_right()
    ax1.set_ylabel(u'出来高', fontproperties = fp, fontsize=16)

    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.setp(ax1.get_xticklabels(), rotation=30, horizontalalignment='right')
    plt.legend(prop = fp);

    plt.show()
