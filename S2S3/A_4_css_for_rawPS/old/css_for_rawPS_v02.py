"""
auther: 서도현
update: 2024.02.27
description: 
    v01: rawPS에 대한 json 생성 (서도현)
    v02: rawPS에 대한 경로 및 토그 생성 (김승환)
"""

import json
import os
import scipy
import h5py
import numpy as np
import pandas as pd
from colorama import Fore
from tqdm import tqdm
import glob
# from Utils_for_PS.base_v1_1 import *
from utils.utilsForPS_v1_1 import *
import natsort
from pathlib import Path
from datetime import datetime  # 추가


##################### Setting ##########################

# 생성할 Logical scenario catalog
TESTBED = 0
SOTIF_1ST = 0
SOTIF_2ND = 0
SOTIF_3RD = 1

# Logical scenario 생성 토글
single_toggle = 1              # 1:ON  0:OFF
i = 0                           # 생성할 Logical scenario 번호 (single toggle에 해당, 가장 아래 번호 리스트 확인 가능)

multiple_toggle = 0             # 1:ON  0:OFF

########################################################




def make_CSS(PS_dir, scenario_name, save_dir = None):
    if save_dir is None:
        tmp_dir = PS_dir.split('\\PS')[0]
        tmp_save_dir = os.path.join(tmp_dir, 'Json', 'rawPS')
        
    # 저장할 경로의 폴더가 없으면 생성
    if os.path.isdir(tmp_save_dir) == False:
        os.makedirs(tmp_save_dir)
        
    path = './Configs/schema_v1.1.json'
    css = read_json(path)
    PS_CSV_File_name = scenario_name + "_rawPS"
    file_name = PS_CSV_File_name + ".json"
    save_dir = os.path.join(tmp_save_dir, file_name)
    tmk = Makejson(PS_dir, PS_CSV_File_name)
    
    #admin
    if '192.168.75.251' in tmk.PS_file_path :
        css['admin']['filePath']['raw'] = tmk.PS_file_path.replace('\\\\192.168.75.251', 'D:')
    else :
        css['admin']['filePath']['raw'] = tmk.PS_file_path
        css['admin']['filePath']['exported'] = " "
        css['admin']['filePath']['registration'] = " "
        css['admin']['filePath']['perception']['LDT'] = " " 
        css['admin']['filePath']['perception']['SF'] = " "
        css['admin']['filePath']['perception']['recognition'] = " "
        css['admin']['filePath']['Decision']['maneuver'] = " "
        css['admin']['date'] = tmk.date
        css['admin']['dataType'] = tmk.dataType
        css['admin']['travelTime'] = " "
        css['admin']['travelDistance'] = " "
        css['admin']['fileSize'] =" "
        css['admin']['geoReference']['type'] = " "
        css['admin']['geoReference']['coordinates'] = " "
        css['admin']['frameInterval']['frameStart'] = " "
        css['admin']['frameInterval']['frameEnd'] = " "
        css['admin']['sampleTime'] = " "
        css['admin']['schemaVersion'] = tmk.schemaVersion
        css['admin']['comment'] = " "
        css['admin']['CMGT'] = " "
        css['admin']['CAGT'] = " "
        css['admin']['sensorConfiguration'] = " "
        css['admin']['qualityOfData'] = " "
    
    #dynamic
    css['dynamic'] = " "
    
    #surroundings
    css['surroundings'] = " "
    
    #scenarios
    css['scenarios'] = " "
    
    #parameterSpace
    css['parameterSpace']['reduceParam'] = " "
    css['parameterSpace']['samplingMethod'] = " "
    css['parameterSpace']['parameters'] = []
    for paramter in tmk.parameters:
        css['parameterSpace']['parameters'].append(
            paramter
        )
            
    #road
    css['road'] = " "
    #Meta
    css['Meta'] = " "

    with open(save_dir, 'w', encoding='utf-8') as file:
        json.dump(css, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":

    # Logical scenario catalog
    if TESTBED == 1:   
        PS_dir =r"D:\Shares\MORAI Scenario Data\SOTIF Catalogue\MORAI Project\PS"
        simulation_datas = ["Backing",                       # 0 
                            "DoubleParked",                  # 1
                            "EndofTrafficJam",               # 2
                            "FrontVehicleDeceleration",      # 3
                            "IgnoreStopSign",                # 4
                            "IlligalParkingOnNarrowRoad",    # 5
                            "NeighboringLaneOccupied",       # 6
                            "NonSignaledIntersection",       # 7
                            "Over_reliance",                 # 8
                            "Overtaker",                     # 9
                            "Overtaking",                    # 10
                            "PassingEgoVehicle",             # 11
                            "RightTurn",                     # 12
                            "SuddenPedestrianAppear",        # 13
                            "TrafficJam",                    # 14
                            "UnprotectedLeftTurn"            # 15
                            ]
    elif SOTIF_1ST == 1:                    
        PS_dir =r"D:\Shares\MORAI Scenario Data\SOTIF Catalogue\MORAI Project\PS"    
        simulation_datas = ["decVehInAnAdjLane",             # 0
                            "LCL_LF_ST",                     # 1
                            "LCR_LF_ST",                     # 2
                            "LK_CIL_ST",                     # 3
                            "LK_CIR_ST",                     # 4
                            "LK_COL_STP_ST",                 # 5
                            "LK_COR_STP_ST",                 # 6
                            "LK_LF_ST",                      # 7
                            "LK_STP_ST",                     # 8
                            "overReliance",                  # 9
                            "nonSigIntersection",            # 10
                            "rearCrash"                      # 11
                            ]
    elif SOTIF_2ND == 1:
        PS_dir =r"D:\Shares\MORAI Scenario Data\SOTIF Catalogue\MORAI Project\PS"    
        simulation_datas = ["LK_LFL2R_IN",                      # 0
                            "LK_LFR2L_IN",                      # 1
                            "LK_LTOD2R_IN",                     # 2
                            "LK_LTL2SD_IN",                     # 3
                            "LK_PCSL_ST",                       # 4
                            "LK_PCSR_ST",                       # 5
                            "LK_POCL_ST",                       # 6
                            "LK_POCR_ST",                       # 7
                            "LK_PSTP_ST",                       # 8
                            "LK_PWAL_ST",                       # 9
                            "LK_PWAR_ST",                       # 10
                            "LT_LFL2R_IN",                      # 11
                            "LT_OVE_IN",                        # 12
                            "LT_PCSL_IN",                       # 13
                            "LT_PCSR_IN",                       # 14
                            "RT_LFL2R_IN",                      # 15
                            "RT_PCSL_IN",                       # 16
                            "RT_PCSR_IN",                       # 17
                            ]
    elif SOTIF_3RD == 1:
        PS_dir =r"D:\Shares\MORAI Scenario Data\SOTIF Catalogue\MORAI Project\PS"    
        simulation_datas = ["drivingAlone",                     # 0
                            ]

    # 하나의 시뮬레이션 데이터에 대해 확인할 때 사용
    if single_toggle == 1:
        print(simulation_datas[i] + '.json 생성중...')
        make_CSS(PS_dir, simulation_datas[i])
        print(simulation_datas[i] + '.json 완성!!!')
        print('-'*30)
    
    # 여러개의 시뮬레이션 데이터에 대해 확인할 때 사용
    elif multiple_toggle == 1:   
        for simulation_data in simulation_datas:
            print(simulation_data + '.json 생성중...')
            make_CSS(PS_dir,simulation_data)
            print(simulation_data + '.json 완성!!!')
            print('-'*30)




    