""" DO NOT import this module anywhere!
    some unit test for complicate functions
    1) addLagLiHIST
"""
#---------------------------------------------
def test_addLagLiHIST():
    # testing on dStats.addLagLiHIST(histRealDict)
    # histRealDict={"lagN", "tkr", "yDate", "yDateLiFull", "useRealDate"}
    import dStats
    from datetime import datetime
    import dPickle as dpk
    import numpy as np
    import arrayTools
    yTkr = "AU0"
    tTkr = "AU0"
    sDate, eDate = datetime(2019,1,1).date(), datetime(2021,1,1).date()
    yData = dpk.getPickle(yTkr)
    yDate = sorted([ele for ele in yData["date"] if sDate<=ele<=eDate])
    yDateLiFull = yData["date"]

    lagN = 1
    histRealDict = {"lagN":lagN, "tkr":tTkr, "yDate":yDate, "yDateLiFull":yDateLiFull}
    test = np.array(dStats.addLagLiHIST(histRealDict))

    sInd, eInd = np.searchsorted(yData["date"], sDate), np.searchsorted(yData["date"], eDate)
    lgRet = arrayTools.price2LgRet(yData["adjClose"])
    ans = lgRet[sInd-lagN:eInd-lagN]

    print("Test 1: dStats.addLagLiHIST lagN=1")
    assert len(ans) == len(test), "Length should match!"
    assert np.sum(np.abs(ans-test)) == 0, "Sum Diff should be 0!"

    lagN = 10
    histRealDict = {"lagN": lagN, "tkr": tTkr, "yDate": yDate, "yDateLiFull": yDateLiFull}
    test = np.array(dStats.addLagLiHIST(histRealDict))

    sInd, eInd = np.searchsorted(yData["date"], sDate), np.searchsorted(yData["date"], eDate)
    lgRet = arrayTools.price2LgRet(yData["adjClose"])
    ans = lgRet[sInd - lagN:eInd - lagN]

    print("Test 2: dStats.addLagLiHIST lagN=10")
    assert len(ans) == len(test), "Length should match!"
    assert np.sum(np.abs(ans - test)) == 0, "Sum Diff should be 0!"

##################################################
##################################################
##################################################

test_addLagLiHIST()