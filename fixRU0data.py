""" RU0 data seems ugly wrong
"""
import pandas as pd
import dPickle
from datetime import datetime
# sym = "RU0"
# data = dPickle.getPickle(sym)
# df = pd.DataFrame(data)
# df.to_excel("C:/Users/shaol/Desktop/stockDownloader/RU0.xlsx")
# print(df)
# fix RU0 data using excel
df = pd.read_excel("C:/Users/shaol/Desktop/stockDownloader/RU0.xlsx")
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