# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 15:31:06 2022

@author: Baerthel
"""

def ThreeInputEval(env):
    
    print('\n--------------')
    print('### Three Input Hypot Evaluation:')
    
    zf_table = env.dictHDL['zf'].instances[0].FctnTable
    zhf_table = env.dictHDL['zhf'].instances[0].FctnTable
    znf_table = env.dictHDL['znf'].instances[0].FctnTable
    
    zf_mean_ones = 0
    zhf_mean_ones = 0
    znf_mean_ones = 0
    
    for inA in range(0,zf_table.datatypeOUT.sornsize):
        for inB in range(0,zf_table.datatypeOUT.sornsize):
            for inC in range(0,zf_table.datatypeOUT.sornsize):
                zf_mean_ones += zf_table.resultSORN[inA][inB][inC].count(1)
                zhf_mean_ones += zhf_table.resultSORN[inA][inB][inC].count(1)
                znf_mean_ones += znf_table.resultSORN[inA][inB][inC].count(1)
                
    zf_mean_ones = zf_mean_ones/(zf_table.datatypeOUT.sornsize**3)
    zhf_mean_ones = zhf_mean_ones/(zf_table.datatypeOUT.sornsize**3)
    znf_mean_ones = znf_mean_ones/(zf_table.datatypeOUT.sornsize**3)
    print('Mean Number of Ones:')
    print('Fused: ', zf_mean_ones)
    print('Half Fused: ', zhf_mean_ones)
    print('Non Fused: ', znf_mean_ones)