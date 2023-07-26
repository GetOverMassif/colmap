# -*- coding: utf-8 -*-

import sys, os
script_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(script_directory))

import argparse
import os
import numpy as np
import sqlite3
from scripts.python.database import *

CAM_DISTORTION_LIST = ['SFW','SLW','SRCW','SRW']   # Dict order

def readCamIntrParams(cameraIntr_path):
    camIntr = {}
    # print("hello")
    with open(cameraIntr_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            cam_name, cam_params = \
                line.split(':')[0], [float(x) for x in line.split(':')[1].split(',')]
            camIntr[cam_name] = tuple(cam_params)
            # print(type(camIntr[cam_name][0]))
    return camIntr

def camTodatabase(database_path, cameraIntr_path):
    camModelDict = {'SIMPLE_PINHOLE': 0,
                    'PINHOLE': 1,
                    'SIMPLE_RADIAL': 2,
                    'RADIAL': 3,
                    'OPENCV': 4,
                    'FULL_OPENCV': 5,
                    'SIMPLE_RADIAL_FISHEYE': 6,
                    'RADIAL_FISHEYE': 7,
                    'OPENCV_FISHEYE': 8,
                    'FOV': 9,
                    'THIN_PRISM_FISHEYE': 10,
                    'OMNI_FISHEYE': 11}

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--database_path", default="database.db")
    # args = parser.parse_args()

    if not os.path.exists(database_path):
        print("ERROR: database path dosen't exist -- please check database.db.")
        return
    print(f"database_path = {database_path}")
    print(f"cameraIntr_path = {cameraIntr_path}")
    # Open the database.
    db = COLMAPDatabase.connect(database_path)

    """ 数据库所包含table: cameras, images, keypoints, descriptors, matches, two_view_geometries """

    db.create_tables()
    
    camIntr = readCamIntrParams(cameraIntr_path)

    cam_info_pairs = db.get_imageCamerasId()

    for camera_id in cam_info_pairs:
        cam = cam_info_pairs[camera_id]
        if cam in CAM_DISTORTION_LIST:
            model = 11
        else:
            model = 0
        params = np.array(camIntr[cam])
        db.update_camera(camera_id, model, params, prior_focal_length=True)

    db.commit()

    db.show_cameras()

    db.close()

if __name__ == "__main__":
    print(f"{'='*78}\nImport CameraIntr into Database\n{'='*78}\n")
    parser = argparse.ArgumentParser(description='需要传入一个database文件路径和一个相机内参文件路径')
    parser.add_argument('database_path', type=str, help='database文件路径')
    parser.add_argument('cameraIntr_path', type=str, help='相机内参文件路径')
    args = parser.parse_args()

    # database_path = f"{args.database_dir}/database.db"
    # cameraIntr_path = f"{args.cameraIntr_dir}/intr_params.txt"
    camTodatabase(args.database_path, args.cameraIntr_path)
