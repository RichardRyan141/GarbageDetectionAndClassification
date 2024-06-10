import argparse
import os
import subprocess
import shutil
from roboflow import Roboflow
import sys

def main():
    parser = argparse.ArgumentParser(description="Download dataset from Kaggle or Roboflow.")
    parser.add_argument('--source', type=str, required=True, choices=['roboflow', 'kaggle'], help="Download source: 'roboflow' or 'kaggle'")
    parser.add_argument('--directory', type=str, required=True, help="Directory to store dataset")
    parser.add_argument('--kaggle_username', type=str, required=False, help="Kaggle username")
    parser.add_argument('--kaggle_key', type=str, required=False, help="Kaggle API key")
    parser.add_argument('--roboflow_key', type=str, required=False, help="Roboflow API key")
    args = parser.parse_args()
    
    if os.path.exists("datasets"):
        shutil.rmtree("datasets")
    os.makedirs("datasets")

    directory = os.path.join("datasets", args.directory)

    if args.source == "kaggle":
        if not args.kaggle_username:
            print("If downloading from kaggle, kaggle_username must be used")
            sys.exit(1)
        if not args.kaggle_key:
            print("If downloading from kaggle, kaggle_key must be used")
            sys.exit(1)
        os.environ['KAGGLE_USERNAME'] = args.kaggle_username
        os.environ['KAGGLE_KEY'] = args.kaggle_key

        os.makedirs(directory)

        download_command = [
            "kaggle", "datasets", "download", "--dataset", "kneroma/tacotrashdataset"
        ]
        subprocess.run(download_command, check=True)

        unzip_command = [
            "unzip", "-q", "tacotrashdataset.zip", "-d", directory
        ]
        subprocess.run(unzip_command, check=True)
    elif args.source == "roboflow":
        if not args.roboflow_key:
            print("If downloading from roboflow, roboflow_key must be used")
            sys.exit(1)

        rf = Roboflow(api_key=args.roboflow_key)
        project = rf.workspace("divya-lzcld").project("taco-mqclx")
        version = project.version(3)
        dataset = version.download("yolov9")

        shutil.move("TACO-3", directory)


if __name__ == "__main__":
    main()
