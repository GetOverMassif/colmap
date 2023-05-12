import os
import os.path as osp
import sys
from loguru import logger


sys.path.append("/home/nio/文档/colmap")

from scripts.python.read_write_model import *

class Reconstruction:
    def __init__(self) -> None:
        self.correspondence_graph_ = None
        self.num_added_points3D_ = 0
    
    def Read(self, path):
        if osp.exists(osp.join(path, "cameras.bin")) and \
           osp.exists(osp.join(path, "images.bin")) and \
           osp.exists(osp.join(path, "points3D.bin")):
            self.ReadBinary(path)
        elif osp.exists(osp.join(path, "cameras.txt")) and \
             osp.exists(osp.join(path, "images.txt")) and \
             osp.exists(osp.join(path, "points3D.txt")):
            self.ReadText(path)
        else:
            logger.error(f"cameras, images, points3D files do not exist at {path}")
    
    def ReadBinary(self, path):
        self.cameras_ = read_cameras_binary(osp.join(path, "cameras.bin"))
        self.images_ = read_images_binary(osp.join(path, "images.bin"))
        self.points3D_ = read_points3D_binary(osp.join(path, "points3D.bin"))
    
    def ReadText(self, path):
        self.cameras_ = read_cameras_text(osp.join(path, "cameras.txt"))
        self.images_ = read_images_text(osp.join(path, "images.txt"))
        self.points3D_ = read_points3D_text(osp.join(path, "points3D.txt"))