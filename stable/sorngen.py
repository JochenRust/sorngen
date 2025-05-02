##################################################################
##
## file: sorngen.py
##
## description: sorngen main file
##
## (c) 2020 Jochen Rust
##     DSI aerospace technology
##
##################################################################

## import python packages
#import string
#import ast
import os

from stable.control.version import version
from stable.designflow.designflow_functions import run_parsing, run_elaboration, run_arch_builder, run_sorn_builder, run_file_writer
## import sorngen packages

#import sorngen_datapath as dp
# import evaluation.ThreeInputEval as evaluator

def info():
    print("###################################################")
    print("##")
    print("## SORNGEN - Sets Of Real Numbers HDL generator")
    print("##")
    print("## (c) 2020 DSI Aerospace Technologie GmbH")
    print("##")
    print(f"## {version}")
    print("##")
    print("###################################################")

def main():

    ## 1/ read data
    env = run_parsing()

    ## 2/ elaborate
    run_elaboration(env)

    ## 3/ generate sorn HDL data
    run_arch_builder(env)

    # 3.8/ build toplevel
    # 3.9/ build sorn components
    run_sorn_builder(env)

    ## 4/ write HDL data to file
    run_file_writer(env)


if __name__ == '__main__':
    info()
    os.environ['standalone'] = 'true'
    main()