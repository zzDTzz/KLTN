import os
import pandas as pd
from scipy.spatial.distance import cosine


# Initialize absolute path
current_directory = os.getcwd()


def handle_role(role):
    data_user = pd.read_csv(
        f'{current_directory}/SOURCE/template_recommend/data/user_information.csv', sep=',', encoding='utf-8')
    template_user_count = pd.read_csv(
        f'{current_directory}/SOURCE/template_recommend/data/clean_template_user_count.csv', sep=',', encoding='utf-8')
    counted_dataset = pd.DataFrame(
        index=template_user_count.index, columns=template_user_count.columns)
    data_user = data_user.loc[data_user['role'] == role]
    prev_count = 0
    curr_count = 0

    for row in range(len(data_user)):
        temp = template_user_count.loc[template_user_count['user_id']
                                       == data_user.iloc[row, 0]]
        curr_count += len(temp)
        counted_dataset.iloc[prev_count:curr_count, :] = temp.iloc[0:, :]
        prev_count = curr_count

    counted_dataset = counted_dataset.iloc[:curr_count, :]
    return counted_dataset


def get_template(clean_template_count_dataset):
    template_id = []

    for row in range(len(clean_template_count_dataset)):
        if clean_template_count_dataset.iloc[row, 0] not in template_id:
            template_id.append(clean_template_count_dataset.iloc[row, 0])

    template_id.sort()
    return template_id


def get_user(counted_dataset):
    user_id = []

    for row in range(len(counted_dataset)):
        if counted_dataset.iloc[row, 0] not in user_id:
            user_id.append(counted_dataset.iloc[row, 0])

    user_id.sort()
    return user_id


def convert_dataset(counted_dataset):
    clean_template_count_dataset = pd.read_csv(
        f'{current_directory}/SOURCE/template_recommend/data/clean_template_count.csv', sep=',', encoding='utf-8')
    user_id = get_user(counted_dataset)
    template_id = get_template(clean_template_count_dataset)
    final_dataset = pd.DataFrame(index=user_id, columns=template_id)
    count = 0

    for row in range(len(counted_dataset)):
        if counted_dataset.iloc[row, 0] == user_id[count]:
            final_dataset.loc[user_id[count],
                              counted_dataset.iloc[row, 1]] = counted_dataset.iloc[row, 2]
        else:
            count += 1
            final_dataset.loc[user_id[count],
                              counted_dataset.iloc[row, 1]] = counted_dataset.iloc[row, 2]

    return final_dataset


def cal_score_1_to_10(final_dataset):
    for row in range(len(final_dataset.index)):
        maximun = final_dataset.iloc[row, :].max()
        final_dataset.iloc[row, :] = (
            final_dataset.iloc[row, :] * 9) / maximun + 1

    return final_dataset


def normalized_matrix(final_dataset):
    normalized_dataset = cal_score_1_to_10(final_dataset)
    normalized_dataset.fillna(0.0, inplace=True)
    return normalized_dataset


def item_similarity_matrix(normalized_dataset, epsilon=1e-8):
    item_similarity_dataset = pd.DataFrame(
        index=normalized_dataset.columns, columns=normalized_dataset.columns)

    for row in range(0, len(item_similarity_dataset.index)):
        for col in range(0, len(item_similarity_dataset.columns)):
            sim = (1 - cosine(normalized_dataset.iloc[:, row] +
                   epsilon, normalized_dataset.iloc[:, col] + epsilon))
            if sim == 1 and row != col:
                item_similarity_dataset.iloc[row, col] = 0.99
            elif sim < 1e-6:
                item_similarity_dataset.iloc[row, col] = 0
            else:
                item_similarity_dataset.iloc[row, col] = sim

    return item_similarity_dataset


def remove_the_same_template(list_name_tags_a_template, list_a_template):
    list_filter_template = []
    list_filter_template.append(list_a_template[0])

    for row in range(1, len(list_a_template)):
        if list_a_template[row] not in list_name_tags_a_template:
            list_filter_template.append(list_a_template[row])

    return list_filter_template


def role_filter(item_similarity_dataset, role):
    data_template_old = pd.read_csv(
        f'{current_directory}/DATASET/template_recommend/result/name tags/table_1.csv', sep=',', encoding='utf-8')
    data_template_new = pd.read_csv(
        f'{current_directory}/DATASET/template_recommend/result/name tags/table_2.csv', sep=',', encoding='utf-8')
    data_recommend = pd.DataFrame(index=item_similarity_dataset.index, columns=[
                                  'template_id', '1', '2', '3', '4', '5', '6', '7', '8'])
    count = 0

    for row in range(len(data_recommend.index)):
        list_a_template = item_similarity_dataset.iloc[:, row].sort_values(
            ascending=False).index.tolist()

        if int(data_template_old.iloc[count, 1]) == row:
            list_template_old = data_template_old.iloc[count, 1:].tolist()
            list_template_new = data_template_new.iloc[count, 1:].tolist()
            list_filter_template = remove_the_same_template(
                list_template_old, list_a_template)
            data_recommend.iloc[row, :6] = list_filter_template[0:6]
            data_recommend.iloc[row, 6:] = list_template_new[1:]
            count += 1
        else:
            data_recommend.iloc[row, :6] = list_a_template[:6]

    data_recommend.to_csv(
        f'{current_directory}/DATASET/template_recommend/result/recommend item/recommend_template_role_' + role + '.csv', sep=',', encoding='utf-8')


def recommend_item_template(role):
    role_dataset = handle_role(role)
    final_dataset = convert_dataset(role_dataset)
    normalized_dataset = normalized_matrix(final_dataset)
    item_similarity_dataset = item_similarity_matrix(normalized_dataset)
    role_filter(item_similarity_dataset, role)
