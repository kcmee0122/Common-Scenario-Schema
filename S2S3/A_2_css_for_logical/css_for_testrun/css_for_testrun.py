import json
import os
import scipy
import h5py
import numpy as np
import pandas as pd
from colorama import Fore
from tqdm import tqdm
import glob
from Utils.schema_for_carmaker_1_1 import *
import natsort
from pathlib import Path
from pymongo import MongoClient


##################### Setting ##########################

# 생성할 Logical scenario catalog

Precrash_Scenario_Catalog_Augmented = 0
Precrash_Scenario_Catalog_IDM = 0
Precrash_Scenario_Catalog_Car_to_Car = 0
Precrash_Scenario_Catalog_Car_to_VRU = 1

# Logical scenario 생성 토글
single_toggle = 0              # 1:ON  0:OFF
i = 0                          # 생성할 Logical scenario 번호 (single toggle에 해당, 가장 아래 번호 리스트 확인 가능)

multiple_toggle = 1             # 1:ON  0:OFF

# 파일 경로
registration_dir = r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for SOTIF\MORAI Project\Registration"

if Precrash_Scenario_Catalog_Augmented:
    save_dir = r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Augmented\Json"
elif Precrash_Scenario_Catalog_IDM:
    save_dir = r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for IDM\Json"
elif Precrash_Scenario_Catalog_Car_to_Car:
    save_dir = r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for car to car\Json"
elif Precrash_Scenario_Catalog_Car_to_VRU:
    save_dir = r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Precrash Scenario(Car-to-VRU)\Json"   

# MongoDB 연결 설정
client = MongoClient('mongodb://192.168.75.251:27017/')
db = client['SOTIF']
collection = db['logicalScenario']  # 업로드할 컬렉션 이름 설정

# if Precrash_Scenario_Catalog_Car_to_VRU or Precrash_Scenario_Catalog_Car_to_Car:
#     db = client['METIS']
#     collection = db['Scenario']


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


def make_CSS(testrun_dir, simulation_name, registration_dir, save_dir):
        
    path = './S2S3/A_2_css_for_logical/css_for_testrun/Configs/schema_v1.1.json'
    # path = './Configs/schema_v1.1.json'
    css = read_json(path)
    
    file_name = simulation_name + ".json"
    file_path = os.path.join(save_dir, file_name)

    tmk = Makejson(testrun_dir, registration_dir, simulation_name)
    
    #admin
    css['admin']['filePath']['raw'] = tmk.testrun_file_path.replace('D:', '\\\\192.168.75.251')
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
    css['admin']['date'] = " "
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
    
    # for data in tmk.accidentData:
    #     css['scenarios']['dataSources']['accidentData'].append(
    #         data
    #     )
    
    css['scenarios']['entities'] = []
    # print(tmk.entities)
    # for entity in tmk.entities:
    #     css['scenarios']['entities'].append(
    #         entity
    #     )

    css['scenarios']['storyboard']['name'] = tmk.scenario

    css['scenarios']['storyboard']['init']['actions']['privates'] = []
    # for private in tmk.privates:
    #     css['scenarios']['storyboard']['init']['actions']['privates'].append(
    #         private
    #     )
    
    css['scenarios']['storyboard']['stories']['maneuverGroups'] = []
    # for maneuver_group in tmk.maneuver_groups:
    #     css['scenarios']['storyboard']['stories']['maneuverGroups'].append(
    #         maneuver_group
    #     )
    
    #parameterSpace
    css['parameterSpace']['reduceParam'] = " "
    css['parameterSpace']['samplingMethod'] = " "
    css['parameterSpace']['parameters'] = []
    # for paramter in tmk.parameters:
    #     css['parameterSpace']['parameters'].append(
    #         paramter
    #     )
            
    #road
    css['road']['roadName'] = " "
    css['road']['A2_LINK']['ID'] = " "
    css['road']['A2_LINK']['AdminCode'] = " " 
    css['road']['A2_LINK']['RoadRank'] = " "
    css['road']['A2_LINK']['RoadType'] = " "
    css['road']['A2_LINK']['LinkType'] = " "

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(css, file, indent=2, ensure_ascii=False)

    print(f"생성된 JSON 파일 경로: {file_path}")

    # JSON 파일 MongoDB에 업로드
    upload_to_mongodb(file_path)
    # jsonList = natsort.natsorted(glob.glob(save_dir + '\\*_tmp.json'))
    # tmp=[]
    # for i in range(np.size(jsonList)):
    #             with open(jsonList[i]) as file:
    #                 data = json.load(file)
    #                 tmp.append(data)

    # with open(save_dir + '\\' + vehicle_data + '.json' ,"w") as new_file:
    #     json.dump([tmp[i] for i in range(np.size(jsonList))] , new_file,indent='\t')
                
            
    # for file in jsonList:
    #     if file.endswith('_tmp.json'):
    #         os.remove(file)

# def check_is_annotation_file(mat_file):
    
#     mat_name = mat_file.split(".mat")[0]
#     annoatation = os.path.join(r'\\192.168.75.251\Shares\FOT_Avante Data_1\Rosbag2Mat', vehicle_data, 'Registration', 'Annotation')
    
#     for idx in os.listdir(annoatation):
#         if mat_name in idx:
#             return True
        
#    return False

if __name__ == "__main__":

# Logical scenario catalog    
    if Precrash_Scenario_Catalog_Augmented == 1:                    
        testrun_dir=r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Augmented\Carmaker Project\Data\TestRun"    
        simulation_datas = ["COR_STP_ST",                    # 0
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

    if Precrash_Scenario_Catalog_IDM == 1:                    
        testrun_dir=r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for IDM\CarMaker Project\Data\TestRun"    
        simulation_datas = ["LCL_LF_ST_only_IDM",            # 0
                            "LCR_LF_ST_only_IDM",            # 1
                            "LK_CIL_CU_only_IDM",            # 2
                            "LK_CIL_ST_only_IDM",            # 3
                            ]

    if Precrash_Scenario_Catalog_Car_to_Car == 1:                    
        testrun_dir=r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for car to car\CarMaker Project\Data\TestRun"    
        simulation_datas = ["LCL_LF_ST",                     # 0
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

    if Precrash_Scenario_Catalog_Car_to_VRU == 1:
        testrun_dir=r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Precrash Scenario(Car-to-VRU)\CarMaker Project\Data\TestRun"    
        simulation_datas = ["LK_CCIR_ST",                    # 0
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
        print(simulation_datas[i] + '.json 생성중...')
        make_CSS(testrun_dir, simulation_datas[i], registration_dir, save_dir)
        print(simulation_datas[i] + '.json 완성!!!')
        print('-'*30)
    
    # 여러개의 시뮬레이션 데이터에 대해 확인할 때 사용
    elif multiple_toggle == 1:   
        for simulation_data in simulation_datas:
            print(simulation_data + '.json 생성중...')
            make_CSS(testrun_dir,simulation_data, registration_dir, save_dir)
            print(simulation_data + '.json 완성!!!')
            print('-'*30)




    