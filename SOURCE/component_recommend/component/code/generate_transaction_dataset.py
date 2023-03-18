import json
import csv
import os
#Lấy đường dẫn 


file_path = "../file_json/data.json"
my_path = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(my_path, file_path)


#------------------------------------------------#

f = open(file_path)

data = json.load(f)
header = ['name','type_components']
list_data = []
# print(data[0])
for pattern in data:
    name_pattern = pattern['name']
    list_components = []
    children_pattern = len(pattern['children'])
    if children_pattern < 2:
        children = pattern['children'][0]['list_components']
        len_children = len(children)
        i = 0
        for i_comp in children:
            type_component = i_comp['type']
            list_components.append(type_component)
        list_data.append([name_pattern,list_components])
print(list_data)

path_result = "../file_csv/list_components.csv"
path_result = os.path.join(my_path, path_result)
with open(path_result, 'w') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    # Use writerows() not writerow()
    writer.writerows(list_data)


