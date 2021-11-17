# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 01:37:09 2020
Get Historical stock price data and upload into DB
@author: Shaolun du
@contact: Shaolun.du@gmail.com
"""

GOLD = ["002237.SZ","600489.SS","600547.SS","600988.SS","002155.SZ"]
                 
COPPER = ["600362.SS","000630.SZ","000878.SZ","002212.SZ","603606.SS",
          "002498.SZ","002451.SZ","002471.SZ","600089.SS","603988.SS"]

ALUMINUM = ["000807.SZ","000933.SZ","000612.SZ","601600.SS","600219.SS",
            "002578.SZ","601677.SS","300428.SZ","600104.SS","002594.SZ",
            "601238.SS","000625.SZ"]
                    
ZINC = ["000688.SZ","600338.SS", "000426.SZ","000960.SZ", "601168.SS",
        "600961.SS","000751.SZ","002114.SZ"]

PB = ["601020.SS","600497.SS","000688.SZ", "600338.SS","000426.SZ",
      "601168.SS","600847.SS","601311.SS"]
   
NI = ["300208.SZ", "000825.SZ","600117.SS","002318.SZ","603878.SS"]
                  
SN = ["000960.SZ","000426.SZ", "002916.SZ","002134.SZ","603936.SS", 
      "600019.SS","000898.SZ","000959.SZ","600126.SS","601005.SS"]
               
ORE = ["601969.SS","000655.SZ", "000426.SZ","600532.SS"]
                 
COAL = ["601225.SS","601898.SS","600188.SS","000933.SZ","600985.SS",
        "601699.SS","603113.SS","601216.SS","000683.SZ","601898.SS",
        "600011.SS","600023.SS","600795.SS","601991.SS","600027.SS"]

COKE = ["601699.SS","600740.SS","603113.SS","601015.SS","600989.SS"]
               
STEEL = ["002110.SZ","600507.SS","600581.SS","600019.SS","600010.SS",
         "002110.SZ","600019.SS","000898.SZ","000959.SZ","600126.SS",
         "601005.SS","600581.SS"]
       
GLASS = ["601636.SS","000012.SZ","600819.SS","600586.SS", "600176.SS",
         "002080.SZ","002201.SZ","600876.SS","300093.SZ","603021.SS",
         "600660.SS"]
#OIL = []
                     
PTA = ["603113.SS","601233.SS","000301.SZ","000703.SZ","000936.SZ",
       "600346.SS","002493.SZ","002493.SZ","601233.SS","000420.SZ",
       "000703.SZ","000782.SZ","600346.SS","000158.SZ","300577.SZ",
       "002293.SZ","002327.SZ","601339.SS"]
             
PP = ["002648.SZ","600989.SS","002812.SZ","002243.SZ","002565.SZ",
      "600210.SS","002522.SZ","002585.SZ","002014.SZ","000333.SZ",
      "000651.SZ","600690.SS","002032.SZ","002050.SZ","002508.SZ",
      "002242.SZ","000921.SZ","603868.SS","603486.SS"]
                   
PVC = ["000635.SZ","002092.SZ","002002.SZ","600409.SS","600618.SS",
       "601216.SS"]
                 
PE = ["600989.SS","600143.SS","300221.SZ","002585.SZ","000859.SZ",
      "002768.SZ","002522.SZ","002735.SZ"]
                   
BU = ["300135.SZ","002377.SZ"]

MA = ["601898.SS","601015.SS","603113.SS","600803.SS","002109.SZ",
      "600722.SS","000683.SZ"]
       
RUBBER = ["600500.SS","601118.SS","002211.SZ","002073.SZ","601966.SS",
          "000599.SZ","000589.SZ","600469.SS","601058.SS"]

SUGAR = ["600737.SS","600191.SS","000576.SZ","000911.SZ","002286.SZ",
         "000848.SZ","600300.SS","603156.SS","603711.SS","600962.SS",
         "002732.SZ"]

FOODOIL = ["000639.SZ","002852.SZ","600127.SS","000505.SZ","002186.SZ",
            "000721.SZ"]

MEAL = ["002311.SZ","000876.SZ","600438.SS","002157.SZ","000702.SZ",
        "002100.SZ","603668.SS","300498.SZ","002741.SZ","002299.SZ",
        "000735.SZ","300761.SZ","002234.SZ"]

COTTON = ["600251.SS","600540.SS","300189.SZ","601339.SS","002042.SZ",
          "002087.SZ","000726.SZ","000850.SZ"]

SHindex = ["000001.SZ"]

##################################################
##################################################
##################################################
METAL = list(set(GOLD+COPPER+ALUMINUM+ZINC+PB+NI+SN))
BLACK = list(set(ORE+COAL+COKE+STEEL))
CHEM = list(set(PTA+PP+PVC+PE+BU+MA+RUBBER))
AGRI = list(set(SUGAR+FOODOIL+MEAL+COTTON))
stockTickers = GOLD+COPPER+ALUMINUM+ZINC+PB+NI+SN+ORE+COAL+COKE+STEEL+GLASS+PTA+PP+PVC+PE+BU+MA+RUBBER+SUGAR+FOODOIL+MEAL+COTTON+SHindex