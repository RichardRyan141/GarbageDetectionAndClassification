import argparse
import os
import subprocess
import random
import shutil
import sys
import json
import yaml

def move_image_and_labels(directory, image_list, split_type, split_directory):
    for img_name in image_list:
        orig_img_path = os.path.join(directory, "images", img_name)
        dest_img_path = os.path.join(split_directory, split_type, "images", img_name)

        label_name = img_name.replace(".jpg", ".txt")
        orig_label_path = os.path.join(directory, "labels", label_name)
        dest_label_path = os.path.join(split_directory, split_type, "labels", label_name)

        shutil.copy(orig_img_path, dest_img_path)
        shutil.copy(orig_label_path, dest_label_path)

def get_category_list(split_directory):
    json_path = os.path.join(split_directory, "annotations.json")
    if not os.path.exists(json_path):
        print(f"Annotation json ({json_path}) not found")
        sys.exit(1)
    
    with open(json_path, "r") as f:
        data = json.loads(f.read())

    categories = data['categories']
    category_set = set()

    for cat in categories:
        cat['supercategory'] = cat['supercategory'].replace('&', 'and')

        if cat['supercategory'] in ['Plastic glooves', 'Plastic utensils', 'Lid']:
            cat['supercategory'] = 'Other plastic'
        if cat['supercategory'] in ['Scrap metal', 'Food waste', 'Shoe', 'Rope and strings', 'Squeezable tube', 'Blister pack', 'Battery', 'Aluminium foil', 'Pop tab', 'Glass jar', 'Unlabeled litter']:
            cat['supercategory'] = 'Miscelaneous'
        if cat['supercategory'] == 'Paper bag':
            cat['supercategory'] = 'Paper'
        
        category_set.add(cat['supercategory'])
    return list(category_set)

def create_yaml_file(split_directory, new_labels):
    yaml_content = {
        'names': new_labels,
        'nc': len(new_labels),
        'train': "../train/images",
        'val': "../valid/images",
    }

    yaml_path = os.path.join(split_directory, "data.yaml")
    
    with open(yaml_path, "w") as f:
        yaml.safe_dump(yaml_content, f)
    
    print(f"New YAML file created at {yaml_path}")


def main():
    parser = argparse.ArgumentParser(description="Split dataset into train-val-test splits.")
    parser.add_argument('--directory', type=str, required=True, help="Dataset directory downloaded from kaggle")
    parser.add_argument('--split_directory', type=str, required=True, help="Directory to store splitted dataset")
    parser.add_argument('--train_split', type=float, required=False, default=0.85, help="Train split size ratio")
    parser.add_argument('--val_split', type=float, required=False, default=0.1, help="Validation split size ratio")
    parser.add_argument('--use_test', action='store_true', help="Choose to use test split as well")
    parser.add_argument('--shuffle', action='store_true', help="Randomize splitting or not")
    args = parser.parse_args()

    args.directory = os.path.join("datasets", args.directory)
    args.split_directory = os.path.join("datasets", args.split_directory)

    train_split = args.train_split
    val_split = args.val_split

    if train_split + val_split > 1:
        print("train split + val split can be at most 100%")
        sys.exit(1)
    if train_split <= 0.5:
        print("Train split must be larger than 50%")
        sys.exit(1)
    if val_split <= 0:
        print("Validation split must be larger than 0%")
        sys.exit(1)
    if not args.use_test:
        train_split = 1 - val_split
    
    train_list, val_list, test_list = [], [], []

    image_dir = os.path.join(args.directory, "images")
    label_dir = os.path.join(args.directory, "labels")
    if not os.path.exists(image_dir):
        print(f"Image directory ({image_dir}) not found")
        sys.exit(1)
    if not os.path.exists(label_dir):
        print(f"Label directory ({label_dir}) not found")
        sys.exit(1)

    img_files = os.listdir(image_dir)
    num_data = len(img_files)

    num_train_split = int(num_data * args.train_split)
    if not args.use_test:
        num_val_split = num_data - num_train_split
    else:
        num_val_split = int(num_data * args.val_split)
    
    if args.shuffle:
        random.shuffle(img_files)
    
    train_files = img_files[:num_train_split]
    val_files = img_files[num_train_split:num_train_split + num_val_split]
    test_files = img_files[num_train_split + num_val_split:]

    if os.path.exists(args.split_directory):
        shutil.rmtree(args.split_directory)
    os.makedirs(args.split_directory)
    os.makedirs(os.path.join(args.split_directory, "train"))
    os.makedirs(os.path.join(args.split_directory, "train", "images"))
    os.makedirs(os.path.join(args.split_directory, "train", "labels"))
    os.makedirs(os.path.join(args.split_directory, "valid"))
    os.makedirs(os.path.join(args.split_directory, "valid", "images"))
    os.makedirs(os.path.join(args.split_directory, "valid", "labels"))
    if args.use_test:
        os.makedirs(os.path.join(args.split_directory, "test"))
        os.makedirs(os.path.join(args.split_directory, "test", "images"))
        os.makedirs(os.path.join(args.split_directory, "test", "labels"))
    
    move_image_and_labels(args.directory, train_files, "train", args.split_directory)
    move_image_and_labels(args.directory, val_files, "valid", args.split_directory)
    if args.use_test:
        move_image_and_labels(args.directory, test_files, "test", args.split_directory)
    
    orig_json_path = os.path.join(args.directory, "annotations.json")
    dest_json_path = os.path.join(args.split_directory, "annotations.json")
    shutil.copy(orig_json_path, dest_json_path)

    new_labels = get_category_list(args.split_directory)
    create_yaml_file(args.split_directory)

if __name__ == "__main__":
    main()
