""" functions to calculate correlation related functions
"""
import numpy as np
import dPickle as dpk
import arrayTools
import dStats

#---------------------------------------------
def findBestCOVs(tgtData, covTks, yDateLiFull, lagSetDict={}):
    # loop to find top N best correlated covs
    y = arrayTools.price2LgRet(tgtData["adjClose"])
    yDateLi = tgtData["date"]
    corBook = []
    for xnm in covTks:
        slag = lagSetDict.get("slag", 0)
        elag = lagSetDict.get("elag", 10)
        smoothN = lagSetDict.get("smoothN", 0)
        histRealDict={"tkr":xnm,"slag":slag, "elag":elag, "smoothN":smoothN,
                      "yDate":yDateLi, "yDateLiFull":yDateLiFull}
        # always assume using historical real data
        lag,cor = findBestLagHIST(y, histRealDict=histRealDict)
        corBook.append([xnm,lag,cor])
    return corBook

#---------------------------------------------
def findBestLagHIST(y, histRealDict={}):
    # assume inputs are all numpy arrays
    # loop from lag=1 to lag=10
    # find the best lag with highest correlation
    # NOTE: if sDate and yDateLiFull are given, will try to find historical
    # data to shift, otherwise will do flat fill.
    if not (isinstance(y,(np.ndarray, np.generic))
            and isinstance(y,(np.ndarray, np.generic))):
        print("inputs must be np array")
        y = np.array(y)
    smoothN = histRealDict["smoothN"]
    slag, elag = histRealDict["slag"], histRealDict["elag"]
    y = dStats.mavg1D(y, N=smoothN)
    bestLag, bestCorr = 0, 0 # correlation bond is [-1,1]
    for ll in range(slag, elag+1, 2):
        # will use real historical data no front filling!
        histRealDict["lagN"] = ll
        xlag = dStats.addLagLiHIST(histRealDict)
        if len(xlag) == 0:
            # no available data
            continue
        assert len(y)==len(xlag), "findBestLagHIST->Length not match!"
        corr = np.corrcoef(y[ll:], xlag[ll:])[0][1]
        if abs(corr)>abs(bestCorr):
            bestCorr, bestLag = corr, ll
    return bestLag, bestCorr

#---------------------------------------------
def calIndexGivenCorLi(corLi, start, end, yDatesFull):
    # calculate index lgRet given correlation list
    # corLi = [tkr,cor,lag]...
    sumWt = np.sum(np.abs([ele[2] for ele in corLi]))
    yDates = list(filter(lambda x:start<=x<=end, yDatesFull))
    indexArr = None
    for ele in corLi:
        tkr, lag, cor = ele
        wt = cor/sumWt
        xDict = dpk.getPickle(tkr)
        # need shift start by one more day
        startNew = shiftDateByLag(start, yDatesFull, lag+1)
        endNew = shiftDateByLag(end, yDatesFull, lag)
        xadjClose = arrayTools.alignPriceWithY(xDict, startNew, endNew, yDatesFull)
        assert len(xadjClose)==len(yDates)+1, "calIndexGivenCorLi->Length not match!"
        xLgRet = arrayTools.price2LgRet(xadjClose)[1:]
        assert len(xLgRet)==len(yDates), "calIndexGivenCorLi->Length not match!"
        if indexArr is None:
            indexArr = wt * xLgRet
        else:
            indexArr += wt * xLgRet
    return indexArr

#---------------------------------------------
def shiftDateByLag(dt, yDatesFull, lag):
    # shift by lag dates and the dates must in date
    if dt in yDatesFull:
        ind = int(max(0, np.searchsorted(yDatesFull, dt) - lag))
    else:
        ind = int(max(0, np.searchsorted(yDatesFull, dt) - lag - 1))
    return yDatesFull[ind]

#---------------------------------------------
def calIndex1DayLgRetWithCorLi(tgtSym, tDate, corrLi):
    # calculate index lgRet one day given correlation structure
    # the correlated index structure is based on lag factors
    # so for index element need to find the correct date lgret to use!
    # if the covariate lag=0, we need to estimate the next lgret
    # here propose to use mavg(lgret, N=5) but it can change to better one
    sumWt = np.sum(np.abs([ele[2] for ele in corrLi]))
    ansLgRet = 0
    for tkr, lag, cor in corrLi:
        wt = cor / sumWt
        if lag == 0:
            # need estimate next lgret here
            lgRet = arrayTools.est_LgRetMAVG(tkr, tDate, lookback=5)
        else:
            lgRet = arrayTools.get_LgRetDate(tkr, tDate, lag)
        ansLgRet += wt*lgRet
    return ansLgRet
