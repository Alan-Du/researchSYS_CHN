# -*- coding: utf-8 -*-
""" Tool box to transfer strings
"""
from datetime import datetime
import pandas as pd

#---------------------------------------------
def SINAtolist(istr):
    # SINA format [date, open, high, low, close, volume]
    ansLi = [[datetime.strptime(ele[0], '%Y-%m-%d').date(), float(ele[1]), float(ele[2]), float(ele[3]), float(ele[4]), float(ele[5])] for ele in eval(istr)]
    return ansLi

#---------------------------------------------
def listToTable(liTup):
    # transfer list of tuple to table
    ansS = ""
    for row in liTup:
        ansS += ";".join([str(ele) for ele in row])
        ansS += "\n"
    return ansS