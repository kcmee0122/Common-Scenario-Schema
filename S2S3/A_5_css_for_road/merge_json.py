import json
import os


path_code = os.getcwd()
path_jsonDir = r'D:\Shares\MORAI Scenario Data\SOTIF Catalogue\MORAI Project\Json'
list_name_json = os.listdir(path_jsonDir)
name_folder = 'json_merge'
path_saveJson = os.path.join(path_code, name_folder + '_combine.json')

with open(path_saveJson, 'w', encoding='UTF-8') as f:
    json_text_merg = '[' + '\n'
    for Cur_name_json in list_name_json:
        if Cur_name_json.endswith('.json'):
            with open(os.path.join(path_jsonDir, Cur_name_json), 'r', encoding='UTF-8') as file:
                Cur_text_json = file.read().strip()
                if Cur_text_json[0] == '[' and Cur_text_json[-1] == ']':
                    Cur_text_json = Cur_text_json[1:-1]
                Cur_text_json += ','
                json_text_merg += Cur_text_json + '\n'
    json_text_merg = json_text_merg[:-2] + ']'  # 마지막 쉼표 및 개행 문자 제거

    f.write(json_text_merg)