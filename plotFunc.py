# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import pandas as pd
import dataTools
from datetime import datetime
import futTickers, fxTickers, futTickersUS
import symFunc

#---------------------------------------------
def plotCompare2(dates, pri1, pri2, label1=None, label2=None, title=None, wantShow=True):
    # plot price1 and price2 compare based on date lits
    fig, ax = plt.subplots()
    ax.plot(dates, pri1, label=label1)
    ax.plot(dates, pri2, label=label2)
    # Major ticks every 6 months.
    fmt_half_year = mdates.MonthLocator(interval=1)
    ax.xaxis.set_major_locator(fmt_half_year)
    # Minor ticks every month.
    fmt_month = mdates.MonthLocator()
    ax.xaxis.set_minor_locator(fmt_month)
    # Text in the x axis will be displayed in 'YYYY-mm' format.
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.format_xdata = mdates.DateFormatter('%Y-%m')
    ax.format_ydata = lambda x: f'${x:.2f}'  # Format the price.
    ax.grid(True)
    fig.autofmt_xdate()
    if title: plt.title(title)
    plt.legend()
    if wantShow: plt.show(block=True)
    return fig

#---------------------------------------------
def plotSingle(dates, pri1, label1=None, title=None):
    # plot price1 and price2 compare based on date lits
    fig, ax = plt.subplots()
    ax.plot(dates, pri1, label=label1)
    # Major ticks every 6 months.
    fmt_half_year = mdates.MonthLocator(interval=1)
    ax.xaxis.set_major_locator(fmt_half_year)
    # Minor ticks every month.
    fmt_month = mdates.MonthLocator()
    ax.xaxis.set_minor_locator(fmt_month)
    # Text in the x axis will be displayed in 'YYYY-mm' format.
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.format_xdata = mdates.DateFormatter('%Y-%m')
    ax.format_ydata = lambda x: f'${x:.2f}'  # Format the price.
    ax.grid(True)
    fig.autofmt_xdate()
    if title: plt.title(title)
    plt.legend()
    plt.show()
    return fig

#---------------------------------------------
def plotBars(symPickle, savePath="C:/plots/"):
    # plot candlestick bars
    # df should contain OHLCV
    sym = symPickle["sym"]
    pdDict = { 
        "Date":symPickle["date"],
        "Open":symPickle["open"],
        "High":symPickle["high"],
        "Low":symPickle["low"],
        "Close":symPickle["close"],
        "Volume":symPickle["volume"]
        }
    df = pd.DataFrame(pdDict).set_index("Date")
    df.index = pd.to_datetime(df.index)
    mpf.plot(df,
             mav=(120),
             type='candle',
             volume=True,
             title=sym+"_BAR",
             ylabel='',
             ylabel_lower='',
             savefig=savePath+sym+'_BAR.png'
             )
    #savefig=savePath+sym+'_BAR.png'
    return None

##################################################
##################################################
##################################################
if __name__ == "__main__":
    tkrs = futTickers.COMMODITYALL+fxTickers.FX+futTickersUS.USCOMMODITYALL
    sDate, eDate = datetime(2021,1,1).date(), datetime(2021,11,1).date()
    for sym in tkrs:
        symPickle = symFunc.getSymByDate(sym, sDate, eDate)
        if len(symPickle["date"])==0: continue
        plotBars(symPickle, savePath="C:/plots/BARS/")
    