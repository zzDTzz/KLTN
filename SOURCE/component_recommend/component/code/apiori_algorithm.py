from itertools import combinations
import pandas as pd
from ast import literal_eval
from collections import Counter
import os
import csv
import json

# Khởi tạo itemset với itemset là 1
def init_one_item(data):
    init_arr = []
    for item in data:
        for comp in item[1]:
            if comp not in init_arr:
                init_arr.append(comp)
    init_arr = sorted(init_arr)
    
    return init_arr

# tính sự xuất hiện của mỗi itemset xuất hiện trong transaction (container)
def frequency_item(list_item,df,check=False):
    candidate = dict()

    for item in list_item:
        set_item = {item}
        if check:
            set_item = set(item)
        for comp in df:
            if set_item.issubset(comp[1]):
                if item in candidate:
                    candidate[item] += 1
                else:
                    candidate[item] = 1
    return candidate

# Dựa vào min_sup để lấy ra được những itemset thoả độ min_sup
def items_greater_than_min_sup(freq_items,min_sup):
    l = dict()
    for item, freq in freq_items.items():
        if freq >= min_sup:
            l[item] = freq
    return l


# Lấy đường dẫn
file_path = '../file_csv/list_components.csv'
my_path = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(my_path, file_path)
#-------------------------------------#
df = pd.read_csv(file_path)
df['type_components'] = df['type_components'].apply(literal_eval)
arr = df.to_numpy()

# APRIORI ALGORITHM
def apriori(data,min_sup):
    list_items_greater_than_min_sup = []
    
    num_min_sup = min_sup*len(data)

    lst_one_item = init_one_item(data)
    freq_one_item = frequency_item(lst_one_item,data)
    items_greater_min_sup = items_greater_than_min_sup(freq_one_item,num_min_sup)
    list_items_greater_than_min_sup.append(items_greater_min_sup)

    for i in range(2,len(lst_one_item) + 1):
        lst_item = combinations(lst_one_item,i)
        freq_items = frequency_item(lst_item,data,check=True)
        items_greater_min_sup = items_greater_than_min_sup(freq_items,num_min_sup)
        if len(items_greater_min_sup) == 0:
            break
        else:
            list_items_greater_than_min_sup.append(items_greater_min_sup)
    return list_items_greater_than_min_sup
a = apriori(arr,0.07)
print(a)
# ASSOCIATION RULE A --> B
def association_rule(freq_itemset,confidence,f_items):
    result_rule = []
    for items in freq_itemset[f_items - 1]:
        quantities_items = len(items)
        list_small_items = combinations(items,len(items)-1)
        for itemset_a in list_small_items:
            quantities_a = len(itemset_a)
            itemset_b = tuple(set(items)^set(itemset_a))
            quantities_b = len(itemset_b)
            if quantities_a == 1:
                itemset_a = itemset_a[0]
                freq_itemset_a = freq_itemset[quantities_a - 1][itemset_a]
            else:
                freq_itemset_a = freq_itemset[quantities_a - 1][itemset_a]
            if quantities_b == 1:
                itemset_b = itemset_b[0]
                freq_itemset_b = freq_itemset[quantities_b - 1][itemset_b]
            else:
                freq_itemset_b = freq_itemset[quantities_b - 1][itemset_b]
            freq_itemset_a_b = freq_itemset[quantities_items - 1][items]
            confidence_a_b = freq_itemset_a_b/freq_itemset_a*100
            lift_a_b = confidence_a_b/freq_itemset_b
            confidence_b_a = freq_itemset_a_b/freq_itemset_b*100
            lift_b_a = confidence_b_a/freq_itemset_a
            if confidence_a_b > confidence:
                result_rule.append({
                "A": itemset_a,
                "B": itemset_b,
                "rule": "A -> B",
                "confidence": confidence_a_b,
                "lift": lift_a_b
            })
            elif confidence_b_a > confidence:
                result_rule.append({
                    "A": itemset_a,
                    "B": itemset_b,
                    "rule": "B -> A",
                    "confidence": confidence_b_a,
                    "lift": lift_b_a
                })
    return result_rule

for i_item in range(2,5):
    rule = []
    rule = association_rule(a,80,i_item)
    header = ["A","B","rule","confidence"]

    my_path = os.path.abspath(os.path.dirname(__file__))
    path = f"../file_csv/association_rule_{i_item}.csv"
    path = os.path.join(my_path, path)
    with open(path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        # Use writerows() not writerow()
        list_rule = []
        for i_rule in rule:
            row = []
            for info in i_rule:
                row.append(str(i_rule[info]))
            # print(row)
            list_rule.append(row)
        writer.writerows(list_rule)
# print(rule)

