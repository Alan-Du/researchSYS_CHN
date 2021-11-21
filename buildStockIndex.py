# -*- coding: utf-8 -*-
""" functions to build stock index correlated to commodity price
    for each stock in pool, we search for a best lag factor 
    then we select top three best predictor with lag
    we want covariates align with target symbol and select
    the top most N covariates to simulate target symbol
"""
import numpy as np
import dPickle as dpk
import dStats
import arrayTools
import stockTickers
from datetime import datetime
import plotFunc as pltF
import symFunc
import dCalCorr

FUTEQmap = {
    # METALS
    "AU0":stockTickers.METAL,"AG0":stockTickers.METAL,"CU0":stockTickers.METAL,
    "AL0":stockTickers.METAL,"ZN0":stockTickers.METAL,"NI0":stockTickers.METAL,
    "PB0":stockTickers.METAL,"SN0":stockTickers.METAL,
    # BLACKS
    "I0":stockTickers.BLACK,"RB0":stockTickers.BLACK,"HC0":stockTickers.BLACK,
    "SS0":stockTickers.BLACK,"ZC0":stockTickers.BLACK,"JM0":stockTickers.BLACK,
    "J0":stockTickers.BLACK,"MA0":stockTickers.BLACK,
    "SC0":stockTickers.CHEM,"FU0":stockTickers.CHEM,"PG0":stockTickers.CHEM,
    "TA0":stockTickers.CHEM,"V0":stockTickers.CHEM,"PP0":stockTickers.CHEM,
    "EB0":stockTickers.CHEM,"L0":stockTickers.CHEM,"BU0":stockTickers.CHEM,
    "RU0":stockTickers.CHEM,
    # AGRIS
    "A0":stockTickers.AGRI,"M0":stockTickers.AGRI,"RM0":stockTickers.AGRI,
    "Y0":stockTickers.AGRI,"OI0":stockTickers.AGRI,"P0":stockTickers.AGRI,
    "CF0":stockTickers.AGRI,"SR0":stockTickers.AGRI,"C0":stockTickers.AGRI,
    "CS0":stockTickers.AGRI,"LH0":stockTickers.AGRI,"JD0":stockTickers.AGRI,
    "AP0":stockTickers.AGRI,"CJ0":stockTickers.AGRI,"PK0":stockTickers.AGRI,
    "SP0":stockTickers.AGRI,
    # SPECIALs
    "FG0":stockTickers.GLASS,"SA0":stockTickers.GLASS,
    }

#---------------------------------------------
def recalIndexTkrs(corList, covData):
    # recaluclate index lgRet from tkr list
    # [ticker, lags, correlation]
    sumWgts = sum([abs(ele[2]) for ele in corList])
    indexLgRet = []
    for tk in corList:
        sym, lag, cor = tk
        colN = symFunc.sym2Colname(sym)
        lgRetX = arrayTools.price2LgRet(covData[colN])
        lagX = dStats.addLagLi(lgRetX, lag)
        wgts = cor/sumWgts
        if len(indexLgRet) == 0:
            indexLgRet = lagX*wgts
        else:
            indexLgRet += lagX*wgts
    return indexLgRet

#---------------------------------------------
def dumpModelSIndex(tgtSym, corList, savePath="C:/models/"):
    fname = tgtSym+"_sIndex"
    sDict = {"tgtSym":tgtSym,
             "corList":corList}
    print("Dump model:%s"%fname)
    dpk.setPickle(sDict, fname, path=savePath)
    return None

#---------------------------------------------
def loadModelSIndex(tgtSym, path="C:/models/"):
    # return model stock index pickle file
    fname = tgtSym+"_sIndex"
    print("Load model:%s"%fname)
    sIndexDict = dpk.getPickle(fname, path=path)
    return sIndexDict

#---------------------------------------------
def calIndexV1(combData, N=2):
    # calculate user defined sector index
    # method 1: cut off highest and lowest lgRet
    priCols = [ele for ele in combData.keys() if "Pri" in ele]
    ansLgRet = []
    for loc in range(1, len(combData["date"])):
        lgRetLi = [np.log(combData[pc][loc]/combData[pc][loc-1]) for pc in priCols]
        lgRetLi = arrayTools.cutOffExtremeN(lgRetLi, N)
        ansLgRet.append(np.average(lgRetLi))
    return arrayTools.lgRet2Price(ansLgRet)

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
        lgRetLi = arrayTools.cutOffExtremeNwtVlm(lgRetLi, priLi, vlmLi, N)
        ansLgRet.append(np.average(lgRetLi))
    return arrayTools.lgRet2Price(ansLgRet)

#---------------------------------------------
def calIndexV3(combData, pct=0.3):
    # calculate user defined sector index
    # method 3: cut off highest and lowest lgRet weighted by money volume
    priCols = sorted([ele for ele in combData.keys() if "Pri" in ele])
    vlmCols = sorted([ele for ele in combData.keys() if "Vlm" in ele])
    ansLgRet = []
    for loc in range(1, len(combData["date"])):
        lgRetLi = [np.log(combData[pc][loc]/combData[pc][loc-1]) for pc in priCols]
        priLi = [combData[pc][loc] for pc in priCols]
        vlmLi = [combData[vm][loc] for vm in vlmCols]
        lgRetLi = arrayTools.cutOffExtremeNwtVlmPct(lgRetLi, priLi, vlmLi, pct)
        ansLgRet.append(np.average(lgRetLi))
    return arrayTools.lgRet2Price(ansLgRet)

#---------------------------------------------
def calSingleSym(tgtSym, sdate, edate, topN=5):
    # calcualte single sym index covariates
    tkrsLi = FUTEQmap.get(tgtSym, None)
    if tkrsLi is None: return None
    tgtData = dpk.getPickle(tgtSym)
    yDateLiFull = tgtData["date"]  # need this as full x-axis
    if len(yDateLiFull) == 0: return None
    tgtData = arrayTools.sliceDataByDates(tgtData, sdate, edate)
    corList = dCalCorr.findBestCOVs(tgtData, tkrsLi, yDateLiFull)
    # select top N best covariates
    corList = sorted(corList, key=lambda x: abs(x[2]), reverse=True)[:topN]
    print("SYM:%s, stock index calibration:" % tgtSym, corList)
    return corList

#---------------------------------------------
def loopAllFUT(sdate, edate, topN=5, plotFalg = True):
    # loop through all fut tickers
    # default assumption is slice from sdate to edate
    # but in realty there could be lag factor
    # in this case start point should move backward
    # but when calculate CORR we have to make sure
    # two series in same length
    for tgtSym,tkrsLi in FUTEQmap.items():
        print("Processing %s"%tgtSym)
        corList = calSingleSym(tgtSym, sdate, edate, topN=topN)
        # save model to disk
        dumpModelSIndex(tgtSym, corList)
        if plotFalg:
            # plot index compare along the way
            tgtData = dpk.getPickle(tgtSym)
            yDateLiFull = tgtData["date"]
            pltF.plotIndexGivenCor(corList, sdate, edate, yDateLiFull, tgtSym, tgtData)
    return None

#---------------------------------------------
def calsIndexfromModel(tgtSym, sdate, edate, smoothN=5):
    # will use model on disk to cal index weights
    # loop through all fut tickers
    # function will use saved weights and lag 
    # also use new sdate and edate to recalculate
    yDates = arrayTools.sliceYDates(tgtSym, sdate, edate)
    corList = loadModelSIndex(tgtSym, path="C:/models/")["corList"]
    print("Load model %s from disk..."%tgtSym, corList)
    lgRetIndex,date = dCalCorr.calIndexGivenCorLi(corList, sdate, edate, yDates)
    lgRetIndex = dStats.mavg1D(lgRetIndex, N=smoothN)
    priceIndex = arrayTools.lgRet2Price(lgRetIndex)
    return priceIndex, date

##################################################
##################################################
##################################################
if __name__ == "__main__":
    sDate, eDate = datetime(2021,8,1).date(), datetime(2021,11,1).date()
    loopAllFUT(sDate, eDate, topN=5)
    # exit()
    # sDate, eDate = datetime(2021,11,1).date(), datetime(2021,11,12).date()
    # tgtSym = "TA0"
    # priceIndex, date = calsIndexfromModel(tgtSym, sDate, eDate, smoothN=5)
    # pltF.plotSingle(date, priceIndex, label1=tgtSym, title=tgtSym+"_sIndex")
    
    
    