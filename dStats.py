""" statistic related calculation functions
    1) findBestCOVs
    2) get1DlgRet
    3) mavg1D
    4) findBestLag
    5) addLagLi
    6) addLagLiHIST
    7) getLgRetWithLag
"""
import stockTickers
import numpy as np
from datetime import datetime
import arrayTools
import dPickle as dpk
import symFunc
import dCalCorr

#---------------------------------------------
def addLagLiHIST(histRealDict):
    # return the real historical lgRet data given shift
    # and sDate and eDate, return value should match y length!
    sShift = 1 # one more day for starting point
    lagN = histRealDict["lagN"]
    tkr = histRealDict["tkr"]
    yDateLi = histRealDict["yDate"]
    yDateLiFull = histRealDict["yDateLiFull"]
    sDate, eDate = yDateLi[0], yDateLi[-1]
    # shift one more day for start to get one more day longer in lgRet
    sDateShiftInd = max(0, np.searchsorted(yDateLiFull, sDate) - lagN-sShift)
    eDateShiftInd = max(0, np.searchsorted(yDateLiFull, eDate) - lagN)
    dataX = arrayTools.alignDataToDateLi([tkr], yDateLiFull[sDateShiftInd:eDateShiftInd+sShift])
    tlistLag = arrayTools.price2LgRet(dataX[symFunc.sym2Colname(tkr)])[sShift:]
    if len(tlistLag) == 0:
        # none available data
        return []
    if len(tlistLag) != len(yDateLi):
        print("tlistLag len:%d, yDateLi len:%d"%(len(tlistLag), len(yDateLi)))
        raise("Length error in listTools.getLagLiHIST()")
    return tlistLag

#---------------------------------------------
def get1DlgRet(sym, tgtDate):
    # return lgRet on target date for a given sym
    # if target date is the last date
    # will return mavg1D(lgRet, N=5) as prediction
    data = dpk.getPickle(sym)
    lgRetLi = arrayTools.price2LgRet(data["adjClose"])
    if tgtDate > data["date"][-1]:
        # last date using mavg5
        lgRet = np.average(lgRetLi[-5:])
    else:
        # target date within list
        ind = np.searchsorted(data["date"], tgtDate)
        lgRet = np.log(data["adjClose"][ind]/data["adjClose"][ind-1])
    return lgRet

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
def getLgRetWithLag(sym, dtLi, lag):
    # return real historical lgRet with lag
    # based on dtLi
    data = dpk.getPickle(sym)
    sDate, eDate = dtLi[0], dtLi[-1]
    sIndLag = np.searchsorted(data["date"], sDate)-lag-1
    eIndLag = np.searchsorted(data["date"], eDate)-lag-1
    lgRet = arrayTools.price2LgRet(data["adjClose"][sIndLag:eIndLag])[1:]
    if len(lgRet)!=len(dtLi):
        raise("length error in dStats.getLgRetWithLag")
    return lgRet

##################################################
##################################################
##################################################
if __name__ == "__main__":
    sDate, eDate = datetime(2021,6,1).date(), datetime(2021,11,1).date()
