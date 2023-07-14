// Copyright (c) 2023, ETH Zurich and UNC Chapel Hill.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//     * Neither the name of ETH Zurich and UNC Chapel Hill nor the names of
//       its contributors may be used to endorse or promote products derived
//       from this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//
// Author: Johannes L. Schoenberger (jsch-at-demuc-dot-de)

#ifndef COLMAP_SRC_BASE_IMAGE_READER_H_
#define COLMAP_SRC_BASE_IMAGE_READER_H_

#include <unordered_set>

#include "base/database.h"
#include "util/bitmap.h"
#include "util/threading.h"

namespace colmap {

struct ImageReaderOptions {
  // Path to database in which to store the extracted data.
  std::string database_path = "";

  // Root path to folder which contains the images.
  std::string image_path = "";

  // Optional root path to folder which contains image masks. For a given image,
  // the corresponding mask must have the same sub-path below this root as the
  // image has below image_path. The filename must be equal, aside from the
  // added extension .png. For example, for an image image_path/abc/012.jpg, the
  // mask would be mask_path/abc/012.jpg.png. No features will be extracted in
  // regions where the mask image is black (pixel intensity value 0 in
  // grayscale).
  // 可选项，包含图像掩码的文件夹的根路径。对于给定的图像，相应的掩码必须具有与图像相同的子路径，该子路径在此根下与图像相同。
  std::string mask_path = "";

  // Optional list of images to read. The list must contain the relative path
  // of the images with respect to the image_path.
  std::vector<std::string> image_list;

  // Name of the camera model.
  // 相机模型的名称
  std::string camera_model = "SIMPLE_RADIAL";

  // Whether to use the same camera for all images.
  // 是否对所有图像使用相同的相机模型
  bool single_camera = false;

  // Whether to use the same camera for all images in the same sub-folder.
  // 是否对同一子文件夹中的所有图像使用相同的相机模型
  bool single_camera_per_folder = false;

  // Whether to use a different camera for each image.
  // 是否对每个图像使用不同的相机模型
  bool single_camera_per_image = false;

  // Whether to explicitly use an existing camera for all images. Note that in
  // this case the specified camera model and parameters are ignored.
  // 是否对所有图像显式使用现有相机。请注意，在这种情况下，忽略指定的相机模型和参数。
  int existing_camera_id = kInvalidCameraId;

  // Manual specification of camera parameters. If empty, camera parameters
  // will be extracted from EXIF, i.e. principal point and focal length.
  // 手动指定相机参数。如果为空，则将从EXIF中提取相机参数，即主点和焦距。
  std::string camera_params = "";

  // If camera parameters are not specified manually and the image does not
  // have focal length EXIF information, the focal length is set to the
  // value `default_focal_length_factor * max(width, height)`.
  // 如果没有手动指定相机参数，并且图像没有焦距EXIF信息，则将焦距设置为值`default_focal_length_factor * max(width, height)`。
  double default_focal_length_factor = 1.2;

  // Optional path to an image file specifying a mask for all images. No
  // features will be extracted in regions where the mask is black (pixel
  // intensity value 0 in grayscale).
  // 可选项，指定所有图像的掩码的图像文件的路径。在掩码为黑色（灰度中的像素强度值为0）的区域中不会提取特征。
  std::string camera_mask_path = "";

  bool Check() const;
};

// Recursively iterate over the images in a directory. Skips an image if it
// already exists in the database. Extracts the camera intrinsics from EXIF and
// writes the camera information to the database.
class ImageReader {
 public:
  enum class Status {
    FAILURE,
    SUCCESS,
    IMAGE_EXISTS,
    BITMAP_ERROR,
    CAMERA_SINGLE_DIM_ERROR,
    CAMERA_EXIST_DIM_ERROR,
    CAMERA_PARAM_ERROR
  };

  ImageReader(const ImageReaderOptions& options, Database* database);

  Status Next(Camera* camera, Image* image, Bitmap* bitmap, Bitmap* mask);
  size_t NextIndex() const;
  size_t NumImages() const;

 private:
  // Image reader options.
  ImageReaderOptions options_;
  Database* database_;
  // Index of previously processed image.
  size_t image_index_;
  // Previously processed camera.
  Camera prev_camera_;
  std::unordered_map<std::string, camera_t> camera_model_to_id_;
  // Names of image sub-folders.
  std::string prev_image_folder_;
  std::unordered_set<std::string> image_folders_;
};

}  // namespace colmap

#endif  // COLMAP_SRC_BASE_IMAGE_READER_H_
