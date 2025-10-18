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
 
    def __init__(self, PS_dir, PS_CSV_File_name, registration_dir, folder_date): 
        self.PS_file_path, self.PS_file, self.raw_dataType  = self.get_PS_file(PS_dir, PS_CSV_File_name, folder_date)
        self.date = self.get_date(self.PS_file_path)
        if 'Dim' in PS_CSV_File_name:
            self.dataType = 'parameterSpace-Dim'
        elif 'Extend' in PS_CSV_File_name:
            self.dataType = 'parameterSpace-Extend'
        elif 'Geometry' in PS_CSV_File_name:
            self.dataType = 'parameterSpace-Geometry'
        elif 'New' in PS_CSV_File_name:
            self.dataType = 'parameterSpace-New'
        else:
            self.dataType = 'parameterSpace'
        self.schemaVersion = "1.1"
        self.parameters = self.get_paramter(self.PS_file)
        self.accidentData = self.get_accidentData(PS_dir, registration_dir, PS_CSV_File_name)
        self.expertKnowledge = self.get_expertKnowledge(registration_dir, PS_CSV_File_name)

    # Parameter space 파일의 path와 root를 얻음
    def get_PS_file(self, PS_dir, PS_CSV_File_name, folder_date):
        scenario_name = PS_CSV_File_name.split('_rawPS')[0]
        if len(PS_CSV_File_name.split('_rawPS')) > 1:
            raw_dataType = PS_CSV_File_name.split('_rawPS')[1]
        else:
            raw_dataType = 'Standard'
        PS_file_name = [file for file in os.listdir(PS_dir) if file.split('.')[0] == scenario_name][0]
        PS_file_path = os.path.join(PS_dir, PS_file_name, folder_date, PS_CSV_File_name+'.csv')
        PS_file = pd.read_csv(PS_file_path)

        return PS_file_path, PS_file, raw_dataType
########################################################

    def get_date(self, PS_file_path):
        # 파일이 존재하는지 확인
        if os.path.isfile(PS_file_path):
            # 파일의 수정 일자를 가져옴
            date = os.path.getmtime(PS_file_path)
            modified_date = datetime.fromtimestamp(date)
            formatted_date = modified_date.strftime("%Y-%m-%dT%H:%M:%S")


            return formatted_date
        else:
            return None  # 파일이 존재하지 않는 경우 None을 반환
    
    ##########################################################



    def get_paramter(self, PS_file):

        parameters = []

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
            
        len_PS = PS_file.shape[1]
        
        for idx in range(len_PS) :
            tmp_parameter = copy.deepcopy(parameter_format)
            tmp_parameter['name'] = PS_file.iloc[:, idx].name
            tmp_parameter['genParam']['range']['min'] = float(PS_file.iloc[0,idx])
            tmp_parameter['genParam']['range']['max'] = float(PS_file.iloc[1,idx])
            
            parameters.append(tmp_parameter)

        return parameters
            
            
        ##########################################################

    def get_expertKnowledge(self, registration_dir, PS_CSV_File_name):

        scenario_name = PS_CSV_File_name.split('_rawPS')[0]

        expertKnowledge = []
        
        expertKnowledge_format = {
                "reference": " ",
                "scenario" : " "
            }
        
        filtered_files = [file for file in os.listdir(registration_dir) if scenario_name in file]
    
        if not filtered_files:
            print(f"[경고] '{scenario_name}'와 일치하는 파일이 {registration_dir}에 없습니다.")
            return expertKnowledge  # 빈 리스트 반환

        try:                    
            registration_file_name = [file for file in os.listdir(registration_dir) if scenario_name in file][0]
            registration_file_path = os.path.join(registration_dir, registration_file_name)
            expertKnowledge_file = pd.read_excel(registration_file_path, sheet_name='expertKnowledge')
            
            reference = expertKnowledge_file.iloc[0,1]
            tmp_expertKnowledge = copy.deepcopy(expertKnowledge_format)
            tmp_expertKnowledge['reference'] = reference

            expertKnowledge.append(tmp_expertKnowledge)
        
        except Exception as e:
            return expertKnowledge
    
        return expertKnowledge

        ##########################################################

    def get_accidentData(self, _xosc_dir, registration_dir, PS_CSV_File_name) :
        
        scenario_name = PS_CSV_File_name.split('_rawPS')[0]
        
        accidentData = []
        
        accidentData_format = {
                "name" : " ",
                "year" : [],
                "COLLTYPE_MAIN" : [],
                "ACCTYPEA" : [],
                "ACCTYPEB" : [],
                "ACCTYPE_unknown" : [],
                "occurrence" : {
                    "rank" : " "
                }
            }
        
        tmp_accidentData = copy.deepcopy(accidentData_format)
        accidentData.append(tmp_accidentData)

        # Registration 파일 필터링
        filtered_files = [file for file in os.listdir(registration_dir) if scenario_name in file]

        if not filtered_files:
            print(f"[경고] '{scenario_name}'와 일치하는 파일이 {registration_dir}에 없습니다.")
            return accidentData
   

        registration_file_name = [file for file in os.listdir(registration_dir) if scenario_name in file][0]
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