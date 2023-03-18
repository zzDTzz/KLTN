import json
import pandas as pd
import numpy as np
import ast
import re
import math
import random

def get_classes(): 
    df = pd.read_csv('list_components.csv')
    df['Components'] = df['Components'].apply(ast.literal_eval)
    
    temp = pd.DataFrame(df['Components'].values.tolist()).transpose()
    temp = temp.replace(np.nan,'',regex=True)
    X = temp.to_numpy()
    X = np.array(X)
    classes = np.unique(X)
    classes = classes[1:]
    return classes

def cal_distance_angle(file_json,classes):
    distance = []
    angle = []
    f = open(file_json)
    input_file = json.load(f)
    for i in range(len(input_file)):
        d_pattern = []
        a_pattern = []
        for class_i in classes:
            class_distance=[]
            class_angle = []
            for j in range(len(input_file[i]['info_children'])):
                comp = re.split('\(|\)|,',input_file[i]['info_children'][j])
                if class_i == comp[0]:
                    temp_distance = math.sqrt(float(comp[1])**2 + float(comp[2])**2)
                    try:
                        temp_angle = float(comp[1]) / temp_distance
                    except:
                        temp_angle = 1
                    
                    class_distance.append(temp_distance)
                    class_angle.append(temp_angle)
                    
            class_distance.sort(reverse=False)
            class_angle.sort(reverse=True)
            
            d_pattern.append(class_distance)
            a_pattern.append(class_angle)
            
        distance.append(d_pattern)
        angle.append(a_pattern)
    return distance,angle

def cal_distance_angle_input(list_input,classes):
    distance = []
    angle = []
    for class_i in classes:
        class_distance=[]
        class_angle = []
        for j in range(len(list_input)):
            comp = re.split('\(|\)|,',list_input[j])
            if class_i == comp[0]:
                temp_distance = math.sqrt(float(comp[1])**2 + float(comp[2])**2)
                try:
                    temp_angle = float(comp[1]) / temp_distance
                except:
                    temp_angle = 1
                
                class_distance.append(temp_distance)
                class_angle.append(temp_angle)
                
        class_distance.sort(reverse=False)
        class_angle.sort(reverse=True)
            
        distance.append(class_distance)
        angle.append(class_angle)
    return distance,angle

def pad_or_truncate(some_list, target_len):
    return some_list[:target_len] + [0]*(target_len - len(some_list))

def get_max_range_classes(classes,feature):
    range_classes = []
    for i in range(len(classes)):
        max_classes = 0
        for j in range(len(feature)):
            if max_classes < len(feature[j][i]):
                max_classes = len(feature[j][i])
        range_classes.append(max_classes)
    return range_classes

def fill_zero(classes,range_classes,distance,angle):
    for i in range(len(range_classes)):
        for j in range(len(distance)):
            distance[j][i] = pad_or_truncate(distance[j][i], range_classes[i])
            angle[j][i] = pad_or_truncate(angle[j][i], range_classes[i])
    return distance,angle

def fill_zero_input(classes,range_classes,distance_input,angle_input):
    for i in range(len(range_classes)):
        for j in range(len(distance_input)):
            distance_input[i] = pad_or_truncate(distance_input[i], range_classes[i])
            angle_input[i] = pad_or_truncate(angle_input[i], range_classes[i])
    return distance_input,angle_input

def merge_sublist(feature):
    total = []
    for pattern in feature:
        temp = []
        for classes in pattern:
            temp += classes
        total.append(temp)
    return np.array(total)

def merge_sublist_input(feature_input):
    total = []
    for classes in feature_input:
        total += classes
    return np.array(total)

def norm_list(l):
    xmin = min(l) 
    xmax = max(l)
    for i, x in enumerate(l):
        l[i] = (x-xmin) / (xmax-xmin)
    return l

def norm_distance(d_array):
    for i in range(len(d_array)):
        d_array[i] = norm_list(d_array[i])
    return d_array

def cos_sim(a, b):
    """Takes 2 vectors a, b and returns the cosine similarity 
    """
    dot_product = np.dot(a, b) # x.y
    norm_a = np.linalg.norm(a) #|x|
    norm_b = np.linalg.norm(b) #|y|
    return dot_product / (norm_a * norm_b)

def similarity(vector_input,vector_pattern):
    similarity_list = []
    for pattern in vector_pattern:
        similarity_list.append(cos_sim(vector_input, pattern))
    return similarity_list

def cal_distance_angle_pattern_vector(file_pattern, classes):
    distance,angle = cal_distance_angle(file_pattern,classes)
    
    range_classes = get_max_range_classes(classes,distance)
    
    distance,angle = fill_zero(classes,range_classes,distance,angle)
    
    distance = merge_sublist(distance)
    angle = merge_sublist(angle)
    distance = norm_distance(distance)
    distance_angle = np.concatenate((distance, angle), axis=1)
    return distance_angle,range_classes

def get_header(classes,range_classes):
    header = []
    for i in range(len(classes)):
        for j in range(range_classes[i]):
            header.append(classes[i] + str(j))
    return header

def cal_distance_angle_input_vector(list_input,classes,range_classes):
    distance_input,angle_input = cal_distance_angle_input(list_input,classes)
    distance_input,angle_input = fill_zero_input(classes,range_classes,distance_input,angle_input)
    
    #input
    distance_input = merge_sublist_input(distance_input)
    angle_input = merge_sublist_input(angle_input)
    
    distance_input = distance_input.T
    angle_input = angle_input.T
    
    distance_input = norm_list(distance_input)
    
    distance_angle_input = np.concatenate((distance_input, angle_input))
    return distance_angle_input

def main():
    classes = get_classes()
    #pattern
    distance_angle_pattern,range_classes = cal_distance_angle_pattern_vector('position.json', classes)
    header = get_header(classes,range_classes)
    df = pd.DataFrame (distance_angle_pattern, columns = header+header)
    df.to_csv('pattern_vector.csv',index = False)
    count_5 = 0
    count_1 = 0
    
    n = 1000
    for i in range(1000):
        #input
        #random choice 1 pattern
        f = open('position.json')
        input_file = json.load(f)
        random_pattern = random.sample(input_file,1)
        #remove 20% components in pattern
        length = len(random_pattern[0]['info_children'])
        k = length * (1 - 0.2)
        id_pattern = random_pattern[0]['id_pattern']
        #print(id_pattern)
        try:
            list_input = random.sample(random_pattern[0]['info_children'],round(k))
        except:
            n -= 1
            continue
            
        #print(list_input)
        try:
            distance_angle_input = cal_distance_angle_input_vector(list_input,classes,range_classes)
        except:
            n -= 1
            continue
        #calculate similarity
        si = similarity(distance_angle_input,distance_angle_pattern)
        df = pd.read_csv('list_components.csv')
        dict_simi = {'similarity':si}
        df_simi = pd.DataFrame(dict_simi)
        df_simi['PatternId'] = df['Id']
        df_simi = df_simi.sort_values(by = 'similarity',ascending=False)
        top_5_df = df_simi.head(5)
        if(int(id_pattern) in top_5_df['PatternId'].values):
            count_5 += 1
            #print(count)
            
        top_1_df = df_simi.head(1)
        if(int(id_pattern) in top_1_df['PatternId'].values):
            count_1 += 1
            #print(count)
    p_5 = count_5 / n
    print(p_5)
    
    p_1 = count_1 / n
    print(p_1)
    

main()