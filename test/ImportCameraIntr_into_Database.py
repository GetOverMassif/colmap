import sys, os
script_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(script_directory))

import argparse
import os
import numpy as np
import sqlite3
from scripts.python.database import *

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
                    'THIN_PRISM_FISHEYE': 10}

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--database_path", default="database.db")
    # args = parser.parse_args()

    if os.path.exists(database_path) == False:
        print("ERROR: database path dosen't exist -- please check database.db.")
        return
    # Open the database.
    db = COLMAPDatabase.connect(database_path)
    db.create_tables()

    # cameraModelId, width, height, (params ... )
    model1, width1, height1, params1 = \
        0, 1024, 768, np.array((1024., 512., 384.))
    model2, width2, height2, params2 = \
        2, 1024, 768, np.array((1024., 512., 384., 0.1))
    
    camera_id1 = db.add_camera(model1, width1, height1, params1)
    camera_id2 = db.add_camera(model2, width2, height2, params2)

    image_id1 = db.add_image("image1.png", camera_id1)
    # image_id2 = db.add_image("image2.png", camera_id1)
    # image_id3 = db.add_image("image3.png", camera_id2)
    # image_id4 = db.add_image("image4.png", camera_id2)

    db.commit()

    db.close()

if __name__ == "__main__":
    data_path = f"/home/nio/文档/colmap/test/data"
    database_path = f"{data_path}/database.db"
    cameraIntr_path = f"{data_path}/intr_params.txt"
    camTodatabase(database_path, cameraIntr_path)


