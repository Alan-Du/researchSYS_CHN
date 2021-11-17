# -*- coding: utf-8 -*-
""" helper functions to get and set pickles
"""
import os, pickle
import numpy as N
import symFunc

#---------------------------------------------
def getPickle(fname, path=None):
    if not path: symtype, path = symFunc.getPathBySym(fname)
    data = None
    if os.path.exists(path+fname):
        data = pickle.load(open(path+fname, "rb"))
    else:
        print("Cannot find pcikles %s"%(path+fname))
    return data

#---------------------------------------------
def setPickle(data, fname, path=None):
    if not path: symtype, path = symFunc.getPathBySym(fname)
    if os.path.exists(path+fname):
        print("Already have pickle file:%s, ATT:will overwrite!"%(path+fname))
        pickle.dump(data, open(path+fname, "wb"))
    else:
        print("Saved pickle:%s"%(path+fname))
        pickle.dump(data, open(path+fname, "wb"))
    return None

#---------------------------------------------
def updatePickle(newData, fname, path=None, forceUpdate=False):
    if not path: symtype, path = symFunc.getPathBySym(fname)
    if not os.path.exists(path+fname):
        print("Pickle not here, create new:%s"%(path+fname))
        setPickle(newData, fname, path=path)
    else:
        data = getPickle(fname, path=path)
        for newInd, dt in enumerate(newData["date"]):
            # check date and update
            if dt in data["date"] and not forceUpdate: continue
            ind = N.searchsorted(data["date"], dt)
            print("Updating %s, ind:%d"%(dt.strftime("%Y%m%d"), ind))
            for col in ["date", "open", "high", "low", "close", "adjClose", "volume"]:
                # update for all columns
                val = newData[col][newInd]
                data[col] = data[col][:ind]+[val]+data[col][ind+1:]
        setPickle(data, fname, path=path)
    return None
            

##################################################
##################################################
##################################################
if __name__ == "__main__":
    path = "C:/FUTdataus/"
    data = getPickle("ALI=F", path=path)
    print(data)