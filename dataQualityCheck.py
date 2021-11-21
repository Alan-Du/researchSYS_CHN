""" check pickle files data quality
    some data from source are so bad like RU0 and AU0
    also need to check missing dates, if need fill
"""
import futTickers, futTickersUS, fxTickers, stockTickers
import dPickle, plotFunc, arrayTools
from datetime import datetime
import pandas as pd
import numpy as np

#---------------------------------------------
def dateFullLi():
    # merge fut based and stock base date list
    # we assume full date list should be
    # union of SH index and gold future contract
    futBase, stockBase = "AU0", "000001.SZ"
    fDate = dPickle.getPickle(futBase)["date"]
    sDate = dPickle.getPickle(stockBase)["date"]
    return sorted(list(set(fDate+sDate)))

#---------------------------------------------
def checkMissingDates(fullDateLi, tgtDateLi):
    misDate = [ele for ele in fullDateLi if ele not in tgtDateLi]
    return misDate

#---------------------------------------------
def checkSinglePDB(data, retThred=0.15):
    # check single PDB price and plot recent history
    if len(data["date"]) == 0:
        return {"lenERR":-1, "retERR":-1, "priceERR":-1}
    adjClose = data["adjClose"]
    priceERR = list(filter(lambda x: x<=0, adjClose))
    arrayP = np.array(adjClose)
    rets = (arrayP[1:]-arrayP[:-1])/arrayP[:-1]
    retERR = list(filter(lambda x: abs(x)>=retThred, rets))
    lenERR = len(data["adjClose"])==len(data["date"])
    ansDict = {"lenERR":lenERR, "retERR":retERR, "priceERR":priceERR}
    return ansDict

#---------------------------------------------
def plotSingle(data, startDate, endDate=datetime.today().date(), savePath="C:/plots/BARS/"):
    # plot single PDB
    data = arrayTools.sliceDataByDates(data, startDate, endDate)
    plotFunc.plotBars(data, savePath=savePath)
    return None

#---------------------------------------------
def dataCheckLoop(tkrLi, startDate, plotFlag = True):
    ans = []
    fullDateLi = dateFullLi()
    for tkr in tkrLi:
        data = dPickle.getPickle(tkr)
        ckDict = checkSinglePDB(data)
        if ckDict["lenERR"]<0: continue
        ckDict["sym"] = tkr
        misDate = checkMissingDates(fullDateLi, data["date"])
        ckDict["misDate"] = misDate
        ans.append(ckDict)
        if plotFlag: plotSingle(data, startDate)
    df = pd.DataFrame(ans)
    df.to_excel("C:/Users/shaol/Desktop/stockDownloader/dataCheckTmp/dataCheck"+("_0" if plotFlag else "_1")+".xlsx")
    return None

#---------------------------------------------
def pullData2Excel(tgtSym, savePath="C:/Users/shaol/Desktop/stockDownloader/dataCheckTmp/"):
    # pull to excel
    data = dPickle.getPickle(tgtSym)
    df = pd.DataFrame(data)
    df.to_excel(savePath + tgtSym + ".xlsx")
    return None

##################################################
##################################################
##################################################
if __name__ == "__main__":
    startDate = datetime(2019, 1, 1).date()
    alltickers = futTickers.COMMODITYALL + futTickersUS.USCOMMODITYALL+fxTickers.FX
    dataCheckLoop(alltickers, startDate, plotFlag=True)
    alltickers = stockTickers.stockTickers
    dataCheckLoop(alltickers, startDate, plotFlag=False)