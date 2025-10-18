"""
auther: 서도현
update: 2024.02.27
description: 
    v01: rawPS에 대한 json 생성 (서도현)
    v02: rawPS에 대한 경로 및 토그 생성 (김승환)
    v03: rawPS DB에 업로드하는 함수 추가 (임동현)
"""

import json
import sys
import os
import numpy as np
import pandas as pd
from colorama import Fore
from tqdm import tqdm
import glob
from utils.utilsForPS_v1_1 import *
import natsort
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient  # 추가

##################### Setting ##########################

# 생성할 Logical scenario catalog
MORAI_Sceanrio_Catalog_KATRI = 1
MORAI_Sceanrio_Catalog_SOTIF = 0
Precrash_Scenario_Catalog_Augmented = 0
Precrash_Scenario_Catalog_IDM = 0
Precrash_Scenario_Catalog_Car_to_Car = 0
Precrash_Scenario_Catalog_Car_to_VRU = 0

# Folder date
# folder_date = '060522'
# folder_date = '123121'
# folder_date = '123021'
# folder_date = '073024'
# folder_date = '103024'
# folder_date = '102124'
# folder_date = '102824'
# folder_date = '013025'
# folder_date = '111424'
folder_date = '111624'


# Logical scenario 생성 토글
single_toggle = 1               # 1:ON  0:OFF
i = 25                           # 생성할 Logical scenario 번호 (single toggle에 해당, 가장 아래 번호 리스트 확인 가능)

multiple_toggle = 0             # 1:ON  0:OFF

# 파일 경로

if MORAI_Sceanrio_Catalog_KATRI:
    save_dir = r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for KATRI\MORAI Project\Json"
    registration_dir = r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for KATRI\MORAI Project\Registration"
else:
    save_dir = r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for SOTIF\MORAI Project\Json"
    registration_dir = r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for SOTIF\MORAI Project\Registration"

# MongoDB 연결 설정
client = MongoClient('mongodb://192.168.75.251:27017/')
db = client['SOTIF']
collection = db['parameterSpace']  # 업로드할 컬렉션 이름 설정

########################################################


def upload_to_mongodb(json_file_path):
    """MongoDB에 JSON 파일 업로드"""
    with open(json_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # 중복 확인 (admin.filePath.raw 기준)
    check_query = {"admin.filePath.raw": json_data["admin"]["filePath"]["raw"]}
    existing_document = collection.find_one(check_query)
    
    if existing_document:
        print(f"[중복] 이미 존재하는 문서: {existing_document['_id']}")
    else:
        result = collection.insert_one(json_data)
        print(f"[업로드 성공] MongoDB Document ID: {result.inserted_id}")


def make_CSS(PS_dir, folder_date, scenario_name, save_dir = None):
    if save_dir is None:
        tmp_dir = PS_dir.split('\\PS')[0]
        raw_PS_dir = os.path.join(PS_dir, scenario_name, folder_date).replace('D:', '\\\\192.168.75.251')
        tmp_save_dir = os.path.join(tmp_dir, 'Json', scenario_name, folder_date).replace('D:', '\\\\192.168.75.251')
            
    if os.path.isdir(raw_PS_dir):
        # 저장할 경로의 폴더가 없으면 생성
        if os.path.isdir(tmp_save_dir) == False:
            os.makedirs(tmp_save_dir)
            
        path = './S2S3/A_4_css_for_rawPS/configs/schema_v1.1.json'
        # path = './Configs/schema_v1.1.json'
        css = read_json(path)

        tmp_PS_dir = os.listdir(raw_PS_dir)
        raw_file = [file for file in tmp_PS_dir if 'raw' in file]

        PS_CSV_File_name = raw_file[0].split('.')[0]
        file_name = PS_CSV_File_name + ".json"
        save_dir = os.path.join(tmp_save_dir, file_name)
        tmk = Makejson(PS_dir, PS_CSV_File_name, registration_dir, folder_date)
        
        #admin
        if 'D:' in tmk.PS_file_path :
            css['admin']['filePath']['raw'] = tmk.PS_file_path.replace('D:', '\\\\192.168.75.251')
        else:
            css['admin']['filePath']['raw'] = tmk.PS_file_path
        css['admin']['filePath']['exported'] = " "

        # registration_dir 확인 및 설정
        if os.path.exists(registration_dir):
            css['admin']['filePath']['registration'] = registration_dir.replace('D:', '\\\\192.168.75.251')
        else:
            css['admin']['filePath']['registration'] = " "
            print(f"[경고] Registration 디렉터리가 존재하지 않습니다: {registration_dir}") # registration 값 설정하지 않음
        
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
        css['scenarios']['dataSources']['expertKnowledge'] = []

        for expert in tmk.expertKnowledge:
            css['scenarios']['dataSources']['expertKnowledge'].append(
                expert
        )

        css['scenarios']['dataSources']['accidentData'] = []
        
        for data in tmk.accidentData:
            css['scenarios']['dataSources']['accidentData'].append(
                data
            )


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
        
        print(f"생성된 JSON 파일 경로: {save_dir}")

        # JSON 파일 MongoDB에 업로드
        upload_to_mongodb(save_dir)
        
        # print(scenario_name + '.json 완성!!!')
        # print('-'*30)

    else:
        print(Fore.RED + f'{folder_date} 폴더가 존재하지 않습니다.' + Fore.RESET)
        return None


if __name__ == "__main__":

    # Logical scenario catalog
    if MORAI_Sceanrio_Catalog_KATRI == 1:
        PS_dir =r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for KATRI\MORAI Project\PS"
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
                            "UnprotectedLeftTurn",            # 15
                            "Cut_in",                         # 16
                            "Cut_Through",                    # 17
                            "교통신호대응(III)",               # 18
                            "Merge",                          # 19
                            "Overtaking_4th",                 # 20
                            "LK-CL",                          # 21
                            "LK-CR",                          # 22
                            "LK-TL",                          # 23
                            "LT-CL",                          # 24
                            "LT-OC",                          # 25
                            ]
    elif MORAI_Sceanrio_Catalog_SOTIF == 1:      
            PS_dir =r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for SOTIF\MORAI Project\PS"
            simulation_datas = ["decVehInAnAdjLane",         # 0
                            "LCL_LF_ST",                     # 1
                            "LCR_LF_ST",                     # 2
                            "LK_CIL_ST",                     # 3
                            "LK_CIR_ST",                     # 4
                            "LK_COL_STP_ST",                 # 5
                            "LK_COR_STP_ST",                 # 6
                            "LK_LF_ST",                      # 7
                            "LK_STP_ST",                     # 8
                            "rearCrash",                     # 9
                            "overReliance",                  # 10
                            "drivingAlone",                  # 11
                            "LK_LFL2R_IN",                      # 12
                            "LK_LFR2L_IN",                      # 13
                            "LK_LTOD2R_IN",                     # 14
                            "LK_LTL2SD_IN",                     # 15
                            "LK_PCSL_ST",                       # 16
                            "LK_PCSR_ST",                       # 17
                            "LK_POCL_ST",                       # 18
                            "LK_POCR_ST",                       # 19
                            "LK_PSTP_ST",                       # 20
                            "LK_PWAL_ST",                       # 21
                            "LK_PWAR_ST",                       # 22
                            "LT_LFL2R_IN",                      # 23
                            "LT_LFR2L_IN",                      # 24
                            "LT_OVE_IN",                        # 25
                            "LT_PCSL_IN",                       # 26
                            "LT_PCSR_IN",                       # 27
                            "RT_LFL2R_IN",                      # 28
                            "RT_PCSL_IN",                       # 29
                            "RT_PCSR_IN",                       # 30
                            "nonSignaledIntersection",          # 31
                            ]

    elif Precrash_Scenario_Catalog_Augmented == 1:      
            PS_dir =r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Augmented\PS"
            simulation_datas = ["COL_STP_ST",                # 0
                            "drivingAlone_AVL_ST",           # 1
                            "drivingAlone_FPR_ST",           # 2
                            "drivingAlone_FVR_ST",           # 3
                            "drivingAlone_RVL_RAB",          # 4
                            "LK_CIR_MER_RAB",                # 5
                            "LK_CIR_ST",                     # 6
                            "LT_LFL2R_IN",                   # 7
                            "parking_FCR_ST",                # 8
                            "UT_LF_ST",                      # 9
                            ]

    elif Precrash_Scenario_Catalog_IDM == 1:      
            PS_dir =r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for IDM\PS"
            simulation_datas = ["LCL_LF_ST_only_IDM",        # 0
                            "LCR_LF_ST_only_IDM",            # 1
                            "LK_CIL_CU_only_IDM",            # 2
                            "LK_CIL_ST_only_IDM",            # 3
                            ]

    elif Precrash_Scenario_Catalog_Car_to_Car == 1:      
            PS_dir =r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Car to Car\PS"
            simulation_datas = ["LCL_LF_ST",                 # 0
                            "LCR_LF_ST",                     # 1
                            "LK_BWD_ST",                     # 2
                            "LK_CIL_CU",                     # 3
                            "LK_CIL_SH",                     # 4
                            "LK_CIL_ST",                     # 5
                            "LK_CIR_CU",                     # 6
                            "LK_CIR_MER",                    # 7
                            "LK_CIR_ST",                     # 8
                            "LK_COL_STP_SH",                 # 9  
                            "LK_COL_STP_ST",                 # 10
                            "LK_COR_STP_CU",                 # 11
                            "LK_COR_STP_ST",                 # 12
                            "LK_LF_SH",                      # 13
                            "LK_LF_ST",                      # 14
                            "LK_LFL2R_IN",                   # 15
                            "LK_LFR2L_IN",                   # 16
                            "LK_LTOD2R_IN",                  # 17
                            "LK_OVE_CU",                     # 18
                            "LK_OVE_ST",                     # 19
                            "LK_RTR2SD_IN",                  # 20
                            "LK_STP_CU",                     # 21
                            "LK_STP_ST",                     # 22
                            "LT_LFL2R_IN",                   # 23
                            "LT_LFR2L_IN",                   # 24
                            "LT_OVE_IN",                     # 25
                            "RT_LFL2R_IN",                   # 26
                            "UT_LF_ST",                      # 27
                            "UT_OVE_ST",                     # 28
                            ]

    elif Precrash_Scenario_Catalog_Car_to_VRU == 1:      
            PS_dir =r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Precrash Scenario(Car-to-VRU)\PS"
            simulation_datas = ["LK_CCIR_ST",                # 0
                            "LK_CCSL_ST",                    # 1
                            "LK_CCSR_ST",                    # 2
                            "LK_CGS_ST",                     # 3
                            "LK_CGSL2R_IN",                  # 4
                            "LK_CGSR2L_IN",                  # 5
                            "LK_CIR_CU",                     # 6
                            "LK_COCL_ST",                    # 7
                            "LK_CSTP_ST",                    # 8
                            "LK_ECSL_ST",                    # 9  
                            "LK_ECSL_STP_ST",                # 10
                            "LK_EGSL2R_IN",                  # 11
                            "LK_EGSR2L_IN",                  # 12
                            "LK_PCSL_ST",                    # 13
                            "LK_PCSL_STP_ST",                # 14
                            "LK_PCSR_ST",                    # 15
                            "LK_PCSR_STP_ST",                # 16
                            "LK_POCL_ST",                    # 17
                            "LK_POCR_ST",                    # 18
                            "LK_PSTP_ST",                    # 19
                            "LK_PWAL_ST",                    # 20
                            "LK_PWAR_ST",                    # 21
                            "LT_CCSL_IN",                    # 22
                            "LT_CCSR_IN",                    # 23
                            "LT_CGSR2L_IN",                  # 24
                            "LT_COC_IN",                     # 25
                            "LT_ECSL_IN",                    # 26
                            "LT_EGSR2L_IN",                  # 27
                            "LT_EOC_IN",                     # 28
                            "LT_PCSL_IN",                    # 29
                            "LT_PCSR_IN",                    # 30
                            "LT_POC_IN",                     # 31
                            "RT_CCSL_IN",                    # 32
                            "RT_CCSR_IN",                    # 33
                            "RT_CGSL2R_IN",                  # 34
                            "RT_CGSR2L_IN",                  # 35
                            "RT_CSD_IN",                     # 36
                            "RT_ECSL_IN",                    # 37
                            "RT_ECSR_IN",                    # 38
                            "RT_EGSL2R_IN",                  # 39
                            "RT_EGSR2L_IN",                  # 40
                            "RT_PCSL_IN",                    # 41
                            "RT_PCSR_IN",                    # 42
                            ]


    # 하나의 시뮬레이션 데이터에 대해 확인할 때 사용
    if single_toggle == 1:
        print(simulation_datas[i] + '_rawPS.json 생성중...')
        make_CSS(PS_dir, folder_date, simulation_datas[i])
        print(simulation_datas[i] + '_rawPS.json 완성!!!')
        print('-'*30)
    
    # 여러개의 시뮬레이션 데이터에 대해 확인할 때 사용
    elif multiple_toggle == 1:   
        for simulation_data in simulation_datas:
            print(simulation_data + '_rawPS.json 생성중...')
            make_CSS(PS_dir, folder_date, simulation_data)
            print('-'*30)



    