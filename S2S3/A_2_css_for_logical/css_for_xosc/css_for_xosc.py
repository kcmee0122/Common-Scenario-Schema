import json
import os
import scipy
import h5py
import numpy as np
import pandas as pd
from colorama import Fore
from tqdm import tqdm
import glob
from Utils.schema_for_morai_1_1 import *
import natsort
from pathlib import Path
from pymongo import MongoClient

##################### Setting ##########################

# 생성할 Logical scenario catalog
MORAI_Sceanrio_Catalog_KATRI = 0
MORAI_Sceanrio_Catalog_SOTIF = 1

# MORAI_Sceanrio_Catalog_SOTIF의 map name
SOTIF_map = 0                        ## 0 : V_RHT_HighwayJunction_1, 1 : V_RHT_Suburb_02

# Logical scenario 생성 토글
single_toggle = 0              # 1:ON  0:OFF
i = 0                           # 생성할 Logical scenario 번호 (single toggle에 해당, 가장 아래 번호 리스트 확인 가능)

multiple_toggle =1             # 1:ON  0:OFF

# 파일 경로
registration_dir = r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for SOTIF\MORAI Project\Registration"
if MORAI_Sceanrio_Catalog_KATRI:
    save_dir = r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for KATRI\MORAI Project\Json"
else:
    save_dir = r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for SOTIF\MORAI Project\Json"

# MongoDB 연결 설정
client = MongoClient('mongodb://192.168.75.251:27017/')
db = client['SOTIF']
collection = db['logicalScenario']  # 업로드할 컬렉션 이름 설정

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


def make_CSS(xosc_dir, simulation_name, registration_dir, save_dir):
        
    path = './S2S3/A_2_css_for_logical/css_for_xosc/Configs/schema_v1.1.json'
    # path = './Configs/schema_v1.1.json'
    css = read_json(path)
    
    file_name = simulation_name + ".json"
    file_path = os.path.join(save_dir, file_name)

    tmk = Makejson(xosc_dir, registration_dir, simulation_name)
    
    #admin
    css['admin']['filePath']['raw'] = tmk.xosc_file_path.replace('D:', '\\\\192.168.75.251')
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
    
    css['scenarios']['entities'] = []
    # print(tmk.entities)
    for entity in tmk.entities:
        css['scenarios']['entities'].append(
            entity
        )

    css['scenarios']['storyboard']['name'] = tmk.scenario

    css['scenarios']['storyboard']['init']['actions']['privates'] = []
    for private in tmk.privates:
        css['scenarios']['storyboard']['init']['actions']['privates'].append(
            private
        )
    
    css['scenarios']['storyboard']['stories']['maneuverGroups'] = []
    for maneuver_group in tmk.maneuver_groups:
        css['scenarios']['storyboard']['stories']['maneuverGroups'].append(
            maneuver_group
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
    if MORAI_Sceanrio_Catalog_KATRI == 1:   
        xosc_dir=r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for KATRI\MORAI Project\openscenario\R_KR_PG_KATRI"
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
                            "LK_LFL2R_IN",                    # 19
                            "LK_LFR2L_IN",                    # 20
                            "LK_LTOD2R_IN",                   # 21
                            "LK_RTR2SD_IN",                   # 22
                            "LT_LFL2R_IN",                    # 23
                            "LT_LFR2L_IN",                    # 24
                            "LT_OVE_IN",                      # 25
                            "Merge",                          # 26
                            "Overtaking_4th",                 # 27
                            "RT_LFL2R_IN",                    # 28
                            ]
    elif MORAI_Sceanrio_Catalog_SOTIF == 1:         
        if SOTIF_map == 0:    ## V_RHT_HighwayJunction_1
            xosc_dir=r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for SOTIF\MORAI Project\openscenario\V_RHT_HighwayJunction_1"    
            simulation_datas = ["decVehInAnAdjLane",             # 0
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
                            ]
        elif SOTIF_map == 1:    ## V_RHT_Suburb_02
            xosc_dir=r"\\192.168.75.251\Shares\MORAI Scenario Data\Scenario Catalog for SOTIF\MORAI Project\openscenario\V_RHT_Suburb_02"    
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
                            "LT_LFR2L_IN",                      # 12
                            "LT_OVE_IN",                        # 13
                            "LT_PCSL_IN",                       # 14
                            "LT_PCSR_IN",                       # 15
                            "RT_LFL2R_IN",                      # 16
                            "RT_PCSL_IN",                       # 17
                            "RT_PCSR_IN",                       # 18
                            "nonSignaledIntersection",          # 19
                            ]
        
    # 하나의 시뮬레이션 데이터에 대해 확인할 때 사용
    if single_toggle == 1:
        print(simulation_datas[i] + '.json 생성중...')
        make_CSS(xosc_dir, simulation_datas[i], registration_dir, save_dir)
        print(simulation_datas[i] + '.json 완성!!!')
        print('-'*30)
    
    # 여러개의 시뮬레이션 데이터에 대해 확인할 때 사용
    elif multiple_toggle == 1:   
        for simulation_data in simulation_datas:
            print(simulation_data + '.json 생성중...')
            make_CSS(xosc_dir,simulation_data, registration_dir, save_dir)
            print(simulation_data + '.json 완성!!!')
            print('-'*30)




    