##################################################################
##
## file: design_parser.py
##
## description: sorngen designflow - input data parser
##
## (c) 2020 Jochen Rust
##     DSI aerospace technology
##
##################################################################

## import python packages
import ast
import os
import re
# import math
# import sys

## import sorngen packages
from stable.control import ctrl_error as error
from stable.designflow import is_standalone
from stable.designflow.design_SORN import createSORN


def parseInput(env, argv, path):
	## 0/ default assignments
	# 0.1/ local AST tree
	treeAST = []
	# 0.2/ local dictionary id -> AST node
	dictIdAST={}
	# 0.3/ global pipeline list
	env.pipeline = []
	# 0.4/ set path to sorngen executable
	env.execPath = path+'/'

	## 1/ global input data handling
	print("1/ Parsing equations...")
	# 1.0/ catch invalid number of input arguments

	if is_standalone():
		match(len(argv)):
			case 2: filename = argv[1]
			case 3: filename, env.save_path = argv[1], argv[2]
			case _: error.message(error.ID.INPUT_ARGS, argv)


		# 1.1/ read from the specified file (catch exceptions)
		try:
			# noinspection PyUnboundLocalVariable
			with open(filename, 'r') as f:		# filename is assigned if code runs this far
				lines = f.readlines()
			f.close()
		except (FileNotFoundError, PermissionError):
			error.message(error.ID.FILE_NOT_FOUND,filename)
	else:
		# TODO: rename
		lines = os.getenv('specification', '').splitlines()

	## 2/ read config data from file
	for cLine in lines:
		cRegex=re.match('@(.*) (.*)',cLine,re.I)
		if not cRegex: continue
		# 2.3/ get name
		if re.match('name',cRegex.group(1),re.I):
			env.name = cRegex.group(2)
			print("INFO: name: '"+env.name+"'")
		# 2.4a/ get datatype
		elif re.match('datatype',cRegex.group(1),re.I):
			datatypeInputs = eval(cRegex.group(2))
			if len(datatypeInputs) == 5:
				env.datatype = createSORN(datatypeInputs[0],datatypeInputs[1],datatypeInputs[2],datatypeInputs[3],datatypeInputs[4])
			elif len(datatypeInputs) == 4:
				env.datatype = createSORN(datatypeInputs[0],datatypeInputs[1],datatypeInputs[2],datatypeInputs[3])
			elif len(datatypeInputs) == 3:
				env.datatype = createSORN(datatypeInputs[0],datatypeInputs[1],datatypeInputs[2])
			else:
				env.datatype = createSORN(datatypeInputs[0],datatypeInputs[1])
			print("INFO: SORNsize: " + str(env.datatype.sornsize))
			print("INFO: datatype: ",end="")
			env.datatype.showIV()
		# 2.4b/ get pipeline configuration
		elif re.match('Pipeline',cRegex.group(1),re.I):
			pipeline = cRegex.group(2)
			# 2.4.1/ neglect invalid pipeline statement
			if not ((isinstance(eval(pipeline),list)) or (isinstance(eval(pipeline),int))): continue
			env.pipeline = eval(pipeline)
			print("INFO: pipeline configuration: "+pipeline)
		# 2.4 catch unknown config data
		else:
			error.message(error.ID.UNKNOWN_CONFIG_DATA, cRegex.group())

	## 3/ read equations and store as abstract syntax tree (AST)
	for cLine in lines:
		# 3.1/ neglect invalid inputs
		cRegex=re.match('.',cLine,re.I)
		if not cRegex : continue
		if (not cRegex.group()) or (cRegex.group()=='@') or (cRegex.group()=='#'): continue
		# 3.2/ match input
		cRegex=re.match('(.*)',cLine,re.I)
		# 3.3/ write to AST
		treeAST.append(ast.parse(cRegex.group()))
		print("INFO: parsing equation: "+cRegex.group())
		# 3.4 set up new dict (id -> ast)
		for node in ast.walk(treeAST[-1]):
			if isinstance(node, ast.Assign):
				dictIdAST[node.targets[0].id] = node    # TODO: id not defined ???

	# 3.5/ register dict to env (catch exceptions)
	if dictIdAST == {}:

		# if filename is in locals(), it is assured to be defined
		if 'filename' in locals():
			# noinspection PyUnboundLocalVariable
			error.message(error.ID.NO_EQUATIONS_FOUND, filename)
		else:
			error.message(error.ID.EMPTY_SPECIFICATION, None)
	env.lValueDictAST = dictIdAST
	return env

