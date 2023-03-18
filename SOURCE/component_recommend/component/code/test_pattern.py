import csv
from distutils.command.check import check
import json
import os
import pandas as pd
import ast
my_path = os.path.abspath(os.path.dirname(__file__))
path = f"../file_csv/association_rule_4.csv"
path = os.path.join(my_path, path)

path_check = f"../file_csv/list_components.csv"
path_check = os.path.join(my_path, path_check)
df = pd.read_csv(path)
df["A"] = df["A"].apply(lambda x: eval(x))
check_df = pd.read_csv(path_check)

check_df["type_components"] = check_df["type_components"].apply(lambda x : pd.unique(ast.literal_eval(x)))
arr_df = check_df.to_numpy()
# print(arr_df)
input_test = ["CHECKBOX","TEXT","BUTTON"]


df_rule_a_b = df[df["rule"] == "A -> B"]
df_rule_b_a = df[df["rule"] == "B -> A"]
set_components = []
new_pattern = []
def recommender_pattern(list_components):
    recommend_pattern = []
    if len(list_components) == 0:
        recommend_pattern = ["None","None"]
    else:
        for pattern in arr_df:
            len_input = len(list_components)
            for component in list_components:
                components_of_pattern = pattern[1]
                if component in components_of_pattern:
                    len_input -= 1
            if len_input == 0:
                recommend_pattern.append(pattern)
    return recommend_pattern
def get_rule_to_recommend_from_input(input,df_rule):
    set_components = []
    for list_components in df_rule["A"]:
        len_input = len(input)
        for components in input:
            if components in list_components:
                len_input -= 1
        if len_input == 0:
            consequence = df_rule[df_rule["A"] == list_components]["B"].to_list()[0]
            set_components = input_test
            set_components.append(consequence)
    return set_components
A = [["AVATAR","TEXT","BUTTON"], ["CHECKBOX","TEXT","BUTTON"]]


def training_pattern_recommendation(list_input):
    list_recommend = []
    for individual_input in list_input:
        result = [individual_input]
        rule_created_by_input = get_rule_to_recommend_from_input(individual_input,df_rule_a_b)
        result.append(recommender_pattern(rule_created_by_input))
        list_recommend.append(result)
    return list_recommend

b = training_pattern_recommendation(A)
print((b))

header = ["input","components_of_pattern","name_pattern"]

my_path = os.path.abspath(os.path.dirname(__file__))
path = f"../file_csv/result_recommendation.csv"
path = os.path.join(my_path, path)
with open(path, 'w') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for i_recommend in b:
        for j_info in i_recommend:
            for t in j_info:
                row = [i_recommend[0],t[0],t[1]]
            writer.writerow(row)
