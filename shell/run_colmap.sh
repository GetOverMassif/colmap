
###
 # @Author: jian.li19 jian.li19@nio.com
 # @Date: 2023-06-15 21:06:11
 # @LastEditors: jian.li19 jian.li19@nio.com
 # @LastEditTime: 2023-06-19 18:03:58
 # @FilePath: /colmap/shell/run_colmap.sh
 # @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%A
### 
# 

# database_path=$1
# image_path=$2

COLAMP_PATH=/home/nio/文档/colmap

database_path=/mnt/dataDisk/reconstructions/20220919T090000_LJ1EFAUU5MG068486/0_allcam_snap
all_image_dir=/mnt/dataDisk/save_masks/20220919T090000_LJ1EFAUU5MG068486
obj_path=/mnt/dataDisk/save_masks/20220919T090000_LJ1EFAUU5MG068486/0
image_path=/mnt/dataDisk/save_masks/20220919T090000_LJ1EFAUU5MG068486/0/camera_full_undistortion

num_threads=10

# rm -r $database_path/*

# 特征提取
colmap feature_extractor \
    --database_path $database_path/database.db \
    --image_path $image_path \
    --ImageReader.camera_model PINHOLE \
    --ImageReader.single_camera_per_folder 1 \
    --SiftExtraction.num_threads $num_threads \
    --SiftExtraction.use_gpu 0 \
    # --ImageReader.mask_path 
    # --ImageReader.camera_mask_path

# 相机内参导入
python $COLAMP_PATH/test/ImportCameraIntr_into_Database.py $database_path $all_image_dir

python $COLAMP_PATH/scripts/writeTwoViewGeometryIntoDatabase.py -d $database_path -i $all_image_dir -e $obj_path

colmap sequential_matcher \
    --database_path $database_path/database.db \
    --SiftMatching.num_threads $num_threads \
    --SequentialMatching.multi_cam 1 \
    --SiftMatching.use_gpu 0 \
    --SiftMatching.guided_matching 1 \
    --SiftMatching.max_error 10 \
    --SequentialMatching.overlap 10 \
    --SequentialMatching.quadratic_overlap 0 \
    --SequentialMatching.loop_detection 1 \
    --SequentialMatching.vocab_tree_path /mnt/dataDisk/colmap/VocabTree/vocab_tree_flickr100K_words1M.bin

mkdir -p $database_path/sparse

colmap mapper \
    --database_path $database_path/database.db \
    --image_path $image_path \
    --output_path $database_path/sparse \
    --Mapper.extract_colors 1 \
    --Mapper.num_threads $num_threads

# 尺度恢复

mv 
python $COLAMP_PATH/test/ExtractRigConfigFromMatches.py \


    

