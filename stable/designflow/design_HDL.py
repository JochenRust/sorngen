##################################################################
##
## file: design_HDL.py
##
## description: sorngen designflow - design HDL datatype
##
## (c) 2020 Jochen Rust
##     DSI aerospace technology
##
##################################################################
 
## import packages
# import parser
# import ast
import re

import sys

from stable.datatypes import type_HDL as dp
from stable.datatypes import type_SST as sst

from stable.datatypes.type_SST import typeNode
from stable.designflow.design_SORNHDL import genFctnSORN

def createHDLGlobalPortsFromSST(HDL,SST):

    ## default assignments
    iCTR = 0
    oCTR = 0

    ## 1/ walk the SST to create instances
    print("INFO: Creating global ports from SST...",end="")
    for node in SST.nodes:
        
        # 1.1/ input ports 
        if node.type == typeNode.VARIABLE:
            newPort =dp.sornPort(HDL)
            newPort.name = node.name
            newPort.isInput = True
            iCTR += 1
            newPort.isGlobal = True
        elif node.type == typeNode.ROOT:
            newPort =dp.sornPort(HDL)
            newPort.name = node.name
            newPort.isInput = False
            newPort.isGlobal = True
            oCTR += 1

    print("INFO: "+str(iCTR)+" input and "+str(oCTR)+" output global port(s) found")

    return HDL

def createHDLInstancesFromSST(HDL,SST):
    
    ## 1/ walk the SST to create instances
    print("creating sorn instances from SST...",end="")
    for node in SST.nodes:
        
        # 1.1/ binary operator
        if node.type == typeNode.VARIABLE or node.type == typeNode.ROOT: continue

        newInput = {}
        # 1.1.1/ create and configure new i/O ports
        for i in range(len(node.siblings)):
            newInput[i] =dp.sornPort(HDL)
            newInput[i].isInput = True
            newInput[i].name = "input"+str(i)

        newOutput = dp.sornPort(HDL)
        newOutput.name = "output0"

        # 1.1.2/ create and configure new instance
        inst = dp.sornInstance(HDL, node.name, node.function, [])
        inst.nodeSST = node
        inst.depth = node.depth
        inst.isRegister = node.type == typeNode.REGISTER

        node.instHDL = inst
        
        
        # 1.1.4/ register instance to ports and vice versa
        for i in newInput:
            dp.register(newInput[i], inst)
        dp.register(newOutput, inst)

    print(str(len(HDL.instances))+" instance(s) in total")
    
    return HDL


def createHDLNetsFromSST(HDL, SST):

    print("creating nets...",end="")
    for inst in HDL.instances:        

        node = inst.nodeSST

         # global output (ROOT node)
        if node.parent.type == typeNode.ROOT:
            parent = node.parent
            # global output
            newNet = dp.sornNet(HDL,inst.name+"_to_"+parent.name)
            
            for i in range(len(inst.ports)):
                port = inst.ports[i]
                if not port.isInput:
                    dp.register(newNet, inst.ports[i])
            
            for j in range(len(HDL.ports)):
                port = HDL.ports[j]
                if port.name == parent.name:
                    dp.register(newNet, HDL.ports[j])

        # other
        for i in range(len(node.siblings)):
            sibling = node.siblings[i]
            newNet = dp.sornNet(HDL,sibling.name+"_to_"+inst.name)
            # global inputs
            if sibling.type == typeNode.VARIABLE:
                for j in range(len(HDL.ports)):
                    port = HDL.ports[j]
                    if port.name == sibling.name:
                        dp.register(newNet, HDL.ports[j])
                        dp.register(newNet, inst.ports[i])
            # instance
            else:
                dp.register(newNet, inst.ports[i])
                for outputPort in sibling.instHDL.ports:
                    if not outputPort.isInput:
                        dp.register(newNet, outputPort)
    
    print(str(len(HDL.nets))+" net(s) in total")
    
    return HDL


def createToplevelInstance(env):

    ## 1/ default assignments and preliminaries
    # cPortNameDict = {}
    print("creating toplevel instance...",end="\n")
    HDL = dp.sornHDL(env.name)
    HDL.isToplevel = True
    # internalConnect = {}

    ## create toplevel ports
    for SST in env.SSTs:
#        if SST.rootNode.parent == None:
        newPort = dp.sornPort(HDL)
        newPort.name = SST.rootNode.name
        newPort.isGlobal = True
        newPort.isInput  = False
        for varNode in SST.varNodes:
            if not (varNode.siblings == []): continue

            ### #01 BUGFIX
            # check for equal names in submodules:
            # rationale: skip, if the name of the actual variable (== toplevel input port) already exists
            #            in the toplevel port list
            skipFlag = 0
            for port in HDL.ports:
                if (varNode.name == port.name):
                    skipFlag = 1
            if (skipFlag == 1): continue
            ### #01 END OF BUGFIX
            
            newPort = dp.sornPort(HDL)
            newPort.name = varNode.name
            newPort.isGlobal = True
            newPort.isInput  = True
    ## create toplevel connections

    for SST in env.SSTs:
        if not (SST.rootNode.parent is None):
            print(SST.rootNode.parent)
            netName = SST.name+"_module_to_"+SST.rootNode.parent.name
            newNet = dp.sornNet(HDL,netName)
            for i in range(len(HDL.ports)):
                if HDL.ports[i].name == SST.rootNode.parent.name:
                    dp.register(newNet, HDL.ports[i])
            
#            print(varNodes.name)
            
#    sys.exit(0)
# =============================================================================
#         for inst in HDL.instances:
#             if inst.nodeSST.type == typeNode.ROOT and (not inst.nodeSST.parent == []):
#                 dictTopNets[nodeSST.parent.name] = []
#                  newPort = dp.sornPort(HDL)
#                  newPort.name = cName
#                  newPort.isGlobal = True;
#                  newPort.isInput = cPortNameDict[cName][0].isInput;
#                 toplevelPairs[nodeSST.parent.name] = node.name
# # #                newNet = dp.sornNet(HDL,cName)
#                 
# =============================================================================
# =============================================================================
#     for cValue in env.HDL:
#         for cPort in env.HDL[cValue].ports:
#             if cPort.isGlobal:
#                 if not cPort.name in cPortNameDict:
#                     cPortNameDict[cPort.name] = [cPort]
#                 else:
#                     cPortNameDict[cPort.name].append(cPort)
#     ## 3/ get internally connected ports
#     for cName in cPortNameDict:
#         equalDirection = True
#         cDirection = cPortNameDict[cName][0].isInput
#         for cNode in cPortNameDict[cName]:
#             if not (cNode.isInput == cDirection): equalDirection = False
#         if equalDirection:
#             cPortNameDict[cName] = [cPortNameDict[cName][0]]
#     ## 4/ set up ports
#     for cName in cPortNameDict:
#             print(cName)
#             if len(cPortNameDict[cName]) == 1:
#                 newPort = dp.sornPort(HDL)
#                 newPort.name = cName
#                 newPort.isGlobal = True;
#                 newPort.isInput = cPortNameDict[cName][0].isInput;
# #            else:
# #                newNet = dp.sornNet(HDL,cName)
#     print("DONE! ")
# =============================================================================
    print(str(len(HDL.nets))+" net(s) in total")
    HDL.show()
    env.dictHDL[env.name] = HDL
    env.HDL.append(HDL)
    return env.dictHDL, env.HDL
            
def generateFunctionTable(env):
    

    ## 1/ iterate through HDL instances
    for cHDL in env.dictHDL:
        for cInst in env.dictHDL[cHDL].instances:
            if cInst.nodeSST.type == sst.typeNode.REGISTER: continue
            ## 2/ determine the kind of operation (one, two or three operands)
            if len(re.findall(r"<op\d*>",cInst.function)) == 3:     # added by MB 24-10-22
                cInst.FctnTable = genFctnSORN(cInst.function,env.datatype,env.datatype,env.datatype,env.datatype)
            elif len(re.findall(r"<op\d*>",cInst.function)) == 2: 
                cInst.FctnTable = genFctnSORN(cInst.function,env.datatype,env.datatype,env.datatype)
            elif len(re.findall(r"<op\d*>",cInst.function)) == 1:
                cInst.FctnTable = genFctnSORN(cInst.function,env.datatype,env.datatype)
            else:
                raise Exception(" ERROR: more than 3 inputs for genFctnSORN are not implemented!")
            
            cInst.FctnTable.name = cInst.name
    

