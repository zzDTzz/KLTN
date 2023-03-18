import random
import math
import csv
import json
import os
from itertools import groupby
import itertools


# Xử lý đường dẫn Local.
current_directory = os.getcwd()


# open json
# class Component(object):
#     def __init__(self, id, name, type, x_c, y_c):
#         self.id = id
#         self.name = name
#         self.type = type
#         self.x_c = x_c
#         self.y_c = y_c
#     def print_item(self):
#         print(self.id, self.name, self.type, self.x_c, self.y_c)


###########################################
# Xử lý phẳng dữ liệu.
###########################################
def flatten_data(data, handle_data):
    for i in data:
        handle_data.append({
            "type": i["type"],
            "data": i["data"]
        })

        if("children" in i and len(i["children"]) > 0):
            flatten_data(i["children"], handle_data)


###########################################
# Xóa các component là thùng chứa trong dữ liệu.
# data: dữ liệu cần xử lý.
# component_container_data: tệp dữ liệu các thùng chứa.
# Kết quả trả về một mảng đã được xóa các thùng chứa và TEXT component.
###########################################
def remove_container_component(data):
    # Lấy đường dẫn tuyệt đối của tệp boxComponent.json.
    abspath_component_container_data = (
        f'{current_directory}/SOURCE/component_recommend/component/boxComponent.json')
    # Mở tệp boxComponent.json.
    file = open(abspath_component_container_data)
    # Lưu dữ liệu các thùng chứa vào biến component_container_data.
    component_container_data = json.load(file)

    temp = []
    for i in range(0, len(component_container_data)):
        for j in range(0, len(data)):
            # Kiểm tra dữ liệu cần xử lý có component nào là thùng chứa hoặc component nào là TEXT hay không
            if data[j]["type"] == component_container_data[i]["type"]:
                # Kiểm tra thành công thì lưu component đó vào list temp.
                temp.append(data[j])

    # Xóa các component là thùng chứa hoặc component là TEXT.
    for items in temp:
        data.remove(items)


###########################################
# Xóa các component trong dữ liệu testing.
# - precision: phần trăm số lượng các component bị xóa.
# - testing_data: tệp dữ liệu cần kiểm tra.
# Kết quả trả về một mảng chứa các component bị xóa.
###########################################
def remove_component(testing_data, precision):
    # Lấy số lượng component bị xóa
    number_of_components_removed = int(len(testing_data) * precision)

    if number_of_components_removed == 0 or number_of_components_removed == 1:
        number_of_components_removed = 3

    # Lưu các component bị xóa vào list target.
    target = []
    count = 0
    while (count < number_of_components_removed):
        # Lưu component được chọn ngẫu nhiên vào biến temp.
        temp = random.choice(testing_data)

        # Nếu component được chọn ngẫu nhiên không có trong list target thì thêm vào list target
        # Và xóa component đó trong dữ liệu test.
        if temp not in target:
            target.append(temp)
            testing_data.remove(temp)
            count += 1

    return target
# add item into
def add_item(data, handle_data):
    for i in data:
        if ("height" not in i["data"] or "width" not in i["data"]):
            height = 0
            width = abs(i["data"]["to"]["x"] - i["data"]["from"]
                        ["x"]) if "to" in i["data"] else 0
        else:
            height = i["data"]["height"] if i["data"]["height"] else 0
            width = i["data"]["width"] if i["data"]["width"] else 0

        x_c = width / 2 + i["data"]["position"]["x"]
        y_c = i["data"]["position"]["y"] - height / 2
        handle_data.append({
            "type": i["type"],
            "x_c": x_c,
            "y_c": y_c
        })
        if("children" in i and len(i["children"]) > 0):
            add_item(i["children"], handle_data)

###########################################
# Lấy các component và các thành phần cần thiết của mỗi component:
# - id của màn hình mà nó thuộc về
# - tên component
# - loại component
# - Tọa độ điểm trung tâm
# Kết quả trả về là một mảng với mỗi phần tử là thông tin của 1 component được đóng gói trong kiểu từ điển
# Ví dụ: [ {id: 1, name: "submit", type: "button", x_c: 12, y_c: 89}, {...}, ... ]
# ###########################################


def screen_parser(screen_json):
    # parse the screen to extract components
    components = []
    add_item(screen_json, components)
    return components


#########################################
# Tính toán khoảng cách giữa một cặp component trong 1 màn hình, lưu kết quả lên database
# Kết quả trả về là một mảng các phần tử với mỗi phần tử chứa thông tin:
# - id của màn hình mà nó thuộc về
# - tên component 1
# - loại component 1
# - tên component 2
# - loại component 2
# - khoảng cách
# Ví dụ: [ { id: 1, com1_name: "submit", com1_type: "button", com2_name: "username", com2_type: "textbox", distance: 150.25}, ...]
# Kết quả cần lưu lên DB trước khi trả vể
#########################################
def distance_calculator(screen_components):
    result = []
    # calculate distance
    for index, item in enumerate(screen_components):
        for next in screen_components[index+1:]:
            result.append({
                "com1_type": item["type"],
                "com2_type": next["type"],
                "distance": math.sqrt((item["x_c"] - next["x_c"]) ** 2 + (item["y_c"] - next["y_c"]) ** 2)
            })

    #print('Total of distance is ' + str(len(result)))
    # title = ["com1_type", "com2_type", "distance"]
    # with open('distance.csv', 'w') as title:
    #     write = csv.writer(title)
    #     write.writerow(title)
    data_values = [list(i.values()) for i in result]
    # store to DB
    with open(f'{current_directory}/SOURCE/component_recommend/component/distance.csv', 'a') as f:
        write = csv.writer(f)
        write.writerows(data_values)

    return result


##########################################
# Tính toán độ tương tự giữa một cặp "loại" component dựa trên khoảng cách
# Kết quả trả về là một mảng các độ tương tự giữa một cặp loại component:
# - loại của component 1
# - loại của component 2
# - độ tương tự
# Vi dụ: [ {com1_type: "button", com2_type: "textbox", similarity: 34.23}, ...]
# Cũng lưu kết quả lên DB trước khi trả về
##########################################

def similarity_calculator(distance_components):

    # Sắp xếp gom nhóm các loại components cho đúng thứ tự và không bị trùng lắp
    distance_components = list(itertools.chain.from_iterable(distance_components))
    result = []
    groupby_data = groupby(distance_components,key=lambda x:(x["com1_type"],x["com2_type"]))
    converted = [{"key": key,"value": list(value)}
                 for key, value in groupby_data]
    for i in range(len(converted)):
        converted[i]['key'] = tuple(sorted(converted[i]['key']))
    converted.sort(key=lambda x: x['key'])
    temp = groupby(converted,key=lambda x:(x['key']))
    result = [{"type_component": key,"similarity": [i['value'] for i in list(value)]}
                 for key, value in temp]

    # tính độ tương tự dựa trên khoảng cách của các component trên mỗi màn hình. 
    # Độ tương tự được tính bằng cách lấy tổng khoảng cách của components trên mỗi màn hình và tất cả màn hình, 
    # sau đó chia cho số lần xuất hiện
    for i in range(len(result)):
        sum_distance = 0
        freq= 0
        for components in result[i]['similarity']:
            freq += len(components)
            sum_distance += sum(i['distance'] for i in components)

        result[i]['similarity'] = {
            "sum_distance": sum_distance,
            "freq": freq
        }
    quantity_components = len(result)
    # chỉnh sửa lại format của list các similarity giữa cái loại component [{"com1_type": ,"com2_type": , "similarity": },...]
    list_similarity_components = []
    for component in result:
        list_similarity_components.append({
            "com1_type": component['type_component'][0],
            "com2_type": component['type_component'][1],
            "similarity": component['similarity']["sum_distance"]/quantity_components,
            "freq": component['similarity']["freq"]

        })
    title = ["com1_type","com2_type", "similarity"]
    data_values = [list(i.values()) for i in list_similarity_components]
    # store to DB
    with open(f'{current_directory}/SOURCE/component_recommend/component/similarity.csv', 'w') as f:
        write = csv.writer(f)
        write.writerow(title)
        write.writerows(data_values)
    return list_similarity_components


##########################################
# Đọc và xử lý lần lượt các màn hình
##########################################
def training(start,end):
    all_distances = []
    current_directory = os.getcwd()
    for i in range(start,end,1):
        f = open(f"{current_directory}/SOURCE/component_recommend/component/visily_json/{i}.json",  encoding="utf-8")
        screen_json = json.load(f)
        screen_flatten = []
        flatten_data(screen_json,screen_flatten)
        remove_container_component(screen_flatten)
        component_list = screen_parser(screen_flatten)
        distance_list = distance_calculator(component_list)
        all_distances.append(distance_list)
    components_similarity = similarity_calculator(all_distances)
        
    return components_similarity