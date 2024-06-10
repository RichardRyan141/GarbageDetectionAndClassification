import argparse
import os
import subprocess
import random
import shutil
import sys

def move_image_and_labels(directory, image_list, split_type, split_directory):
    for img_name in image_list:
        orig_img_path = os.path.join(directory, "images", img_name)
        dest_img_path = os.path.join(split_directory, split_type, "images", img_name)

        label_name = img_name.replace(".jpg", ".txt")
        orig_label_path = os.path.join(directory, "labels", label_name)
        dest_label_path = os.path.join(split_directory, split_type, "labels", label_name)

        shutil.copy(orig_img_path, dest_img_path)
        shutil.copy(orig_label_path, dest_label_path)

def main():
    parser = argparse.ArgumentParser(description="Download dataset from Kaggle.")
    parser.add_argument('--directory', type=str, required=True, help="Preprocessed dataset directory")
    parser.add_argument('--split_directory', type=str, required=True, help="Directory to store splitted dataset")
    parser.add_argument('--train_split', type=float, required=False, default=0.85, help="Train split size ratio")
    parser.add_argument('--val_split', type=float, required=False, default=0.1, help="Validation split size ratio")
    parser.add_argument('--use_test', action='store_true', help="Choose to use test split as well")
    parser.add_argument('--shuffle', action='store_true', help="Randomize splitting or not")
    args = parser.parse_args()

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
        train_split = 100 - val_split
    
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
    os.makedirs(os.path.join(args.split_directory, "val"))
    os.makedirs(os.path.join(args.split_directory, "val", "images"))
    os.makedirs(os.path.join(args.split_directory, "val", "labels"))
    if args.use_test:
        os.makedirs(os.path.join(args.split_directory, "test"))
        os.makedirs(os.path.join(args.split_directory, "test", "images"))
        os.makedirs(os.path.join(args.split_directory, "test", "labels"))
    
    move_image_and_labels(args.directory, train_files, "train", args.split_directory)
    move_image_and_labels(args.directory, val_files, "val", args.split_directory)
    if args.use_test:
        move_image_and_labels(args.directory, test_files, "test", args.split_directory)
    
    orig_json_path = os.path.join(args.directory, "annotations.json")
    dest_json_path = os.path.join(args.split_directory, "annotations.json")
    shutil.copy(orig_json_path, dest_json_path)

if __name__ == "__main__":
    main()
