# -*- coding: utf-8 -*-

import downloaderSINA as dSINA
import downloaderYAHOO as dYAHOO
import futTickers, futTickersUS
import stockTickers, fxTickers

sdate = "2021-11-01"
edate = "2021-11-13"

# download commodity data
stkr = dSINA.sinaDownloader(commodityTickers.COMMODITY0, "C:/FUTdata/")
stkr._runTickers(sdate, edate)

# download stock and currency data
stkr = dYAHOO.yahooDownloader(stockTickers.stockTickers, "C:/EQdata/")
stkr._runTickers(sdate, edate)

stkr = dYAHOO.yahooDownloader(fxTickers.FX, "C:/FXdata/")
stkr._runTickers(sdate, edate)

stkr = dYAHOO.yahooDownloader(commodityTickersUS.USCOMMODITYALL, "C:/FUTdataus/")
stkr._runTickers(sdate, edate)