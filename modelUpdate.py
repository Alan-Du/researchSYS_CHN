""" reran model build
"""
from datetime import datetime
import buildStockIndex
import buildFXIndex
import buildEXOGIndex

##################################################
##################################################
##################################################
sDate, eDate = datetime(2021, 8, 1).date(), datetime(2021, 11, 1).date()

# stock index build
buildStockIndex.loopAllFUT(sDate, eDate, topN=5, plotFalg=True)

# FX index build
buildFXIndex.loopAllFX(sDate, eDate, topN=2, plotFalg=True)

# exogenous vars index build
buildEXOGIndex.loopAllEXOG(sDate, eDate, topN=2, plotFalg=True)
