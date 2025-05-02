# -*- coding: utf-8 -*-
##################################################################
##
## file: design_optimize.py
##
## description: sorngen designflow - optimize design
##
## (c) 2020 Jochen Rust
##     DSI aerospace technology
##
##################################################################

## import packages
import re
# import sys

# import sorngen_syntaxTree as sst
from ..datatypes.type_SST import typeNode
# import sorngen_error as error
# import sorngen_global as sorn
# from sorngen_defineSORN import defineSORN

def optimize(env):

    print("2b/ Optimization...")

    env = setUNOPs(env)
    env = merge(env)
    
 #   sys.exit(0);
    return env

def setUNOPs(env):

    print("INFO: Unary operand identification...")
    
    for nameSST in env.lValueDictSST:
        SST = env.lValueDictSST[nameSST]
        for node in SST.listNode:
            if node.isRoot: continue
            print(node.name+" "+str(node.type))
            print(node.parent.name+" "+str(node.parent.type))
            
            if node.type == typeNode.BINOP and (node.siblings[0].type == typeNode.NUMERIC or node.siblings[1].type == typeNode.NUMERIC):
                print("INFO: note "+node.name+" is considered as unary operator")
                node.type = typeNode.UNOP

            # TODO: CALL not defined???
            if node.type == typeNode.CALL and (len(node.siblings) == 1):
                print("INFO: note "+node.name+" is considered as unary operator")
                node.type = typeNode.UNOP
                
    return env

    
def merge(env):

    print("INFO: Merging operands...")
    
    isTouched = True
    while isTouched:
        isTouched = False
        for nameSST in env.lValueDictSST:
            SST = env.lValueDictSST[nameSST]
            for node in SST.listNode:
                if node.isRoot: continue
            
                if node.type == typeNode.BINOP and (node.parent.type == typeNode.UNOP or node.parent.type == typeNode.FUNCTION):
                    parentNode = node.parent
                    # 1/ set function
                    node.function = re.sub('<op0>', node.function, parentNode.function)
                    node.parent = parentNode.parent
                    node.name = parentNode.name + node.name
                    
                    # reset parent siblings
                    if parentNode.parent.siblings[0] == parentNode:
                        parentNode.parent.siblings[0] =node
                    elif len(parentNode.parent.siblings) == 2:
                        parentNode.parent.siblings[1] =node
    
                    # 2/ remove UNOP node from list
                    SST.listNode.remove(parentNode)
                     
                    # 3/ set touched flag
                    isTouched= True
                   #sys.exit(0)
                    print(node.name+" "+str(node.type))
                    print(node.parent.name+" "+str(node.parent.type))
                
    return env
