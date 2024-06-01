import os
import requests
from PIL import Image
import sys
import shutil
import json
from concurrent.futures import ThreadPoolExecutor
import argparse
from io import BytesIO
import gdown
import subprocess

def download_image(image):
    file_name = image['file_name'].split('/')[1].split('.jpg')[0]
    image_url = image['flickr_640_url']
    file_path = image['file_path']

    if not os.path.isfile(file_path):
      if image_url is None:
        image_url = image['flickr_url']
      response = requests.get(image_url)
      img = Image.open(BytesIO(response.content))
      if img.size != (480,640):
        img = img.resize((480,640))
      if img.mode == 'RGBA':
          img = img.convert('RGB')
      try:
          img.save(file_path, exif=img.info["exif"])
      except:
          img.save(file_path)

def resize_bbox(bbox, original_size, new_size):
    original_width, original_height = original_size
    x, y, width, height = bbox

    width_scale = new_size[0] / original_width
    height_scale = new_size[1] / original_height

    new_x = x * width_scale
    new_y = y * height_scale
    new_width = width * width_scale
    new_height = height * height_scale

    x_min = new_x
    y_min = new_y
    x_max = new_x + new_width
    y_max = new_y + new_height

    return [x_min, y_min, x_max, y_max]

def process_json(json_path, directory, dataset_source, max_workers):
    if dataset_source == "official":
        data_dir = os.path.join(directory, "official")
        if (json_path is None):
            print("Downloading official.json from TACO Github (latest update: 13 Feb 2023)")
            id = "1TzxsRbWdp3y8Mr6oiRQqynDo_MqkOaQi"
            json_path = "official.json"
            gdown.download(id=id, output=json_path)
    else:
        data_dir = os.path.join(directory, "unofficial")
        if (json_path is None):
            print("Downloading unofficial.json from TACO Github (latest update: 19 Dec 2019)")
            id = "11tzOy41twUboqYDZx0-AnPNDsGq2A3cn"
            json_path = "unofficial.json"
            gdown.download(id=id, output=json_path)
    
    with open(json_path, "r") as f:
        data = json.loads(f.read())
        nr_images = len(data['images'])
        file_names = {}
        image_sizes = {}

        for i in range(nr_images):
            image = data['images'][i]
            file_name = image['file_name'].split('/')[0] + "_" + image['file_name'].split('/')[1].split('.')[0]
            id = image['id']
            file_names[id] = file_name
            image_sizes[id] = (image['width'], image['height'])
            data['images'][i]['file_path'] = os.path.join(data_dir, "images", file_name + ".jpg")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(download_image, image) for image in data['images']]
            for future in futures:
                future.result()

        nr_anno = len(data['annotations'])
        labels = [[] for _ in range(nr_images)]
        for i in range(nr_anno):
            annotation = data['annotations'][i]
            category_id = annotation['category_id']
            bbox = annotation['bbox']
            image_id = annotation['image_id']

            new_bbox = resize_bbox(bbox, image_sizes[image_id], (480, 640))
            labels[image_id].append([category_id, new_bbox[0], new_bbox[1], new_bbox[2], new_bbox[3]])

        for image_id, annotation_list in enumerate(labels):
            file_path = os.path.join(data_dir, "labels", f"{file_names[image_id]}.txt")
            with open(file_path, "w") as file:
                for annotation in annotation_list:
                    line = " ".join(map(str, annotation)) + "\n"
                    file.write(line)

def download_from_drive(gdriveID, data_dir):
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)

    if not os.path.exists("data.zip"):
        subprocess.run(['gdown', '--id', gdriveID, '--output', "data.zip"], check=True)

        subprocess.run(['unzip', '-q', "data.zip", '-d', data_dir], check=True)

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    parser = argparse.ArgumentParser(description="Process images and annotations.")
    parser.add_argument('--source', type=str, required=True, choices=['JSON', 'drive'], help="Download source: 'JSON' or 'drive'")
    parser.add_argument('--directory', type=str, required=True, help="Directory to store dataset")
    parser.add_argument('--officialJSON', type=str, required=False, help="Official TACO dataset JSON or a JSON of similar format")
    parser.add_argument('--unofficialJSON', type=str, required=False, help="Unofficial TACO dataset JSON or a JSON of similar format")
    parser.add_argument('--maxWorker', type=int, required=False, default=8, help="Number of concurrent workers to speed up download")
    parser.add_argument('--GDriveID', type=str, required=False, default="sFefuUtI7ZuaA7rLPb_nlzCpy96l", help="ID of a Google Drive zip of dataset")
    parser.add_argument('--OfficialDL', type=str2bool, required=False, default=True, help="Whether to download the official dataset (only for JSON download)")
    parser.add_argument('--UnofficialDL', type=str2bool, required=False, default=True, help="Whether to download the unofficial dataset (only for JSON download)")

    args = parser.parse_args()
    source = args.source
    data_dir = args.directory
    official_json = args.officialJSON
    unofficial_json = args.unofficialJSON
    maxWorker = args.maxWorker
    gdriveID = args.GDriveID
    officialDL = args.OfficialDL
    unofficialDL = args.UnofficialDL

    if os.path.exists(data_dir):
        shutil.rmtree(data_dir, ignore_errors=True)

    os.makedirs(data_dir)
    os.makedirs(os.path.join(data_dir, "official", "images"))
    os.makedirs(os.path.join(data_dir, "official", "labels"))
    os.makedirs(os.path.join(data_dir, "unofficial", "images"))
    os.makedirs(os.path.join(data_dir, "unofficial", "labels"))

    if source == "JSON":
        if (not officialDL) and (not unofficialDL):
            print("If downloading from JSON, both officialDL and unofficialDL cannot be both False at the same time")
            sys.exit(1)
        if (officialDL):
            if not (official_json is None) and (not os.path.exists(official_json)):
                print(f"Official json data not found, please make sure the path ({official_json}) is correct")
            print("Downloading official data from JSON")
            process_json(official_json, data_dir, "official", maxWorker)
        if (unofficialDL):
            if not (unofficial_json is None) and (not os.path.exists(unofficial_json)):
                print(f"Unofficial json data not found, please make sure the path ({unofficial_json}) is correct")
            print("Downloading unofficial data from JSON")
            process_json(unofficial_json, data_dir, "unofficial", maxWorker)
        print("Download completed")
    elif source == "drive":
        print("Downloading from Google Drive")
        download_from_drive(gdriveID, data_dir)
        print("Download completed")
    else:
        print("Invalid source. Please use 'JSON' or 'drive'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
