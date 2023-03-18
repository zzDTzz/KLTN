import os
import random
import json
import csv
from recommender import get_recommendData_and_targetData
from distance_feature_extractor import training

###########################################
# Xử lý đường dẫn Local.
###########################################
current_directory = os.getcwd()


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



def run_all_testing_data(path, start, end, precision, rate,similarity_list):
    title = ['Name file', 'Recommend', 'Target', 'Precision', 'True/False']
    with open(path, mode='w', encoding='UTF-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=title, delimiter=',')
        writer.writeheader()

        testing_result = []
        for items in range(start, end + 1):
            result_recommend = []
            result_target = []

            try:
                namefile = str(items) + '.json'
                print("Name file: ", namefile)
                recommend_data, target_data, handle_target_data, len_handle_target_data = get_recommendData_and_targetData(namefile, precision,similarity_list)

                for row_recommend in range(len(recommend_data)):
                    result_recommend.append(
                        recommend_data[row_recommend]["comp_type"])

                for row_target in range(len(target_data)):
                    result_target.append(target_data[row_target]["type"])
                
                result_precision = float((len(handle_target_data)/len_handle_target_data)*100)
                
                result_true_or_false = str
                if result_precision >= float(rate):
                    result_true_or_false = "True"
                else:
                    result_true_or_false = "False"    

                testing_result.append({
                    "Name file": namefile,
                    "Recommend": result_recommend,
                    "Target": result_target,
                    "Precision": result_precision,
                    "True/False": result_true_or_false
                })
                print("Done!")

            except:
                print("Error!")

        writer.writerows(testing_result)


if __name__ == '__main__':
    similarity_list = training(100000,100500)
    # print(similarity_list)
    run_all_testing_data(f'{current_directory}/SOURCE/component_recommend/component/test_case.csv', 100501, 100659, 0.2, 60,similarity_list)