""" sym related functions
    get symtype environment
    get sym path
    transfer sym to file name or otherwise
    ...
"""
import dPickle as dpk
import arrayTools
import os
# global dictionary
symtpyeDict = {
        "FUT":"C:/FUTdata/",
        "FUTus":"C:/FUTdataus/",
        "EQ":"C:/EQdata/",
        "FX":"C:/FXdata/",
        }

#---------------------------------------------
def getSymByDate(tgtSym, sDate, eDate, symtpye=None):
    # return pickles given sym and dates
    # right now can only support FUT environment
    if not symtpye: symtpye,path=getPathBySym(tgtSym)
    pData = dpk.getPickle(tgtSym, path=getPathPickle(symtpye))
    pData = listTools.sliceDataByDates(pData, sDate, eDate)
    return pData

#---------------------------------------------
def getPathBySym(tgtSym):
    # we assume one sym one in one directory
    # if cannot find such sym return NAN
    for symtype, path in symtpyeDict.items():
        if any([tgtSym in ele for ele in os.listdir(path)]):
            return symtype, path
    return "NAN", "NAN"

#---------------------------------------------
def getPathPickle(symtype):
    return symtpyeDict.get(symtype, "NA")

#---------------------------------------------
def sym2Colname(sym):
    return sym.split(".")[0]+"Pri"

##################################################
##################################################
##################################################
if __name__ == "__main__":
    print(getPathBySym("THB"))