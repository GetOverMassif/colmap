import os
import argparse

from python.database import *

def main(database_file):
    if os.path.exists(database_file) == False:
        print("ERROR: database path dosen't exist -- please check database.db.")
        return
    # Open the database.
    db = COLMAPDatabase.connect(database_file)
    db.show_two_view_geometries()

    db.commit()
    db.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='需要传入一个database文件路径和一个相机内参文件路径')
    default_database_dir = f'/mnt/dataDisk/reconstructions/20220919T090000_LJ1EFAUU5MG068486/0_allcam_snap'
    parser.add_argument('-d','--database_dir', type=str, default=default_database_dir, help='database文件路径')
    args = parser.parse_args()
    database_file = os.path.join(args.database_dir, 'database.db')
    main(database_file)