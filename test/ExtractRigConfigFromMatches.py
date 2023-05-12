# -*- coding: utf-8 -*-

import sys, os
script_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(script_directory))

import argparse
import os
import numpy as np
import sqlite3
from scripts.python.database import *
import json
import networkx as nx

def searchMatchCams(db):
    cam_list_in_snapshot = set()
    image_cam_pairs = db.get_ImageCam_pairs()
    matched_pairs = db.get_two_view_geometries()

    cams_pair = []
    for [img1, img2] in matched_pairs:
        # if img1_stamp = img2_stamp, cam_list_in_snapshot.append(cam_name)
        if image_cam_pairs[img1][0] == image_cam_pairs[img2][0] :
            cam1, cam2 = image_cam_pairs[img1][1], image_cam_pairs[img2][1]
            if set({cam1,cam2}) not in cams_pair:
                cams_pair.append(set({cam1,cam2}))
                cam_list_in_snapshot.add(cam1)
                cam_list_in_snapshot.add(cam2)
                print(f"{cam1}/{image_cam_pairs[img1][0]} - {cam2}/{image_cam_pairs[img2][0]}")

    print(f"\nraw_cam_pairs = {cams_pair}")
    G = nx.Graph()
    for node in cam_list_in_snapshot:
        G.add_node(node)
    for cam1, cam2 in cams_pair:
        G.add_edge(cam1, cam2)
        
    cams_pair = []

    for c in nx.connected_components(G):
        subgraph = G.subgraph(c).copy()
        while len(subgraph.nodes()) > 1:
            max_degree , max_node = -1, -1
            nodes = sorted(subgraph.nodes())
            for node in nodes:
                if subgraph.degree(node) > max_degree or (subgraph.degree(node) == max_degree and node < max_node):
                    max_node = node
                    max_degree = subgraph.degree(max_node)
            pairs = [max_node]
            neighbor_nodes = list(subgraph.neighbors(max_node))
            for node in neighbor_nodes:
                pairs.append(node)
                subgraph.remove_node(node)
            subgraph.remove_node(max_node)
            cams_pair.append(pairs)
    print(f"\nnew_cam_pairs = {cams_pair}")

def extractFromMatched(work_dir):

    database_path = f"{work_dir}/database.db"
    rig_config_raw_path = f"{work_dir}/rig_config_raw.json"

    if os.path.exists(database_path) == False:
        print("ERROR: database path dosen't exist -- please check database.db.")
        return
    
    f = open(rig_config_raw_path, 'r')
    json_data = json.load(f)
    f.close()
    cams_info = json_data[0]['cameras']
    cams_info_dic = {}

    for cam_info in cams_info:
        cam = cam_info['image_prefix'].split('_')[0]
        cams_info_dic[cam] = cam_info
    
    # Open the database.
    db = COLMAPDatabase.connect(database_path)

    """ 数据库所包含table: cameras, images, keypoints, descriptors, matches, two_view_geometries """

    db.create_tables()

    searchMatchCams(db)

    # 需要得到一个相机编号与相机名称的对应关系: id -> name
    cams_id2name = db.get_imageCamerasId()
    # cams_name2id = {}
    # for id in cams_id2name.keys():
    #     cams_name2id[cams_id2name[id]] = id


    sparse_dir = f"{work_dir}/sparse"
    sparse_nums = sorted(os.listdir(sparse_dir))

    for sparse_id in sparse_nums:
        bin_path = f"{sparse_dir}/{sparse_id}"
        txt_path = f"{sparse_dir}/{sparse_id}/txt"
        rig_config_path = f"{work_dir}/rig_config_{sparse_id}.json"
        os.system(f"mkdir -p {txt_path}")
        os.system(f"colmap model_converter --input_path {bin_path} --output_path {txt_path} --output_type TXT")

        cameras_txt = f"{txt_path}/cameras.txt"
        with open(cameras_txt, 'r') as f:
            cams_ids_txt = []
            line = f.readline()
            while line != "" and line[0] == '#':
                line = f.readline()
            while line != "":
                cams_ids_txt.append(int(line.split(' ')[0]))
                line = f.readline()
        
        cams_ids_txt = sorted(cams_ids_txt)

        new_json_data = []

        rig_info = {}
        rig_info['ref_camera_id'] = cams_ids_txt[0]
        rig_info['cameras'] = []
        for cam_id in cams_ids_txt:
            cam_info = cams_info_dic[cams_id2name[cam_id]]
            cam_info['camera_id'] = cam_id
            rig_info['cameras'].append(cam_info)

        new_json_data.append(rig_info)
        json_str = json.dumps(new_json_data, indent = 4, separators=(',', ': '))
        f = open(rig_config_path, 'w')
        f.write(json_str)
        f.close()

    db.commit()
    db.close()

if __name__ == "__main__":
    print(f"{'='*78}\nExtract RigConfig From Matches\n{'='*78}\n")
    parser = argparse.ArgumentParser(description='需要传入一个路径, 包含database文件和相机外参配置文件')
    parser.add_argument('work_dir', type=str, help='database文件路径')
    args = parser.parse_args()

    # database_dir = f"/home/nio/data/colmap/NIO_data/20211221T165619_8N1800__1640077220.000000__1640077240.000000/0/new_ws"
    # rig_config_path = f"/home/nio/data/save_masks/20211221T165619_8N1800__1640077220.000000__1640077240.000000"


    extractFromMatched(args.work_dir)
