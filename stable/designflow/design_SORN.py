##################################################################
##
## file: design_SORN.py
##
## description: sorngen designflow - set up SORN datatypes
##
## (c) 2018/2019 Moritz Bärthel
##     University of Bremen
## (c) 2020 Jochen Rust
##     DSI aerospace technology
##
##################################################################


## import packages
import re 					
import numpy as np
from ..datatypes import type_SORN as SORN
from ..datatypes.type_SORN import sornInterval
from fractions import Fraction

# function defineSORN 
def createSORN(style,res_str,*varargs):
	""" Defines the interval ranges and boundary conditions of a SORN datatype.
	
	Input Arguments:
		style = "lin"/"log"/"man"      			 -- defines the shape of the SORN datatype ("man": manually defined datatype)
		res_str = (start,end,*step)     			 -- defines the start and endpoints of the datatype (start...end for linear style with stepsize step, 2^start...2^end for logarithmic style)
		varargs = "zero","infinity","negative"   -- when set, the datatype includes zero and/or infinity and negative values
	
	Output Arguments:
		DATATYPE		-- formatted as class "sornDatatype"
	"""
	
	
	## 1/ set arguments
	ENABLE_ZERO = 0
	ENABLE_INFTY = 0
	ENABLE_NEGATIVE = 0
	ENABLE_LINEAR = 1 if re.search(r"[lL]in(ear)?",style) else 0
	ENABLE_MANUAL = 1 if re.search(r"[mM][aA][nN]",style) else 0
	
	## 2/ build value sequence
	valSeq_LEFT = [] 	# sequence of values of the left interval bound 
	valSeq_RIGHT = []	# sequence of values of the right interval bound
	
	# 2.1/ set interval conditions
	condSeq_LEFT = [] # entries: isopen=0/1
	condSeq_RIGHT = []
	
	if ENABLE_MANUAL == 0:  
	
		for arg in varargs:
			ENABLE_ZERO = 1 if re.search(r"[zZ]ero",arg) else ENABLE_ZERO
			ENABLE_INFTY = 1 if re.search(r"[iI]nf(inity)?",arg) else ENABLE_INFTY
			ENABLE_NEGATIVE = 1 if re.search(r"[nN]eg(ative)?",arg) else ENABLE_NEGATIVE
			
		# 2.2/ replace fractions with "Fraction(...)" 
		res_str = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",res_str)
		
		# 2.3/ evaluate input "res_str" (Resolution)
		res=eval(res_str)
		
		
		# 2.4/ zero
		if ENABLE_ZERO == 1:
			valSeq_LEFT.append(0)
			valSeq_RIGHT.append(0)
		# 2.5/ logarithmic style	
		if ENABLE_LINEAR == 0: 
			# 2.5.1/ positive numbers
			for element_CNT in range(res[0],res[1]+1):
				valSeq_LEFT.append(0.0 if element_CNT == res[0] else 2**(element_CNT-1))
				valSeq_RIGHT.append(2**element_CNT)
		# 2.6/ linear style
		elif ENABLE_LINEAR == 1: 
			# 2.6.1/ positive numbers
			for element_CNT in range(int(res[0]/res[2]),int(round(res[1]/res[2]))):     # round() added by MB 14-11-24 because 0.15/0.5 was calculated to 2.99999 and rounded to 2 instead of 3
				valSeq_LEFT.append(round(element_CNT*res[2],15))    # round(...,15) added by MB 14-11-24 because 3*0.05 results in 0.15000000000000002
				valSeq_RIGHT.append(round((element_CNT+1)*res[2],15)) 
		# 2.7/ infinity
		if ENABLE_INFTY == 1:
			valSeq_LEFT.append(valSeq_RIGHT[-1])
			valSeq_RIGHT.append(np.inf)
		# 2.8/ negative numbers
		if ENABLE_NEGATIVE == 1:
			for element_CNT in range(0,len(valSeq_LEFT)-1):
				valSeq_LEFT.insert(0,-valSeq_RIGHT[2*element_CNT+1])
				valSeq_RIGHT.insert(0,-valSeq_LEFT[2*element_CNT+2])
		
		## 3/ set interval conditions
		condSeq_LEFT = [] # entries: isopen=0/1
		condSeq_RIGHT = []
	
		for index in range(0,len(valSeq_LEFT)):
			# 3.1/ negative and zero values     (changed/added by MB 20-01-2025 to fix an issue with open/closed zero interval bounds when using datatypes without negatives)
			if ENABLE_NEGATIVE and ENABLE_ZERO:
                # negatives
				if index < (len(valSeq_LEFT)-1)/2:
					condSeq_LEFT.append(0) 
					condSeq_RIGHT.append(1)
                # zero
				elif index == (len(valSeq_LEFT)-1)/2: 
					condSeq_LEFT.append(0)
					condSeq_RIGHT.append(0)
                # positives
				elif index > (len(valSeq_LEFT)-1)/2: 
					condSeq_LEFT.append(1) 
					condSeq_RIGHT.append(0)
			# 3.2/ zero value without negatives or no exact zero value                
			else:
                # zero (exact or in first interval)
				if index == 0: 
					condSeq_LEFT.append(0)
					condSeq_RIGHT.append(0)
                # positives
				elif index > 0: 
					condSeq_LEFT.append(1) 
					condSeq_RIGHT.append(0)
				
	elif ENABLE_MANUAL == 1:
	
		## 4/ manually specified style
		# 4.1/ replace "inf" with "np.inf"
		res_str = re.sub("inf","np.inf",res_str)
		
		# 4.2/ separate the input string into single strings for the different intervals
		int_seq_str = re.findall(r"(?<=[\{;]).+?(?=[;\}])",res_str)
		
		# 4.3/ iterate through specified intervals and store them in required format
		for int_el in int_seq_str:
			# 4.3.1/ evaluate the bracket
			cond_LEFT = 1 if re.search("\(",int_el) else 0
			cond_RIGHT = 1 if re.search("\)",int_el) else 0
			# 4.3.2/ find the values
			val_LEFT = re.findall(r".+(?=,)",int_el)
			val_RIGHT = re.findall(r"(?<=,).+",int_el)
			# 4.3.3/ remove the brackets
			val_LEFT[0] = re.sub(r"[\(\[]",r"",val_LEFT[0])
			val_RIGHT[0] = re.sub(r"[\]\)]",r"",val_RIGHT[0])
			# 4.3.4/ replace fractions with "Fraction(...)" 
			val_LEFT[0] = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",val_LEFT[0])
			val_RIGHT[0] = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",val_RIGHT[0])
			# 4.3.5/ append the final values to their list
			valSeq_LEFT.append(eval(val_LEFT[0]))
			valSeq_RIGHT.append(eval(val_RIGHT[0]))
			condSeq_LEFT.append(cond_LEFT)
			condSeq_RIGHT.append(cond_RIGHT)
			
	## 5/ convert to sornDatatype class
	DATATYPE = SORN.type_SORN()
	for index in range(0,len(valSeq_LEFT)):
		DATATYPE.intervals.append(sornInterval(valSeq_LEFT[index],valSeq_RIGHT[index],condSeq_LEFT[index],condSeq_RIGHT[index]))
	
	## 6/ return SORN datatype
	DATATYPE.sornsize = len(valSeq_LEFT)
	
	return DATATYPE
