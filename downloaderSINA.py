# -*- coding: utf-8 -*-
""" Download commodity market data from SINA
"""
import os
import requests
import dString
import dPickle as dpk
import futTickers

##################################################
##################################################
##################################################
class sinaDownloader():
    """ object downloads stock data and save it into pickle files
        two modes when downloading 1) save new 2) update existing
    """
    #---------------------------------------------
    def __init__(self, tkrNames, savePath):
        self.__log_name = "Error_Log.txt"
        self.__s_tickers = tkrNames
        self.__path = savePath
        self.__error_msg = []
        self.__HTML = "https://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol=%s"
        self.__HTMLcff = "https://stock2.finance.sina.com.cn/futures/api/json.php/CffexFuturesService.getCffexFuturesDailyKLine?symbol=%s"

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
        if ticker in ["IF0", "IH0", "IC0", "T0", "TS0", "TF0"]:
            resp = requests.get(self.__HTMLcff % ticker)
        else:
            resp = requests.get(self.__HTML % ticker)
        page = resp.content.decode('utf-8')
        if page is None or len(page)==0 or page == "null":
            print("Cannot get continues data %s return {}"%ticker)
            return {"sym":ticker, "date":[], "open":[], "high":[], "low":[], "close":[], "volume":[]}
        ans = dString.SINAtolist(page)
        dataDict = {"sym":ticker, 
                    "date":[ele[0] for ele in ans], 
                    "open":[ele[1] for ele in ans],
                    "high":[ele[2] for ele in ans], 
                    "low":[ele[3] for ele in ans],
                    "close":[ele[4] for ele in ans], 
                    "adjClose":[ele[4] for ele in ans], 
                    "volume":[ele[5] for ele in ans]}
        return dataDict
    
    #---------------------------------------------
    def _savePickle(self, data, fname=""):
        # save new data into pickles
        if os.path.exists(self.__path+fname):
            print("Will update pickles instead of create...%s"%fname)
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
    savepath = "C:/FUTdata/"
    tkrNames = futTickers.BOND0+futTickers.INDEX
    stkr = sinaDownloader(tkrNames, savepath)
    stkr._runTickers("2015-01-01", "2021-11-16", use_tickers=testTickers)