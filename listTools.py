# -*- coding: utf-8 -*-
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
def sliceDataByDates(dataDict, sdate, edate):
    ansDict = {"sym":dataDict["sym"],"date":[],"adjClose":[],
               "open":[],"close":[],"high":[],"low":[],"volume":[]}
    for dt in dataDict["date"]:
        if sdate<=dt<=edate:
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
    lgRetLi = [0]+lgRetLi
    return np.exp(np.cumsum(lgRetLi))

#---------------------------------------------
def price2LgRet(priLi):
    # log return to price list
    pArr = np.array(priLi)
    ans = np.log(pArr[1:]/pArr[:-1])
    ans = np.concatenate((np.array([0]), ans))
    return ans

#---------------------------------------------
def mavg1D(arrx, N=1):
    # return moving average 1D with window=N
    # will flat the first n points
    # return size is equal to input size
    if not isinstance(arrx,(np.ndarray, np.generic)):
        arrx = np.array(arrx)
    if N<=0: return arrx
    arrx = np.concatenate((np.ones(N)*arrx[0],arrx))
    ret = np.cumsum(arrx, dtype=float)
    ret[N:] = (ret[N:] - ret[:-N])/N
    return ret[N:]

#---------------------------------------------
def findBestLag(y, x, slag=0, elag=10, smoothN=0, histRealDict={}):
    # assume inputs are all numpy arrays
    # loop from lag=1 to lag=10
    # find the best lag with highest correlation
    # NOTE: if sDate and yDateLiFull are given, will try to find historical
    # data to shift, otherwise will do flat fill.
    if not (isinstance(y,(np.ndarray, np.generic)) \
            and isinstance(y,(np.ndarray, np.generic))):
        print("inputs must be np array")
        y,x = np.array(y),np.array(x)
    y,x = mavg1D(y,N=smoothN), mavg1D(x,N=smoothN)
    bestLag, bestCorr = 0, 0 # correlation bond is [-1,1]
    for ll in range(slag, elag+1, 2):
        if not histRealDict["useRealDate"]:
            xlag = addLagLi(x, ll) # lag shift fill flat
        else:
            # will use real historical data no front filling!
            histRealDict["lagN"] = ll
            xlag = getLagLiHIST(histRealDict)
        corr = np.corrcoef(y[ll:], xlag[ll:])[0][1]
        if abs(corr)>abs(bestCorr):
            bestCorr,bestLag = corr,ll
    return bestLag,bestCorr

#---------------------------------------------
def addLagLi(tlist, lagN):
    # apply lag and flat the front end
    # when calculate correlation
    # we will cut off those flat points
    if not isinstance(tlist,(np.ndarray, np.generic)):
        tlist = np.array(tlist)
    if lagN==0: return tlist
    # no real historical dates given
    # use flat starting points to fill
    tlistLag = np.concatenate((np.ones(lagN)*tlist[0],tlist[:-lagN]))
    return tlistLag

#---------------------------------------------
def getLagLiHIST(histRealDict):
    # return the real historical lgRet data given shift
    # and sDate and eDate, return value should match y length!
    lagN = histRealDict["lagN"]
    tkr = histRealDict["tkr"]
    yDateLi = histRealDict["yDate"]
    yDateLiFull = histRealDict["yDateLiFull"]
    sDate, eDate = yDateLi[0], yDateLi[-1]
    sDateShiftInd = max(0, np.searchsorted(yDateLiFull, sDate) - lagN)
    eDateShiftInd = max(0, np.searchsorted(yDateLiFull, eDate) - lagN)
    dataX = alignDataToDateLi([tkr], yDateLiFull[sDateShiftInd:eDateShiftInd + 1])
    tlistLag = price2LgRet(dataX[symFunc.sym2Colname(tkr)])
    if len(tlistLag) != len(yDateLi):
        raise("Length error in listTools.getLagLiHIST()")
    return tlistLag

##################################################
##################################################
##################################################
if __name__ == "__main__":
    x = np.array([1,3,6,9,10])
    print(mavg1D(x,N=1))
    print(mavg1D(x,N=2))
    print(mavg1D(x,N=3))
