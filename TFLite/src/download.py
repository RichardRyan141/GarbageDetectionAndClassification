import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Download dataset from Kaggle.")
    parser.add_argument('--directory', type=str, required=True, help="Directory to store dataset")
    parser.add_argument('--username', type=str, required=True, help="Kaggle username")
    parser.add_argument('--key', type=str, required=True, help="Kaggle API key")
    args = parser.parse_args()

    os.environ['KAGGLE_USERNAME'] = args.username
    os.environ['KAGGLE_KEY'] = args.key

    if not os.path.exists(args.directory):
        os.makedirs(args.directory)

    download_command = [
        "kaggle", "datasets", "download", "--dataset", "kneroma/tacotrashdataset"
    ]
    subprocess.run(download_command, check=True)

    unzip_command = [
        "unzip", "-q", "tacotrashdataset.zip", "-d", args.directory
    ]
    subprocess.run(unzip_command, check=True)

if __name__ == "__main__":
    main()
