# -*- coding: utf-8 -*-
""" functions to build stock index correlated to commodity price
    for each stock in pool, we search for a best lag factor 
    then we select top three best predictor with lag
    we want covariates align with target symbol and select
    the top most N covariates to simulate target symbol
"""
import numpy as np
import dPickle as dpk
import dataTools
import listTools
import stockTickers
from datetime import datetime
import plotFunc as pltF
import symFunc

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
        lgRetX = listTools.price2LgRet(covData[colN])
        lagX = listTools.addLagLi(lgRetX, lag)
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
def loopAllFUT(sdate, edate, topN=5):
    # loop through all fut tickers
    # default assumption is slice from sdate to edate
    # but in realty there could be lag factor
    # in this case start point should move backward
    # but when calculate CORR we have to make sure
    # two series in same length
    for tgtSym,tkrsLi in FUTEQmap.items():
        print("Processing %s"%tgtSym)
        tgtData = dpk.getPickle(tgtSym, path="C:/FUTdata/")
        yDateLiFull = tgtData["date"] # need this as full x-axis
        if len(yDateLiFull)==0: continue
        tgtData = listTools.sliceDataByDates(tgtData, sdate, edate)
        covData = listTools.alignDataToYdata(tkrsLi, tgtData)
        corList = dataTools.findBestCOVs(tgtData, tkrsLi, covData, yDateLiFull)
        # select top N best covariates
        corList = sorted(corList, key=lambda x:abs(x[2]),reverse=True)[:topN]
        print("SYM:%s, stock index calibration:"%tgtSym, corList)
        # save model to disk
        dumpModelSIndex(tgtSym, corList)
        indexLgRet = recalIndexTkrs(corList, covData)
        indexLgRet = listTools.mavg1D(indexLgRet, N=5)
        indexPrice = listTools.lgRet2Price(indexLgRet)
        tgtNormPri = tgtData["adjClose"]/tgtData["adjClose"][0]
        fig = pltF.plotCompare2(tgtData["date"], tgtNormPri, indexPrice,
                                label1=tgtSym, label2="sIndex", title=tgtSym+"_SIM",
                                wantShow=False)
        plotPath="C:/plots/sIndex/"
        fig.savefig(plotPath+tgtSym+"_SIM.png")
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
    loopAllFUT(sDate, eDate, topN=5)
    # exit()
    # sDate, eDate = datetime(2021,11,1).date(), datetime(2021,11,12).date()
    # tgtSym = "TA0"
    # priceIndex, date = calsIndexfromModel(tgtSym, sDate, eDate, smoothN=5)
    # pltF.plotSingle(date, priceIndex, label1=tgtSym, title=tgtSym+"_sIndex")
    
    
    