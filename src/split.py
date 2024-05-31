import os
import argparse
import sys
import shutil
import random

def split_data(data_dir, train_split, val_split, data_type, shuffle):
    data_dir = os.path.join(data_dir, data_type)
    img_dir = os.path.join(data_dir, "images")
    label_dir = os.path.join(data_dir, "labels")

    if not os.path.exists(data_dir):
        print(f"{data_type} directory ({data_dir}) not found")
        sys.exit(1)
    if not os.path.exists(img_dir):
        print(f"{data_type} image directory ({img_dir}) not found")
        sys.exit(1)
    if not os.path.exists(label_dir):
        print(f"{data_type} label directory ({label_dir}) not found")
        sys.exit(1)

    img_files = os.listdir(img_dir)
    total_count = len(img_files)
    num_train = int(total_count * train_split / 100)
    num_val = int(total_count * val_split / 100)
    num_test = total_count - num_train - num_val

    if shuffle:
        random.shuffle(img_files)

    train_files = img_files[:num_train]
    val_files = img_files[num_train:num_train + num_val]
    test_files = img_files[num_train + num_val:]

    def create_file_list(files):
        data_list = []
        for img_file in files:
            img_path = os.path.join(img_dir, img_file)
            label_file = img_file.replace(".jpg", ".txt")
            label_path = os.path.join(label_dir, label_file)
            if not os.path.exists(label_path):
                print(f"Label {label_path} not found")
                continue
            data_list.append((img_path, label_path))
        return data_list

    return create_file_list(train_files), create_file_list(val_files), create_file_list(test_files)

def split_dataset(split_dir, train_list, val_list, test_list):
    if os.path.exists(split_dir):
        shutil.rmtree(split_dir)

    os.makedirs(os.path.join(split_dir, "train", "images"))
    os.makedirs(os.path.join(split_dir, "train", "labels"))
    os.makedirs(os.path.join(split_dir, "val", "images"))
    os.makedirs(os.path.join(split_dir, "val", "labels"))
    os.makedirs(os.path.join(split_dir, "test", "images"))
    os.makedirs(os.path.join(split_dir, "test", "labels"))

    def copy_data(data_list, split_type):
        for img_path, label_path in data_list:
            img_name = os.path.basename(img_path)
            label_name = os.path.basename(label_path)
            dest_img_path = os.path.join(split_dir, split_type, "images", img_name)
            dest_label_path = os.path.join(split_dir, split_type, "labels", label_name)
            shutil.copy(img_path, dest_img_path)
            shutil.copy(label_path, dest_label_path)

    copy_data(train_list, "train")
    copy_data(val_list, "val")
    copy_data(test_list, "test")

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
    parser.add_argument('--directory', type=str, required=True, help="Directory where dataset is stored")
    parser.add_argument('--splitDirectory', type=str, required=True, help="Directory where splitted dataset is stored")
    parser.add_argument('--useTest', type=str2bool, required=False, default=False, help="Used if you want a separate test set from the validation")
    parser.add_argument('--trainSplit', type=int, required=False, default=85, help="Percentage of data to be put on training set")
    parser.add_argument('--valSplit', type=int, required=False, default=10, help="Percentage of data to be put on validation set")
    parser.add_argument('--no_official', type=str2bool, required=False, default=False, help="Do not add official dataset to the split")
    parser.add_argument('--no_unofficial', type=str2bool, required=False, default=False, help="Do not add unofficial dataset to the split")
    parser.add_argument('--unofficial_train_mainly', type=str2bool, required=False, default=True, help="All unofficial data will be first put to training split. Only relevant if both official and unofficial dataset are split")
    parser.add_argument('--shuffle', type=str2bool, required=False, default=True, help="Whether to shuffle dataset before splitting")
    
    args = parser.parse_args()
    data_dir = args.directory
    split_dir = args.splitDirectory
    use_test = args.useTest
    train_split = args.trainSplit
    val_split = args.valSplit
    no_official = args.no_official
    no_unofficial = args.no_unofficial
    unofficial_train_only = args.unofficial_train_mainly
    shuffle = args.shuffle

    if train_split + val_split > 100:
        print("train split + val split can be at most 100")
        sys.exit(1)
    if train_split <= 50:
        print("Train split must be larger than 50%")
        sys.exit(1)
    if val_split <= 0:
        print("Validation split must be larger than 0%")
        sys.exit(1)


    if not os.path.exists(data_dir):
        print("Data directory not found")
        sys.exit(1)

    if no_official and no_unofficial:
        print("At most one flag of no_official or no_unofficial can be used")
        sys.exit(1)

    if not use_test:
        train_split = 100 - val_split

    train_list, val_list, test_list = [], [], []

    if no_official:
        train_list, val_list, test_list = split_data(data_dir, train_split, val_split, "unofficial", shuffle)
    elif no_unofficial:
        train_list, val_list, test_list = split_data(data_dir, train_split, val_split, "official", shuffle)
    elif unofficial_train_only:
        unoff_train, unoff_val, _ = split_data(data_dir, train_split, val_split, "unofficial", shuffle)
        off_train, off_val, off_test = split_data(data_dir, train_split, val_split, "official", shuffle)
        train_list = unoff_train + off_train
        val_list = unoff_val + off_val
        test_list = off_test
    else:
        off_train, off_val, off_test = split_data(data_dir, train_split, val_split, "official", shuffle)
        unoff_train, unoff_val, _ = split_data(data_dir, train_split, val_split, "unofficial", shuffle)
        train_list = off_train + unoff_train
        val_list = off_val + unoff_val
        test_list = off_test

    split_dataset(split_dir, train_list, val_list, test_list)

    print(f"{len(os.listdir(os.path.join(split_dir, 'train', 'images')))} data in training set")
    print(f"{len(os.listdir(os.path.join(split_dir, 'val', 'images')))} data in validation set")
    if os.path.exists(os.path.join(split_dir, 'test', 'images')):
        print(f"{len(os.listdir(os.path.join(split_dir, 'test', 'images')))} data in test set")

    
if __name__ == "__main__":
    main()
