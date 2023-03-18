import json
import os
from distance_feature_extractor import screen_parser, similarity_calculator, flatten_data, flatten_data, remove_component, remove_container_component


# Xử lý đường dẫn Local.
current_directory = os.getcwd()


def component_extractor(training_data):
    return screen_parser(training_data)

def get_top_k_similar(similar_list, k):
    top_k_similar = []

    if len(similar_list) == 0:
        return []

    # Sắp xếp danh sách similar tăng dần.
    temp = []
    for i in range(0, len(similar_list)):
        for j in range(0, len(similar_list)):
            if similar_list[i]['similarity'] > similar_list[j]['similarity']:
                temp = similar_list[i]
                similar_list[i] = similar_list[j]
                similar_list[j] = temp

    # Lấy top k similar từ danh sách similar.
    if len(similar_list) < k:
        k = len(similar_list) - 1
    for i in range(0, k):
        top_k_similar.append(similar_list[i])

    return top_k_similar

def get_len_target(target_data):
    data = []
    len_target = 0
    for pos_target in range(len(target_data)):
        ans = target_data[pos_target]["type"] not in data
        if ans:
            data.append(target_data[pos_target]["type"])
            len_target += 1
    return len_target


def selective_component(recommend_data, target_data):
    handle_target_data = []
    for pos_target in range(len(target_data)):
        for pos_recommend in range(len(recommend_data)):
            if target_data[pos_target]["type"] in recommend_data[pos_recommend]["comp_type"]:
                ans = target_data[pos_target]["type"] not in handle_target_data
                if ans:
                    handle_target_data.append(target_data[pos_target]["type"])

    return handle_target_data


#############################################
# Từ màn hình của người dùng đang thiết kế:
# - Trích ra các component
# - Lấy những loại component tương tự với loại đang có từ cơ sở dữ liệu
# - Lọc lại top k thằng có độ tương tự nhất
# - Chuyển đổi thành json và trả về cho người dùng
#############################################
def recommend_component(list_input, similar_list, k):
    current_similar_list = []
    for pos in range(0, len(list_input)):
        # current_similar_list = []
        input_item_type = list_input[pos]['type'].upper()

        for item in similar_list:
            if item['com1_type'] in input_item_type:
                current_similar_list.append({
                    'comp_type': item['com2_type'],
                    'similarity': item['similarity']
                })
            elif item['com2_type'] in input_item_type:
                current_similar_list.append({
                    'comp_type': item['com1_type'],
                    'similarity': item['similarity']
                })

    return get_top_k_similar(current_similar_list, k)

def get_recommendData_and_targetData(namefile, precision,similarity_list):
    # Lấy đường dẫn tuyệt đối của tệp dữ liệu traning
    # abspath_training_data = (f'{current_directory}/trainingData.json')

    # Mở tệp dữ liệu training.
    # training_data = load_similar_components(abspath_training_data)

    # Lấy đường dẫn tuyệt đối của tệp dữ liệu testing
    abspath_testing_data = (f'{current_directory}/SOURCE/component_recommend/visily_json/' + namefile)

    # Mở tệp dữ liệu testing
    file = open(abspath_testing_data)
    testing_data = json.load(file)

    # Xử lý làm phẳng tệp dữ liệu testing.
    handle_testing_data = []
    flatten_data(testing_data, handle_testing_data)

    # Xóa các component là thùng chứa và TEXT component.
    remove_container_component(handle_testing_data)

    # Xóa % số lượng các component và lưu vào list target.
    target_data = remove_component(handle_testing_data, precision)

    # Lưu các component được đề xuất.
    recommend_data = recommend_component(handle_testing_data, similarity_list, 5)

    # Lọc và lưu dữ liệu có các conponent bị xóa mà có trùng trong list recommend_data.
    handle_target_data = selective_component(recommend_data, target_data)

    # Lấy chiều dài của list target_data mà không bị trùng các component.
    len_handle_target_data = get_len_target(target_data)

    return recommend_data, target_data, handle_target_data, len_handle_target_data

