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

#ifndef COLMAP_SRC_CONTROLLERS_INCREMENTAL_MAPPER_H_
#define COLMAP_SRC_CONTROLLERS_INCREMENTAL_MAPPER_H_

#include "base/reconstruction_manager.h"
#include "sfm/incremental_mapper.h"
#include "util/threading.h"

namespace colmap {

struct IncrementalMapperOptions {
 public:
  // The minimum number of matches for inlier matches to be considered.
  // 被认为是内点匹配的最小匹配数
  int min_num_matches = 15;

  // Whether to ignore the inlier matches of watermark image pairs.
  // 是否忽略水印图像对的内点匹配
  bool ignore_watermarks = false;

  // Whether to reconstruct multiple sub-models.
  // 是否重建多个子模型
  bool multiple_models = true;

  // The number of sub-models to reconstruct.
  // 重建的子模型数量
  int max_num_models = 50;

  // The maximum number of overlapping images between sub-models. If the
  // current sub-models shares more than this number of images with another
  // model, then the reconstruction is stopped.
  // 子模型之间的最大重叠图像数。如果当前子模型与另一个模型共享的图像超过此数目，则停止重建。
  int max_model_overlap = 20;

  // The minimum number of registered images of a sub-model, otherwise the
  // sub-model is discarded.
  // 子模型的最小注册图像数，否则子模型将被丢弃。
  int min_model_size = 10;

  // The image identifiers used to initialize the reconstruction. Note that
  // only one or both image identifiers can be specified. In the former case,
  // the second image is automatically determined.
  // 用于初始化重建的图像标识符。请注意，只能指定一个或两个图像标识符。在前一种情况下，第二个图像会自动确定。
  int init_image_id1 = -1;
  int init_image_id2 = -1;

  // The number of trials to initialize the reconstruction.
  // 初始化重建的尝试次数
  int init_num_trials = 200;

  // Whether to extract colors for reconstructed points.
  // 是否提取重建点的颜色
  bool extract_colors = true;

  // The number of threads to use during reconstruction.
  // 重建过程中使用的线程数
  int num_threads = -1;

  // Thresholds for filtering images with degenerate intrinsics.
  // 用于过滤具有退化内参的图像的阈值
  double min_focal_length_ratio = 0.1;
  double max_focal_length_ratio = 10.0;
  double max_extra_param = 1.0;

  // Which intrinsic parameters to optimize during the reconstruction.
  // 重建过程中优化哪些内参
  bool ba_refine_focal_length = true;
  bool ba_refine_principal_point = false;
  bool ba_refine_extra_params = true;

  // The minimum number of residuals per bundle adjustment problem to
  // enable multi-threading solving of the problems.
  // 每个Bundle Adjustment问题启用多线程求解的最小残差数
  int ba_min_num_residuals_for_multi_threading = 50000;

  // The number of images to optimize in local bundle adjustment.
  // 局部Bundle Adjustment中要优化的图像数
  int ba_local_num_images = 6;

  // Ceres solver function tolerance for local bundle adjustment
  // 局部Bundle Adjustment的Ceres求解器函数容差
  double ba_local_function_tolerance = 0.0;

  // The maximum number of local bundle adjustment iterations.
  // 局部Bundle Adjustment的最大迭代次数
  int ba_local_max_num_iterations = 25;

  // The growth rates after which to perform global bundle adjustment.
  // 执行全局Bundle Adjustment的增长率
  double ba_global_images_ratio = 1.1;
  double ba_global_points_ratio = 1.1;
  int ba_global_images_freq = 500;
  int ba_global_points_freq = 250000;

  // Ceres solver function tolerance for global bundle adjustment
  // 全局Bundle Adjustment的Ceres求解器函数容差
  double ba_global_function_tolerance = 0.0;

  // The maximum number of global bundle adjustment iterations.
  // 全局Bundle Adjustment的最大迭代次数
  int ba_global_max_num_iterations = 50;

  // The thresholds for iterative bundle adjustment refinements.
  // 迭代Bundle Adjustment细化的阈值
  int ba_local_max_refinements = 2;
  double ba_local_max_refinement_change = 0.001;
  int ba_global_max_refinements = 5;
  double ba_global_max_refinement_change = 0.0005;

  // Path to a folder with reconstruction snapshots during incremental
  // reconstruction. Snapshots will be saved according to the specified
  // frequency of registered images.
  // 增量重建过程中重建快照的文件夹路径。快照将根据注册图像的指定频率保存。
  std::string snapshot_path = "";
  int snapshot_images_freq = 0;

  // Which images to reconstruct. If no images are specified, all images will
  // be reconstructed by default.
  // 重建哪些图像。如果未指定图像，则默认情况下将重建所有图像。
  std::unordered_set<std::string> image_names;

  // If reconstruction is provided as input, fix the existing image poses.
  // 如果重建作为输入提供，则固定现有图像姿势。
  bool fix_existing_images = false;

  IncrementalMapper::Options Mapper() const;
  IncrementalTriangulator::Options Triangulation() const;
  BundleAdjustmentOptions LocalBundleAdjustment() const;
  BundleAdjustmentOptions GlobalBundleAdjustment() const;

  bool Check() const;

 private:
  friend class OptionManager;
  friend class MapperGeneralOptionsWidget;
  friend class MapperTriangulationOptionsWidget;
  friend class MapperRegistrationOptionsWidget;
  friend class MapperInitializationOptionsWidget;
  friend class MapperBundleAdjustmentOptionsWidget;
  friend class MapperFilteringOptionsWidget;
  friend class ReconstructionOptionsWidget;
  IncrementalMapper::Options mapper;
  IncrementalTriangulator::Options triangulation;
};

// Class that controls the incremental mapping procedure by iteratively
// initializing reconstructions from the same scene graph.
class IncrementalMapperController : public Thread {
 public:
  enum {
    INITIAL_IMAGE_PAIR_REG_CALLBACK,
    NEXT_IMAGE_REG_CALLBACK,
    LAST_IMAGE_REG_CALLBACK,
  };

  IncrementalMapperController(const IncrementalMapperOptions* options,
                              const std::string& image_path,
                              const std::string& database_path,
                              ReconstructionManager* reconstruction_manager);
  void SetLogFilePtr(std::ofstream* log_file_ptr) {
    log_file_ptr_ = log_file_ptr;
  };

 private:
  void Run();
  bool LoadDatabase();
  void Reconstruct(const IncrementalMapper::Options& init_mapper_options);

  std::ofstream* log_file_ptr_;
  const IncrementalMapperOptions* options_;
  const std::string image_path_;
  const std::string database_path_;
  ReconstructionManager* reconstruction_manager_;
  DatabaseCache database_cache_;
};

// Globally filter points and images in mapper.
size_t FilterPoints(const IncrementalMapperOptions& options,
                    IncrementalMapper* mapper);
size_t FilterImages(const IncrementalMapperOptions& options,
                    IncrementalMapper* mapper);

// Globally complete and merge tracks in mapper.
size_t CompleteAndMergeTracks(const IncrementalMapperOptions& options,
                              IncrementalMapper* mapper);

}  // namespace colmap

#endif  // COLMAP_SRC_CONTROLLERS_INCREMENTAL_MAPPER_H_
