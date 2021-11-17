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
import fxTickers
import symFunc
import plotFunc as pltF

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
    fname = tgtSym+"_FX"
    sDict = {"tgtSym":tgtSym,
             "corList":corList}
    print("Dump model:%s"%fname)
    dpk.setPickle(sDict, fname, path=savePath)
    return None

#---------------------------------------------
def loadModelSIndex(tgtSym, path="C:/models/"):
    # return model stock index pickle file
    fname = tgtSym+"_FX"
    print("Load model:%s"%fname)
    sIndexDict = dpk.getPickle(fname, path=path)
    return sIndexDict

#---------------------------------------------
def loopAllFUT(sdate, edate, topN=5):
    # loop through all fut tickers
    tkrsLi = fxTickers.FX
    for tgtSym in commodityTickers.COMMODITY0:
        print("Processing %s"%tgtSym)
        tgtData = dpk.getPickle(tgtSym, path="C:/FUTdata/")
        if len(tgtData["date"])==0: continue
        tgtData = listTools.sliceDataByDates(tgtData, sdate, edate)
        covData = listTools.alignDataToYdata(tkrsLi, tgtData)
        corList = dataTools.findBestCOVs(tgtData, tkrsLi, covData)
        # select top N best covariates
        corList = sorted(corList, key=lambda x:abs(x[2]),reverse=True)[:topN]
        print("SYM:%s, fx index calibration:"%tgtSym, corList)
        # save model to disk
        dumpModelFX(tgtSym, corList)
        indexLgRet = recalIndexTkrs(corList, covData)
        indexLgRet = listTools.mavg1D(indexLgRet, N=5)
        indexPrice = listTools.lgRet2Price(indexLgRet)
        tgtNormPri = tgtData["adjClose"]/tgtData["adjClose"][0]
        fig = pltF.plotCompare2(tgtData["date"], tgtNormPri, indexPrice,
                                label1=tgtSym, label2="FXIndex", title=tgtSym+"_fxSIM",
                                wantShow=False)
        plotPath="C:/plots/FXIndex/"
        fig.savefig(plotPath+tgtSym+"_fxSIM.png")
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
    sDate, eDate = datetime(2021,9,1).date(), datetime(2021,11,1).date()
    loopAllFUT(sDate, eDate, topN=2)
    # exit()
    # sDate, eDate = datetime(2021,11,1).date(), datetime(2021,11,12).date()
    # tgtSym = "TA0"
    # priceIndex, date = calsIndexfromModel(tgtSym, sDate, eDate, smoothN=5)
    # pltF.plotSingle(date, priceIndex, label1=tgtSym, title=tgtSym+"_FXIndex")
    
    
    