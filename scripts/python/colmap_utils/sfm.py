import argparse
from reconstruction import Reconstruction
import json
import numpy as np

from camera_rig import CameraRig

def PrintHeading1(heading):
  print(f"\n{'='*78}\n",end='')
  print(f"{heading}\n",end='')
  print(f"\n{'='*78}\n",end='')

def ReadCameraRigConfig(rig_config_path, reconstruction, estimate_rig_relative_poses):
  pt = json.load(open(rig_config_path))
  camera_rigs = []
  for rig_config in pt:
    print(type(rig_config))
    print(f"rig_config ref = {rig_config['ref_camera_id']}")
    
    camera_rig = CameraRig()
    image_prefixes = []

    for camera in rig_config['cameras']:
      camera_id = camera['camera_id']
      image_prefixes.append(camera['image_prefix'])
      
      rel_tvec = np.zeros((3,),dtype=np.float32)
      rel_qvec = np.zeros((4,),dtype=np.float32)
      rel_tvec_node = camera['rel_tvec']
      if len(rel_tvec_node)==3:
          rel_tvec = np.array(rel_tvec_node)
      else:
        estimate_rig_relative_poses = True
      rel_qvec_node = camera['rel_qvec']
      if len(rel_qvec_node)==4:
          rel_qvec = np.array(rel_qvec_node)
      else:
        estimate_rig_relative_poses = True
      print(f"  add camera_id {camera_id}")
      camera_rig.AddCamera(camera_id, rel_qvec, rel_tvec)

    camera_rig.SetRefCameraId(rig_config.second.get<int>("ref_camera_id"))

    std::unordered_map<std::string, std::vector<image_t>> snapshots
    for (const auto image_id : reconstruction.RegImageIds()) {
      // std::cout << "reconstruction.RegImageIds() : " << image_id << std::endl;
      const auto& image = reconstruction.Image(image_id);
      for (const auto& image_prefix : image_prefixes) {
        if (StringContains(image.Name(), image_prefix)) {
          const std::string image_suffix =
              StringGetAfter(image.Name(), image_prefix);
          # std::cout << "image_suffix = " << image_suffix << std::endl;
          snapshots[image_suffix].push_back(image_id);
        }
      }
    }

  #   for snapshot in snapshots:
  #     has_ref_camera = False
  #     for image_id in snapshot.second:
  #       image = reconstruction.Image(image_id);
  #       if image.CameraId() == camera_rig.RefCameraId():
  #         has_ref_camera = True

  #     if has_ref_camera:
  #       camera_rig.AddSnapshot(snapshot.second)

  #   camera_rig.Check(reconstruction)
  #   if (estimate_rig_relative_poses):
  #     PrintHeading2("Estimating relative rig poses");
  #     if not camera_rig.ComputeRelativePoses(reconstruction):
  #       print("WARN: Failed to estimate rig poses from reconstruction; ", \
  #             "cannot use rig BA")
  #       return std::vector<CameraRig>()
  #   camera_rigs.append(camera_rig)

  return camera_rigs

def RunRigBundleAdjuster(input_path, output_path, rig_config_path):
  # input_path = ""
  # output_path = ""
  # rig_config_path = ""
  # bool estimate_rig_relative_poses = True
  estimate_rig_relative_poses = False

#   std::cout << "estimate_rig_relative_poses = " << estimate_rig_relative_poses << std::endl

  # RigBundleAdjuster::Options rig_ba_options

  # OptionManager options
  # options.AddRequiredOption("input_path", &input_path)
  # options.AddRequiredOption("output_path", &output_path)
  # options.AddRequiredOption("rig_config_path", &rig_config_path)
  # options.AddDefaultOption("estimate_rig_relative_poses",
  #                          &estimate_rig_relative_poses)
  # options.AddDefaultOption("RigBundleAdjustment.refine_relative_poses",
  #                          &rig_ba_options.refine_relative_poses)
  # options.AddBundleAdjustmentOptions()
  # options.Parse(argc, argv)

  reconstruction = Reconstruction()
  reconstruction.Read(input_path)

  PrintHeading1("Camera rig configuration")

  camera_rigs = ReadCameraRigConfig(rig_config_path, reconstruction,
                                         estimate_rig_relative_poses)

  # config = BundleAdjustmentConfig()
  # for i in range(len(camera_rigs)):
  #   camera_rig = camera_rigs[i]
  #   # PrintHeading2(StringPrintf("Camera Rig %d", i + 1))
  #   # std::cout << StringPrintf("Cameras: %d", camera_rig.NumCameras())
  #   #           << std::endl
  #   # std::cout << StringPrintf("Snapshots: %d", camera_rig.NumSnapshots())
  #   #           << std::endl

  #   # Add all registered images to the bundle adjustment configuration.
  #   for image_id in reconstruction.RegImageIds():
  #     config.AddImage(image_id)

  # PrintHeading1("Rig bundle adjustment")

  # BundleAdjustmentOptions ba_options = *options.bundle_adjustment
  # ba_options.solver_options.minimizer_progress_to_stdout = True
  # RigBundleAdjuster bundle_adjuster(ba_options, rig_ba_options, config)
  # CHECK(bundle_adjuster.Solve(&reconstruction, &camera_rigs))

  # reconstruction.Write(output_path)

  # return EXIT_SUCCESS

if __name__=="__main__":
  clip_name = "20211221T104518_8N1800__1640054864.000000__1640054884.000000"
  nio_data = "/home/nio/data/colmap/NIO_data"
  input_path = f"{nio_data}/{clip_name}/7/WITH_EXTRINSICS/sparse/1"
  output_path = f"{nio_data}/{clip_name}/7/WITH_EXTRINSICS/sparse_rig_ba/1"
  rig_config_path = f"{nio_data}/{clip_name}/7/WITH_EXTRINSICS/rig_config_b2c_1.json"
  RunRigBundleAdjuster(input_path, output_path, rig_config_path)