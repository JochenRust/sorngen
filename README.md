# SORN Generator
## Requirements:
- python 3.* installation (recommended version: 3.12.3)
- Numpy installation (recommended version: 1.26.3)

## Description:
Hardware Generator for SORN Arithmetic

This is a Python-based tool to generate VHDL code for arithmetic algorithms processed in SORN arithmetic.

SORN (set of real numbers) is a datatype related to type-2 unum format. For more information see http://www.johngustafson.net/pubs/RadicalApproach.pdf

The specification file has a '.sorn' ending and contains all information about name, datatype, pipeline registers and the equations.

- Name: Set the name of the design. The toplevel VHDL file will be "name.vhd".

- Datatype: ['lin'/'log'/'man', '[start,stop,step]', 'zero', 'negative', 'infinity']

	-- 'lin'/'log': choose either a linear or logarithmic spacing of the lattice values

		-- '[start,stop,step]': choose the start and end value for the lattice values and a stepsize for a linear scale 

		-- 'zero', 'negative', 'infinity': extend the datatype by the given options (any combination can be choosen)
		
	-- 'man': choose a fully manually defined datatype
	
		-- define datatype as ['man','{<interval1>;<interval2>;<...>}'] with <interval> having open "(" and closed "[" interval bounds

		-- see "MIMO_solver_N2" for an example
	
- Pipeline registers: The amount of specified registers will be inserted in the design.

- Equations: Specify one or multiple equations with consistent variable names, round brackets and python-based arithmetic operators. Variables may appear in multiple equations.

- Examples: See the files "MIMO_solver_N2.sorn" and "MIMO_solver_N4.sorn".

## Starting the generation:
1. create a specification file (e.g. in the "playground" directory)
2. Navigate to the project root (which contains "playground" and "stable" directories).
3. execute 'python3 -m stable.sorngen \<specification file> \[output directory]'

### examples: 
- Copy the contents from .playground/example to your local ./playground directory (do not make any changes within .playground/example)
- To generate code in the current directory: 
  - 'python3 -m stable.sorngen ./playground/basic_OPs.sorn'
- To generate code in a specific directory (e.g., playground):
  - 'python3 -m stable.sorngen ./playground/basic_OPs.sorn ./playground'

### output:
The folder ".\VHDL" contains all the created VHDL files including submodules and the toplevel file. The basic arithmetic SORN modules are stored in the subfolder ".\VHDL\VHDLbasic".
The ".\VHDL" directory is either located in the current directory or in an specified directory

## Launching the GUI:
1. navigate to project root
2. execute 'python3 -m stable.App'

### How to use the GUI:
- Enter or load a specification using the "Open Specification" button.
- Save your specification with the "Save Specification" button.
- Press "Next Step" to proceed (additional screens not yet implemented).
- To regenerate output, switch to the relevant tab and press "Regenerate."