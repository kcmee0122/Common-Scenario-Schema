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


def read_json(path):
    
    with open(path, 'r') as file:
        data = json.load(file)  
    return data

class Makejson():
 
    def __init__(self,_xosc_dir): 
        self.xosc_file_path, self.xosc_file_root = self.get_xosc_file(_xosc_dir)
        self.date = self.get_date(self.xosc_file_root)
        self.dataType = 'xosc'
        self.schemaVersion = "1.1"
        self.expertKnowledge = self.get_expertKnowledge(_xosc_dir)
        self.scenario = self.get_scenario(_xosc_dir)
        # self.COLLTYPE_MAIN = self.get_collType(self.xosc_file_root)
        self.entities = self.get_entities(self.xosc_file_root)
        self.privates = self.get_privates(self.xosc_file_root)
        self.maneuver_groups = self.get_maneuver_groups(self.xosc_file_root)
        self.parameters = self.get_paramter(self.xosc_file_root)

    # .xosc 파일의 path와 root를 얻음
    def get_xosc_file(self, _xosc_dir):
        xosc_file_name = [file for file in os.listdir(_xosc_dir) if file.split('.')[-1] == "xosc"][0]
        xosc_file_path = _xosc_dir + '/' + xosc_file_name
        xosc_file = ET.parse(xosc_file_path) 
        xosc_file_root = xosc_file.getroot()

        return xosc_file_path, xosc_file_root
        
    def get_date(self, root):
        date = root.find('.//FileHeader').get('date')
        return date
    
    def get_expertKnowledge(self, _xosc_dir):
        expertKnowledge = []
        
        expertKnowledge_format = {
                "reference": " ",
                "scenario" : " "
            }
        
        tmp_expertKnowledge = copy.deepcopy(expertKnowledge_format)
        registration_file_name = [file for file in os.listdir(_xosc_dir) if file.split('.')[-1] == 'xlsx'][0]
        registration_file_path = os.path.join(_xosc_dir, registration_file_name)
        registration_file = pd.read_excel(registration_file_path, sheet_name='expertKnowledge')
        reference = registration_file.iloc[0,1]

        tmp_expertKnowledge['reference'] = reference
        expertKnowledge.append(tmp_expertKnowledge)
        
        return expertKnowledge
    
    def get_scenario(self, _xosc_dir):
        scenario = _xosc_dir.split('/')[-1]
        
        return scenario
    
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
    
    def get_entities(self, root):
        entities = []
        
        entites_format = {
            "name" : " ",
            "category" : " ",
            "target"  : " ",
            "boundingBox" : {
                "dimensions" : {
                    "height" : " ",
                    "length" : " ",
                    "width" : " "
                }
            },
            "files" : {
                "filepath" : " "
            }
        }
        
        object_category = {
            'pedestrian' : '1',
            'car' : '2',
            'truck' : '3',
            'bus' : '4',
            'van' : '5',
            'motorcycle' : '6',
            'cyclist' : '7',
            'bicycle' : '8',
            'motorcycle_only' : '9',
            'bicycle_only' : '10',
            'traffic_light' : '11',
            'traffic_sign' : '12',
            'person_sitting' : '13',
            'train' : '14',
            'E-scooter' : '15',
            'Misc' :' 16',
            'DontCare' : '16'
        }
        
        xosc_entities = root.findall('.//ScenarioObject')
        
        for xosc_entity in xosc_entities:
            tmp_entity = copy.deepcopy(entites_format)
            tmp_entity['name'] = xosc_entity.get('name')
            
            # object가 vehicle인 경우
            if xosc_entity.find('./Vehicle') is not None:
                tmp_entity['category'] = \
                    object_category[xosc_entity.find('./Vehicle').get('vehicleCategory')]            
                tmp_entity['boundingBox']['dimensions']['height'] = 1.45
                tmp_entity['boundingBox']['dimensions']['length'] = 4.47
                tmp_entity['boundingBox']['dimensions']['width'] = 1.82

            # object가 pedestrian인 경우
            elif xosc_entity.find('./Pedestrian') is not None:
                tmp_entity['category'] =\
                    object_category[xosc_entity.find('./Pedestrian').get('pedestrianCategory')]
                tmp_entity['boundingBox']['dimensions']['height'] = " "
                tmp_entity['boundingBox']['dimensions']['length'] = " "
                tmp_entity['boundingBox']['dimensions']['width'] = " "
                
            if xosc_entity.get('name') != 'Stop_Point':
                entities.append(tmp_entity)

        return entities
    
    def get_privates(self, root):
        privates = []

        private_format ={
            "entityRef" : " ",
            "maneuver" : " "
        }
        
        xosc_privates = root.findall('.//Private')
        
        for xosc_private in xosc_privates:
            if xosc_private.get('entityRef') != 'Stop_Point':
                tmp_private = copy.deepcopy(private_format)
                tmp_private['entityRef'] = xosc_private.get('entityRef')
                tmp_private['maneuver'] = " "
                
                # 시나리오 시작 시 차량의 속도가 0이면 STP. 아니면 LK
                # if private.find('./AbsoluteTargetSpeed').get('value') == '0':
                #     privates['name']['maneuver'] = 'STP'
                # else:
                #     privates['name']['maneuver'] = 'LK'
                
                ######################### entity의 position에 관한 것 ##################################
                # # worldPosition일 때
                # if xosc_private.find('.//WorldPosition') is not None:
                #     # worldPosition
                #     for key in tmp_private['privateActions']['teleportAction']['position']['worldPosition'].keys():
                #         tmp_private['privateActions']['teleportAction']['position']['worldPosition'][key] =\
                #             xosc_private.find('.//WorldPosition').get(key)                
                        
                # # relativeObjectPosition일 때
                # elif xosc_private.find('.//RelativeObjectPosition') is not None:
                #     # relativeObjectPosition
                #     for key in tmp_private['privateActions']['teleportAction']['position']['relativeObjectPosition'].keys():
                #         if key != 'orientation':
                #             attribute = xosc_private.find('.//RelativeObjectPosition').get(key)
                #             if  attribute is not None:
                #                 tmp_private['privateActions']['teleportAction']['position']['relativeObjectPosition'][key] =\
                #                     attribute
                #         else:
                #             for orientation_key in tmp_private['privateActions']['teleportAction']['position']['relativeObjectPosition'][key].keys():
                #                 attribute = xosc_private.find('.//RelativeObjectPosition').get(orientation_key)
                #                 if attribute is not None:
                #                     tmp_private['privateActions']['teleportAction']['position']['relativeObjectPosition'][key][orientation_key] =\
                #                         attribute
    
                # # roadPosition일 때
                # elif xosc_private.find('.//RoadPosition') is not None:
                #     # roadPosition
                #     for key in tmp_private['privateActions']['teleportAction']['position']['roadPosition'].keys():
                #         tmp_private['privateActions']['teleportAction']['position']['roadPosition'][key] =\
                #             xosc_private.find('.//RoadPosition').get(key)
                
                # # linkPosition일 때
                # elif xosc_private.find('.//LinkPosition') is not None:                          
                #     # linkPosition
                #     for key in tmp_private['privateActions']['teleportAction']['position']['linkPosition'].keys():
                #         tmp_private['privateActions']['teleportAction']['position']['linkPosition'][key] =\
                #             xosc_private.find('.//LinkPosition').get(key)

                # tmp_private['longitudinalAction']['speedAction']['speedActionTarget']['absoluteTargetSpeed']['value'] = \
                #     xosc_private.find('.//AbsoluteTargetSpeed').get('value')
                ######################################################################################################
                
                privates.append(tmp_private)

        return privates
    
    def get_events(self, maneuver):
        events = []

        event_format = {
            "maneuver" : " "
        }

        xosc_events = maneuver.findall('.//Event')
        
        for xosc_event in xosc_events:
            tmp_event = copy.deepcopy(event_format)
            
            tmp_event['maneuver'] = " "
            
            events.append(tmp_event)
            
        return events

    def get_maneuver_groups(self, root):
        maneuver_groups = []

        maneuver_group_format = { 
            "actors" : {
                "entityRefs" : " "
            },
            "maneuvers" : {
                "events" : []
            }
        }

        xosc_maneuver_groups = root.findall('.//ManeuverGroup')

        for xosc_maneuver_group in xosc_maneuver_groups:
            tmp_maneuver_group = copy.deepcopy(maneuver_group_format)

            if xosc_maneuver_group.find('./Actors').find('./EntityRef') is not None:
                tmp_maneuver_group['actors']['entityRefs'] =\
                    xosc_maneuver_group.find('./Actors').find('./EntityRef').get('entityRef')
            else:
                continue
                            
            xosc_maneuver = xosc_maneuver_group.find('./Maneuver')
            events = self.get_events(xosc_maneuver)

            tmp_maneuver_group['maneuvers']['events'] = events

            maneuver_groups.append(tmp_maneuver_group)

        return maneuver_groups

    def get_paramter(self, root):
        parameters = []
        
        xosc_parameter_declarations = root.find('.//ParameterDeclarations')
        parameter_format = {
            "name" : " ",
            "genParam" : {
                "range" : {
                    "max" : " ",
                    "min" : " "
                },
                "samplePoint" : " ",
                "value" : " "
            }
        }
        
        if xosc_parameter_declarations is not None:
            for xosc_parameter_declaration in xosc_parameter_declarations.findall('.//ParameterDeclaration'):
                tmp_parameter = copy.deepcopy(parameter_format)
                
                tmp_parameter['name'] = xosc_parameter_declaration.get('name')
                
                parameters.append(tmp_parameter)
        else:
            print('There is no "ParameterDeclarations"')

        return parameters
            
            
        
    
