# =============================================================================
##
## file: design_elaborate.py
##
## description: sorngen designflow - elaborate design
##
## (c) 2020 Jochen Rust
##     DSI aerospace technology
##
# =============================================================================

## import packages
import ast
import re
import math
import sys

# import sorngen_error as error
from stable.datatypes import type_SST as sst
from stable.datatypes.type_SST import typeNode

from stable.control import ctrl_env as ctrl


# import sorngen_global as sorn
# from sorngen_defineSORN import defineSORN


# =============================================================================
## function createSST: AST -> SST
# =============================================================================
def createSST(env):
    for node in env.lValueDictAST:
        SST = extractSST(env, env.lValueDictAST[node])
        env.SSTs.append(SST)
        SST.show()
    #        print(" "+str(len(SST.nodes))+" node(s) found")
    return env


# =============================================================================
def extractSST(env, AST):
    ## 0/ default assignments
    SST = sst.sornSyntaxTree(env)
    dictIdOpAST = {}

    # 1/ set up initial sorn syntax tree
    for nodeAST in ast.walk(AST):

        # 1.1/ set current node id
        cID = id(nodeAST)

        # 1.2/ iterate through AST nodes and add nodes to SST
        # 1.2.1/ assignment (root node)
        if isinstance(nodeAST, ast.Assign):
            rootID = nodeAST.targets[0]
            dictIdOpAST[rootID] = nodeAST
            SST.add(nodeAST)

        # 1.2.2/ unary operator
        elif isinstance(nodeAST, ast.UnaryOp):
            dictIdOpAST[cID] = nodeAST
            SST.add(nodeAST)

        # 1.2.3/ binary
        elif isinstance(nodeAST, ast.BinOp):
            dictIdOpAST[cID] = nodeAST
            SST.add(nodeAST)

        # 1.2.4/ call (function)
        elif isinstance(nodeAST, ast.Call):
            dictIdOpAST[cID] = nodeAST
            SST.add(nodeAST)

        # 1.2.5/ numeric 
        elif isinstance(nodeAST, ast.Num):
            dictIdOpAST[cID] = nodeAST
            SST.add(nodeAST)

        # 1.2.5/ name (variable)
        elif isinstance(nodeAST, ast.Name):
            if nodeAST in SST.virtualNodesAST:
                continue

            dictIdOpAST[cID] = nodeAST
            SST.add(nodeAST)

    # 2/ connect nodes
    SST.setSiblings()
    SST.setParents()

    # 3/ set tree depth
    SST.setDepth('totalDepth', True)
    return SST


# =============================================================================
def connectSSTs(env):
    print("# ===== Connect SSTs =============== #")
    # get important nodes
    rootNodes = []
    varNodes = []
    matchedNodes = {}
    matchedRootNodes = []
    #    matchedVarNodes = []
    for SST in env.SSTs:
        for node in SST.nodes:
            if node.type == typeNode.ROOT:
                rootNodes.append(node)
            if node.type == typeNode.VARIABLE:
                varNodes.append(node)

    # search root names in variables
    for rNode in rootNodes:
        cName = rNode.name
        for vNode in varNodes:
            if cName == vNode.name:
                matchedNodes[rNode] = vNode
                rNode.SST.rootNode.parent = vNode
                vNode.siblings.append(rNode)
                if not (rNode in matchedRootNodes):
                    matchedRootNodes.append(rNode)
    #                if not (vNode in matchedVarNodes): matchedVarNodes.append(vNode)

    print(str(len(matchedRootNodes)) + " internal connections found ")
    print(" checking for loops ")
    # detect loops in equation set
    trueRootNodes = list(set(rootNodes) - set(matchedRootNodes))
    if len(trueRootNodes) == 0:
        print('ERROR: loop detected!')
        sys.exit(1)

    for currentNode in trueRootNodes:
        visitedRootNames = [currentNode.name]
        while not matchedNodes.get(currentNode) is None:

            currentNode = matchedRootNodes[currentNode]
            if currentNode.name in visitedRootNames:
                print('ERROR: loop detected!')
                sys.exit(1)
            else:
                visitedRootNames.append(currentNode.name)

    print('DONE, no loops in design')

    env.setTotalDepth()
    print("# ===== End of Connect SSTs ====== #\n")

    # env.show()
    #    sys.exit(9)

    return env


# noinspection PyUnboundLocalVariable
def merge(env, *varargs):
    """ set the actual depth of the tree
    
      Input Arguments:
        'numeric'    = True/False -- defines if numeric leaves are removed
        'univariate' = True/False -- defines if univariate functions are merged
        'trivariate' = True/False -- defines if trivariate functions are merged/fused   # added by MB 24.10.22
           
        """
    [num, univar, trivar] = ctrl.argParser(varargs, [1, 3], 'numeric', 'univariate', 'trivariate')

    print("# ===== Merge Nodes =============== #")
    print("")
    # 1/ numeric reduction
    if num:
        print("# === Merge/remove NUMERICS:")
        numNodes = []
        # iterate through all SSTs
        for SST in env.SSTs:
            # iterate through all nodes of current SST
            for node in SST.nodes:

                # iterate through siblings of current node
                for sibling in node.siblings:
                    # skip all non-numeric node types
                    if not (sibling.type == typeNode.NUMERIC):
                        continue
                    numNodes.append(sibling)
                    # remove sibling
                    SST.remove(sibling)
        for node in numNodes:
            node.show()

        print(str(len(numNodes)) + " node(s) of type NUMERIC merged into parent node")
        # print("# === End of Numeric Merge ====== #")
        print("")

    # env.show()

    # 3/ trivariate merging/fusing      # added by MB 24.10.22
    if trivar:
        print("# === Merge trivariate arithmetic functions:")
        # iterate through all SSTs
        for SST in env.SSTs:
            # iterate through all nodes of current SST
            for node in SST.nodes:
                # identify valid candidates for applying fusion:
                # BinOp, 2 Siblings, (at least) one Sibling is also BinOp and has 2 Siblings
                if node.type == typeNode.BINOP and len(node.siblings) == 2 and (
                        (node.siblings[0].type == typeNode.BINOP and len(node.siblings[0].siblings) > 1) or (
                        node.siblings[1].type == typeNode.BINOP and len(node.siblings[1].siblings) > 1)):

                    # mark the sibling involved in fusion and save it 
                    if node.siblings[0].type == typeNode.BINOP:
                        fusedSib = 0
                    else:
                        fusedSib = 1
                    savedSib = node.siblings[fusedSib]

                    # swap siblings of node if left/first sibling is "variable" and
                    # right/second sibling is "BinOp" in order to maintain the correct
                    # order of calculations (otherwise problems in design_SORNHDL.genFctnSORN() are occurring)
                    if fusedSib == 1:
                        node.siblings[0], node.siblings[1] = node.siblings[1], node.siblings[0]
                        fusedSib = 0
                        print("Swapped siblings in current node:")
                        print(" ", end="")
                        node.show()
                        print("#")

                    # display nodes to be merged/fused
                    print("Nodes")
                    print(" ", end="")
                    node.show()
                    print(" ", end="")
                    node.siblings[fusedSib].show()

                    # re-define function call (node.function)
                    # if fusedSib == 0:
                    node.function = re.sub('<op1>', '<op2>', node.function)
                    node.function = re.sub('\(<op0>\)', node.siblings[fusedSib].function, node.function)
                    # else: # fusedSib == 1
                    # node.siblings[fusedSib].function = re.sub('<op1>','<op2>', node.siblings[fusedSib].function)
                    # node.siblings[fusedSib].function = re.sub('<op0>','<op1>', node.siblings[fusedSib].function)
                    # node.function = re.sub('\(<op1>\)',node.siblings[fusedSib].function, node.function)

                    # remove fused sibling from SST
                    SST.remove(node.siblings[fusedSib])

                    # update siblings
                    node.siblings.insert(fusedSib, savedSib.siblings[0])
                    node.siblings.insert(fusedSib + 1, savedSib.siblings[1])
                    node.siblings[fusedSib].parent = node
                    node.siblings[fusedSib + 1].parent = node

                    # update node.name
                    node.name = savedSib.name + node.name

                    # display new merged/fused node
                    print("merged to")
                    print(" ", end="")
                    node.show()
                    print("#")

    # 2/ univariate merging
    if univar:
        print("# === Merge univariate arithmetic functions:")
        # iterate through all SSTs
        for SST in env.SSTs:
            isTouched = True
            while isTouched:
                isTouched = False
                # iterate through all nodes of current SST
                for node in SST.nodes:
                    # skip root and variables
                    if node.type == typeNode.ROOT or node.type == typeNode.VARIABLE:
                        continue
                    # catch univariates of parent
                    # get parent
                    parent = node.parent
                    if parent.type == typeNode.ROOT: continue
                    if len(parent.siblings) == 1 or ((len(parent.siblings) == 2 or len(parent.siblings) == 3) and len(
                            node.siblings) == 1):  # after "or": added by MB 27.01.21: Before: Merge only if parent node has just one sibling. Now: Also merge if parent node has 2 or 3 siblings but current node has only one sibling.
                        print(" ", end="")

                        parent.show()
                        print(" ", end="")
                        node.show()

                        # register this node to SST
                        SST.nodes[SST.nodes.index(node)] = node
                        SST.dictId[id(node)] = node
                        SST.dictNameNode[parent.name + node.name] = node

                        # Added by MB 27.01.21:
                        # If parent has two siblings (one is current node), save the other sibling for new, merged node
                        if len(parent.siblings) == 2:
                            for parsib in parent.siblings:
                                if parsib.name != node.name:
                                    savedsibs = parsib
                        elif len(parent.siblings) == 3:  # added by MB 28.10.22
                            savedsibs = []
                            for parsib in parent.siblings:
                                if parsib.name != node.name:
                                    savedsibs.append(parsib)

                        # re-define function call (node.function)
                        if parent.siblings[
                            0].name == node.name:  #added by MB 27.01.21: If current node is left/first sibling, sub <op0> in parent function with node function
                            node.function = re.sub('<op0>', node.function, parent.function)
                            swapsib = 0
                        elif parent.siblings[
                            1].name == node.name:  #added by MB 27.01.21: Else if current node is right/middle/second sibling, sub <op1> in parent function with node function. When subbed node function contains <op0>, replace with <op1>
                            newfunction = node.function
                            newfunction = re.sub('<op0>', '<op1>', newfunction)
                            node.function = re.sub('<op1>', newfunction, parent.function)
                            swapsib = 1  # store information that current node is second sibling and siblings in new node have to be interchanged
                        elif parent.siblings[
                            2].name == node.name:  # added by MB 28.10.22: Else if current node is right/third sibling, sub <op2> in parent function with node function. When subbed node function contains <op0>, replace with <op2>
                            newfunction = node.function
                            newfunction = re.sub('<op0>', '<op2>', newfunction)
                            node.function = re.sub('<op2>', newfunction, parent.function)
                            swapsib = 2  #

                        node.name = parent.name + node.name
                        node.type = parent.type

                        # Added by MB 27.01.21, changed by MB 28.10.22:
                        if len(node.siblings) == 1 and (len(parent.siblings) == 2 or len(parent.siblings) == 3):
                            if len(parent.siblings) == 2:
                                savedsibs.parent = node  # apply new created node as new parent node to the saved sibling
                                if swapsib == 0:
                                    node.siblings.append(
                                        savedsibs)  # apply saved sibling to siblings of this new created node (as right/second sibling)
                                elif swapsib == 1:
                                    node.siblings.insert(0,
                                                         savedsibs)  # apply saved sibling to siblings of this new created node (as left/first sibling)
                            elif len(parent.siblings) == 3:
                                for sib in savedsibs:
                                    sib.parent = node
                                if swapsib == 0:
                                    node.siblings.append(savedsibs[0])
                                    node.siblings.append(savedsibs[1])
                                elif swapsib == 1:
                                    node.siblings.insert(0, savedsibs[0])
                                    node.siblings.append(savedsibs[1])
                                elif swapsib == 2:
                                    node.siblings.insert(0, savedsibs[1])
                                    node.siblings.insert(0, savedsibs[0])

                        SST.replace(parent, node)
                        # SST.show()

                        # set touched flag
                        isTouched = True
                        print("merged to")
                        print(" ", end="")
                        node.show()
                        print("#")
        print("")

    # x/ some output stuff
    print("# ===== End of Merge Nodes ======== #")
    print("")

    # re-set depths
    for SST in env.SSTs:
        SST.setDepth('totalDepth', True)
    return env


def insertRegister(env):
    ## 0/ default assignments
    maxDepth = env.maxDepth - 1
    pipelineLocation = []

    ## 2/ handle pipeline divider
    if isinstance(env.pipeline, int):
        if env.pipeline >= maxDepth:
            for it in range(maxDepth, 0, -1): pipelineLocation.append(it)
        if 0 < env.pipeline < maxDepth:
            pipeStep = maxDepth / (env.pipeline + 1)
            pipeCTR = pipeStep
            while pipeCTR < maxDepth:
                if not math.ceil(maxDepth - pipeCTR) in pipelineLocation:
                    pipelineLocation.append(math.ceil(maxDepth - pipeCTR))
                    pipeCTR += pipeStep
    ## 3/ handle fixed position of pipelines
    else:
        for cValue in env.pipeline:
            if cValue in range(maxDepth, 0, -1): pipelineLocation.append(maxDepth - cValue + 1)

    env.pipelineLocation = pipelineLocation

    # insert register at specified level
    for SST in env.SSTs:
        for node in SST.nodes:
            if node.totalDepth in pipelineLocation:
                # set up new register node
                REGnode = sst.sornSyntaxTreeNode(SST)
                REGnode.ast = typeNode.REGISTER
                REGnode.type = typeNode.REGISTER
                REGnode.name = env.getNodeName("REG")
                REGnode.function = "z^-1"
                # insert node to SST
                SST.insert(REGnode, node)
                SST.hasRegister = True
                env.hasRegister = True

    # re-set depths
    for SST in env.SSTs:
        SST.setDepth('totalDepth', True)
    return env
