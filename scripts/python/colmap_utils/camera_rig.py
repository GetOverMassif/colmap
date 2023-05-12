import numpy as np

class CameraRig:
    def __init__(self) -> None:
        self.rig_cameras_ = {}

    def AddCamera(self, camera_id, rel_qvec, rel_tvec):
        # CHECK(!HasCamera(camera_id));
        # CHECK_EQ(NumSnapshots(), 0);
        rig_camera = RigCamera()
        rig_camera.rel_qvec = rel_qvec
        rig_camera.rel_tvec = rel_tvec
        self.rig_cameras_[camera_id] = rig_camera
    
    def SetRefCameraId():
    
class RigCamera:
    rel_qvec = np.array([1, 0, 0, 0])
    rel_tvec = np.array([0, 0, 0])