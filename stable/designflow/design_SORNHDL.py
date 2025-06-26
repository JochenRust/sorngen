##################################################################
##
## file: design_SORNHDL.py
##
## description: sorngen designflow - design HDL SORN functions
##
## (c) 2020 Jochen Rust
##     DSI aerospace technology
##
##################################################################

# function genFctnSORN
    # import packages
import re
# import sys
import numpy as np

#from type_SORN import sornDatatype
from ..datatypes.type_SORN import sornInterval
from ..datatypes.type_SORN import sornFctnTable
from ..datatypes.type_SORN import type_SORN                    # added by MB/Chen 21.10.22
from fractions import Fraction

##def genFctnSORN(OP,*datatypes):
def genFctnSORN(function,*datatypes):
     #""" Defines a SORN LUT object for a certain math. operation.
     #
     #Input Arguments:
     #    OP            -- mathematical operation formatted as a string (eg. "+", "*", "**2", "sqrt", "log", "log2")
     #    datatypes     -- SORN datatype for {IN0/*IN1/OUT} formatted as class "sornDatatype"
     #    
     #Output Arguments:
     #    sornTable    -- object of class "sornTable" containing the input and output datatypes and SORN values
     #"""
    # define the SORN table object
    FctnTab = sornFctnTable()
        
    # determine number of inputs
    FctnTab.Nin = len(datatypes)-1
    if FctnTab.Nin > 3:              # changed ">2" to ">3" by MB/Chen 21.10.22 
        raise Exception("More than 3 inputs are not implemented!")
        
    # set the operation
    # FctnTab.OP = OP
        
    # set the datatypes
    FctnTab.datatypeIN0 = datatypes[0]
    FctnTab.datatypeIN1 = datatypes[1] if FctnTab.Nin > 1 else []
    FctnTab.datatypeIN2 = datatypes[2] if FctnTab.Nin == 3 else []    #added by Chen
    if FctnTab.Nin == 3:
        FctnTab.datatypeOUT = datatypes[3] #added by Chen
    elif FctnTab.Nin == 2:
        FctnTab.datatypeOUT = datatypes[2] 
    else:
        FctnTab.datatypeOUT = datatypes[1] 
    
    # set the pools of SORN values
    FctnTab.poolIN0SORN = np.eye(len(FctnTab.datatypeIN0.intervals), dtype=int)
    FctnTab.poolIN1SORN = np.eye(len(FctnTab.datatypeIN1.intervals), dtype=int) if FctnTab.Nin > 1 else []
    FctnTab.poolIN2SORN = np.eye(len(FctnTab.datatypeIN2.intervals), dtype=int) if FctnTab.Nin == 3 else []#added by Chen
    FctnTab.poolOUTSORN = np.eye(len(FctnTab.datatypeOUT.intervals), dtype=int)
    
    # calculate the resulting intervals
    
    if FctnTab.Nin == 3:            # 3 input section added by Chen
        
        # separate the nested input function into two parts // added by MB 01.11.22
        symbols = re.search(r"[)]*\s.\s[(]*",function) # search for basic operation enclosed by brackets
       
        firstClosingBrackets = re.findall(r"[)]+",symbols[0]) # find the first pattern of consecutive closing brackets
        NoClosingBrackets = len(firstClosingBrackets[0]) # count the number of closing brackets
        for i in range(symbols.start(0)-1,-1,-1):
            # determine the start index of the first equation by counting the closing brackets
            if function[i] == '(':
                NoClosingBrackets -= 1
            elif function[i] == ')':
                NoClosingBrackets += 1
            if NoClosingBrackets == 0:
                startIndex = i
                break

        firstOpeningBrackets = re.findall(r"[(]+",symbols[0]) # find the first pattern of consecutive opening brackets
        NoOpeningBrackets = len(firstOpeningBrackets[0]) # count the number of opening brackets   
        for i in range(symbols.end(0)+1,len(function)):
            # determine the end index of the first equation by counting the opening brackets
            if function[i] == ')':
                NoOpeningBrackets -= 1
            elif function[i] == '(':
                NoOpeningBrackets += 1
            if NoOpeningBrackets == 0:
                endIndex = i
                break

        # noinspection PyUnboundLocalVariable
        operation1 = function[startIndex:endIndex+1]
        operation2 = function.replace(operation1, '(<op0>)')
        operation2 = operation2.replace('op2','op1')
    
        # OLD: grab the operator symbol 
        # symbol = re.findall(r"\)([^\)]*?)\([^0-9]",function)
        # operation1 = "(<op0>)"+symbol[0]+"((<op1>))"
        # operation2 = "(<op0>)"+symbol[1]+"((<op1>))"
        
        # Calculate the first two inputs to get 2D_table
        midtable1 = genFctnSORN(operation1, datatypes[0], datatypes[1],datatypes[3])
        # Calculate each element in the 2D_table with the third input to get 3D_table
        midvalue = type_SORN()
        midvalue.intervals.append([])
        for i in range(0,len(midtable1.datatypeIN0.intervals)):
            FctnTab.resultValues.append([])
            FctnTab.resultSORN.append([])
            for j in range(0,len(midtable1.datatypeIN1.intervals)):
                midvalue.intervals[0] = midtable1.resultValues[i][j]#get sornInterval
                if (midvalue.intervals[0].lowerBoundary==0) and (midvalue.intervals[0].upperBoundary==0) and (midvalue.intervals[0].lowerIsOpen==1) and (midvalue.intervals[0].upperIsOpen==1):
                    FctnTab.resultSORN[i].append([])
                    FctnTab.resultValues[i].append([])
                    for l in range(len(midtable1.resultSORN[i][j])):
                        FctnTab.resultSORN[i][j].append([])
                        FctnTab.resultValues[i][j].append([])
                        FctnTab.resultValues[i][j][l]=midtable1.resultValues[i][j]
                        FctnTab.resultSORN[i][j][l] = midtable1.resultSORN[i][j]
                else:
                    midtable2 = genFctnSORN(operation2, midvalue, datatypes[2],datatypes[3])
                    FctnTab.resultValues[i].append(midtable2.resultValues[0])
                    FctnTab.resultSORN[i].append(midtable2.resultSORN[0])
                    
    elif FctnTab.Nin == 2:
        
        # two inputs
        c_lowerIsOpen = 1 # added by MB 21.05.21
        c_upperIsOpen = 1 # added by MB 21.05.21
        for op0CTR in range(0,len(FctnTab.datatypeIN0.intervals)): # loop over OP0
            FctnTab.resultValues.append([]) # create an (empty) row in the matrix "resultValues"
            FctnTab.resultSORN.append([]) # create an (empty) row in the matrix "resultSORN"
            for op1CTR in range(0,len(FctnTab.datatypeIN1.intervals)): # loop over OP1
                FctnTab.resultSORN[op0CTR].append([]) # create an (empty) col in the matrix "resultSORN"
                
                # handle signs // added by MR 08.10.24
                OPa_is_neg = (np.sign(FctnTab.datatypeIN0.intervals[op0CTR].lowerBoundary) == -1.0) 
                OPb_is_neg = (np.sign(FctnTab.datatypeIN1.intervals[op1CTR].lowerBoundary) == -1.0)
                divisor_Interval_Contains_Zero = True if(FctnTab.datatypeIN1.intervals[op1CTR].lowerBoundary < 0 < FctnTab.datatypeIN1.intervals[op1CTR].upperBoundary) else False
            
                # left bound of result
                c_startValue = np.inf
                for caseCTR in range(0,4):
                #define for two operands (lower or upper boundary) and convert them to strings
                   OPa = str(FctnTab.datatypeIN0.intervals[op0CTR].lowerBoundary) if ((caseCTR == 0) or (caseCTR == 1)) else str(FctnTab.datatypeIN0.intervals[op0CTR].upperBoundary)
                   OPb = str(FctnTab.datatypeIN1.intervals[op1CTR].lowerBoundary) if ((caseCTR == 0) or (caseCTR == 2)) else str(FctnTab.datatypeIN1.intervals[op1CTR].upperBoundary)
                        # replace "a/b" with "Fraction(a,b)"
                   OPa = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",OPa)    
                   OPb = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",OPb)    
                        # check for infinity value and replace with "np.inf" in string
                   OPa = re.sub("inf", "np.inf", OPa)
                   OPb = re.sub("inf", "np.inf", OPb)
                   cFctn = re.sub('<op0>', OPa, function)
                   cFctn = re.sub('<op1>', OPb, cFctn)
                   cFctn = re.sub(r"(Fraction\([^\)]*\))",r"float(\g<1>)",cFctn) # added by MB 02.11.22
                   
                   # handle isopen conditions // added my MB 21.05.21
                   OPa_isopen = FctnTab.datatypeIN0.intervals[op0CTR].lowerIsOpen if ((caseCTR == 0) or (caseCTR == 1)) else FctnTab.datatypeIN0.intervals[op0CTR].upperIsOpen
                   OPb_isopen = FctnTab.datatypeIN1.intervals[op1CTR].lowerIsOpen if ((caseCTR == 0) or (caseCTR == 2)) else FctnTab.datatypeIN1.intervals[op1CTR].upperIsOpen

                    # handle default and normal functions/operators
#                   try:
#                       c_intValue = eval(cFctn)
#                   except NameError:
#                       c_intValue = eval('np.'+cFctn)
                   if np.count_nonzero(eval(OPb)) == 0 and cFctn.find("/") > -1 and OPb_isopen == False: # added by MB 11.06.21: search for divison by zero, changed by MR 08.10.2024: division by zero = NaN only when Interval closed (0 within) otherwhise inf
                        c_intValue = np.nan
                   elif np.count_nonzero(eval(OPb)) == 0 and cFctn.find("/") > -1 and OPb_isopen == True and np.count_nonzero(eval(OPa)) == 0:
                        c_intValue = np.nan
                   elif np.count_nonzero(eval(OPb)) == 0 and cFctn.find("/") > -1 and OPb_isopen == True and (OPa_is_neg ^ OPb_is_neg): #added by MR 08.10.24 division by zero = NaN only when Interval closed (0 within) otherwhise inf
                       c_intValue = -np.inf
                   elif np.count_nonzero(eval(OPb)) == 0 and cFctn.find("/") > -1 and OPb_isopen == True and not(OPa_is_neg ^ OPb_is_neg): #added by MR 08.10.24 division by zero = NaN only when Interval closed (0 within) otherwhise inf
                       c_intValue = np.inf
                   else:
                        c_intValue = round(eval(cFctn),14)              # round(...,14) added by MB 14-11-24 because 0.05 - 0.15 results in -0.09999999999999999
                        #c_intValue = eval(OPa + FctnTab.OP + OPb)
                        
                   if c_intValue < c_startValue:
                        c_startValue = c_intValue
                        c_lowerIsOpen = int(OPa_isopen or OPb_isopen) # added by MB 21.05.21
                        # caseLower = caseCTR # added by MB 21.05.21
                   elif (c_intValue == c_startValue) or (np.isneginf(float(c_intValue)) and np.isneginf(float(c_startValue))) or (np.isposinf(float(c_intValue)) and np.isposinf(float(c_startValue))): # added by MB 21.05.21 // changed c_startValue --> float(c_startValue) 30.08.22
                        c_startValue = c_intValue  # added by MB 21.05.21
                        c_lowerIsOpen = int((c_lowerIsOpen and OPa_isopen) or (c_lowerIsOpen and OPb_isopen)) # added by MB 21.05.21
                        # caseLower = caseCTR # added by MB 21.05.21
                                                                            
                
                      # right bound of result
                c_endValue = -np.inf
                       
                for caseCTR in range(0,4):
                    # define the two operands (lower or upper boundary) and convert them to strings
                    OPa = str(FctnTab.datatypeIN0.intervals[op0CTR].lowerBoundary) if ((caseCTR == 0) or (caseCTR == 1)) else str(FctnTab.datatypeIN0.intervals[op0CTR].upperBoundary)
                    OPb = str(FctnTab.datatypeIN1.intervals[op1CTR].lowerBoundary) if ((caseCTR == 0) or (caseCTR == 2)) else str(FctnTab.datatypeIN1.intervals[op1CTR].upperBoundary)
                    # replace "a/b" with "Fraction(a,b)"
                    OPa = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",OPa)    
                    OPb = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",OPb)     
                    # check for infinity value and replace with "np.inf" in string
                    OPa = re.sub("inf", "np.inf", OPa)
                    OPb = re.sub("inf", "np.inf", OPb)
                    cFctn = re.sub('<op0>', OPa, function)
                    cFctn = re.sub('<op1>', OPb, cFctn)
                    cFctn = re.sub(r"(Fraction\([^\)]*\))",r"float(\g<1>)",cFctn) # added by MB 02.11.22
                    #c_intValue = eval(cFctn)
                    
                    # handle isopen conditions // added my MB 21.05.21
                    OPa_isopen = FctnTab.datatypeIN0.intervals[op0CTR].lowerIsOpen if ((caseCTR == 0) or (caseCTR == 1)) else FctnTab.datatypeIN0.intervals[op0CTR].upperIsOpen
                    OPb_isopen = FctnTab.datatypeIN1.intervals[op1CTR].lowerIsOpen if ((caseCTR == 0) or (caseCTR == 2)) else FctnTab.datatypeIN1.intervals[op1CTR].upperIsOpen

                    # handle default and normal functions/operators
#                    try:
#                        c_intValue = eval(cFctn)
#                    except NameError:
#                        c_intValue = eval('np.'+cFctn)
          
                    if np.count_nonzero(eval(OPb)) == 0 and cFctn.find("/") > -1 and OPb_isopen == False: # added by MB 11.06.21: search for divison by zero, changed by MR 08.10.2024: division by zero = NaN only when Interval closed (0 within) otherwhise inf
                        c_intValue = np.nan
                    elif np.count_nonzero(eval(OPb)) == 0 and cFctn.find("/") > -1 and OPb_isopen == True and np.count_nonzero(eval(OPa)) == 0: # added by MR 08.10.24 division by zero; if denominator is 0, then result is 0
                         c_intValue = np.nan
                    elif np.count_nonzero(eval(OPb)) == 0 and cFctn.find("/") > -1 and OPb_isopen == True and (OPa_is_neg ^ OPb_is_neg): #added by MR 08.10.24 division by zero = NaN only when Interval closed (0 within) otherwhise inf
                        c_intValue = -np.inf
                    elif np.count_nonzero(eval(OPb)) == 0 and cFctn.find("/") > -1 and OPb_isopen == True and not(OPa_is_neg ^ OPb_is_neg): #added by MR 08.10.24 division by zero = NaN only when Interval closed (0 within) otherwhise inf
                        c_intValue = np.inf
                    else:
                        c_intValue = round(eval(cFctn),14)              # round(...,14) added by MB 14-11-24 because 0.05 - 0.15 results in -0.09999999999999999
                    #print(cFctn)
                    #c_intValue = eval(OPa + FctnTab.OP + OPb)
                    if c_intValue > c_endValue: 
                        c_endValue = c_intValue
                        c_upperIsOpen = int(OPa_isopen or OPb_isopen) # added by MB 21.05.21
                        # caseUpper = caseCTR # added by MB 21.05.21
                    elif (c_intValue == c_endValue) or (np.isneginf(float(c_intValue)) and np.isneginf(float(c_endValue))) or (np.isposinf(float(c_intValue)) and np.isposinf(float(c_endValue))): # added by MB 21.05.21 // changed c_endValue --> float(c_endValue) 30.08.22
                        c_endValue = c_intValue  # added by MB 21.05.21
                        c_upperIsOpen = int((c_upperIsOpen and OPa_isopen) or (c_upperIsOpen and OPb_isopen)) # added by MB 21.05.21
                        # caseUpper = caseCTR # added by MB 21.05.21
                        
                # calculate the "isopen" condition rewritten by MB 21.05.21
                #c_lowerIsOpen = 0 if (np.absolute(c_startValue) >= np.absolute(c_endValue)) else 1
                #c_upperIsOpen = 0 if (np.absolute(c_startValue) <= np.absolute(c_endValue)) else 1    
                                        
                # store the result values
                FctnTab.resultValues[op0CTR].append(sornInterval(c_startValue,c_endValue,c_lowerIsOpen,c_upperIsOpen))
                
                # DEBUG MB 21.05.21
                # print('\n===== DEBUG MB 21.05.21 =====',end='\n')
                # print('OP0:',end='\t')
                # print(FctnTab.datatypeIN0.intervals[op0CTR].getName(),end='\t')
                # print('OP1:',end='\t')
                # print(FctnTab.datatypeIN1.intervals[op1CTR].getName(),end='\t')
                # print('Function:\t'+function,end='\n')
                # print('Result:',end='\t')        
                # print(sornInterval(c_startValue,c_endValue,c_lowerIsOpen,c_upperIsOpen).getName(),end='\t')
                # print('Lower Case: '+str(caseLower)+'\tUpper Case: '+str(caseUpper),end='\n')
                # print(OPa_isopen,end='\n')                
                # print('===== END DEBUG =====',end='\n')
                
                # generate the SORN result
                c_SORN = []
                for poolCTR in range(0,len(FctnTab.datatypeOUT.intervals)):
                    c_poolStartValue = round(float(FctnTab.datatypeOUT.intervals[poolCTR].lowerBoundary),14)    # round((float(...),14) added by MB 26-11-24 to match the rounding of c_intValue from above
                    c_poolEndValue = round(float(FctnTab.datatypeOUT.intervals[poolCTR].upperBoundary),14)      # round((float(...),14) added by MB 26-11-24 to match the rounding of c_intValue from above
                    c_poolLowerIsOpen = FctnTab.datatypeOUT.intervals[poolCTR].lowerIsOpen
                    c_poolUpperIsOpen = FctnTab.datatypeOUT.intervals[poolCTR].upperIsOpen
                    if (c_endValue < c_poolStartValue) or ((c_endValue == c_poolStartValue) and (c_upperIsOpen == 1 or c_poolLowerIsOpen == 1)) or (c_startValue > c_poolEndValue) or ((c_startValue == c_poolEndValue) and (c_lowerIsOpen == 1 or c_poolUpperIsOpen == 1)):
                        c_SORN.append(0)
                    else:
                        c_SORN.append(1)
                
                # check for NAN (all bits '0') and replace with all bits '1' // added by MB 25/08/22
                if c_SORN.count(1) == 0:
                    for bit in range(0,len(c_SORN)):
                        c_SORN[bit] = 1
                
                # store the SORN results
                FctnTab.resultSORN[op0CTR][op1CTR] = c_SORN 
                
    elif FctnTab.Nin == 1:
    
        # Added by MB 24-06-25: set reciprocal flag
        # symbol = re.findall(r"/",function)
        symbol = re.findall(r"/|\*\*\-|\*\*\(\-",function) ## Added by MB 26-06-25: search not only for slash "/" but also for "**-" or "**(-" defining a reciprocal with negative exponent
        reciprocal = 1 if len(symbol) >0 else 0
    
        # one input
        for op0CTR in range(0,len(FctnTab.datatypeIN0.intervals)): # loop over OP0
        
            c_startValue = np.inf # left bound of result
            c_endValue = -np.inf # right bound of result
            for caseCTR in range(0,2):
                OPa = str(FctnTab.datatypeIN0.intervals[op0CTR].lowerBoundary) if (caseCTR == 0) else str(FctnTab.datatypeIN0.intervals[op0CTR].upperBoundary)
                OPa = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",OPa)    # replace "a/b" with "Fraction(a,b)"
                OPa = re.sub("inf", "np.inf", OPa) 
                # check for infinity value and replace with "np.inf" in string
                # determine the kind of operation
                #if re.search(r"[a-zA-Z]+[\d]*",FctnTab.OP):
                #    c_intValue = eval("np." + FctnTab.OP + "(float(" + OPa + "))")
                #else:
                
                cFctn = re.sub('<op0>', OPa, function)
                cFctn = re.sub(r"(Fraction\([^\)]*\))",r"float(\g<1>)",cFctn) # added by MB 02.11.22
                
                # Added by MB 25-06-25: catch division by open/closed zero for reciprocal
                OPa_is_neg = (np.sign(FctnTab.datatypeIN0.intervals[op0CTR].lowerBoundary) == -1.0) 
                OPa_is_zero = (np.count_nonzero(eval(OPa)) == 0)
                OPa_is_open = FctnTab.datatypeIN0.intervals[op0CTR].lowerIsOpen if (caseCTR == 0) else FctnTab.datatypeIN0.intervals[op0CTR].upperIsOpen
                if reciprocal and OPa_is_zero and OPa_is_open:
                    if OPa_is_neg:
                        c_intValue = -np.inf
                    else:
                        c_intValue = np.inf
                elif reciprocal and OPa_is_zero:
                    c_intValue = np.nan
                else:
                    # handle default and normal functions/operators
                    try:
                        c_intValue = eval(cFctn)
                    except NameError:
                        c_intValue = eval('np.'+cFctn)
                    
                if c_intValue < c_startValue or np.isnan(float(c_intValue)):
                    c_startValue = c_intValue
                if c_intValue > c_endValue or np.isnan(float(c_intValue)):
                    c_endValue = c_intValue
                    
            # calculate the "isopen" condition
            if reciprocal == 1: # Added by MB 24-06-25
                c_lowerIsOpen = FctnTab.datatypeIN0.intervals[op0CTR].upperIsOpen
                c_upperIsOpen = FctnTab.datatypeIN0.intervals[op0CTR].lowerIsOpen
            else:
                c_lowerIsOpen = 0 if (np.absolute(c_startValue) >= np.absolute(c_endValue)) else 1
                c_upperIsOpen = 0 if (np.absolute(c_startValue) <= np.absolute(c_endValue)) else 1
                    
            # store the results
            FctnTab.resultValues.append(sornInterval(c_startValue,c_endValue,c_lowerIsOpen,c_upperIsOpen))
            
            # generate the SORN result
            c_SORN = []
            for poolCTR in range(0,len(FctnTab.datatypeOUT.intervals)):
                c_poolStartValue = FctnTab.datatypeOUT.intervals[poolCTR].lowerBoundary
                c_poolEndValue = FctnTab.datatypeOUT.intervals[poolCTR].upperBoundary
                c_poolLowerIsOpen = FctnTab.datatypeOUT.intervals[poolCTR].lowerIsOpen
                c_poolUpperIsOpen = FctnTab.datatypeOUT.intervals[poolCTR].upperIsOpen
                if np.isnan(float(c_startValue)) or np.isnan(float(c_endValue)) or (c_endValue < c_poolStartValue) or ((c_endValue == c_poolStartValue) and (c_upperIsOpen == 1 or c_poolLowerIsOpen == 1)) or (c_startValue > c_poolEndValue) or ((c_startValue == c_poolEndValue) and (c_lowerIsOpen == 1 or c_poolUpperIsOpen == 1)):
                    c_SORN.append(0)
                else:
                    c_SORN.append(1)
            
            # store the SORN results
            FctnTab.resultSORN.append(c_SORN)
            


########################
#     ## debug
#     probTable = np.zeros((len(FctnTab.datatypeIN0.intervals), len(FctnTab.datatypeIN0.intervals)), dtype=int)
    
    
#     for k in range(0,len(FctnTab.datatypeIN0.intervals)):
        
#         for i in range(0,len(FctnTab.datatypeIN1.intervals)): 
           
        
#             for j in range(0,len(FctnTab.datatypeIN1.intervals)):
#                 probTable[i][j] = probTable[i][j] + FctnTab.resultSORN[i][j][k]
#                 print(FctnTab.resultSORN[i][j][k], end='')
#             print('')
#         print('')
                
   
#     print('')
#     print(probTable)
        
# #    sys.exit(0)  

########################                
    # return the output
    return FctnTab
    
# EOF genFctnSORN