""" array manipulation related functions most of them are
    slicing dictionary, align dictionary etc...
"""
import numpy as np
import stockTickers
import dPickle as dpk
from collections import defaultdict
import symFunc

#---------------------------------------------
def alignData2StockIndex(sDate, eDate, tkrsLi):
    # retrun date aligned dictionary 
    # basecase is always shanghai index
    idxName = stockTickers.SHindex[0]
    dataYDate = dpk.getPickle(idxName)["date"]
    dtLi = [ele for ele in dataYDate if ele>=sDate and ele<=eDate]
    tkrsData = [dpk.getPickle(name) for name in tkrsLi]
    combData = defaultdict(list)
    for dt in dtLi:
        combData["date"].append(dt)
        for tkrdata in tkrsData:
            sym = tkrdata["sym"].split(".")[0]
            pName, vName = sym+"Pri", sym+"Vlm"
            if dt in tkrdata["date"]:
                ind = np.searchsorted(tkrdata["date"], dt)
                combData[pName].append(tkrdata["adjClose"][ind])
                combData[vName].append(tkrdata["volume"][ind])
            else:
                # stale data could be stop trading
                combData[pName].append(combData[pName][-1])
                combData[vName].append(combData[vName][-1])
    return combData

#---------------------------------------------
def alignDataToYdata(tkrsLi, Ydata, path=None):
    # return data aligned to Y data date list
    # if missing date will use the previous date to fill
    tkrsData = [dpk.getPickle(name, path=path) for name in tkrsLi]
    combData = defaultdict(list)
    for dt in Ydata["date"]:
        combData["date"].append(dt)
        for tkrdata in tkrsData:
            sym = tkrdata["sym"].split(".")[0]
            pName, vName = sym+"Pri", sym+"Vlm"
            if dt in tkrdata["date"]:
                ind = np.searchsorted(tkrdata["date"], dt)
                combData[pName].append(tkrdata["adjClose"][ind])
                combData[vName].append(tkrdata["volume"][ind])
            elif len(combData[pName])==0:
                # mean start date is holiday or missing data
                continue
            else:
                # stale data could be stop trading
                combData[pName].append(combData[pName][-1])
                combData[vName].append(combData[vName][-1])
            #print("Align %s, pLen:%d, vLen:%d"%(tkrdata["sym"],len(combData[pName]),len(combData[vName])))
    return combData

#---------------------------------------------
def alignPriceWithY(xdata, start, end, yDatesFull):
    # create xdate align with yDates
    xDates = list(filter(lambda x: start<=x<=end, yDatesFull))
    priceLi = []
    for dt in xDates:
        ind = np.searchsorted(xdata["date"], dt)
        priceLi.append(xdata["adjClose"][ind])
    return np.array(priceLi)

#---------------------------------------------
def alignDataWithY(sDate, eDate, tkrsLi, Ydata):
    # retrun date aligned dictionary 
    # basecase is always shanghai index
    idxName = stockTickers.SHindex[0]
    dataYDate = dpk.getPickle(idxName)["date"]
    dtLi = [ele for ele in dataYDate if ele>=sDate and ele<=eDate]
    tkrsData = [dpk.getPickle(name) for name in tkrsLi] + [Ydata]
    combData = defaultdict(list)
    for dt in dtLi:
        combData["date"].append(dt)
        for tkrdata in tkrsData:
            sym = tkrdata["sym"].split(".")[0]
            pName, vName = sym+"Pri", sym+"Vlm"
            if dt in tkrdata["date"]:
                ind = np.searchsorted(tkrdata["date"], dt)
                combData[pName].append(tkrdata["adjClose"][ind])
                combData[vName].append(tkrdata["volume"][ind])
            else:
                # stale data could be stop trading
                combData[pName].append(combData[pName][-1])
                combData[vName].append(combData[vName][-1])
            #print("Align %s, pLen:%d, vLen:%d"%(tkrdata["sym"],len(combData[pName]),len(combData[vName])))
    return combData

#---------------------------------------------
def alignDataToDateLi(tkrsLi, dtLi, path=None):
    # return data aligned to Y data date list
    # if missing date will use the previous date to fill
    tkrsData = [dpk.getPickle(name, path=path) for name in tkrsLi]
    combData = defaultdict(list)
    for dt in dtLi:
        combData["date"].append(dt)
        for tkrdata in tkrsData:
            sym = tkrdata["sym"].split(".")[0]
            pName, vName = sym+"Pri", sym+"Vlm"
            if dt in tkrdata["date"]:
                ind = np.searchsorted(tkrdata["date"], dt)
                combData[pName].append(tkrdata["adjClose"][ind])
                combData[vName].append(tkrdata["volume"][ind])
            elif len(combData[pName]) == 0:
                # mean start date is holiday or missing data
                # flat price the first missing point
                combData[pName].append(tkrdata["adjClose"][0])
                combData[vName].append(tkrdata["volume"][0])
                continue
            else:
                # stale data could be stop trading
                combData[pName].append(combData[pName][-1])
                combData[vName].append(combData[vName][-1])
    return combData

#---------------------------------------------
def sliceDataByDates(dataDict, sdate, edate):
    ansDict = {"sym":dataDict["sym"],"date":[],"adjClose":[],
               "open":[],"close":[],"high":[],"low":[],"volume":[]}
    tgtDates = filter(lambda x:sdate<=x<=edate, dataDict["date"])
    for dt in tgtDates:
        ansDict["date"].append(dt)
        ind = np.searchsorted(dataDict["date"], dt)
        for coln in ["open","high","low","close","adjClose","volume"]:
            ansDict[coln].append(dataDict[coln][ind])
    for coln in ["date","open","high","low","close","adjClose","volume"]:
        ansDict[coln] = np.array(ansDict[coln])
    return ansDict

#---------------------------------------------
def cutOffExtremeN(dataLi, N):
    # cutoff extreme N values
    return sorted(dataLi)[N:len(dataLi)-N]

#---------------------------------------------
def cutOffExtremeNwtVlm(retLi, pLi, vLi, N):
    # cutoff extreme N values weighted by money volume
    mVlm = [e1*e2 for e1,e2 in zip(pLi,vLi)]
    temp = sorted(zip(retLi,mVlm), key=lambda x:x[0])[N:len(retLi)-N]
    totalmVlm = sum([ele[1] for ele in temp])
    return [e1*e2/totalmVlm for e1,e2 in temp]

#---------------------------------------------
def cutOffExtremeNwtVlmPct(retLi, pLi, vLi, pct):
    # only keep the midle pct% ones
    N = len(retLi)
    ll = int(N*pct)+1
    mVlm = [e1*e2 for e1,e2 in zip(pLi,vLi)]
    sInd, eInd = max(0,(N-ll)//2-1), min(N,(N+ll)//2)
    temp = sorted(zip(retLi,mVlm), key=lambda x:x[0])[sInd:eInd]
    totalmVlm = sum([ele[1] for ele in temp])
    return [e1*e2/totalmVlm for e1,e2 in temp]

#---------------------------------------------
def lgRet2Price(lgRetLi):
    # log return to price list
    if (isinstance(lgRetLi, (np.ndarray, np.generic)) or
            isinstance(lgRetLi, (np.ndarray, np.generic))):
        lgRetLi = [ele for ele in lgRetLi]
    return np.exp(np.cumsum([0]+lgRetLi))

#---------------------------------------------
def price2LgRet(priLi):
    # log return to price list
    pArr = np.array(priLi)
    ans = np.log(pArr[1:]/pArr[:-1])
    ans = np.concatenate((np.array([0]), ans))
    return ans

#---------------------------------------------
def sliceYDates(tgtSym, sdate, edate):
    # slice and return tgtSym dates with date range
    Ydates = dpk.getPickle(tgtSym)["date"]
    return filter(lambda x:sdate<=x<=edate, Ydates)

#---------------------------------------------
def est_LgRetMAVG(tkr, tDate, lookback=5):
    # log return to price list
    data = dpk.getPickle(tkr)
    ind = np.searchsorted(data["date"], tDate)
    pSlice = data["adjClose"][ind-lookback-1:ind]
    estLgRet = np.mean(price2LgRet(pSlice)[1:])
    return estLgRet

#---------------------------------------------
def get_LgRetDate(tkr, tDate, lag):
    # get real historical lgRet
    data = dpk.getPickle(tkr)
    ind = max(0, np.searchsorted(data["date"], tDate)-lag)
    if ind == 0:
        lgRet = 0
    else:
        lgRet = np.log(data["adjClose"][ind]/data["adjClose"][ind-1])
    return lgRet
