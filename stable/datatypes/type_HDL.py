##################################################################
##
## file: type_HDL.py
##
## description: sorngen datatypes - HDL datatype declaration
##
## (c) 2020 Jochen Rust
##     DSI aerospace technologie GmbH
##
##################################################################

import copy
import sys

## 1/ global SORN HDL environment
class sornHDL:

  name      = "n/a"
  ports     = []
  instances = []
  nets      = []
  datatype  = "n/a"
  idInst    = {}
  isToplevel = False

  def __init__(self, name):
    self.name = name

  def clear(self):
    self.name = "n/a"
    self.datatype = "n/a"
    del self.ports[:]
    del self.instances[:]
    del self.nets[:]
    self.idInst.clear()

  def copy(self):

    ## #i02 BUGFIX
    ## rationale: replaced deepcopy command by copy command to save memory resources
    
#    newInst = sornHDL(self.name)
#    newInst.name = copy.deepcopy(self.name)
#    newInst.name = self.name
#    newInst.datatype = copy.deepcopy(self.datatype)
#    newInst.ports = copy.deepcopy(self.ports)
#    newInst.instances = copy.deepcopy(self.instances)
#    newInst.nets = copy.deepcopy(self.nets)
#    newInst.idInst = copy.deepcopy(self.idInst)

    newInst = sornHDL(self.name)
    newInst.name = copy.copy(self.name)
    newInst.datatype = copy.copy(self.datatype)
    newInst.ports = copy.copy(self.ports)
    newInst.instances = copy.copy(self.instances)
    newInst.nets = copy.copy(self.nets)
    newInst.idInst = copy.copy(self.idInst)
    ## #i02 END OF BUGFIX

    return newInst

  def show(self):
      print("--------")
      print("-- Name: "+self.name)
      print("--------")
      print("")
      print("global ports")
      print("--------")
      for it in self.ports:
          if not it.isGlobal: continue
          print("inputs:  " if it.isInput else "outputs: ", end="")
          print("/"+it.name+"/")
      print("")
      print("internal ports")
      print("--------")
      for it in self.instances:
        for it2 in it.ports:
          if self.isToplevel and (not it2.isGlobal): continue
          print("inputs:  " if it2.isInput else "outputs: ", end="")
          print("/"+it.name+"/"+it2.name+"/")
      print("")
      print("instances")
      print("--------")
      for it in self.instances:
          print(it.name)
      print("")
      print("nets: ")
      print("--------")
      for it in self.nets:
          print(it.name+"\t", it.getConnectionStr())

## 2/ SORN nets
class sornNet:

    def __init__(self, env, name):
        self.name     = name
        self.env      = env
        self.ports    = []
        self.datatype = "n/a"
        env.nets.append(self)
  
    def clear(self):
        self.name     = ""
        self.env      = []
        self.ports    = []
        self.datatype = ""
        
    def getConnectionStr(self):
        connectionStr = "["
        # get inputs
        for port in self.ports:
            # global input port
            if port.isInput and port.isGlobal:
                connectionStr = connectionStr+port.name+" -> "
            elif not port.isInput and not port.isGlobal:
                connectionStr = connectionStr+port.instances[0].name+"("+port.name+") -> "

        # get outputs
        for port in self.ports:
            if not port.isInput and port.isGlobal:
                connectionStr = connectionStr+port.name+"]"
            elif port.isInput and not port.isGlobal:
                connectionStr = connectionStr+port.instances[0].name+"("+port.name+")]"

        
        return connectionStr

## 3/ SORN instances
class sornInstance:

  # constructor
  def __init__(self, env, name, function, inputList):
      # 3.1/ default assignments
      self.id = None
      self.name = name
      self.env = env
      self.function = function
      self.FctnTable = []
      self.ports = []
      self.nodeSST = None
      self.depth = 0
      self.isRegister = False
      self.fromRegister = False
      self.toRegister = False
      # 3.2/ register instance to environment
      env.instances.append(self)

  def clear(self):
      self.name     = ""
      self.env      = []
      self.function = []
      self.FctnTable = []
      self.ports    = []
      self.depth = 0
      self.id       = 0

## 4/ SORN ports
class sornPort:

  def __init__(self, env):

      # 4.1/ default assignments
      self.name      = ""
      self.env       = env
      self.isInput   = False
      self.isGlobal  = False
      self.nets      = []
      self.instances = []
      self.datapath  = []
      # 4.2/ register ports to environment
      env.ports.append(self)

  def clear(self):
      self.name     = ""
      self.env      = []
      self.isInput  = []
      self.isGlobal  = []
      self.nets    = []
      self.instances = []
      self.datapath = []

## 5 register elements
def register(type0, type1):

    ## 5.1/ catch invalid types
    if not (type(type0) is sornPort or type(type0) is sornInstance or type(type0) is sornNet):
        print("ERROR: type "+str(type(type0))+" not supported!")
        sys.exit(0)
    if not (type(type1) is sornPort or type(type1) is sornInstance or type(type1) is sornNet):
        print("ERROR: type "+str(type(type1))+" not supported!")
        sys.exit(0)
    ## 5.2/ catch invalid combination of types
    if (type(type0) is sornNet and type(type1) is sornInstance) or (type(type1) is sornNet and type(type0) is sornInstance) :
        print("ERROR: type "+str(type(type0))+" cannot directly be connected to type "+str(type(type0))+"!")
        sys.exit(0)

    ## 5.3/ register type1 to type0
    # TODO: Match case?
    if type(type1) is sornPort:
      type0.ports.append(type1)
    elif type(type1) is sornInstance:
      type0.instances.append(type1)
    elif type(type1) is sornNet:
      type0.nets.append(type1)

    # 5.4/ register type0 to type1
    if type(type0) is sornPort:
      type1.ports.append(type0)
    elif type(type0) is sornInstance:
      type1.instances.append(type0)
    elif type(type0) is sornNet:
      type1.nets.append(type0)
