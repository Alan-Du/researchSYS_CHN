""" weekly data donwload
"""
import downloaderYAHOO as dYHO
import downloaderSINA as dSIN
import stockTickers, fxTickers, futTickersUS, futTickers
import dataQualityCheck
from datetime import datetime
##################################################
##################################################
##################################################
sdate = "2021-11-13"
edate = "2021-11-20"

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

# run data quality check
startDate = datetime(2019, 1, 1).date()
alltickers = futTickers.COMMODITYALL + futTickersUS.USCOMMODITYALL+fxTickers.FX
dataQualityCheck.dataCheckLoop(alltickers, startDate, plotFlag=True)
alltickers = stockTickers.stockTickers
dataQualityCheck.dataCheckLoop(alltickers, startDate, plotFlag=False)