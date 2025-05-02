##################################################################
##
## file: ctrl_env.py
##
## description: sorngen control - global environment declaration
##
## (c) 2018/2019 Jochen Rust
##     University of Bremen
##
##################################################################

#import ast
import sys

from ..datatypes.type_SST import typeNode

class sornEnv:
    def __init__(self):
        self.env      = "n/a"
        self.name      = "n/a"
        self.dictNodeIter = {}
        self.SSTs = []
        self.dictSSTdepths = {}
        self.lValueDictAST = {}
        self.maxDepth = 0
        self.pipeline = None
        self.HDL = []
        self.dictHDL = {}
        self.hasRegister = False

        self.exexPath = None
        self.datatype  = "n/a"
        self.pipelineLocation = "n/a"
        self.save_path = "."


    def getNodeName(self,name):
      if not (name in self.dictNodeIter):
        self.dictNodeIter[name] = 0  
      else:
        self.dictNodeIter[name] += 1
      return name+str(self.dictNodeIter[name])
  
  
    def setTotalDepth(self):
      # re-set depths
      self.maxDepth = 0
      isTouched = True
      # 3.3 / iterate through remaining nodes
      while isTouched:
          isTouched = False
          for SST in self.SSTs:
              for node in SST.nodes:
                  if not (node.depth is None):
                      for sibling in node.siblings: 
                          sibling.totalDepth = node.totalDepth if sibling.type == typeNode.ROOT else node.totalDepth + 1
                          self.maxDepth = sibling.totalDepth if sibling.totalDepth > self.maxDepth else self.maxDepth
                  else:
                      isTouched = True
  
    def show(self):
      for SST in self.SSTs:
          SST.show()    
    
  


def argParser(args, size, *parameters):
    
    returnData = []
    
    if len(args) < size[0]:
        print('ERROR: too few arguments passed to arg interpreter!')
        sys.exit(9)
    elif len(args) > size[1]*2:
        print('ERROR: too many arguments passed to arg interpreter!')
        sys.exit(9)

    parseValue = False
       
    for arg in args:
        if parseValue:
            returnData.append(arg)
            parseValue = False
            continue
        
        for parameter in parameters:
            if parameter == arg: 
                parseValue = True
                break
        if not parseValue:            
            print('ERROR: key is not defined!')
            sys.exit(9)
               

    return returnData
