'''
Author: jian.li19 jian.li19@nio.com
Date: 2023-06-19 11:13:35
LastEditors: jian.li19 jian.li19@nio.com
LastEditTime: 2023-06-19 16:47:37
FilePath: /colmap/scripts/writeExtrIntoDatabase.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import os
import argparse

from python.database import *
import json
from transform import pose_to_homogeneous_matrix, params_to_Kalibration_matrix

def readCamExtrParams(extr_file):
    if os.path.exists(extr_file) == False:
        print("ERROR: database path dosen't exist -- please check rig_config.json.")
        sys.exit()
    camExtr = {}
    with open(extr_file) as f:
        json_data = json.load(f)
        for camera in json_data[0]['cameras']:
            cam_name = camera['image_prefix'].split('_')[0]
            tx, ty, tz = camera['rel_tvec']
            qw,qx,qy,qz = camera['rel_qvec']
            pose = [tx,ty,tz,qx,qy,qz,qw]
            camExtr[cam_name] = pose_to_homogeneous_matrix(pose)
    return camExtr

def readCamIntrParams(intr_file):
    if os.path.exists(intr_file) == False:
        print("ERROR: database path dosen't exist -- please check intr_params.txt.")
        return
    camIntr = {}
    with open(intr_file) as f:
        lines = f.readlines()
        for line in lines:
            if line[0] == '#' or len(line) < 2:
                continue
            cam_name, cam_params = \
                line.split(':')[0], [float(x) for x in line.split(':')[1].split(',')]
            camIntr[cam_name] = params_to_Kalibration_matrix(cam_params)
    return camIntr

def main(database_file, intr_file, extr_file):
    if os.path.exists(database_file) == False:
        print("ERROR: database path dosen't exist -- please check database.db.")
        return
    # Open the database.
    db = COLMAPDatabase.connect(database_file)
    db.create_tables()
    # 获取所有图像的id和对应的相机名称、时间戳: {image_id: [stamp, cam]}
    imageInfo = db.get_ImageCam_pairs()
    # 读取相机外参信息：{cam_name: T_body2cam}
    camExtr = readCamExtrParams(extr_file)
    # 读取相机内参信息：{cam_name: K_cam}
    camIntr = readCamIntrParams(intr_file)

    # 生成相机对的外参信息：{(cam1,cam2):{'E':E,'F':F}}
    cam_pair_info = {}
    cam_list = list(camExtr.keys())
    for cam1 in cam_list:
        for cam2 in cam_list:
            if cam1 == cam2:
                continue
            key = (cam1, cam2)
            T_21 = camExtr[cam1] @ np.linalg.inv(camExtr[cam2])
            R = np.linalg.inv(T_21[:3,:3])
            tx, ty, tz = T_21[:3,3]
            # qv
            E = R @ np.array([[0, -tz, ty], [tz, 0, -tx], [-ty, tx, 0]])
            F = np.linalg.inv(camIntr[cam2]).T @ E @ np.linalg.inv(camIntr[cam1])
            # tvec = [tx, ty, tz]
            cam_pair_info[key] = {'E':E, 'F':F}

    common_matches = np.array([[i,i] for i in range(20)])
    image_ids = list(imageInfo.keys())
    for img_id1 in image_ids:
        for img_id2 in image_ids:
            if img_id1 == img_id2:
                continue
            if imageInfo[img_id1][0] != imageInfo[img_id2][0] or \
                imageInfo[img_id1][1] == imageInfo[img_id2][1]:
                continue
            # To avoid duplicate pairs.
            if img_id2 < img_id1:
                continue
            info = cam_pair_info[(imageInfo[img_id1][1], imageInfo[img_id2][1])]
            # 首先检查该pair行是否已经存在
            if not db.exist_two_view_geometries(img_id1,img_id2):
                db.add_two_view_geometry(img_id1,img_id2,matches=common_matches,\
                                        F=info['F'],E=info['E'], \
                                        #  H=H,
                                        #  qvec=qvec, tvec=tvec, \
                                        config=2)
            else:
                pass
                # db.update_two_view_geometry(img_id1,img_id2,matches=common_matches,\
                #                         F=info['F'],E=info['E'], \
                #                         #  H=H,
                #                         #  qvec=qvec, tvec=tvec, \
                #                         config=2)
    
    db.commit()
    db.close()
    
    db = COLMAPDatabase.connect(database_file)
    db.show_two_view_geometries()

    db.commit()
    db.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='需要传入一个database文件路径和一个相机内参文件路径')
    default_database_dir = f'/mnt/dataDisk/reconstructions/20220919T090000_LJ1EFAUU5MG068486/0_allcam_snap'
    default_intr_file_path = f'/mnt/dataDisk/save_masks/20220919T090000_LJ1EFAUU5MG068486'
    default_extr_file_path = f'/mnt/dataDisk/save_masks/20220919T090000_LJ1EFAUU5MG068486/0'
    parser.add_argument('-d','--database_dir', type=str, default=default_database_dir, help='database文件路径')
    parser.add_argument('-i','--intr_file_path', type=str, default=default_intr_file_path, help='相机内参文件路径')
    parser.add_argument('-e','--extr_file_path', type=str, default=default_extr_file_path, help='相机外参文件路径')
    args = parser.parse_args()
    database_file = os.path.join(args.database_dir, 'database.db')
    intr_file = os.path.join(args.intr_file_path, 'intr_params.txt')
    extr_file = os.path.join(args.extr_file_path, 'rig_config.json')
    main(database_file, intr_file, extr_file)