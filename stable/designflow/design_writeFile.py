##################################################################
##
## file: design_writeFile.py
##
## description: sorngen designflow - write data to file
##
## (c) 2020 Jochen Rust
##     DSI aerospace technology
##
#################################################################
import os
import string
# import sys
import re

from stable.datatypes import type_SST as sst

def writeEqsToVHDL(env, HDL, name, st):

	## 1/ header: set default data
	header = string.Template(st["header"]).substitute({'version': "0.1", 'filename': name+".vhd", 'author': "n/a", 'info': "SORNGEN TOPLEVEL", 'date': "2019"})
	# write to template
	# toplevel = header

	## 2/ entity
	inputPorts = ""
	outputPorts = ""
	# 2.1/ sequential ports
	if HDL.instances[0].nodeSST.SST.hasRegister: inputPorts = inputPorts + st['sequential_port_declarations']
	# 2.2/ extract global ports from environment
	for it in HDL.ports:
		if it.isGlobal:
			if it.isInput:
				inputPorts = inputPorts + string.Template(st["port_declaration"]).substitute({'portname': it.name, 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
			else:
				outputPorts = outputPorts + string.Template(st["port_declaration"]).substitute({'portname': it.name, 'direction': "OUT", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"

	# cleanup
	inputPorts=inputPorts[0:-1]
	outputPorts=outputPorts[0:-2]
	# write to template
	entity =  string.Template(st["entity"]).substitute({'entityname': name, 'inputports': inputPorts, 'outputports': outputPorts})


	## 3/ components
	hasRegister = False
	components=""
	for it in HDL.instances:
		# 3.1/ catch register component
		if it.nodeSST.type == sst.typeNode.REGISTER:
			if not hasRegister: components = components+st["register_component"]
			hasRegister = True
			continue

		# 3.2/ other components
		inputPorts = ""
		outputPorts = ""
		for it2 in it.ports:
				if it2.isInput:
					inputPorts = inputPorts + string.Template(st["port_declaration"]).substitute({'portname': it2.name, 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
				else:
					outputPorts = outputPorts + string.Template(st["port_declaration"]).substitute({'portname': it2.name, 'direction': "OUT", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
		# ports cleanup
		inputPorts=inputPorts[0:-1]
		outputPorts=outputPorts[0:-2]
		components = components+string.Template(st["component"]).substitute({'componentname': it.name, 'inputports': inputPorts, 'outputports': outputPorts})


	## 4/ signals
	signals=""
	for it in HDL.nets:
		signals = signals + string.Template(st["signal_declaration"]).substitute({'signalname': it.name, 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"


	## 5/ instances
	instances=""
	for it in HDL.instances:
		# 3.1/ component ports
		ports = ""
		for it2 in it.ports:
			ports = ports + string.Template(st["port_assignment"]).substitute({'portname': it2.name, 'signalname': it2.nets[0].name})+",\n"
		# ports cleanup
		ports=ports[0:-2]
		# create instance
		if not it.nodeSST.type == sst.typeNode.REGISTER:
			instances = instances + string.Template(st["instance"]).substitute({'instancename': "i_"+it.name, 'componentname': it.name, 'portassignment': ports})+"\n"
		else:
			instances = instances + string.Template(st["register_instance"]).substitute({'instancename': "i_"+it.name, 'uppervalue': env.datatype.sornsize, 'portassignment': ports})+"\n"


	## 6/ assignments
	assignments=""
	for it in HDL.ports:
		if it.isGlobal:
			#print(it.nets)
			if it.isInput:
				assignments = assignments + string.Template(st["signal_assignment"]).substitute({'signalname': it.nets[0].name, 'value': it.name})+";\n"
			else:
				assignments = assignments + string.Template(st["signal_assignment"]).substitute({'signalname': it.name, 'value': it.nets[0].name})+";\n"


	## 6/ architecture
	architecture = string.Template(st["architecture"]).substitute({'behavior': "Behavior", 'archname': name, 'components': components, 'signals': signals, 'instances': instances, 'assignments': assignments})

	## 8/ registers
	if hasRegister:
		with open(f'{env.save_path}/VHDL/VHDLbasic/'+'REG.vhd', 'w') as f:
			f.write(st['register_module'])
		f.close()

	## 7/ toplevel
	with open(f'{env.save_path}/VHDL/'+name+'.vhd', 'w') as f:
		f.write(header+entity+architecture)
	f.close()


def writeTopToVHDL(env, HDL, name, st):

	## 1/ header: set default data
	header = string.Template(st["header"]).substitute({'version': "0.1", 'filename': name+".vhd", 'author': "n/a", 'info': "SORNGEN TOPLEVEL", 'date': "2019"})
	# write to template
	#toplevel = header;

	## 2/ entity
	inputPorts = ""
	outputPorts = ""
	# 2.1/ sequential ports
	if env.hasRegister: inputPorts = inputPorts + st['sequential_port_declarations']
	# 2.2/ extract global ports from environment
	for it in HDL.ports:
		if it.isGlobal:
			if it.isInput:
				inputPorts = inputPorts + string.Template(st["port_declaration"]).substitute({'portname': it.name, 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
			else:
				outputPorts = outputPorts + string.Template(st["port_declaration"]).substitute({'portname': it.name, 'direction': "OUT", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"

	# cleanup
	inputPorts=inputPorts[0:-1]
	outputPorts=outputPorts[0:-2]
	# write to template
	entity =  string.Template(st["entity"]).substitute({'entityname': name, 'inputports': inputPorts, 'outputports': outputPorts})


	## 3/ components
	components=""
	for cValue in env.HDL:
		if cValue.isToplevel: continue
		inputPorts = ""
		outputPorts = ""
		# 3.1/ sequential ports
		if cValue.instances[0].nodeSST.SST.hasRegister: inputPorts = inputPorts + st['sequential_port_declarations']
		# 3.2/ component ports
		for cPort in cValue.ports:
			if not cPort.isGlobal: continue
			if cPort.isInput:
				inputPorts = inputPorts + string.Template(st["port_declaration"]).substitute({'portname': cPort.name, 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
			else:
				outputPorts = outputPorts + string.Template(st["port_declaration"]).substitute({'portname': cPort.name, 'direction': "OUT", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
		# ports cleanup
		inputPorts=inputPorts[0:-1]
		outputPorts=outputPorts[0:-2]
		components = components+string.Template(st["component"]).substitute({'componentname': cValue.name, 'inputports': inputPorts, 'outputports': outputPorts})


	## 4/ signals
	signals=""
	for it in HDL.nets:
		signals = signals + string.Template(st["signal_declaration"]).substitute({'signalname': it.name, 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"


	## 5/ instances
	instances=""
	for cValue in env.HDL:
		if cValue.isToplevel: continue
		ports = ""
		# 5.1/ sequential ports
		if cValue.instances[0].nodeSST.SST.hasRegister: ports = ports + st['sequential_port_assignments']
		# 5.2/ component ports
		for cPort in cValue.ports:
			if not cPort.isGlobal: continue
			## !!! signal input !!!
			netFlag = False
			for it in HDL.nets:
				if  it.ports[0].name == cPort.name:
					ports = ports + string.Template(st["port_assignment"]).substitute({'portname': cPort.name, 'signalname': it.name})+",\n"
					netFlag = True

			if not netFlag:
				ports = ports + string.Template(st["port_assignment"]).substitute({'portname': cPort.name, 'signalname': cPort.name})+",\n"

			#ports = ports + string.Template(st["port_assignment"]).substitute({'portname': cPort.name, 'signalname': cPort.name})+",\n"
			## !!! END OF signal input !!!
		# ports cleanup
		ports=ports[0:-2]
		# create instance
		instances = instances + string.Template(st["instance"]).substitute({'instancename': "i_"+cValue.name, 'componentname': cValue.name, 'portassignment': ports})+"\n"

	## 6/ assignments
	assignments=""
	for it in HDL.nets:
		assignments = assignments + string.Template(st["signal_assignment"]).substitute({'signalname': it.ports[0].name, 'value': it.name})+";\n"
  
	## 6/ architecture
	architecture = string.Template(st["architecture"]).substitute({'behavior': "Behavior", 'archname': name, 'components': components, 'signals': signals, 'instances': instances, 'assignments': assignments})

	## 7/ toplevel
	with open(f'{env.save_path}/VHDL/'+name+'.vhd', 'w') as f:
		f.write(header+entity+architecture)
	f.close()


def writeFunctionToVHDL(env, FctnTab, name, st):
	""" 
	Input Arguments:
		sornTable	-- object of class "sornTable" containing the input and output datatypes and SORN values
		varargs: 	'name'      -- names the file after the string defined afterward
					'author'    -- set author to the string defined afterward
					'info'      -- declaration will be specified as given in the
								string afterward
	"""
	
	## 1/ default assignments
	#author = "unknown"
	#info = "not specified"
	
	## 2/ generate SORN function
	vhdlSTR = ""
	
	# 2.1a/ three input function 		//		added by Chen in 22/06/2022
	if FctnTab.Nin == 3:
		# 2.1a.1/ loop over bits in result
		for digitCTR in range(0,len(FctnTab.poolOUTSORN)): 
			isFirstDigit = 0
			vhdlSTR = vhdlSTR + "result(" + str(digitCTR) + ") <= "
			# 2.1a.2/ loop over values in operand 0
			for op0CTR in range(0,len(FctnTab.poolIN0SORN)): 
				# 2.1a.3/ loop over values in operand 1
				for op1CTR in range(0,len(FctnTab.poolIN1SORN)): 
					hasDigitONE = 0
					for op2CTR in range(0,len(FctnTab.poolIN2SORN)):
						c_SORN = FctnTab.resultSORN[op0CTR][op1CTR][op2CTR]
						# 2.1a.4/ write resulting assignment
						if c_SORN[digitCTR] == 1:
							if hasDigitONE == 1 or isFirstDigit == 1:
								vhdlSTR = vhdlSTR + "or "
							isFirstDigit = 1
							hasDigitONE = 1
							vhdlSTR = vhdlSTR + "(x0(" + str(op0CTR) + ") and x1(" + str(op1CTR) + ") and x2(" + str(op2CTR) + ")) "
				# 2.1a.5/ write end of line
				if op0CTR == len(FctnTab.poolIN0SORN)-1:
					if isFirstDigit == 0:
						vhdlSTR = vhdlSTR + " '0'"
					vhdlSTR = vhdlSTR + ";\n"
					# hasDigitONE = 0
	
	# 2.1/ two input function
	if FctnTab.Nin == 2:
		
		# 2.1.1/ loop over bits in result
		for digitCTR in range(0,len(FctnTab.poolOUTSORN)): 
			isFirstDigit = 0
			vhdlSTR = vhdlSTR + "result(" + str(digitCTR) + ") <= "
			# 2.1.2/ loop over values in operand 0
			for op0CTR in range(0,len(FctnTab.poolIN0SORN)): 
				hasDigitONE = 0
				# 2.1.3/ loop over values in operand 1
				for op1CTR in range(0,len(FctnTab.poolIN1SORN)): 
					c_SORN = FctnTab.resultSORN[op0CTR][op1CTR]
					# 2.1.4/ write resulting assignment
					if c_SORN[digitCTR] == 1:
						if hasDigitONE == 1 or isFirstDigit == 1:
							vhdlSTR = vhdlSTR + "or "
						isFirstDigit = 1
						hasDigitONE = 1
						vhdlSTR = vhdlSTR + "(x0(" + str(op0CTR) + ") and x1(" + str(op1CTR) + ")) "
				# 2.1.5/ write end of line
				if op0CTR == len(FctnTab.poolIN0SORN)-1:
					if isFirstDigit == 0:
						vhdlSTR = vhdlSTR + " '0'"
					vhdlSTR = vhdlSTR + ";\n"
					# hasDigitONE = 0
		
	# 2.2/ one input function	
	elif FctnTab.Nin == 1:
		
		# 2.2.1/ loop over bits in result
		for digitCTR in range(0,len(FctnTab.poolOUTSORN)):
			isFirstDigit = 0
			vhdlSTR = vhdlSTR + "result(" + str(digitCTR) + ") <= "
			# 2.2.2/ loop over values in operand 0
			for op0CTR in range(0,len(FctnTab.poolIN0SORN)):
				hasDigitONE = 0
				c_SORN = FctnTab.resultSORN[op0CTR]
				# 2.2.3/ write resulting assignment
				if c_SORN[digitCTR] == 1:
					if hasDigitONE == 1 or isFirstDigit == 1:
						vhdlSTR = vhdlSTR + "or "
					isFirstDigit = 1
					# hasDigitONE = 1
					vhdlSTR = vhdlSTR + "x0(" + str(op0CTR) + ") "
				# 2.2.4/ write end of line
				if op0CTR == len(FctnTab.poolIN0SORN)-1:
					if isFirstDigit == 0:
						vhdlSTR = vhdlSTR + " '0'"
					vhdlSTR = vhdlSTR + ";\n"
					# hasDigitONE = 0
	
	# 2.3/ remove space at the end of every line (") ;" -> ");")
	vhdlSTR = re.sub(r"\)\s;", r");", vhdlSTR)
	
	# 2.4/ generate comments
	vhdlIN0commentSTR = ""
	vhdlIN1commentSTR = ""
	vhdlIN2commentSTR = ""		#added by Chen
	vhdlOUTcommentSTR = ""
	for poolCTR in range(0,len(FctnTab.poolIN0SORN)):
		vhdlIN0commentSTR = vhdlIN0commentSTR + "-- x0(" + str(poolCTR) + "): " + FctnTab.datatypeIN0.intervals[poolCTR].getName() + "\n"
	if FctnTab.Nin > 1:		# changed by Chen
		for poolCTR in range(0,len(FctnTab.poolIN1SORN)):
			vhdlIN1commentSTR = vhdlIN1commentSTR + "-- x1(" + str(poolCTR) + "): " + FctnTab.datatypeIN1.intervals[poolCTR].getName() + "\n"
	if FctnTab.Nin == 3:	# added by Chen
		for poolCTR in range(0,len(FctnTab.poolIN2SORN)):
			vhdlIN2commentSTR = vhdlIN2commentSTR + "-- x2(" + str(poolCTR) + "): " + FctnTab.datatypeIN2.intervals[poolCTR].getName() + "\n"
	for poolCTR in range(0,len(FctnTab.poolOUTSORN)):
		vhdlOUTcommentSTR = vhdlOUTcommentSTR + "-- result(" + str(poolCTR) + "): " + FctnTab.datatypeOUT.intervals[poolCTR].getName() + "\n"

		
	## 3/ assign to VHDL function template

	# 3.1/ header: set default data
	header = string.Template(st["header"]).substitute({'version': "0.1", 'filename': name+".vhd", 'author': "n/a", 'info': "SORN function", 'date': "2019"})

	# 3.2/ entity
	inputPorts = string.Template(st["port_declaration"]).substitute({'portname': "input0", 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
	if FctnTab.Nin > 1:		# changed by Chen
		inputPorts = inputPorts + string.Template(st["port_declaration"]).substitute({'portname': "input1", 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
	if FctnTab.Nin == 3:	# added by Chen
		inputPorts = inputPorts + string.Template(st["port_declaration"]).substitute({'portname': "input2", 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
	outputPorts = string.Template(st["port_declaration"]).substitute({'portname': "output0", 'direction': "OUT", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
	# 3.2.1/ cleanup
	inputPorts=inputPorts[0:-1]
	outputPorts=outputPorts[0:-2]
	# 3.2.2/ write to template
	entity =  string.Template(st["entity"]).substitute({'entityname': name, 'inputports': inputPorts, 'outputports': outputPorts})

	# 3.3/ comments
	comments = string.Template(st["function_comments"]).substitute({'commentInput0': vhdlIN0commentSTR,
																	'commentInput1': vhdlIN1commentSTR if FctnTab.Nin > 1 else "-- none",
																	'commentInput2': vhdlIN2commentSTR if FctnTab.Nin > 2 else "-- none",
																	'commentResult': vhdlOUTcommentSTR})

	# 3.4/ signal declaration
	signals = string.Template(st["signal_declaration"]).substitute({'signalname': "x0", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
	if FctnTab.Nin > 1:	# changed by Chen
		signals = signals + string.Template(st["signal_declaration"]).substitute({'signalname': "x1", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
	if FctnTab.Nin == 3:	# added by Chen
		signals = signals + string.Template(st["signal_declaration"]).substitute({'signalname': "x2", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
	signals = signals + string.Template(st["signal_declaration"]).substitute({'signalname': "result", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"

	# 3.5/ signal assignments
	assignments= string.Template(st["signal_assignment"]).substitute({'signalname': "x0", 'value': "input0"})+";\n"
	if FctnTab.Nin > 1:		# changed by Chen
		assignments= assignments + string.Template(st["signal_assignment"]).substitute({'signalname': "x1", 'value': "input1"})+";\n"
	if FctnTab.Nin == 3: 	# added by Chen
		assignments= assignments + string.Template(st["signal_assignment"]).substitute({'signalname': "x2", 'value': "input2"})+";\n"
	assignments= assignments + string.Template(st["signal_assignment"]).substitute({'signalname': "output0", 'value': "result"})+";\n"

	# 3.6/ function
	instances = vhdlSTR

	# 3.7/ architecture
	architecture = string.Template(st["architecture"]).substitute({'behavior': "Behavior", 'archname': name, 'components': "-- none", 'signals': signals, 'instances': instances, 'assignments': assignments})

	## 4/ write to file
	with open(f"{env.save_path}/VHDL/VHDLbasic/" + name + ".vhd", "w") as f:
		f.write(header+entity+comments+architecture)
#		print(templateSTR, file=f)
	f.close()



def writeToVHDL(env):
	# 1/ load templates
	st = loadVHDLTemplates(env.execPath)
	# 2/ generate VHDL instances for each equation

	print("")
	print("--------")
	print("-- Write VHDL data")
	print("--------")

	for inst in env.HDL:
		if inst.isToplevel:
			writeTopToVHDL(env, inst, inst.name, st)
			print("Toplevel: "+inst.name+" generated")
		else:
			writeEqsToVHDL(env, inst, inst.name, st)
			print("Module: "+inst.name+" generated")

			# 3/ generate VHDL files for basic operations
			for cInst in inst.instances:
				if cInst.nodeSST.type == sst.typeNode.REGISTER: continue
#               write2VHDL(cInst.FctnTable,'name',cInst.FctnTable.name)
				writeFunctionToVHDL(env, cInst.FctnTable, cInst.FctnTable.name, st)
                # writeFunctionToVHDL(env, cInst.FctnTable, env.name+"_"+cInst.FctnTable.name, st)   # env.name added by MB 30-07-2024 to change entity name of LUT modules to inlcude the design name; not compatible with top level modules, use only when using the basic LUT modules without toplevels
				print("  Submodule: "+cInst.name+" generated")

	print(f"SUCCESS: VHDL data generated in {os.path.abspath(env.save_path)}")

#           
#        print(inst)
#        print(inst.isToplevel)

# =============================================================================
#     for lValueDictHDL in env.HDL:
#         if env.HDL[lValueDictHDL].isToplevel:
#             writeTopToVHDL(env, env.HDL[lValueDictHDL], env.HDL[lValueDictHDL].name, st)
#         else:
#             writeEqsToVHDL(env, env.HDL[lValueDictHDL], env.HDL[lValueDictHDL].name, st)
# 		
# 			# 3/ generate VHDL files for basic operations
#             for cInst in env.HDL[lValueDictHDL].instances:
#                 if cInst.nodeSST.type == sst.typeNode.REGISTER: continue
# #                write2VHDL(cInst.FctnTable,'name',cInst.FctnTable.name)
#                 writeFunctionToVHDL(env, cInst.FctnTable, cInst.FctnTable.name, st)
# 
# =============================================================================

def loadVHDLTemplates(path):
	st = {}
	with open(path+'templates/VHDL_entity.stpy', 'r') as f:
		st["entity"] = f.read()
	f.close()
	with open(path+'templates/VHDL_component.stpy', 'r') as f:
		st["component"] = f.read()
	f.close()
	with open(path+'templates/VHDL_architecture.stpy', 'r') as f:
		st["architecture"] = f.read()
	f.close()
	with open(path+'templates/VHDL_header.stpy', 'r') as f:
		st["header"] = f.read()
	f.close()
	with open(path+'templates/VHDL_instance.stpy', 'r') as f:
		st["instance"] = f.read()
	f.close()
	with open(path+'templates/VHDL_port_declaration.stpy', 'r') as f:
		st["port_declaration"] = f.read()
	f.close()
	with open(path+'templates/VHDL_port_assignment.stpy', 'r') as f:
		st["port_assignment"] = f.read()
	f.close()
	with open(path+'templates/VHDL_signal_declaration.stpy', 'r') as f:
		st["signal_declaration"] = f.read()
	f.close()
	with open(path+'templates/VHDL_signal_assignment.stpy', 'r') as f:
		st["signal_assignment"] = f.read()
	f.close()
	with open(path+'templates/VHDL_register_module.stpy', 'r') as f:
		st["register_module"] = f.read()
	f.close()
	with open(path+'templates/VHDL_register_instance.stpy', 'r') as f:
		st["register_instance"] = f.read()
	f.close()
	with open(path+'templates/VHDL_register_component.stpy', 'r') as f:
		st["register_component"] = f.read()
	f.close()
	with open(path+'templates/VHDL_sequential_port_declarations.stpy', 'r') as f:
		st["sequential_port_declarations"] = f.read()
	f.close()
	with open(path+'templates/VHDL_sequential_port_assignments.stpy', 'r') as f:
		st["sequential_port_assignments"] = f.read()
	f.close()
	with open(path+'templates/VHDL_function_comments.stpy', 'r') as f:
		st["function_comments"] = f.read()
	f.close()

	return st
