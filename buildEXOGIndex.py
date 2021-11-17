# -*- coding: utf-8 -*-
""" functions to build stock index correlated to commodity price
    for each stock in pool, we search for a best lag factor 
    then we select top three best predictor with lag
    we want covariates align with target symbol and select
    the top most N covariates to simulate target symbol
"""
import numpy as np
from datetime import datetime
import dPickle as dpk
import dataTools
import listTools
import futTickers
import futTickersUS
import plotFunc as pltF
import symFunc

EXOGmap = {
# METALS
    "AU0":futTickersUS.METALS+futTickers.FINANCE,"AG0":futTickersUS.METALS+futTickers.FINANCE,"CU0":futTickersUS.METALS+futTickers.FINANCE,
    "AL0":futTickersUS.METALS+futTickers.FINANCE,"ZN0":futTickersUS.METALS+futTickers.FINANCE,"NI0":futTickersUS.METALS+futTickers.FINANCE,
    "PB0":futTickersUS.METALS+futTickers.FINANCE,"SN0":futTickersUS.METALS+futTickers.FINANCE,
    # BLACKS
    "I0":futTickersUS.ENG+futTickers.FINANCE,"RB0":futTickersUS.ENG+futTickers.FINANCE,"HC0":futTickersUS.ENG+futTickers.FINANCE,
    "SS0":futTickersUS.ENG+futTickers.FINANCE,"ZC0":futTickersUS.ENG+futTickers.FINANCE,"JM0":futTickersUS.ENG+futTickers.FINANCE,
    "J0":futTickersUS.ENG+futTickers.FINANCE,"MA0":futTickersUS.ENG+futTickers.FINANCE,
    "SC0":futTickersUS.ENG+futTickers.FINANCE,"FU0":futTickersUS.ENG+futTickers.FINANCE,"PG0":futTickersUS.ENG+futTickers.FINANCE,
    "TA0":futTickersUS.ENG+futTickers.FINANCE,"V0":futTickersUS.ENG+futTickers.FINANCE,"PP0":futTickersUS.ENG+futTickers.FINANCE,
    "EB0":futTickersUS.ENG+futTickers.FINANCE,"L0":futTickersUS.ENG+futTickers.FINANCE,"BU0":futTickersUS.ENG+futTickers.FINANCE,
    "RU0":futTickersUS.ENG+futTickers.FINANCE,
    # AGRIS
    "A0":futTickersUS.AGRI+futTickers.FINANCE,"M0":futTickersUS.AGRI+futTickers.FINANCE,"RM0":futTickersUS.AGRI+futTickers.FINANCE,
    "Y0":futTickersUS.AGRI+futTickers.FINANCE,"OI0":futTickersUS.AGRI+futTickers.FINANCE,"P0":futTickersUS.AGRI+futTickers.FINANCE,
    "CF0":futTickersUS.AGRI+futTickers.FINANCE,"SR0":futTickersUS.AGRI+futTickers.FINANCE,"C0":futTickersUS.AGRI+futTickers.FINANCE,
    "CS0":futTickersUS.AGRI+futTickers.FINANCE,"LH0":futTickersUS.AGRI+futTickers.FINANCE,"JD0":futTickersUS.AGRI+futTickers.FINANCE,
    "AP0":futTickersUS.AGRI+futTickers.FINANCE,"CJ0":futTickersUS.AGRI+futTickers.FINANCE,"PK0":futTickersUS.AGRI+futTickers.FINANCE,
    "SP0":futTickersUS.AGRI+futTickers.FINANCE,
    # SPECIALs
    "FG0":futTickersUS.ENG+futTickers.FINANCE,"SA0":futTickersUS.ENG+futTickers.FINANCE,
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
        lgRetX = listTools.price2LgRet(covData[colN])
        lagX = listTools.addLagLi(lgRetX, lag)
        wgts = cor/sumWgts
        if len(indexLgRet) == 0:
            indexLgRet = lagX*wgts
        else:
            indexLgRet += lagX*wgts
    return indexLgRet

#---------------------------------------------
def dumpModelFX(tgtSym, corList, savePath="C:/models/"):
    fname = tgtSym + "_EXOG"
    sDict = {"tgtSym":tgtSym,
             "corList":corList}
    print("Dump model:%s"%fname)
    dpk.setPickle(sDict, fname, path=savePath)
    return None

#---------------------------------------------
def loadModelSIndex(tgtSym, path="C:/models/"):
    # return model stock index pickle file
    fname = tgtSym + "_EXOG"
    print("Load model:%s"%fname)
    sIndexDict = dpk.getPickle(fname, path=path)
    return sIndexDict

#---------------------------------------------
def loopAllFUT(sdate, edate, topN=5):
    # loop through all fut tickers
    for tgtSym in futTickers.COMMODITY0:
        tkrsLi = EXOGmap.get(tgtSym, None)
        if not tkrsLi: continue # model not implemented yet
        print("Processing %s"%tgtSym)
        tgtData = dpk.getPickle(tgtSym)
        if len(tgtData["date"])==0: continue
        tgtData = listTools.sliceDataByDates(tgtData, sdate, edate)
        covData = listTools.alignDataToYdata(tkrsLi, tgtData)
        corList = dataTools.findBestCOVs(tgtData, tkrsLi, covData)
        # select top N best covariates
        corList = sorted(corList, key=lambda x:abs(x[2]),reverse=True)[:topN]
        print("SYM:%s, EXOG index calibration:"%tgtSym, corList)
        # save model to disk
        dumpModelFX(tgtSym, corList)
        indexLgRet = recalIndexTkrs(corList, covData)
        indexLgRet = listTools.mavg1D(indexLgRet, N=5)
        indexPrice = listTools.lgRet2Price(indexLgRet)
        tgtNormPri = tgtData["adjClose"]/tgtData["adjClose"][0]
        fig = pltF.plotCompare2(tgtData["date"], tgtNormPri, indexPrice,
                                label1=tgtSym, label2="EXOGIndex", title=tgtSym+"_EXOG",
                                wantShow=False)
        plotPath="C:/plots/EXOGIndex/"
        fig.savefig(plotPath+tgtSym+"_EXOG.png")
    return None

#---------------------------------------------
def calsIndexfromModel(tgtSym, sdate, edate, smoothN=5):
    # will use model on disk to cal index weights
    # loop through all fut tickers
    # function will use saved weights and lag 
    # also use new sdate and edate to recalculate
    corList = loadModelSIndex(tgtSym, path="C:/models/")["corList"]
    print("Load model %s from disk..."%tgtSym)
    print(corList)
    lgRetIndex,date = dataTools.getIndexLgRet(sdate, edate, corList)
    lgRetIndex = listTools.mavg1D(lgRetIndex, N=smoothN)
    priceIndex = listTools.lgRet2Price(lgRetIndex)
    return priceIndex, date

##################################################
##################################################
##################################################
if __name__ == "__main__":
    sDate, eDate = datetime(2021,8,1).date(), datetime(2021,11,1).date()
    loopAllFUT(sDate, eDate, topN=2)
    # exit()
    # sDate, eDate = datetime(2021,11,1).date(), datetime(2021,11,12).date()
    # tgtSym = "TA0"
    # priceIndex, date = calsIndexfromModel(tgtSym, sDate, eDate, smoothN=5)
    # pltF.plotSingle(date, priceIndex, label1=tgtSym, title=tgtSym+"_FXIndex")
    
    
    