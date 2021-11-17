# -*- coding: utf-8 -*-
"""
Download stock price write stock price into pickle files
@author: Shaolun Du
@contact: Shaolun.du@gmail.com
"""
import math
import os
import pandas as pd
import yfinance as yf
import stockTickers, fxTickers, futTickersUS
import dPickle as dpk
from datetime import datetime

##################################################
##################################################
##################################################
class yahooDownloader():
    """ object downloads stock data and save it into pickle files
        two modes when downloading 1) save new 2) update existing
    """
    #---------------------------------------------
    def __init__(self, tkrNames, savePath):
        self.__log_name = "Error_Log.txt"
        self.__s_tickers = tkrNames
        self.__path = savePath
        self.__error_msg = []
        
    #---------------------------------------------
    def _runTickers(self, start_t, end_t, use_tickers=[]):
        # run all tickers or test run tickers
        self.__s_tickers = use_tickers if len(use_tickers)>0 else self.__s_tickers
        for ticker in self.__s_tickers:
            print("Downloading:%s"%(ticker))
            data = self._download(ticker,start_t,end_t)
            self._savePickle(data,fname=ticker)
        
    #---------------------------------------------
    def _download(self, ticker, start_t, end_t):
        data = yf.download(tickers=ticker, start=start_t, end=end_t)
        data = data.reset_index().to_dict(orient='list')
        dataDict = {
            "sym":ticker,
            "date":[pd.to_datetime(ele).date() for ele in data["Date"]],
            "open":data["Open"],
            "high":data["High"],
            "low":data["Low"],
            "close":data["Close"],
            "adjClose":data["Adj Close"],
            "volume":data["Volume"],
            }
        return dataDict
    
    #---------------------------------------------
    def _savePickle(self, data, fname=""):
        # save new data into pickles
        if os.path.exists(self.__path+fname):
            dpk.updatePickle(data, fname, path=self.__path)
        else:
            dpk.setPickle(data, fname, path=self.__path)
        return None
    
    #---------------------------------------------
    def _writeLog(self):
        with open("Error_MSG.txt", "w") as text_file:
            for msg in self.__error_msg:
                text_file.write(msg)
                text_file.write("\n")
        text_file.close()
    

##################################################
##################################################
##################################################
if __name__ == "__main__":
    testTickers = []
    savepath = "C:/EQdata/"
    #savepath = "C:/FXdata/"
    #savepath = "C:/FUTdataus/"
    tkrNames = stockTickers.stockTickers
    #tkrNames = fxTickers.FX
    #tkrNames = commodityTickersUS.USCOMMODITYALL
    stkr = yahooDownloader(tkrNames, savepath)
    stkr._runTickers("2015-01-01", "2021-11-13", use_tickers=testTickers)
    