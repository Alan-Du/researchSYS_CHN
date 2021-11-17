# -*- coding: utf-8 -*-
""" SINA tickers, naming style sym+"0" means continous front contract
    sym+year means the  actual ric contract
"""
COMMODITY0 = ["AU0", "AG0", "CU0", "AL0", "ZN0", "NI0", "PB0", "SN0",
              "I0", "RB0", "HC0", "SS0", "FG0", "SA0", "ZC0", "JM0",
              "J0", "MA0", "EG0", "UR0", 
              "SC0", "FU0", "PG0", "TA0", "V0", "PP0", "EB0", "L0",
              "BU0", "RU0",
              "A0", "M0", "RM0", "Y0", "OI0", "P0", "CF0", "SR0",
              "C0", "CS0", "LH0", "JD0", "AP0", "CJ0", "PK0", "SP0"]

BOND0 = ["TS0", "TF0", "T0"]

INDEX = ["IF0", "IH0", "IC0"]

##################################################
##################################################
##################################################
FINANCE = BOND0+INDEX
COMMODITYALL = COMMODITY0+BOND0+INDEX
