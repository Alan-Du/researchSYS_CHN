""" Day run prediction
"""
import dModelSim
import dString
import downloaderYAHOO as dYHO
import downloaderSINA as dSIN
from datetime import datetime
import stockTickers, fxTickers, futTickersUS, futTickers

# update market daily data
sdate = "2021-11-15"
edate = "2021-11-22"
tkrNames = stockTickers.stockTickers
stkr = dYHO.yahooDownloader(tkrNames, "C:/EQdata/")
stkr._runTickers(sdate, edate)

tkrNames = fxTickers.FX
stkr = dYHO.yahooDownloader(tkrNames, "C:/FXdata/")
stkr._runTickers(sdate, edate)

tkrNames = futTickersUS.USCOMMODITYALL
stkr = dYHO.yahooDownloader(tkrNames, "C:/FUTdataus/")
stkr._runTickers(sdate, edate)

tkrNames = futTickers.BOND0+futTickers.INDEX
stkr = dSIN.sinaDownloader(tkrNames, "C:/FUTdata/")
stkr._runTickers(sdate, edate)

# day run for next day lgRet prediction
tgtDate = datetime.strptime(edate, '%Y-%m-%d').date()
tkrLi = [ "AU0", "AG0", "CU0", "AL0", "ZN0", "NI0", "PB0", "SN0",
          "I0", "RB0", "HC0", "FG0", "ZC0", "JM0", "J0", "MA0",
          "TA0", "V0", "PP0", "L0", "BU0", "RU0",
          "A0", "M0", "RM0", "Y0", "OI0", "P0", "CF0", "SR0", "C0", "CS0"
          ]
lgRetPred = dModelSim.modelPred1DLoop(tgtDate, tkrLi)
print(dString.listToTable(lgRetPred[:6]))