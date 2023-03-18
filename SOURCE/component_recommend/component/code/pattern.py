import json
import pandas as pd
import numpy as np
import json
from distance_feature_extractor import flatten_data,screen_parser,remove_container_component
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.patches as patches



file_path_json = '../file_json/patterns.1643275945108.json'
my_path = os.path.abspath(os.path.dirname(__file__))
file_path_json = os.path.join(my_path, file_path_json)
f = open(file_path_json)
screen_json = json.load(f)
data = []

def get_children_info(pattern_children):
    data_child = []
    result_info_child = []
    result_info_child_container = []
    result = []
    check_container = False
    for child in pattern_children:
        # if check_container == True:
        #     data_child_container = []
        if "height" not in child['data'] or "width" not in child['data'] or child["data"]['height'] == None or child["data"]['width'] == None:
            height_parents = 1
            width_parents = 1
        else:
            if child['type'] == "DIVIDER":
                height_parents = 0
                width_parents = child['data']['to']['x'] - child['data']['from']['x']
            else:
                height_parents = child['data']['height']
                width_parents = child['data']['width']
        if child['type'] == "CONTAINER" or child['type'] == "TAG" or child['type'] == "SIDEBAR_MENU" or child['type'] == "COLLAPSED_SIDEBAR_MENU" or child['type'] == "HEADER_MENU" or child['type'] == "TABBAR_MENU":
            name_comp = child['data']['name']
            x_comp = child['data']['position']['x']
            y_comp = child['data']['position']['y']
            # height_comp = child['data']['height']
            # width_comp = child['data']['width']
            check_container = True
            data_child_container = []
            for child_child in child['children']:
                
                if "height" not in child_child['data'] or "width" not in child_child['data'] or child_child["data"]['height'] == None or child_child["data"]['width']==None:
                    height = 1
                    width = 1
                else:
                    if child_child['type'] == "DIVIDER":
                        height = 0
                        width = child_child['data']['to']['x'] - child_child['data']['from']['x']
                    else:
                        height = child_child['data']['height']
                        width = child_child['data']['width']
                parentId = child_child['parentId']
                data_child_container.append({
                    'type': child_child['type'],
                    "x": child_child['data']['position']['x'],
                    "y": child_child['data']['position']['y'],
                    "height": height,
                    "width": width,
                })
                result_info_child_container = ({
                    'check': "container",
                    'name_parent': name_comp,
                    'parentId': parentId ,
                    'x_parent': x_comp,
                    'y_parent': y_comp,
                    'height_parent': height_parents,
                    'width_parent': width_parents,
                    'list_components': data_child_container,
                })
            result.append(result_info_child_container)
        else:
            check_container = False
            parentId = child['parentId']
            data_child.append({
                'type': child['type'],
                "x": child['data']['position']['x'],
                "y": child['data']['position']['y'],
                "height": height_parents,
                "width": width_parents,
            })
            result_info_child = ({
                'parentId': parentId ,
                'list_components': data_child,
            })
    if check_container == False:
        result.append(result_info_child)
    return result

def struct_data(patterns_json,data):
    for table_pattern in patterns_json:
        data_pattern = table_pattern['data']
        children_pattern = data_pattern['children']
        data_child = []
        data_child = (get_children_info(children_pattern))
        data.append({
            "id" : table_pattern["id"],
            "name": table_pattern["name"],
            "x": data_pattern["data"]["position"]["x"],
            "y": data_pattern["data"]["position"]["y"],
            "height": data_pattern["data"]["height"],
            "width": data_pattern["data"]["width"],
            "children": data_child,

        })
    return data


# print(screen_json['data']['children'])
# Test filter components in pattern

# data = get_children_info(screen_json[0]['data']['children'])
# print(data)
file_path_json = os.path.join(my_path, '../file_json/data.json')
data = []
struct_data(screen_json,data)
# print(data[1])
with open(file_path_json, 'w') as f:
    json.dump(data, f)