##################################################################
##
## file: type_SST.py
##
## description: sorngen datatypes - sorn syntax tree datatype
##
## (c) 2020 Jochen Rust
##     DSI aerospace technologie GmbH
##
##################################################################

import ast
import re
import sys
# import numpy as np


from ..control import ctrl_env as ctrl

# import sorngen_global as sorn

class sornSyntaxTree:

    def __init__(self, env):
        self.env            = env
      
        self.dictIdAST      = {}
        self.dictId         = {}
        self.name           = ""
        self.rootNode       = None
        self.varNodes       = []
        self.nodes          = []
        self.virtualNodesAST = []
        self.dictNameNode   = {}
      
        self.SSTDepth      = 0
        self.totalDepth      = 0
      
        # ???
        self.dictNodeIter  = {}
        
        
        self.hasRegister  = False
        self.listInternalConnection  = []
        self.listNameInternalConnection  = []
      
      
      
        self.dictDepthNode = {}
        self.maxDepthLocal = 0
        self.maxAddDepth   = 0

    
    def add(self, *varargs):
      
        nodeSST = sornSyntaxTreeNode(self)
             
        for arg in varargs:
            
            # 1/ ast module
            
            ## Info
            ## hier gibt es Abweichungen zwischen Linux python3.10 und Windows/spyder python3.8
            ## arg.__module__ liefert '_ast' oder 'ast'

            if arg.__module__== '_ast' or arg.__module__== 'ast':
                nodeAST = varargs[0]
                nodeSST.setAST(nodeAST)
                self.dictIdAST[id(nodeAST)] = nodeSST
            # 2/ name
            elif arg=='REGISTER' or arg=='REG':
                nodeSST.setREG()
            
        self.nodes.append(nodeSST)
        self.dictNameNode[nodeSST.name] = nodeSST
        
        self.dictId[id(nodeSST)]  = nodeSST


    def setSiblings(self):
        for node in self.nodes:
            node.setSiblingNodes()

    def setParents(self):
        for node in self.nodes:
            node.setParentNode()

    def setDepth(self, *varargs):
        """ set the actual depth of the tree
       	
       	 Input Arguments:
       		'totalNodes'= True/False -- defines if the overall node count (prevasively through all the connected SST) is considered
       	
   	     """
        
        [totalNodes] = ctrl.argParser(varargs, [0,1],'totalDepth')
        

        self.rootNode.depth = -1
        self.rootNode.totalDepth = -1
        self.SSTDepth = -1
        isTouched = True
        while isTouched:
            isTouched = False
            for node in self.nodes:
                if not (node.depth is None):
                    for sibling in node.siblings: 
                        sibling.depth = node.depth +1
                        if totalNodes: sibling.totalDepth = node.totalDepth +1
                    self.SSTDepth = (node.depth + 1) if (node.depth + 1) > self.SSTDepth else self.SSTDepth
                else:
                    isTouched = True

# =============================================================================
#     def insertReg(self, node, level):
#         
#         for 
#         # check if parent 
#         if not (sibling.parent == parent and parent.isSibling(sibling)):
#             print("ERROR: "+parent.name+" (parent) and "+sibling.name+" nodes are not directly connected")
#             sys.exit(0)
#         # 2/ register node to SST
#         if not node in self.SST.nodes: 
#             self.SST.node.append()
# 
#         # 2/ set new parent
#         sibling.parent = node
#     
# =============================================================================
        

    def insert(self, newNode, node):
        
        if node.parent is None:
            print("ERROR: no parent node available")
            sys.exit(9)

        
        newNode.parent = node.parent
        newNode.parentId = node.parentId
        newNode.siblings.append(node)

        # reset parent siblings
        if node.parent.siblings[0] == node:
            node.parent.siblings[0] = newNode
        elif len(node.parent.siblings) == 2:
            node.parent.siblings[1] = newNode
        
        node.parent = newNode
        
        self.nodes.append(newNode)
        self.dictId[id(newNode)] = newNode
        self.dictNameNode[newNode.name] = newNode

      
    def replace(self, oldNode, newNode):
        
        # 2/ catch some irregularities
        if oldNode.type == typeNode.ROOT:
            print("ERROR: root nodes must not be merged")
            sys.exit(9)
        if oldNode is None or newNode is None:
            print("ERROR: one or two node that should be merged do(es) not exist.")
            sys.exit(9)
        
        newNode.parent = oldNode.parent
        newNode.parentId = id(oldNode.parent)
 #       newNode.name = oldNode.name

        # reset parent siblings
        if oldNode.parent.siblings[0] == oldNode:
            oldNode.parent.siblings[0] = newNode
        elif len(oldNode.parent.siblings) == 2:
            oldNode.parent.siblings[1] = newNode

        # 1/ get node id
        oldNodeId = id(oldNode)
    
        # 3/ remove from SST lists
        self.nodes.remove(oldNode)
        self.dictId.pop(oldNodeId)           
        self.dictNameNode.pop(oldNode.name)           


    def remove(self, node):
        
        # 1/ get node
        nodeId = id(node)
        # 2/ catch some irregularities
        if node.type == typeNode.ROOT:
            print("ERROR: root must not be removed from SST")
            sys.exit(9)
        if node.parent is None:
            print("CRITICAL ERROR: node has no parent node. There has something gone terribly wrong!")
            sys.exit(9)
    
        # 3/ remove from SST lists
    #        self.nodes          = []
        self.nodes.remove(node)
    #        self.dictId         = {}
        self.dictId.pop(nodeId)           
    #        self.dictNameNode   = {}
        if node.name in self.dictNameNode : # DEBUG insert MB 27.01.
            self.dictNameNode.pop(node.name) 
			
        # 4/ tie parent node
        node.parent.siblings.remove(node)
        

    def show(self):
        print("# ===== Sorn Syntax Tree '"+self.name+"' ===== #")
        print("SST depth: "+str(self.SSTDepth))
        print("Nodes: ")

        for node in self.nodes:
            node.show()
            
        print("# ===== "+str(len(self.nodes))+" node(s) found ====== #")
        print("")



# =============================================================================
# =============================================================================

class sornSyntaxTreeNode:

    def __init__(self, SST):
        
        # set during initialization
        self.operand            = None
        self.SST                = SST
        self.env                = self.SST.env
        
        self.type               = None
        self.name               = ""
        self.siblingIdAST       = []
        self.ast                = None
        self.function           = ""
        self.isRoot             = False
        self.siblings           = []
        self.parent             = None
        self.parentId           = None
        self.depth              = None
        self.totalDepth         = None
        self.hasRegister        = False
        self.instHDL            = None
        
#        self.depthLocal         = 0
        
        #    self.islValue           = False
#        self.hasInternalConnection = False
#        self.isRegister         = False

    def setSiblingNodes(self):
        for idAST in self.siblingIdAST:
            self.siblings.append(self.SST.dictIdAST[idAST])

    def setParentNode(self):
        for cNode in self.SST.nodes:
            for sibling in cNode.siblings:
                if id(sibling) == id(self):
                    self.parent = cNode
                    self.parentId = id(cNode)
              
    def isSibling(self,node):
        for sibling in self.siblings:
            if sibling == node: return True
        return False
       

    def setREG(self):
        self.type = typeNode.REGISTER
        self.operand = "REG" 
        self.name = self.env.getNodeName("REG")

    def setAST(self, nodeAST):
        self.ast = nodeAST
        if isinstance(nodeAST, ast.BinOp):
            self.type = typeNode.BINOP 
            self.operand = getBinOpAST(nodeAST)[0]
            self.name = self.env.getNodeName(getBinOpAST(nodeAST)[0])
            self.function = getBinOpAST(nodeAST)[1]
            self.siblingIdAST.append(id(nodeAST.left))
            self.siblingIdAST.append(id(nodeAST.right))
        elif isinstance(nodeAST, ast.UnaryOp):
            self.type = typeNode.UNOP
            self.name = self.env.getNodeName(getUnOpAST(nodeAST)[0])
            self.function = getUnOpAST(nodeAST)[1]
            self.siblingIdAST.append(id(nodeAST.operand))
        elif isinstance(nodeAST, ast.Name):
            self.type = typeNode.VARIABLE 
            self.name = nodeAST.id
            self.SST.varNodes.append(self)
        elif isinstance(nodeAST, ast.Call):
            self.type = typeNode.FUNCTION
            self.name = self.SST.env.getNodeName(getFuncAST(nodeAST)[0])
            for operand in nodeAST.args:
                self.siblingIdAST.append(id(operand))
            self.SST.virtualNodesAST.append(nodeAST.func)
            self.function = getFuncAST(nodeAST)[1]
        elif isinstance(nodeAST, ast.Num):
            self.type = typeNode.NUMERIC
            self.name = str(nodeAST.n)
        elif isinstance(nodeAST, ast.Assign):
            self.type = typeNode.ROOT

            # only one variable is allowed!!!
            self.name = nodeAST.targets[0].id
            self.siblingIdAST.append(id(nodeAST.value))
            self.SST.name = nodeAST.targets[0].id
            self.SST.rootNode = self
            self.isRoot = True
            self.SST.virtualNodesAST.append(nodeAST.targets[0])


    def show(self):
            print(" '"+str(self.name)+"',",end="")
            #if len(str(node.name)) < 3: print("\t",end="")
            print("   \t parent: [",end="")
            if not (self.parent is None):
                print("'"+self.parent.name+"'",end="")
            else:
                print("'None'",end="")
                
            print("], \t siblings: [",end="")

            if len(self.siblings) > 0:
                if not (self.siblings[0] is None):
                    print("'"+self.siblings[0].name+"', ",end="")
            else:
                print("'None', ",end="")
            if len(self.siblings) > 1:
                if not (self.siblings[1] is None):
                    print("'"+self.siblings[1].name+"'", end="")
                if len(self.siblings) > 2:                               # added by MB 25.10.22
                    if not (self.siblings[2] is None):                 
                        print(", '"+self.siblings[2].name+"'", end="")
            else:
                print("'None'",end="")


            print("], \t depth/total: "+str(self.depth)+"/"+str(self.totalDepth),end="")
            print(", \t type: "+typeNode.name[self.type], end="")
            print(", \t AST id: "+str(id(self.ast)), end="")
            print(", \t function: '",self.function+"'",end="")
            print("")



# =============================================================================
# =============================================================================

def getUnOpAST(AST):
  ## 0/ default assignments
  strOP = ""
  strFunc = ""
  if type(AST.op) is ast.USub:
    strOP = "NEG"
    strFunc = "(-1 * (<op0>))"
  elif type(AST.op) is ast.UAdd:
    strOP = "POS"
    strFunc = "(<op0>)"

  return strOP, strFunc

def getFuncAST(nodeAST):

    strOP = nodeAST.func.id

    # handle default and normal functions/operators
    try:
        eval('type('+strOP+')')
        strFunc = strOP+"(<op0>)"
    except NameError:
        eval('type(np.'+strOP+')')
        strFunc = "np."+strOP+"(<op0>)"

    return strOP, strFunc




def getBinOpAST(AST):
  
  ## 0/ default assignments
  strOP = ""
  strFunc = ""

  ## 1/ set up initial operand namings and functions
  if type(AST.op) is ast.Add:
    strOP = "ADD"
    strFunc = "((<op0>) + (<op1>))"
  elif type(AST.op) is ast.Sub:
    strOP = "SUB"
    strFunc = "((<op0>) - (<op1>))"
  elif type(AST.op) is ast.Div:
    strOP = "DIV"
    strFunc = "((<op0>) / (<op1>))"
  elif type(AST.op) is ast.Mult:
    strOP = "MUL"
    strFunc = "((<op0>) * (<op1>))"
  elif type(AST.op) is ast.Mod:
    strOP = "MOD"
    strFunc = "((<op0>) % (<op1>))"
  elif type(AST.op) is ast.Pow:
    strOP = "POW"
    strFunc = "((<op0>) ** (<op1>))"

  ## 2/ replace with numeric (if specified)
  if type(AST.left) is ast.Constant:
    strFunc= re.sub('<op0>', str(AST.left.n), strFunc)
    strFunc= re.sub('<op1>', '<op0>', strFunc )

  if type(AST.right) is ast.Constant:                      # Changed by MB 21.10.22: changed "is ast.Num" to "is ast.Constant"
    strFunc= re.sub('<op1>', str(AST.right.n), strFunc)

  return strOP, strFunc



class typeNode:

    BINOP = 0
    UNOP = 1
    FUNCTION = 2
    NUMERIC = 3
    VARIABLE = 4
    REGISTER = 5
    ROOT = 6

    name = ["BINOP\t", "UNOP\t", "FUNCTION\t", "NUMERIC\t", "VARIABLE\t", "REGISTER\t", "ROOT\t"]  