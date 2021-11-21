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
import dStats
import arrayTools
import futTickers
import fxTickers
import symFunc
import plotFunc as pltF
import dCalCorr

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
def loopAllFX(sdate, edate, topN=5, plotFalg = True):
    # similar to buildStockIndex.py loopallfut
    tkrsLi = fxTickers.FX
    for tgtSym in futTickers.COMMODITY0:
        print("Processing %s"%tgtSym)
        tgtData = dpk.getPickle(tgtSym)
        yDateLiFull = tgtData["date"] # need this as full x-axis
        if len(yDateLiFull)==0: continue
        tgtData = arrayTools.sliceDataByDates(tgtData, sdate, edate)
        corList = dCalCorr.findBestCOVs(tgtData, tkrsLi, yDateLiFull)
        # select top N best covariates
        corList = sorted(corList, key=lambda x:abs(x[2]),reverse=True)[:topN]
        print("SYM:%s, stock index calibration:"%tgtSym, corList)
        # save model to disk
        dumpModelFX(tgtSym, corList)
        if plotFalg:
            # plot index compare along the way
            plotPath = "C:/plots/FXindex/"
            pltF.plotIndexGivenCor(corList, sdate, edate, yDateLiFull, tgtSym, tgtData, plotPath=plotPath)
    return None

##################################################
##################################################
##################################################
if __name__ == "__main__":
    sDate, eDate = datetime(2021,8,1).date(), datetime(2021,11,1).date()
    loopAllFX(sDate, eDate, topN=2)
    # exit()
    # sDate, eDate = datetime(2021,11,1).date(), datetime(2021,11,12).date()
    # tgtSym = "TA0"
    # priceIndex, date = calsIndexfromModel(tgtSym, sDate, eDate, smoothN=5)
    # pltF.plotSingle(date, priceIndex, label1=tgtSym, title=tgtSym+"_FXIndex")
    
    
    