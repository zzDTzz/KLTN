import os
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine


# Initialize absolute path
current_directory = os.getcwd()


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


def convert_dataset(namefile):
    clean_template_count_dataset = pd.read_csv(
        f'{current_directory}/SOURCE/template_recommend/data/clean_template_count.csv', sep=',', encoding='utf-8')
    counted_dataset = pd.read_csv(
        f'{current_directory}' + namefile, sep=',', encoding='utf-8')
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


def user_similarity_matrix(normalized_dataset, epsilon=1e-8):
    user_similarity_dataset = pd.DataFrame(
        index=normalized_dataset.index, columns=normalized_dataset.index)

    for row in range(0, len(user_similarity_dataset.index)):
        for col in range(0, len(user_similarity_dataset.columns)):
            sim = (1 - cosine(normalized_dataset.iloc[row, :] +
                   epsilon, normalized_dataset.iloc[col, :] + epsilon))
            if sim == 1 and row != col:
                user_similarity_dataset.iloc[row, col] = 0
            elif sim < 1e-6:
                user_similarity_dataset.iloc[row, col] = 0
            else:
                user_similarity_dataset.iloc[row, col] = sim

    return user_similarity_dataset


def score_prediction(history, similarities, k):
    if len(similarities) < k:
        return 1

    sum_numerator = 0
    sum_denominator = 0

    for i in range(k):
        sum_numerator += (history[i] * similarities[i])
        sum_denominator += similarities[i]

    return sum_numerator / sum_denominator


def user_pos_loc(data_users, column):
    user_purchases = []

    for i in range(len(data_users.index)):
        if data_users.iloc[i, column] > 0:
            user_purchases.append(str(i))

    return user_purchases


def user_value_loc(data_users, pos_sims, column):
    product_top_names = []

    for i in range(len(pos_sims)):
        for j in range(len(data_users.index)):
            if j == int(pos_sims[i]):
                product_top_names.append(data_users.iloc[j, column])

    return product_top_names


def predict_normalized_matrix(user_similarity_dataset, final_dataset, k):
    data_users = final_dataset.drop(columns='user_id')
    predict_normalized_dataset = pd.DataFrame(
        index=final_dataset.index, columns=final_dataset.columns)
    predict_normalized_dataset.iloc[:, :1] = final_dataset.iloc[:, :1]

    for i in range(0, len(predict_normalized_dataset.index)):
        for j in range(1, len(predict_normalized_dataset.columns)):
            if final_dataset.iloc[i, j] == 0:
                user_purchases = user_pos_loc(data_users, j - 1)
                product_top_sims = user_similarity_dataset.loc[i, user_purchases].sort_values(
                    ascending=False)[0:k]
                product_top_names = user_value_loc(
                    data_users, product_top_sims.index.values.tolist(), j - 1)
                predict_normalized_dataset.iloc[i][j] = score_prediction(
                    product_top_names, product_top_sims, k)
            else:
                predict_normalized_dataset.iloc[i][j] = final_dataset.iloc[i][j]

    return predict_normalized_dataset


def get_old_template(user_id, data_template_user_count):
    data_user_selected = data_template_user_count.loc[data_template_user_count['user_id'] == user_id, [
        'template_id', 'counting']]
    get_max_count = data_user_selected['counting'].max()
    data_user_selected.loc[data_template_user_count['counting']
                           == get_max_count, ['template_id']]
    the_most_selected_template = data_user_selected['template_id'].tolist()
    the_most_selected_template.sort()
    return the_most_selected_template


def get_new_template(the_most_selected_template, data_template_new):
    temp = []
    data_template_new = data_template_new.iloc[:, 1:]

    for row in range(len(data_template_new)):
        if int(data_template_new.iloc[row, 0]) in the_most_selected_template:
            if data_template_new.iloc[row, 1] > 0:
                temp.append(data_template_new.iloc[row, 1])
                if data_template_new.iloc[row, 2] > 0:
                    temp.append(data_template_new.iloc[row, 2])
                    if data_template_new.iloc[row, 3] > 0:
                        temp.append(data_template_new.iloc[row, 3])

    if len(temp) > 3:
        temp = rd.sample(temp, k=3)

    return temp


def user_filter(predict_normalized_dataset):
    data_template_user_count = pd.read_csv(
        f'{current_directory}/SOURCE/template_recommend/data/clean_template_user_count.csv', sep=',', encoding='utf-8')
    data_template_new = pd.read_csv(
        f'{current_directory}/DATASET/template_recommend/result/name tags/table_2.csv', sep=',', encoding='utf-8')
    data_recommend = pd.DataFrame(index=predict_normalized_dataset.index, columns=[
                                  'user_id', '1', '2', '3', '4', '5', '6', '7', '8'])
    data_recommend.iloc[0:, 0] = predict_normalized_dataset.iloc[:, 0]

    for row in range(len(predict_normalized_dataset.index)):
        data_recommend.iloc[row, 1:6] = predict_normalized_dataset.iloc[row, 1:].sort_values(
            ascending=False).iloc[1:6, ].index.transpose()
        the_most_selected_template = get_old_template(
            data_recommend.iloc[row, 0], data_template_user_count)
        temp_new = get_new_template(
            the_most_selected_template, data_template_new)

        if len(temp_new) == 0:
            pass
        elif len(temp_new) == 1:
            data_recommend.iloc[row, 6] = temp_new[0]
        elif len(temp_new) == 2:
            data_recommend.iloc[row, 6:8] = temp_new[0:]
        else:
            data_recommend.iloc[row, 6:9] = temp_new[0:]

    data_recommend.to_csv(
        f'{current_directory}/DATASET/template_recommend/result/recommend user/recommend_user_template.csv', sep=',', encoding='utf-8')


def recommend_user_template(namefile):
    final_dataset = convert_dataset(namefile)
    normalized_dataset = normalized_matrix(final_dataset)
    user_similarity_dataset = user_similarity_matrix(normalized_dataset)
    predict_normalized_dataset = predict_normalized_matrix(
        user_similarity_dataset, final_dataset, k)
    user_filter(predict_normalized_dataset)
