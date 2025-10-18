import json
import os
import scipy
import h5py
import numpy as np
import pandas as pd
from colorama import Fore
from tqdm import tqdm
import glob
from datetime import datetime
import xml.etree.ElementTree as ET
import copy
import math
import re

def read_json(path):
    
    with open(path, 'r') as file:
        data = json.load(file)  
    return data

class Makejson():
 
    # def __init__(self,_xosc_dir, simulation_name): 
    def __init__(self,_xodr_dir, registration_dir, simulation_name): 
        self.xodr_file_path, self.xodr_file = self.get_xodr_file(_xodr_dir, simulation_name)
        self.config = self.parse_config(self.xodr_file)
        # self.config = {}
        ### 여기서부터는 수정 필요
        # self.date = self.get_date(self.xodr_file)
        self.dataType = 'rd5'
        self.schemaVersion = "1.1"
        self.laneSection = self.get_road(self.config, simulation_name)
        self.lanes = []
        self.coordinate = self.get_coordinate(registration_dir, simulation_name)
        # self.expertKnowledge = self.get_expertKnowledge(registration_dir, simulation_name)
        # self.scenario = self.get_scenario(simulation_name)
        # self.accidentData = self.get_accidentData(_xodr_dir, registration_dir, simulation_name)
        # self.entities = self.get_entities(self.xodr_file_root)
        # self.privates = self.get_privates(self.xodr_file_root)
        # self.maneuver_groups = self.get_maneuver_groups(self.xodr_file_root)
        # self.parameters = self.get_paramter(self.xodr_file_root)
        # parse_config = self.parse_config(self.xodr_file)
        print()
    # 파싱 함수
    def parse_config(self, data):
        config = {}
        lines = data.strip().split('\n')  # 줄 단위로 나누기
        for line in lines:
            line = line.strip()  # 앞뒤 공백 제거
            if not line or line.startswith('#'):  # 빈 줄이나 주석 무시
                continue
            
            # '='를 기준으로 키와 값 분리
            if '=' in line:
                key, value = line.split('=', 1)  # 첫 번째 '=' 기준으로 분리
                config[key.strip()] = value.strip()  # 딕셔너리에 추가
            else:
                # '='가 없는 경우는 그냥 키로 사용
                config[line.strip()] = None

        self.config = config
        return config



    # def get_xodr_file(self, _xodr_dir, simulation_name):
    #     xodr_file_name = [
    #         file for file in os.listdir(_xodr_dir)
    #         if (file == simulation_name or file.split('.')[0] == simulation_name)
    #     ]

    #     if not xodr_file_name:
    #         raise FileNotFoundError(f"No matching file found for simulation '{simulation_name}' in directory '{_xodr_dir}'.")

    #     xodr_file_name = xodr_file_name[0]
    #     xodr_file_path = os.path.join(_xodr_dir, xodr_file_name)
    #     with open(xodr_file_path, 'r', encoding='utf-8') as file:
    #         xodr_file = json.load(file)

    #     return xodr_file_path, xodr_file
    
    # .xodr 파일의 path와 root를 얻음
    def get_xodr_file(self, _xodr_dir, simulation_name):
        xodr_file_name = [file for file in os.listdir(_xodr_dir) if (file == simulation_name or file.split('.')[0] == simulation_name)][0]

        # xodr_file_path = _xodr_dir + '/' + xodr_file_name
        xodr_file_path = os.path.join(_xodr_dir, xodr_file_name)
        with open(xodr_file_path, 'r', encoding='utf-8') as file:
            # xodr_file = file.read()
            xodr_file = file.read().strip()

        return xodr_file_path, xodr_file
    
    
# 도로 정보 추출 (도로의 width, curvature, 차선 ID)
    def get_road(self, config, simulation_name):
                
        lane_id = None
        width = None
        curvature = None
        lanes = None
        
        laneSection = []
        tmp_laneSection = []
        Link_data = []
        Link_array = {
            "Link": " ",
            "Lanes": " "
        }
        Link_array_data = {}
        Lanes_data = {}       

        for key, value in config.items(): 
                ## Link array
                if ("Link" in key and "ID" in key and "LaneSection" not in key and "Seg" not in key and "RL" not in key and "Profile" not in key) or ("MaxUsedObjId" in key):
                        if Link_array_data: # Link_data가 비어있지 않으면
                            only_dicts = [item for item in Link_data if isinstance(item, dict)]
                            if "TAAS" in simulation_name:                                
                                laneSection.append(Link_array)
                                Link_array_data = {}
                                Link_array = {
                                    "Link": " ",
                                    "Lanes": " "
                                    }
                                Link_data = []
                                Lanes_data = {} 
                            else:
                                lanes = int((len(only_dicts) / 2) - 2)
                                Link_array['Lanes'] = lanes
                                laneSection.append(Link_array)
                                
                                Link_array_data = {}
                                Link_array = {
                                    "Link": " ",
                                    "Lanes": " "
                                    }
                                Link_data = []
                                Lanes_data = {}                              
                        
                elif "Link" in key and "LaneSection" in key and ("LaneL" in key or "LaneR" in key) and "ID" in key:
                        try:
                            lane_id = int(value)
                        except (TypeError, ValueError):
                            print(f"Key: {key}, Value is not an integer-compatible type: {value}")
                    
                elif "Link" in key and "LaneSection" in key and ("LaneL" in key or "LaneR" in key) and "ARP" not in key and "Width" not in key:
                        try: # cal width
                            value_split = value.split()
                            start_width = float(value_split[1])
                            end_width = float(value_split[2])
                            lane_width = (start_width + end_width) / 2
                            width = float(lane_width)
                        except (TypeError, ValueError):
                            print(f"Key: {key}, Value is not an integer-compatible type: {value}")
 
                elif "Link" in key and "Seg" in key and "Param" in key:
                        try: # cal curvature
                            value_split = value.split()
                            arc_length = float(value_split[0])
                            angle_degrees = float(value_split[1])
                            angle_radians = math.radians(angle_degrees)
                            curvature = float(angle_radians / arc_length)
                        except (TypeError, ValueError):
                            print(f"Key: {key}, Value is not an integer-compatible type: {value}")
                
                ## Link array 
                elif re.search(r"LaneSection\.(?!0)\d+", key):
                    if ("Link" in key and "ID" in key and "Seg" not in key and "RL" not in key and "Profile" not in key):
                        if Link_array_data and "Link" in key and "ID" in key and "Start" not in key and "LaneL" not in key and "LaneR" not in key: # Link_data가 비어있지 않으면
                            only_dicts = [item for item in Link_data if isinstance(item, dict)]
                            
                            if "TAAS" in simulation_name:
                                
                                laneSection.append(Link_array)
                                Link_array_data = {}
                                Link_array = {
                                    "Link": " ",
                                    "Lanes": " "
                                    }
                                Link_data = []
                                Lanes_data = {} 
                            else:
                                lanes = int((len(only_dicts) / 2) - 2)
                                Link_array['Lanes'] = lanes
                                laneSection.append(Link_array)
                                
                                Link_array_data = {}
                                Link_array = {
                                    "Link": " ",
                                    "Lanes": " "
                                    }
                                Link_data = []
                                Lanes_data = {} 
                
                    
                if lane_id is not None or width is not None or curvature is not None:
                        Link_array_data = {
                                "ID": lane_id,
                                "width": width,
                                "curvature": curvature
                        }
                                                
                        # ID, width, curvature 값이 모두 None이 아닌 경우에만 저장
                        if all(Link_array_data.get(key) is not None for key in ["ID", "width", "curvature"]):
                            Link_data.append(Link_array_data)
                            Link_array['Link'] = Link_data
                            
                        
                        if all(v is not None for v in Link_array_data.values()):
                            lane_id, width = None, None
                         
                
                        # if tmp_laneSection:
                        #     laneSection.append(tmp_laneSection)
                        #     tmp_laneSection = []
        return laneSection
                
                
                
    def get_coordinate(self, registration_dir, simulation_name):
        if registration_dir =="":
            coordinate = []
        else:
            coordinate = []
            
            coordinate_format = {
                    "type": " ",
                    "coordinate" : " "
                }
            
            variation_num = int(re.sub(r'\D', '', simulation_name))
            tmp_coordinate = copy.deepcopy(coordinate_format)        
            registration_file_name = [file for file in os.listdir(registration_dir) if 'TAAS' in file][0]
            registration_file_path = os.path.join(registration_dir, registration_file_name)
            coordinate_file = pd.read_csv(registration_file_path, encoding='utf-8') 
            latitude_longitude = coordinate_file[['위도', '경도']]
            
            # 특정 행 값 추출 (예: 0번째 행)
            trans_coordinate = latitude_longitude.iloc[variation_num]
            tmp_coordinate = trans_coordinate.tolist()
            coordinate.append(tmp_coordinate)
            
            return coordinate 
            
     
     
     
    # def get_date(self, root):
    #     date = root.find('.//FileHeader').get('date')
    #     return date
    
    # def get_expertKnowledge(self, registration_dir, simulation_name):
    #     expertKnowledge = []
        
    #     expertKnowledge_format = {
    #             "reference": " ",
    #             "scenario" : " "
    #         }
        
            tmp_expertKnowledge = copy.deepcopy(expertKnowledge_format)        
            registration_file_name = [file for file in os.listdir(registration_dir) if simulation_name in file][0]
            registration_file_path = os.path.join(registration_dir, registration_file_name)
            expertKnowledge_file = pd.read_excel(registration_file_path, sheet_name='expertKnowledge')
            reference = expertKnowledge_file.iloc[0,1]
            tmp_expertKnowledge['reference'] = reference

            expertKnowledge.append(tmp_expertKnowledge)
            
            return expertKnowledge
    
    # def get_scenario(self, simulation_name):
    #     scenario = simulation_name
        
    #     return scenario
    
    ############# CSS v1.0에 존재하는 COLLTYPE을 계산하는 함수#############
    # def get_collType(self, root):
    #     npc = 0
    #     pedestrian = 0
    #     collType = " "
    #     scenario_objects = root.findall('.//ScenarioObject')
        
    #     for scenario_object in scenario_objects:
    #         name = scenario_object.get('name')[:3]
    #         if name == "NPC":
    #             npc += 1
    #         elif name == "Ped":
    #             pedestrian += 1
        
    #     if npc == 0 and pedestrian == 0:
    #         collType == 'error - not defined'
    #     elif npc == 0 and pedestrian == 1:
    #         collType = '차대사람'
    #     elif npc == 1 and pedestrian == 0:
    #         collType = '차대차'
    #     else:
    #         collType = '차대다중'
    
    #     return collType
    ####################################################################
    # def get_accidentData(self, _xodr_dir, registration_dir, simulation_name) :
    #     accidentData = []
        
    #     accidentData_format = {
    #             "name" : " ",
    #             "year" : [],
    #             "COLLTYPE_MAIN" : [],
    #             "ACCTYPEA" : [],
    #             "ACCTYPEB" : [],
    #             "ACCTYPE_unknown" : [],
    #             "occurrence" : {
    #                 "rank" : " "
    #             }
    #         }
        
            tmp_accidentData = copy.deepcopy(accidentData_format)
            accidentData.append(tmp_accidentData)

            registration_file_name = [file for file in os.listdir(registration_dir) if simulation_name in file][0]
            registration_file_path = os.path.join(registration_dir, registration_file_name)
            xl = pd.ExcelFile(registration_file_path)
            sheet_names = xl.sheet_names
            if 'IGLAD' in sheet_names:
                IGLAD_sheet = pd.read_excel(registration_file_path, sheet_name='IGLAD')
                TAAS_sheet = pd.read_excel(registration_file_path, sheet_name='TAAS')

                # ACCTYPE
                ACCTYPE = str(IGLAD_sheet.iloc[0, 1])

                # ACCTYPEA
                ACCTYPEA_array = np.array([])
                for ACCTYPEA_idx in range(TAAS_sheet.iloc[1,:].size):
                    if ACCTYPEA_idx == 0:
                        continue
                    else:
                        ACCTYPEA_array = np.append(ACCTYPEA_array, TAAS_sheet.iloc[1, ACCTYPEA_idx])
                
                # ACCTYPEB
                ACCTYPEB_array = np.array([])
                for ACCTYPEB_idx in range(TAAS_sheet.iloc[2,:].size):
                    if ACCTYPEB_idx == 0:
                        continue
                    else:
                        ACCTYPEB_array = np.append(ACCTYPEB_array, TAAS_sheet.iloc[1, ACCTYPEB_idx])
                
                # ACCTYPE_unknown
                ACCTYPE_unknown_array = np.array(['99999', '799', '999', '679', '229',
                                                '249', '676', '226', '495', '246',
                                                '713', '456', '494', '499', '583',
                                                '282', '492', '539', '279', '491',
                                                '493', '431', '451'])
                
                # TAAS rank
                if np.array([TAAS_sheet.iloc[0, 1]]).tolist() == ['차대차']:
                    TAAS_rank_df = pd.DataFrame({'601':[1], '601-a':[1], '601-b':[1], '601-c':[1], '601-f':[1], '601-g':[1], '681':[2], '621':[3], 
                                                '682':[4], '501':[5], '321':[6], '211':[7], '741':[8], '301':[9], '635':[10],'302':[11], '351':[12],
                                                '646':[13], '543':[14], '502':[15], '722':[16], '352':[17], '721':[18], '303':[19]})
                elif np.array([TAAS_sheet.iloc[0, 1]]).tolist() == ['차대사람']:
                    TAAS_rank_df = pd.DataFrame({'401':[1], '421':[2], '451':[3], '471':[4], '671':[5], '423':[6], '461':[7], '422':[8], '431':[9],
                                                '411':[10],'713':[11], '675':[12], '241':[13], '242':[13], '424':[14], '222':[15], '405':[16], '221':[17], 
                                                '672':[18], '481':[19], '414':[20], '673':[21], '674':[22]})
                rank = ''
                for rank_idx in range(TAAS_rank_df.columns.size):
                    if TAAS_rank_df.columns[rank_idx] == ACCTYPE:
                        rank = TAAS_rank_df.iloc[0, rank_idx]
                    else:
                        continue

                accidentData[0]['name'] = 'TAAS'
                accidentData[0]['year'] = np.array([2012, 2014]).tolist()
                accidentData[0]['COLLTYPE_MAIN'] = np.array([TAAS_sheet.iloc[0, 1]]).tolist()
                accidentData[0]['ACCTYPEA'] = ACCTYPEA_array.tolist()
                accidentData[0]['ACCTYPEB'] = ACCTYPEB_array.tolist()
                accidentData[0]['ACCTYPE_unknown'] = ACCTYPE_unknown_array.tolist()
                accidentData[0]['occurrence']['rank'] = int(rank)

            return accidentData


    # def get_entities(self, root):
    #     entities = []
        
    #     entites_format = {
    #         "name" : " ",
    #         "category" : " ",
    #         "target"  : " ",
    #         "boundingBox" : {
    #             "dimensions" : {
    #                 "height" : " ",
    #                 "length" : " ",
    #                 "width" : " "
    #             }
    #         },
    #         "files" : {
    #             "filepath" : " "
    #         }
    #     }
        
    #     object_category = {
    #         'pedestrian' : '1',
    #         'car' : '2',
    #         'truck' : '3',
    #         'bus' : '4',
    #         'van' : '5',
    #         'motorcycle' : '6',
    #         'cyclist' : '7',
    #         'bicycle' : '8',
    #         'motorcycle_only' : '9',
    #         'bicycle_only' : '10',
    #         'traffic_light' : '11',
    #         'traffic_sign' : '12',
    #         'person_sitting' : '13',
    #         'train' : '14',
    #         'E-scooter' : '15',
    #         'Misc' :' 16',
    #         'DontCare' : '16'
    #     }
        
    #     testrun_entities = root.findall('.//ScenarioObject')
        
    #     for testrun_entity in testrun_entities:
    #         tmp_entity = copy.deepcopy(entites_format)
    #         tmp_entity['name'] = testrun_entity.get('name')
            
    #         # object가 vehicle인 경우
    #         if testrun_entity.find('./Vehicle') is not None:
    #             tmp_entity['category'] = \
    #                 object_category[testrun_entity.find('./Vehicle').get('vehicleCategory')]            
    #             tmp_entity['boundingBox']['dimensions']['height'] = 1.28
    #             tmp_entity['boundingBox']['dimensions']['length'] = 4.28
    #             tmp_entity['boundingBox']['dimensions']['width'] = 1.82

    #         # object가 pedestrian인 경우
    #         elif testrun_entity.find('./Pedestrian') is not None:
    #             tmp_entity['category'] =\
    #                 object_category[testrun_entity.find('./Pedestrian').get('pedestrianCategory')]
    #             tmp_entity['boundingBox']['dimensions']['height'] = " "
    #             tmp_entity['boundingBox']['dimensions']['length'] = " "
    #             tmp_entity['boundingBox']['dimensions']['width'] = " "
                
    #         if testrun_entity.get('name') != 'Stop_Point':
    #             entities.append(tmp_entity)

    #     return entities
    
    # def get_privates(self, root):
    #     privates = []

    #     private_format ={
    #         "entityRef" : " ",
    #         "maneuver" : " "
    #     }
        
    #     testrun_privates = root.findall('.//Private')
    #     testrun_story = root.findall('.//Story')
    #     for testrun_private in testrun_privates:
    #         if testrun_private.get('entityRef') != 'Stop_Point':
    #             tmp_private = copy.deepcopy(private_format)
    #             tmp_private['entityRef'] = testrun_private.get('entityRef')
    #             tmp_private['maneuver'] = " "
                
    #             # # 시나리오 시작 시 차량의 속도가 0이면 STP. 아니면 LK
    #             # if testrun_privates.find('./AbsoluteTargetSpeed').get('value') == '0':
    #             #     privates['name']['maneuver'] = 'STP'
    #             # else:
    #             #     privates['name']['maneuver'] = 'LK'
                
    #             ######################### entity의 position에 관한 것 ##################################
    #             # # worldPosition일 때
    #             # if testrun_private.find('.//WorldPosition') is not None:
    #             #     # worldPosition
    #             #     for key in tmp_private['privateActions']['teleportAction']['position']['worldPosition'].keys():
    #             #         tmp_private['privateActions']['teleportAction']['position']['worldPosition'][key] =\
    #             #             testrun_private.find('.//WorldPosition').get(key)                
                        
    #             # # relativeObjectPosition일 때
    #             # elif testrun_private.find('.//RelativeObjectPosition') is not None:
    #             #     # relativeObjectPosition
    #             #     for key in tmp_private['privateActions']['teleportAction']['position']['relativeObjectPosition'].keys():
    #             #         if key != 'orientation':
    #             #             attribute = testrun_private.find('.//RelativeObjectPosition').get(key)
    #             #             if  attribute is not None:
    #             #                 tmp_private['privateActions']['teleportAction']['position']['relativeObjectPosition'][key] =\
    #             #                     attribute
    #             #         else:
    #             #             for orientation_key in tmp_private['privateActions']['teleportAction']['position']['relativeObjectPosition'][key].keys():
    #             #                 attribute = testrun_private.find('.//RelativeObjectPosition').get(orientation_key)
    #             #                 if attribute is not None:
    #             #                     tmp_private['privateActions']['teleportAction']['position']['relativeObjectPosition'][key][orientation_key] =\
    #             #                         attribute
    
    #             # # roadPosition일 때
    #             # elif testrun_private.find('.//RoadPosition') is not None:
    #             #     # roadPosition
    #             #     for key in tmp_private['privateActions']['teleportAction']['position']['roadPosition'].keys():
    #             #         tmp_private['privateActions']['teleportAction']['position']['roadPosition'][key] =\
    #             #             testrun_private.find('.//RoadPosition').get(key)
                
    #             # # linkPosition일 때
    #             # elif testrun_private.find('.//LinkPosition') is not None:                          
    #             #     # linkPosition
    #             #     for key in tmp_private['privateActions']['teleportAction']['position']['linkPosition'].keys():
    #             #         tmp_private['privateActions']['teleportAction']['position']['linkPosition'][key] =\
    #             #             testrun_private.find('.//LinkPosition').get(key)

    #             # tmp_private['longitudinalAction']['speedAction']['speedActionTarget']['absoluteTargetSpeed']['value'] = \
    #             #     testrun_private.find('.//AbsoluteTargetSpeed').get('value')
    #             ######################################################################################################
                
    #             privates.append(tmp_private)

    #     return privates
    
    # def get_events(self, maneuver):
    #     events = []

    #     event_format = {
    #         "maneuver" : " "
    #     }

    #     testrun_events = maneuver.findall('.//Event')
        
    #     for testrun_event in testrun_events:
    #         tmp_event = copy.deepcopy(event_format)
            
    #         tmp_event['maneuver'] = " "
            
    #         events.append(tmp_event)
            
    #     return events

    # def get_maneuver_groups(self, root):
    #     maneuver_groups = []

    #     maneuver_group_format = { 
    #         "actors" : {
    #             "entityRefs" : " "
    #         },
    #         "maneuvers" : {
    #             "events" : []
    #         }
    #     }

    #     testrun_maneuver_groups = root.findall('.//ManeuverGroup')

    #     for testrun_maneuver_group in testrun_maneuver_groups:
    #         tmp_maneuver_group = copy.deepcopy(maneuver_group_format)

    #         if testrun_maneuver_group.find('./Actors').find('./EntityRef') is not None:
    #             tmp_maneuver_group['actors']['entityRefs'] =\
    #                 testrun_maneuver_group.find('./Actors').find('./EntityRef').get('entityRef')
    #         else:
    #             continue
                            
    #         testrun_maneuver = testrun_maneuver_group.find('./Maneuver')
    #         events = self.get_events(testrun_maneuver)

    #         tmp_maneuver_group['maneuvers']['events'] = events

    #         maneuver_groups.append(tmp_maneuver_group)

    #     return maneuver_groups

    # def get_paramter(self, root):
    #     parameters = []
        
    #     testrun_parameter_declarations = root.find('.//ParameterDeclarations')
    #     parameter_format = {
    #         "name" : " ",
    #         "genParam" : {
    #             "range" : {
    #                 "max" : " ",
    #                 "min" : " "
    #             },
    #             "samplePoint" : " ",
    #             "value" : " "
    #         }
    #     }
        
    #     if testrun_parameter_declarations is not None:
    #         for testrun_parameter_declaration in testrun_parameter_declarations.findall('.//ParameterDeclaration'):
    #             tmp_parameter = copy.deepcopy(parameter_format)
                
    #             tmp_parameter['name'] = testrun_parameter_declaration.get('name')
                
    #             parameters.append(tmp_parameter)
    #     else:
    #         print('There is no "ParameterDeclarations"')

    #     return parameters
            
            
        
    
