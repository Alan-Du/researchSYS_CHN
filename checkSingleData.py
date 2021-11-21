""" some data seems has ugly point
    will be clean here
"""
import dPickle
import pandas as pd
from datetime import datetime

#---------------------------------------------
def dump2Excel(sym, path="C:/Users/shaol/Desktop/stockDownloader/dataCheckTmp/"):
    data = dPickle.getPickle(sym)
    df = pd.DataFrame(data)
    df.to_excel(path+sym+".xlsx")
    return None

#---------------------------------------------
def updatePickleFromExcel(sym, path="C:/Users/shaol/Desktop/stockDownloader/dataCheckTmp/"):
    # fix data using excel ohlcvX
    df = pd.read_excel(path+sym+".xlsx")
    sym = df["sym"].values[0]
    date = [pd.to_datetime(ele).date() for ele in df["date"].values]
    data = {
        "sym":sym,
        "date":date,
        "open":df["open"].values,
        "high":df["high"].values,
        "low":df["low"].values,
        "close":df["close"].values,
        "adjClose":df["adjClose"].values,
        "volume":df["volume"].values}
    dPickle.updatePickle(data, sym, forceUpdate=True)
    return None

##################################################
##################################################
##################################################
if __name__ == "__main__":
    sym = "AU0"
    #dump2Excel(sym)
    #updatePickleFromExcel(sym)