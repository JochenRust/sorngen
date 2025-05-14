# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 14:55:13 2024

@author: Administrator
"""

# note: you have to insert the path of the SORN_HW_Generator folder under tools->PYTHONPATH
#from SORN_HW_Generator.datatypes.type_SORN import sornInterval
#from SORN_HW_Generator.datatypes.type_SORN import sornFctnTable
#from SORN_HW_Generator.datatypes.type_SORN import type_SORN    
from stable.designflow.design_SORNHDL import genFctnSORN
from stable.designflow.design_SORN import createSORN

# create DTs
DT1 = createSORN("lin", "[0,0.15,0.05]", "zero","infinity","negative")
# DT2 = createSORN("log", "[-2,0]", "zero","infinity","negative")
DT2 = createSORN("man","{[-inf,-0.15);[-0.15,-0.1);[-0.1,-0.05);[-0.05,0);[0,0];(0,0.05];(0.05,0.1];(0.1,0.15];(0.15,inf]}")

DT1.showIV()
DT2.showIV()

# create LUTs

LUT1add = genFctnSORN("(<op0>) + (<op1>)", DT1,DT1,DT1)
LUT2add = genFctnSORN("(<op0>) + (<op1>)", DT2,DT2,DT2)

# access LUT
print(LUT1add.resultValues[0][5].getName())
print(LUT1add.resultSORN[2][3])
# print(LUT2add.resultValues[1][2].getName())
# print(LUT2add.resultSORN[1][2])