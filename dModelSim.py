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
import arrayTools, dStats, dCalCorr
from datetime import datetime
import symFunc
from sklearn import linear_model

#---------------------------------------------
def writeModel(modelName, tgtSym, intercept, score, indexDict,
               printFlag=False, path="C:/models/"):
    # save model pars into pickle
    sDict = {"tgtSym": tgtSym,
             "score": score,
             "intercept": intercept,
             "corDict": indexDict}
    print("Dump model:%s" % modelName)
    if printFlag:
        print("--->Model details below")
        print(sDict)
        print("Will dump into: %s"%path)
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
    return sIndex, fx, exog

#---------------------------------------------
def calModel(tgtSym, sDate, eDate, savePath="C:/models/"):
    # function to solve weights for model covariates
    # calibrate model using stock index and exog covariates
    # return value is a dictionary of weights of sIndex, FXs, and exogs
    yData = dpk.getPickle(tgtSym)
    yDateFull = yData["date"]
    if len(yDateFull) == 0: return None
    sDateShift = dCalCorr.shiftDateByLag(sDate, yDateFull, 1)
    yDataSlice = arrayTools.sliceDataByDates(yData, sDateShift, eDate)
    yLgRet = arrayTools.price2LgRet(yDataSlice["adjClose"])[1:]
    # 1) get calibrated stock index covariates
    corListSIND = dpk.getPickle(tgtSym + "_sIndex", path=savePath)["corList"]
    sIndexLgRet = dCalCorr.calIndexGivenCorLi(corListSIND, sDate, eDate, yDateFull)
    assert len(sIndexLgRet) == len(yLgRet), "Len error in calModel->stock index"

    # 2) get calibrated FX covariates
    # NEED write buildFXIndex.py module and dump modelFX int C:/models/
    corListFX = dpk.getPickle(tgtSym + "_FX", path=savePath)["corList"]
    fxLgRet = dCalCorr.calIndexGivenCorLi(corListFX, sDate, eDate, yDateFull)
    assert len(fxLgRet) == len(yLgRet), "Len error in calModel->fx index"

    # 3) get calibrated EXOG covariates
    corListEXOG = dpk.getPickle(tgtSym + "_EXOG", path=savePath)["corList"]
    exogLgRet = dCalCorr.calIndexGivenCorLi(corListEXOG, sDate, eDate, yDateFull)
    assert len(exogLgRet) == len(yLgRet), "Len error in calModel->exog index"

    # 4) calibrate model to Y data
    # solve for best weights between stock index, fx index and exgos index
    modelName = tgtSym + "_MODEL"
    wts, intercept, score = calibrate(yLgRet, sIndexLgRet, fxLgRet, exogLgRet)
    indexDict = {"corListSIND": [wts[0], corListSIND],
                 "corListFX": [wts[1], corListFX],
                 "corListEXOG": [wts[2], corListEXOG]}
    writeModel(modelName, tgtSym, intercept, score, indexDict, printFlag=True, path=savePath)
    return None

#---------------------------------------------
def calibrate(y, x1, x2, x3):
    # regression model solving weights
    regr = linear_model.LinearRegression()
    X = np.vstack((x1, x2, x3)).T
    regr.fit(X, y)
    score = regr.score(X, y)
    wts, intercept = regr.coef_, regr.intercept_
    return wts, intercept, score

#---------------------------------------------
def modelPreOneDay(tgtSym, tDate):
    # predict from model parameters
    # if there is lag factor will apply the real
    # lgRet given lag date
    # if lag=0 that means current date
    # will use mavg1D(lgRet, N=5) to predict next date lgret
    modelName = tgtSym + "_MODEL"
    modelData = dpk.getPickle(modelName, path="C:/models/")
    score = modelData["score"]
    intercept = modelData["intercept"]
    print("Model:%s, Score:%f, intercept, %f"%(modelName, score, intercept))
    indexDict = modelData["corDict"]
    predLgRet = calPreOneDay(tgtSym, tDate, indexDict, intercept)
    return predLgRet

#---------------------------------------------
def calPreOneDay(tgtSym, tDate, indexDict, intercept):
    # calculate predicted one day lgret given correlation structure
    swt, stCorLi = indexDict["corListSIND"]
    stLgRet = dCalCorr.calIndex1DayLgRetWithCorLi(tgtSym, tDate, stCorLi)
    fwt, fxCorLi = indexDict["corListFX"]
    fxLgRet = dCalCorr.calIndex1DayLgRetWithCorLi(tgtSym, tDate, fxCorLi)
    ewt, egCorLi = indexDict["corListEXOG"]
    egLgRet = dCalCorr.calIndex1DayLgRetWithCorLi(tgtSym, tDate, egCorLi)
    predLgRet = swt*stLgRet+fwt*fxLgRet+ewt*egLgRet
    # considering if we want intercept
    predLgRet += intercept
    return predLgRet

#---------------------------------------------
def modelPred1DLoop(tgtDate, tkrLi, lgRetOutput=False):
    # predicate one day lgRet for tkrLi
    ansDic = {}
    for tkr in tkrLi:
        predRet = modelPreOneDay(tkr, tgtDate)
        if not lgRetOutput: predRet = np.exp(predRet)-1
        ansDic[tkr] = predRet
    ans = sorted(ansDic.items(), key=lambda x:abs(x[1]), reverse=True)
    return ans

##################################################
##################################################
##################################################
if __name__ == "__main__":
    tkrLi = ["AU0", "AG0", "CU0", "AL0", "ZN0", "NI0", "PB0", "SN0",
              "I0", "RB0", "HC0", "SS0", "FG0", "SA0", "ZC0", "JM0",
              "J0", "MA0", "UR0",
              "TA0", "V0", "PP0", "EB0", "L0", "BU0", "RU0",
              "A0", "M0", "RM0", "Y0", "OI0", "P0", "CF0", "SR0",
              "C0", "CS0", "SP0"]
    sDate, eDate = datetime(2021, 9, 1).date(), datetime(2021, 11, 19).date()
    for tgtSym in tkrLi:
        calModel(tgtSym, sDate, eDate)
