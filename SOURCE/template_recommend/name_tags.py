import os
import pandas as pd
from math import log10
from scipy.spatial.distance import cosine


# Initialize absolute path
current_directory = os.getcwd()


# Chuyển những name tag thành chữ in thường.
# Xóa những name tag giống nhau trong cùng template.
def handle_dataset(template_with_tags):
    template_with_tags['tag_name'] = template_with_tags['tag_name'].str.lower()
    template = template_with_tags.iloc[0, 0]
    name_tags = []
    name_tags_del = []

    for row in range(len(template_with_tags)):
        if template_with_tags.iloc[row, 0] == template:
            if template_with_tags.iloc[row, 1] not in name_tags:
                name_tags.append(template_with_tags.iloc[row, 1])
            else:
                name_tags_del.append(row)
        else:
            template = template_with_tags.iloc[row, 0]
            name_tags = []

            if template_with_tags.iloc[row, 1] not in name_tags:
                name_tags.append(template_with_tags.iloc[row, 1])
            else:
                name_tags_del.append(row)

    template_with_tags.drop(name_tags_del, axis=0, inplace=True)
    template_with_tags.sort_values(by='name', axis = 0, ascending = True, inplace = True, na_position ='last')
    return template_with_tags


# Lấy name tag.
def get_name_tags(template_with_tags):
    name_tags = []
    for row in range(len(template_with_tags)):
        if template_with_tags.iloc[row, 1] not in name_tags:
            name_tags.append(template_with_tags.iloc[row, 1])

    name_tags.sort()
    return name_tags


# Lấy template.
def get_template(template_with_tags):
    template = []
    for row in range(len(template_with_tags)):
        if template_with_tags.iloc[row, 0] not in template:
            template.append(template_with_tags.iloc[row, 0])

    template.sort()
    return template


# Tạo bảng TF-IDF.
def tf_idf_matrix(template_with_tags):
    name_tags = get_name_tags(template_with_tags)
    template = get_template(template_with_tags)
    TF_IDF = pd.DataFrame(index=template, columns=name_tags)
    
    for row in range(len(template_with_tags)):
       
        TF = 1
        number_of_templates = int(template_with_tags.iloc[len(template_with_tags) - 1, 0])
        number_of_templates_that_contain_the_tag = len(template_with_tags.loc[template_with_tags['tag_name'] == template_with_tags.iloc[row, 1]])
        IDF = log10(number_of_templates / number_of_templates_that_contain_the_tag)
        TF_IDF.loc[template_with_tags.iloc[row, 0], template_with_tags.iloc[row, 1]] = TF * IDF

    TF_IDF.fillna(0, inplace=True)
    return TF_IDF


# Tính độ tương tự của các template dựa trên name tag.
def tag_similarity_matrix(TF_IDF, epsilon= 1e-8):
    tag_similarity_dataset = pd.DataFrame(index=TF_IDF.index, columns=TF_IDF.index)

    for row in range(0, len(tag_similarity_dataset.index)):
        for col in range(0, len(tag_similarity_dataset.columns)):
            sim = (1 - cosine(TF_IDF.iloc[row, :] + epsilon, TF_IDF.iloc[col, :] + epsilon))
            if sim == 1 and row != col:
                tag_similarity_dataset.iloc[row, col] = 0.99
            else:
                tag_similarity_dataset.iloc[row, col] = sim

    return tag_similarity_dataset


def split_template_old_and_new(template_with_tags):
    template_old = []
    template_new = template_with_tags.loc[template_with_tags['tag_name'] == 'new', 'name'].tolist()

    for row in range(len(template_with_tags)):
        if template_with_tags.iloc[row, 0] not in template_new:
            if template_with_tags.iloc[row, 0] in template_old:
                pass
            else:
                template_old.append(int(template_with_tags.iloc[row, 0]))

    for row in range(len(template_new)):
        template_new[row] = int(template_new[row])
    
    return template_old, template_new


# Lọc những template giống nhau dựa trên name tag.
def filter_name_tags(template_with_tags, tag_similarity_dataset, k):
    template_old, template_new = split_template_old_and_new(template_with_tags)

    the_same_name_tag_table = pd.DataFrame(index=range(len(template_old)), columns=['template_id', '1', '2', '3', '4', '5', '6', '7', '8'])

    # Bảng template có template cũ giống phần lớn name tag.
    table_1 = pd.DataFrame(index=range(len(template_old)), columns=['template_id', '1', '2', '3', '4', '5'])
    #Bảng template có template mới giống phần lớn name tag.
    table_2 = pd.DataFrame(index=range(len(template_old)), columns=['template_id', '1', '2', '3'])
    
    for row in range(len(template_old)):
        the_same_name_tag_table.iloc[row, 0] = template_old[row]
        the_same_name_tag_table.iloc[row, 1:] = tag_similarity_dataset.iloc[0:, row].sort_values(ascending=False).iloc[1:9].index

        count_1 = 1
        count_2 = 1

        for col in range(0, k):
            if col == 0:
                table_1.iloc[row, 0] = the_same_name_tag_table.iloc[row, 0]
                table_2.iloc[row, 0] = the_same_name_tag_table.iloc[row, 0]
        
            elif the_same_name_tag_table.iloc[row, col] in template_new:
                if count_2 < len(table_2.columns):
                    table_2.iloc[row, count_2] = the_same_name_tag_table.iloc[row, col]
                    count_2 += 1
            else:
                if count_1 < len(table_1.columns):
                    table_1.iloc[row, count_1] = the_same_name_tag_table.iloc[row, col]
                    count_1 += 1

    table_1.to_csv(f'{current_directory}/DATASET/template_recommend/result/name tags/table_1.csv', sep=',', encoding='utf-8')
    table_2.to_csv(f'{current_directory}/DATASET/template_recommend/result/name tags/table_2.csv', sep=',', encoding='utf-8')


def print_name_tag_table(namefile):
    template_with_tags = pd.read_csv(f'{current_directory}' + namefile, sep=',', encoding='utf-8')
    dataset = handle_dataset(template_with_tags)
    TF_IDF = tf_idf_matrix(dataset)
    tag_similarity_dataset = tag_similarity_matrix(TF_IDF)
    filter_name_tags(dataset, tag_similarity_dataset, 9)