'''
Author: jian.li19 jian.li19@nio.com
Date: 2023-06-15 14:29:31
LastEditors: jian.li19 jian.li19@nio.com
LastEditTime: 2023-06-19 13:31:14
FilePath: /colmaptomesh/test/util/transform.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import numpy as np
from scipy.spatial.transform import Rotation

def pose_to_homogeneous_matrix(pose):
    """ 将pose转换为齐次变换矩阵
        - pose : [tx,ty,tz,qx,qy,qz,qw]
        —> homogeneous_matrix : T_4×4
    """
    tx, ty, tz, qx, qy, qz, qw = pose
    translation = np.array([tx, ty, tz])
    rotation = Rotation.from_quat([qx, qy, qz, qw])
    rotation_matrix = rotation.as_matrix()
    homogeneous_matrix = np.eye(4)
    homogeneous_matrix[:3, :3] = rotation_matrix
    homogeneous_matrix[:3, 3] = translation
    return homogeneous_matrix

def params_to_Kalibration_matrix(params):
    """ 将相机内参转换为内参矩阵
        - params : [focal_length, cx, cy]
        —> Kalibration_matrix : K_3×3
    """
    fx, cx, cy = params
    Kalibration_matrix = np.array([[fx, 0, cx],
                                   [0, fx, cy],
                                   [0, 0, 1]])
    return Kalibration_matrix