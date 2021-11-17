""" model calibration functions
    each sym we have covariates: 
        1) stock index (build from buildStockIndex.py)
        2) currency FX (build from buildFXIndex.py)
        3) other related commodity (EXOGs) (build from buildEXOG.py)
        4) FUT roll yields (NOT IMPLEMENTED YET...)
"""
import numpy as np
import dPickle as dpk
import fxTickers, futTickers, futTickersUS
import listTools, dataTools
import buildStockIndex
from datetime import datetime
import symFunc

#---------------------------------------------
def writeModel(modelName, tgtSym, corList, path="C:/models/"):
    # save model pars into pickle
    sDict = {"tgtSym": tgtSym,
             "corList": corList}
    print("Dump model:%s" % modelName)
    dpk.setPickle(sDict, modelName, path=path)
    return None

#---------------------------------------------
def loadModel(tgtSym, path="C:/models/"):
    # load model pars from pickle
    # 1) stock index pars
    # 2) exog pars
    sIndex = dpk.getPickle(tgtSym + "_sIndex", path=path)["corList"]
    fx = dpk.getPickle(tgtSym + "_FX", path=path)["corList"]
    exog = dpk.getPickle(tgtSym + "_EXOG", path=path)["corList"]
    print("loaded model:%s"%tgtSym, sIndex, "\n", exog)
    return sIndex, exog

#---------------------------------------------
def calModel(tgtSym, sDate, eDate, exogLi,
             topN=2, lagSetDict={}, savePath="C:/models/" ):
    # function to solve weights for model covariates
    # calibrate model using stock index and exog covariates
    # return value is a dictionary of weights of sIndex, FXs, and exogs

    # 1) get calibrated stock index covariates
    corListSIND = dpk.getPickle(tgtSym + "_sIndex", path=savePath)["corList"]
    sIndexLgRet, dateLi = dataTools.getIndexLgRet(sDate, eDate, corListSIND)

    # 2) get calibrated FX covariates
    # NEED write buildFXIndex.py module and dump modelFX int C:/models/
    corListFX = dpk.getPickle(tgtSym + "_FX", path=savePath)["corList"]
    fxLgRet, dateLi = dataTools.getIndexLgRet(sDate, eDate, corListFX)

    # 3) find other EXOGs variables
    corListEXOG = findBestEXOG(tgtSym, sDate, eDate, exogLi, topN=topN, lagSetDict=lagSetDict)
    print(corListEXOG)
    corListEXOG = dpk.getPickle(tgtSym + "_EXOG", path=savePath)["corList"]
    exogLgRet, dateLi = dataTools.getIndexLgRet(sDate, eDate, corListEXOG)
    raise()
    # solve for best weights between stock index and exgos
    modelName = tgtSym + "_EXOG"
    writeModel(modelName, tgtSym, corListEXOG, path=savePath)
    return None

#---------------------------------------------
def modelPreOneDay(tgtSym, tDate, exogs):
    # predict from model parameters
    # if there is lag factor will apply the real
    # lgRet given lag date
    # if lag=0 that means current date
    # will use mavg1D(lgRet, N=5) to predict next date lgret
    tgtData = dpk.getPickle(tgtSym)
    for vars in exogs:
        sym,lag,wt = vars
    return None

#---------------------------------------------
def findBestEXOG(tgtSym, sDate, eDate, exogLi, topN=2, lagSetDict={}):
    # return best correlated FX with lags
    print("Processing %s" % tgtSym)
    symtype, path = symFunc.getPathBySym(tgtSym)
    tgtData = dpk.getPickle(tgtSym)
    tgtData = listTools.sliceDataByDates(tgtData, sDate, eDate)
    covData = listTools.alignDataToYdata(exogLi, tgtData)
    corList = dataTools.findBestCOVs(tgtData, exogLi, covData, lagSetDict=lagSetDict)
    # select top N best covariates
    corList = sorted(corList, key=lambda x: abs(x[2]), reverse=True)[:topN]
    return corList

##################################################
##################################################
##################################################
if __name__ == "__main__":
    exogLi = fxTickers.FX
    lagSetDict = {"slag": 0, "elag": 20, "smoothN": 5}
    tkrLi = commodityTickers.COMMODITY0
    sDate, eDate = datetime(2021, 7, 1).date(), datetime(2021, 11, 1).date()
    for tgtSym in tkrLi:
        calModel(tgtSym, sDate, eDate, exogLi, topN=2, lagSetDict=lagSetDict)
