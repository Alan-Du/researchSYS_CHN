""" model test with prediction accuracy
    here the accuracy defined could be very different from
    traditional way
    we do chain back-testing, each batch calibrate to 3 month hist
    predict for next month and calculate the accuracy
"""
import dModelSim
import dCalCorr
import arrayTools
import dPickle as dpk
from buildStockIndex import FUTEQmap
from buildEXOGIndex import EXOGmap
import fxTickers
import plotFunc
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
def calRealLgRet(tgtSym, sdate, edate):
    # return the real lgret between sdate to edate
    data = dpk.getPickle(tgtSym)
    data = arrayTools.sliceDataByDates(data, sdate, edate)
    lgRet = arrayTools.price2LgRet(data["adjClose"])
    return lgRet

#---------------------------------------------
def calAccuracy(realLgRet, predLgRet):
    # calcuatle accuracy given real and prediction LgRets
    # only consider if predict correct direction
    # assume the diff should be normal(0,sig)
    diff = np.exp(realLgRet)-np.exp(predLgRet)
    u, sig = np.mean(np.abs(diff)), np.std(diff)
    return u/sig

#---------------------------------------------
def calSingleSymIndex(tgtSym, tkrsLi, sdate, edate, topN=5):
    # calcualte single sym index covariates
    tgtData = dpk.getPickle(tgtSym)
    yDateLiFull = tgtData["date"]  # need this as full x-axis
    if len(yDateLiFull) == 0: return None
    tgtData = arrayTools.sliceDataByDates(tgtData, sdate, edate)
    corList = dCalCorr.findBestCOVs(tgtData, tkrsLi, yDateLiFull)
    # select top N best covariates
    corList = sorted(corList, key=lambda x: abs(x[2]), reverse=True)[:topN]
    print("SYM:%s xxx index calibration from %s to %s:" % (tgtSym, str(sdate), str(edate)), corList)
    return corList

#---------------------------------------------
def calModelOnFly(tgtSym, sDate, eDate,
                  corListSIND, corListFX, corListEXOG):
    # calibrate model on the fly not from pickled files
    yData = dpk.getPickle(tgtSym)
    yDateFull = yData["date"]
    if len(yDateFull) == 0: return None
    sDateShift = dCalCorr.shiftDateByLag(sDate, yDateFull, 1)
    yDataSlice = arrayTools.sliceDataByDates(yData, sDateShift, eDate)
    yLgRet = arrayTools.price2LgRet(yDataSlice["adjClose"])[1:]

    # 1) get calibrated stock index covariates
    sIndexLgRet = dCalCorr.calIndexGivenCorLi(corListSIND, sDate, eDate, yDateFull)
    assert len(sIndexLgRet) == len(yLgRet), "Len error in calModel->stock index"

    # 2) get calibrated FX covariates
    # NEED write buildFXIndex.py module and dump modelFX int C:/models/
    fxLgRet = dCalCorr.calIndexGivenCorLi(corListFX, sDate, eDate, yDateFull)
    assert len(fxLgRet) == len(yLgRet), "Len error in calModel->fx index"

    # 3) get calibrated EXOG covariates
    exogLgRet = dCalCorr.calIndexGivenCorLi(corListEXOG, sDate, eDate, yDateFull)
    assert len(exogLgRet) == len(yLgRet), "Len error in calModel->exog index"

    # 4) calibrate model to Y data
    # solve for best weights between stock index, fx index and exgos index
    wts, intercept, score = dModelSim.calibrate(yLgRet, sIndexLgRet, fxLgRet, exogLgRet)
    indexDict = {"corListSIND": [wts[0], corListSIND],
                 "corListFX": [wts[1], corListFX],
                 "corListEXOG": [wts[2], corListEXOG]}
    modelDict = {"score":score,
                 "intercept":intercept,
                 "corDict":indexDict}
    return modelDict

#---------------------------------------------
def predModelOnFly(tgtSym, tDate, modelDict):
    # calcualte lgret prediction
    # score = modelDict["score"]
    intercept = modelDict["intercept"]
    indexDict = modelDict["corDict"]
    predLgRet = dModelSim.calPreOneDay(tgtSym, tDate, indexDict, intercept)
    return predLgRet

#---------------------------------------------
def singleTestRun(tgtSym, sdate, edate, edateTest, hypDict={}):
    # calibrate from sdate to edate
    # predict from edate to edateTest

    ##################################################
    # step 1 calibrate model to [sdate,edate]
    tkrsLi = FUTEQmap.get(tgtSym, None)
    stCorLi = calSingleSymIndex(tgtSym, tkrsLi, sdate, edate, topN=hypDict["topNstock"])
    tkrsLi = fxTickers.FX
    fxCorLi = calSingleSymIndex(tgtSym, tkrsLi, sdate, edate, topN=hypDict["topNfx"])
    tkrsLi = EXOGmap.get(tgtSym, None)
    egCorLi = calSingleSymIndex(tgtSym, tkrsLi, sdate, edate, topN=hypDict["topNexog"])
    modelDict =calModelOnFly(tgtSym, sdate, edate, stCorLi, fxCorLi, egCorLi)

    ##################################################
    # step 2-a prediction [edate, edateTest]
    predDate = list(filter(lambda x:edate<=x<=edateTest, dpk.getPickle(tgtSym)["date"]))
    predLgRetLi = [predModelOnFly(tgtSym, tDate, modelDict) for tDate in predDate]
    # step 2-b get real lgRets
    realLgRetLi = calRealLgRet(tgtSym, edate, edateTest)

    ##################################################
    # step 3 plot comparison and calculate accuracy
    zScore = calAccuracy(realLgRetLi, predLgRetLi)
    print("Prediction zScore:%f, SYM:%s, pSDate:%s, pEDate:%s" % (zScore, tgtSym, str(edate), str(edateTest)))
    assert len(realLgRetLi) == len(predLgRetLi), "Length error in singleTestRun"
    # whenever change list size do assert on length
    pri1 = arrayTools.lgRet2Price(predLgRetLi)[1:]
    pri2 = arrayTools.lgRet2Price(realLgRetLi)[1:]
    assert len(pri2) == len(pri1), "Length error in singleTestRun"

    fName = tgtSym + "_" + str(edate) + "_" + str(edateTest)
    title = "Price_Cpr_" + fName
    fig = plotFunc.plotCompare2(predDate, pri1, pri2,
                                label1="Pred", label2="Real",
                                title=title, wantShow=False)
    plotPath = "C:/plots/ModelTest/"
    fig.savefig(plotPath + fName + ".png")
    return zScore

#---------------------------------------------
def singleTestChain(tgtSym, start, end, lookback = 60):
    # process chain testing from sdate to edate
    # chop data into 3 month (22*3 days) pieces by pieces
    # each time calibrate
    # there is a bug that start and end date mush be within
    # yDate full list, if not shift to the nearest point
    dayInMonth = 20
    yDateFull = dpk.getPickle(tgtSym)["date"]
    ind = np.searchsorted(yDateFull, start)
    hypDict = {"topNstock":5, "topNfx":2, "topNexog":1}
    zScoreLi = []
    while ind+lookback+dayInMonth < len(yDateFull) \
            and yDateFull[ind+lookback] <= end:
        sdate = yDateFull[ind]
        edate = yDateFull[ind+lookback]
        edateTest = yDateFull[ind+lookback+dayInMonth]
        print("Processing :%s" % str(sdate))
        zScore = singleTestRun(tgtSym, sdate, edate, edateTest, hypDict=hypDict)
        zScoreLi.append([edateTest, zScore])
        # update next run
        sdate = yDateFull[ind + dayInMonth]
        ind = np.searchsorted(yDateFull, sdate)

    print(zScoreLi)
    plotFunc.plotSingle([ele[0] for ele in zScoreLi], [ele[1] for ele in zScoreLi], label1="zScore", title=None)
    return None

##################################################
##################################################
##################################################
if __name__ == "__main__":
    tgtSym = "CU0"
    sdate = datetime(2020, 1, 1).date()
    edate = datetime(2021, 11, 1).date()
    for tgtSym in ["AL0", "ZN0", "NI0", "PB0", "SN0",
              "I0", "RB0", "HC0", "SS0", "FG0", "SA0", "ZC0", "JM0",
              "J0", "MA0", "EG0", "UR0",
              "TA0", "V0", "PP0", "EB0", "L0", "BU0", "RU0",
              "A0", "M0", "RM0", "Y0", "OI0", "P0", "CF0", "SR0",
              "C0", "CS0",]:
        singleTestChain(tgtSym, sdate, edate)