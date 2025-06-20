##################################################################
##
## file: designflow_functions.py
##
## description: provides functions for every designflow step
##
## (c) 2020-25 
##     Hamburg University of Applied Sciences
##     University of Bremen
##
## Contributors
##  Jochen Rust, Moritz Bärthel, Nils Hülsmeier, Marvin Henkel
##
##################################################################

import os
import sys

from stable import __file__ as module_root
from stable.control import ctrl_env as sornenv
from stable.designflow import design_parser as parser
from stable.designflow import design_elaborator as elaborator
from stable.designflow import design_HDL as builder
from stable.datatypes import type_HDL as dp
from stable.designflow import design_writeFile as write

def run_parsing():
    ## 1/ read data
    # 1.1/ initialize global sorngen environment
    env = sornenv.sornEnv()
    # 1.2/ read input data
    env = parser.parseInput(env, sys.argv, os.path.dirname(os.path.abspath(module_root)))

    return env

def run_elaboration(env):
    ## 2/ elaborate
    ## 2.1/ save abstract syntax tree (AST) to  sorn syntax tree (SST)
    env = elaborator.createSST(env)
    env = elaborator.merge(env, 'numeric', True, 'univariate', True, 'trivariate', True)
    env = elaborator.connectSSTs(env)
    env = elaborator.insertRegister(env)
    env.show()

    return env

def run_arch_builder(env):
    ## 3/ generate sorn HDL data
    for SST in env.SSTs:
        print("3/ *** Start of '" + SST.name + "' SORN HDL file build ***")
        # 3.1/ insert register
        #    env.lValueDictSST[cValue] = builder.insertRegisterToSST(env.lValueDictSST[cValue], env.pipelineLocation)
        # 3.2/ set up new HDL datatype
        HDL = dp.sornHDL(SST.name + "_module")
        # 3.3/ build instances
        HDL = builder.createHDLInstancesFromSST(HDL, SST)
        # 3.4/ build ports
        HDL = builder.createHDLGlobalPortsFromSST(HDL, SST)
        # 3.5/ build nets
        HDL = builder.createHDLNetsFromSST(HDL, SST)
        # 3.6/ register HDL data to SORN environment
        env.dictHDL[SST.name] = HDL.copy()
        env.HDL.append(env.dictHDL[SST.name])
        HDL.show()
        # 3.7/ clear local HDL datatype
        HDL.clear()

    return env

def run_sorn_builder(env):
    # 3.8/ build toplevel
    [env.dictHDL, env.HDL] = builder.createToplevelInstance(env)

    # 3.9/ build sorn components
    builder.generateFunctionTable(env)

    return env

def run_file_writer(env):
    ## 0/ check for existing folder structure
    if not os.path.exists(f"{env.save_path}/VHDL"):
        # create subfolder ".\VHDL"
        os.makedirs(f"{env.save_path}/VHDL")
    if not os.path.exists(f"{env.save_path}/VHDL/VHDLbasic"):
        # create subfolder "./VHDL/VHDLbasic"
        os.makedirs(f"{env.save_path}/VHDL/VHDLbasic")

    ## 4/ write HDL data to file
    write.writeToVHDL(env)


def is_standalone():
    return os.getenv('standalone', False) == 'true'
