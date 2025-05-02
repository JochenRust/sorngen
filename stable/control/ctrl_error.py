##################################################################
##
## file: ctrl_error.py
##
## description: sorngen control - error handling
##
## (c) 2020 Jochen Rust
##     DSI aerospace technology
##
##################################################################
import sys

from stable.designflow import is_standalone


class ID:
    INPUT_ARGS          = 0
    FILE_NOT_FOUND      = 1
    NO_EQUATIONS_FOUND  = 2
    UNKNOWN_CONFIG_DATA = 3
    EMPTY_SPECIFICATION = 4
    
def message(msg, data):
    print("ERROR("+str(msg)+"): ",end="")
    if msg==ID.INPUT_ARGS:
        print("Invalid number of arguments: "+str(data[1:]))
    elif msg==ID.FILE_NOT_FOUND:
        print("Input file '"+data+"' not found")
    elif msg==ID.NO_EQUATIONS_FOUND:
        print("No input data found in file '"+data+"'")
    elif msg==ID.UNKNOWN_CONFIG_DATA:
        print("Instruction '"+data+"' is unknown")
    elif msg==ID.EMPTY_SPECIFICATION:
        print("Specification was empty or incomplete")
    
    print("sorngen halted with error(s)")

    if is_standalone():
        sys.exit(2)
    else:
        raise Exception("sorngen halted with error(s)")



