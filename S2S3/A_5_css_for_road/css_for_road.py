### v1 by donghyeonLim : rd5파일을 json으로 변환하는 코드 생성
### Common Scenario Schema v1.1_112824.ppt를 참고하여 laneSection field 및 "coordinate"를 추가하였음 
# 특이사항 - (utilsForRoad.py) 
#           1. 시뮬레이션 도로는 laneSection field만 추가하였음
#           2. 실도로는 laneSection field의 "lanes"는 로직 수정이 필요하여 제외, "coordinate" 추가하였음

import json
import os
import scipy
import h5py
import numpy as np
import pandas as pd
from colorama import Fore
from tqdm import tqdm
import glob
from Utils.utilsForRoad import *
import natsort
from pathlib import Path
from pymongo import MongoClient


##################### Setting ##########################

# 생성할 Logical scenario catalog
SOTIF = 0
preCrash = 0
AES_TAAS_PCM = 1

# Logical scenario 생성 토글
single_toggle = 0              # 1:ON  0:OFF
i = 28                          # 생성할 Logical scenario 번호 (single toggle에 해당, 가장 아래 번호 리스트 확인 가능)

multiple_toggle = 1             # 1:ON  0:OFF

# 파일 경로
if SOTIF == 1:  
    registration_dir = ""
    # registration_dir = r"D:\Shares\MORAI Scenario Data\SOTIF Catalogue\MORAI Project\Registration"
    save_dir = r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Augmented\Json\Road"
elif preCrash == 1:
    registration_dir = ""
    save_dir = r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Car to Car\Json\Road"
elif AES_TAAS_PCM == 1:    
    # TAAS 교통사고 데이터 분석 경로 (위,경도)
    registration_dir = r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Augmented\Registration"
    save_dir = r"\\192.168.75.251\Shares\AES Scenario Data\Simulation\TAAS-PCM\Json\Road"

# MongoDB 연결 설정
client = MongoClient('mongodb://192.168.75.251:27017/')
db = client['SOTIF']
collection = db['road']  # 업로드할 컬렉션 이름 설정

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


def make_CSS(xodr_dir, simulation_name, registration_dir, save_dir):
# def make_CSS(xodr_dir, simulation_name, save_dir):
        
    path = './S2S3/A_5_css_for_road/Configs/schema_v1.1.json'
    css = read_json(path)
    
    file_name = simulation_name + ".json"
    file_path = os.path.join(save_dir, file_name)

    tmk = Makejson(xodr_dir, registration_dir, simulation_name)
    # tmk = Makejson(xodr_dir, simulation_name)

    # xodr 파일 경로 및 내용 가져오기
    xodr_file_path, xodr_file = tmk.get_xodr_file(xodr_dir, simulation_name)
    
    # road info
    config = tmk.parse_config(xodr_file)
    road_info = tmk.get_road(config, simulation_name)  # get_road 호출
    
    #admin
    css['admin']['filePath']['raw'] = tmk.xodr_file_path.replace('D:', '\\\\192.168.75.251')
    css['admin']['filePath']['exported'] = " "
    css['admin']['filePath']['registration'] = registration_dir.replace('D:', '\\\\192.168.75.251')
    # css['admin']['filePath']['registration'] = ""
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
    if registration_dir:
        css['admin']['geoReference']['coordinates'] = tmk.coordinate
    else:
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
    # for expert in tmk.expertKnowledge:
    #     css['scenarios']['dataSources']['expertKnowledge'].append(
    #         expert
    # )


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

    css['scenarios']['storyboard']['name'] = ""

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
    css['road']['laneSection'] = tmk.laneSection
    
    # for road in tmk.laneSection:
    #     css['road']['laneSection'].append(
    #         road)
    
    # css['road']['laneSection']['ID'] = " "
    # css['road']['laneSection']['width'] = " "
    # css['road']['laneSection']['curvature'] = " "
    # css['road']['Lanes'] = tmk.lanes
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
    
    if SOTIF == 1:                    
        xodr_dir=r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Augmented\Carmaker Project\Data\Road"    
        simulation_datas = ["roundabout_1",                     # 0
                            "roundabout_2",                     # 1
                            "Straight_curved_3_3",              # 2
                            ]

    elif preCrash == 1:                    
        xodr_dir=r"\\192.168.75.251\Shares\Precrash Scenario Data\Scenario Catalog for Car to Car\Carmaker Project\Data\Road"    
        simulation_datas = ["Curved_3_3",                       # 0
                            "Intersection_2_2",                 # 1
                            "Straight_1_1",                     # 2
                            "Straight_2_2",                     # 3
                            "Straight_3_3",                     # 4
                            "Straight_Merged_2_2",              # 5
                            "Straight_shoulder",                # 6
                            ]
    
    elif AES_TAAS_PCM == 1:
        xodr_dir=r"\\192.168.75.251\Shares\AES Scenario Data\Simulation\TAAS-PCM\TAAS-PCM(0721)\Data\Road"    
        simulation_datas = ["TAAS_Ansan_3549",                  # 0
                            "TAAS_Ansan_11108",                 # 1
                            "TAAS_Changwon_190",                # 2
                            "TAAS_Gunpo_8368",                  # 3
                            "TAAS_Gwangmyung_7965",             # 4
                            "TAAS_Pyeontak_1902",               # 5
                            "TAAS_Sungnam_4145",                # 6
                            "TAAS_Suwon_28",                    # 7
                            "TAAS_Suwon_219",                   # 8
                            "TAAS_Suwon_829",                   # 9
                            "TAAS_Suwon_912",                   # 10
                            "TAAS_Suwon_1188",                  # 11
                            "TAAS_Suwon_2968",                  # 12
                            "TAAS_Suwon_8022",                  # 13
                            "TAAS_Suwon_10201",                 # 14
                            "TAAS_Suwon_10532",                 # 15
                            "TAAS_Suwon_12072",                 # 16
                            "TAAS_Suwon_12134",                 # 17
                            "TAAS_Suwon_12502",                 # 18
                            "TAAS_Suwon_12517",                 # 19
                            "TAAS_Suwon_13138",                 # 20
                            "TAAS_Suwon_13325",                 # 21
                            "TAAS_Suwon_13343",                 # 22
                            "TAAS_Suwon_13488",                 # 23
                            "TAAS_Suwon_13802",                 # 24
                            "TAAS_Suwon_14309",                 # 25
                            "TAAS_Suwon_14448",                 # 26
                            "TAAS_Yongin_1723",                 # 27
                            "TAAS_Suwon_8215",              # 28
                            ]
    
    # 하나의 시뮬레이션 데이터에 대해 확인할 때 사용
    if single_toggle == 1:
        print(simulation_datas[i] + '.json 생성중...')
        make_CSS(xodr_dir, simulation_datas[i], registration_dir, save_dir)
        # make_CSS(xodr_dir, simulation_datas[i], save_dir)
        print(simulation_datas[i] + '.json 완성!!!')
        print('-'*30)
    
    # 여러개의 시뮬레이션 데이터에 대해 확인할 때 사용
    elif multiple_toggle == 1:   
        for simulation_data in simulation_datas:
            print(simulation_data + '.json 생성중...')
            make_CSS(xodr_dir,simulation_data, registration_dir, save_dir)
            # make_CSS(xodr_dir,simulation_data, save_dir)
            print(simulation_data + '.json 완성!!!')
            print('-'*30)




    