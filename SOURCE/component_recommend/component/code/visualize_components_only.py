import pandas as pd
import numpy as np
import json
from distance_feature_extractor import flatten_data, screen_parser, remove_container_component
from pattern import struct_data
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image


def visualize_screen(file_json, mode, frame, path_save_pic):
    im = Image.open(frame)
    fig, ax = plt.subplots()
    ax.imshow(im)
    f = open(file_json)
    screen_json = json.load(f)
    screen_flatten = []
    if mode == 0:
        flatten_data(screen_json, screen_flatten)
    else:
        flatten_data(screen_json, screen_flatten)
        remove_container_component(screen_flatten)
    for component in screen_flatten:
        x_pos = component['data']['position']['x']
        y_pos = component['data']['position']['y']
        type_component = component['type']
        rect = patches.Rectangle(
            (x_pos, y_pos), 100, 50, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        rx, ry = rect.get_xy()
        cx = rx + rect.get_width()/2.0
        cy = ry + rect.get_height()/2.0
        ax.annotate(type_component, (cx, cy), color='black',
                    weight='bold', fontsize=3, ha='center', va='center')
    # plt.savefig(path_save_pic, bbox_inches='tight')
    plt.show()


file_json = '/Users/MinhHieu/Documents/Recommened-system/visily_json/100000.json'
path_frame = '/Users/MinhHieu/Documents/Recommened-system/component/frame.png'
path_save_pic = '/Users/MinhHieu/Documents/Recommened-system/component/image_test_screen/test.png'
visualize_screen(file_json, 1, path_frame, path_save_pic)


# im = Image.open(path_frame)
# fig, ax = plt.subplots()
# ax.imshow(im)
# f = open('/Users/MinhHieu/Documents/Recommened-system/lmhieu/patterns.1643275945108.json')
# screen_json = json.load(f)
# data = []
# data = struct_data(screen_json,data)
# im = Image.open(path_frame)
# fig, ax = plt.subplots()
# ax.imshow(im)
# f = open(file_json)
# screen_json = json.load(f)
# screen_flatten = []
# flatten_data(screen_json, screen_flatten)
# remove_container_component(screen_flatten)
# print(screen_flatten)
# print(data[1])