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


my_path = os.path.abspath(os.path.dirname(__file__))
path_pattern_json = os.path.join(my_path, '../file_json/patterns.1643275945108.json')
path_frame = os.path.join(my_path, '../frame.png')
path_save_pic = os.path.join(my_path, '../picture_visualize_pattern')

def visualize_pattern(file_path,frame_path):
    f = open(file_path)
    screen_json = json.load(f)
    data = []
    data = struct_data(screen_json,data)
    for pattern in data:
        im = Image.open(path_frame)
        fig, ax = plt.subplots()
        ax.imshow(im)
        name_pattern = pattern['name']
        path_pic = path_save_pic + f"/{name_pattern}"
        num_children = len(pattern['children'])
        list_children = pattern['children']
        x_pos = pattern['x']
        y_pos = pattern['y']
        height = pattern['height']
        width = pattern['width']
        rect = patches.Rectangle(
            (x_pos, y_pos), width,height, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        for item in list_children:
            if len(item) != 0:
                if 'check' in item.keys():
                    x = item['x_parent']
                    y = item['y_parent']
                    height = item['height_parent']
                    width = item['width_parent']
                    rect_container = patches.Rectangle((x, y), width,height, linewidth=1, edgecolor='r', facecolor='none')
                    ax.add_patch(rect_container)
                    for i_comp in item["list_components"]:
                        x_comp = i_comp['x']
                        y_comp = i_comp['y']
                        height = i_comp['height']
                        width = i_comp['width']
                        rect_component = patches.Rectangle((x_comp, y_comp), width,height, linewidth=1, edgecolor='r', facecolor='none')
                        ax.add_patch(rect_component)
                        rx, ry = rect_component.get_xy()
                        cx = rx + rect_component.get_width()/2.0
                        cy = ry + rect_component.get_height()/2.0
                        ax.annotate(i_comp['type'], (cx, cy), color='black',
                                            weight='bold', fontsize=3, ha='center', va='center')
                else:
                    for i_comp in item['list_components']:
                        # print(item)
                        x = i_comp['x']
                        y = i_comp['y']
                        height = i_comp['height']
                        width = i_comp['width']
                        rect_component = patches.Rectangle((x, y), width,height, linewidth=1, edgecolor='r', facecolor='none')
                        ax.add_patch(rect_component)
                        rx, ry = rect_component.get_xy()
                        cx = rx + rect_component.get_width()/2.0
                        cy = ry + rect_component.get_height()/2.0
                        ax.annotate(i_comp['type'], (cx, cy), color='black',
                                                weight='bold', fontsize=3, ha='center', va='center')
            # plt.show()
            plt.savefig(path_pic, bbox_inches='tight')
        plt.close('all')
        # break



visualize_pattern(path_pattern_json,path_frame)