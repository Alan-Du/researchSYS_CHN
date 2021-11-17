# -*- coding: utf-8 -*-
import stockTickers
import numpy as np
from datetime import datetime
import listTools
import dPickle as dpk
import symFunc

#---------------------------------------------
def calIndexV1(combData, N=2):
    # calculate user defined sector index
    # method 1: cut off highest and lowest lgRet
    priCols = [ele for ele in combData.keys() if "Pri" in ele]
    ansLgRet = []
    for loc in range(1, len(combData["date"])):
        lgRetLi = [np.log(combData[pc][loc]/combData[pc][loc-1]) for pc in priCols]
        lgRetLi = listTools.cutOffExtremeN(lgRetLi, N)
        ansLgRet.append(np.average(lgRetLi))
    return listTools.lgRet2Price(ansLgRet)

#---------------------------------------------
def calIndexV2(combData, N=1):
    # calculate user defined sector index
    # method 2: cut off highest and lowest lgRet weighted by money volume
    priCols = sorted([ele for ele in combData.keys() if "Pri" in ele])
    vlmCols = sorted([ele for ele in combData.keys() if "Vlm" in ele])
    ansLgRet = []
    for loc in range(1, len(combData["date"])):
        lgRetLi = [np.log(combData[pc][loc]/combData[pc][loc-1]) for pc in priCols]
        priLi = [combData[pc][loc] for pc in priCols]
        vlmLi = [combData[vm][loc] for vm in vlmCols]
        lgRetLi = listTools.cutOffExtremeNwtVlm(lgRetLi, priLi, vlmLi, N)
        ansLgRet.append(np.average(lgRetLi))
    return listTools.lgRet2Price(ansLgRet)

#---------------------------------------------
def calIndexV3(combData, pct=0.3):
    # calculate user defined sector index
    # method 2: cut off highest and lowest lgRet weighted by money volume
    priCols = sorted([ele for ele in combData.keys() if "Pri" in ele])
    vlmCols = sorted([ele for ele in combData.keys() if "Vlm" in ele])
    ansLgRet = []
    for loc in range(1, len(combData["date"])):
        lgRetLi = [np.log(combData[pc][loc]/combData[pc][loc-1]) for pc in priCols]
        priLi = [combData[pc][loc] for pc in priCols]
        vlmLi = [combData[vm][loc] for vm in vlmCols]
        lgRetLi = listTools.cutOffExtremeNwtVlmPct(lgRetLi, priLi, vlmLi, pct)
        ansLgRet.append(np.average(lgRetLi))
    return listTools.lgRet2Price(ansLgRet)

#---------------------------------------------
def findBestCOVs(tgtData, covTks, combData, yDateLiFull, lagSetDict={}):
    # loop to find top N best correlated covs
    y = listTools.price2LgRet(tgtData["adjClose"])
    yDateLi = tgtData["date"]
    corBook = []
    for xnm in covTks:
        xRaw = combData[symFunc.sym2Colname(xnm)]
        xLgRet = listTools.price2LgRet(xRaw)
        if len(xRaw) <= 1: continue
        if len(xLgRet) != len(y):
            print("Checking sym:%s, yLen:%d, xLen:%d, xRawLen:%d"%\
                  (xnm,len(y),len(xLgRet),len(xRaw)))
            raise("ERROR...")
        slag = lagSetDict.get("slag", 0)
        elag = lagSetDict.get("elag", 10)
        smoothN = lagSetDict.get("smoothN", 0)
        histRealDict={"tkr":xnm, "yDate":yDateLi, "yDateLiFull":yDateLiFull}
        lag,cor = listTools.findBestLag(y, xLgRet, histRealDict=histRealDict,
                                        slag=slag, elag=elag, smoothN=smoothN, )
        # function signature: findBestLag(y, x, slag=0, elag=10, smoothN=0)
        corBook.append([xnm,lag,cor])
    return corBook

#---------------------------------------------
def getIndexLgRet(sdate, edate, corList):
    # something wrong here need to add lag
    # then cut not cut then add lag!
    # calculate index lgret
    covData = listTools.alignData(sdate, edate, [ele[0] for ele in corList])
    sumWgts = sum([ele[2] for ele in corList])
    indexLgRet = []
    for tk in corList:
        sym, lag, cor = tk
        colN = symFunc.sym2Colname(sym)
        lgRetX = listTools.price2LgRet(covData[colN])
        lagX = listTools.addLagLi(lgRetX, lag)
        wgts = cor/sumWgts
        if len(indexLgRet) == 0:
            indexLgRet = lagX*wgts
        else:
            indexLgRet += lagX*wgts
    return indexLgRet, covData["date"]

#---------------------------------------------
def get1DlgRet(sym, tgtDate):
    # return lgRet on target date for a given sym
    # if target date is the last date
    # will return mavg1D(lgRet, N=5) as prediction
    data = dpk.getPickle(sym)
    lgRetLi = listTools.price2LgRet(data["adjClose"])
    if tgtDate > data["date"][-1]:
        # last date using mavg5
        lgRet = np.average(lgRetLi[-5:])
    else:
        # target date within list
        ind = np.searchsorted(data["date"], tgtDate)
        lgRet = np.log(data["adjClose"][ind]/data["adjClose"][ind-1])
    return lgRet

##################################################
##################################################
##################################################
if __name__ == "__main__":
    sDate, eDate = datetime(2021,6,1).date(), datetime(2021,11,1).date()
    tkrsLi = stockTickers.GOLD
    combData = listTools.alignData(sDate, eDate, tkrsLi)
    indexLi = calIndexV2(combData, N=2)
    import matplotlib.pyplot as plt
    plt.plot(indexLi)
    plt.show()