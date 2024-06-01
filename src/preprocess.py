import os
import argparse
import gdown
import json
import random

def read_label_file(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f]

def write_label_file(file_path, lines):
    with open(file_path, "w") as f:
        for line in lines:
            f.write(line + "\n")

def remove_invalid_box_boundaries(directory, imgWidth=480, imgHeight=640):
    label_dir = os.path.join(directory, "labels")
    invalid_boxes = 0

    for file_name in os.listdir(label_dir):
        file_path = os.path.join(label_dir, file_name)
        annotations = read_label_file(file_path)
        new_annotations = []

        for line in annotations:
            class_id, bbox_x, bbox_y, bbox_xmax, bbox_ymax = map(float, line.split())
            if bbox_x < 0 or bbox_xmax > imgWidth or bbox_y < 0 or bbox_ymax > imgHeight:
                invalid_boxes += 1
            else:
                new_annotations.append(line)

        write_label_file(file_path, new_annotations)

    print(f"Found and removed {invalid_boxes} invalid boxes in {directory}")

def remove_boxes_from_images_with_high_box_count(directory, threshold):
    label_dir = os.path.join(directory, "labels")
    total_removed_boxes = 0

    for label_file in os.listdir(label_dir):
        label_path = os.path.join(label_dir, label_file)
        boxes = read_label_file(label_path)

        if len(boxes) > threshold:
            total_removed_boxes += len(boxes) - threshold
            selected_boxes = random.sample(boxes, threshold)
        else:
            selected_boxes = boxes

        write_label_file(label_path, selected_boxes)

    print(f"Found and removed {total_removed_boxes} boxes from {directory} due to high box count")

def remove_very_small_boxes(directory, threshold, imgWidth, imgHeight):
    label_dir = os.path.join(directory, "labels")
    total_removed_boxes = 0

    for label_file in os.listdir(label_dir):
        label_path = os.path.join(label_dir, label_file)
        annotations = read_label_file(label_path)
        new_annotations = []

        for line in annotations:
            class_id, bbox_x, bbox_y, bbox_xmax, bbox_ymax = line.split()
            bbox_w = float(bbox_xmax) - float(bbox_x)
            bbox_h = float(bbox_ymax) - float(bbox_y)
            bbox_area = bbox_w * bbox_h / (imgWidth * imgHeight)
            #print(line, "\t", bbox_w, " ", bbox_h, " ", bbox_area)
            if bbox_area >= threshold:
                new_annotations.append(line)
            else:
                total_removed_boxes += 1

        write_label_file(label_path, new_annotations)

    print(f"Found and removed {total_removed_boxes} very small boxes from {directory}")

def remove_boxes_with_high_same_class_box_overlap(directory, threshold):
    label_dir = os.path.join(directory, "labels")
    total_removed_boxes = 0

    for label_file in os.listdir(label_dir):
        label_path = os.path.join(label_dir, label_file)
        boxes = read_label_file(label_path)
        if len(boxes) < 2:
            continue

        removed_boxes = set()
        for i in range(len(boxes) - 1):
            for j in range(i + 1, len(boxes)):
                if i in removed_boxes or j in removed_boxes:
                    continue

                class1, x1, y1, x1_max, y1_max = map(float, boxes[i].split())
                class2, x2, y2, x2_max, y2_max = map(float, boxes[j].split())

                if class1 != class2:
                    continue

                x_overlap = max(0, max(x1, x2) - min(x1_max, x2_max))
                y_overlap = max(0, max(y1, y2) - min(y1_max, y2_max))

                intersect = x_overlap * y_overlap
                area1 = (x1_max-x1) * (y1_max-y1)
                area2 = (x2_max-x2) * (y2_max-y2)
                union = area1 + area2 - intersect
                IoU = intersect / union
                if IoU > threshold:
                    removed_boxes.add(i if area1 < area2 else j)

        new_annotations = [boxes[i] for i in range(len(boxes)) if i not in removed_boxes]
        total_removed_boxes += len(removed_boxes)

        write_label_file(label_path, new_annotations)

    print(f"Found and removed {total_removed_boxes} boxes from {directory} due to high overlap")

def remove_images_without_label(directory):
    img_dir = os.path.join(directory, "images")
    label_dir = os.path.join(directory, "labels")
    total_removed_img = 0

    for img_file in os.listdir(img_dir):
        label_file = img_file.replace(".jpg", ".txt")
        if not os.path.exists(os.path.join(label_dir, label_file)):
            total_removed_img += 1
            os.remove(os.path.join(img_dir, img_file))

    print(f"Found and removed {total_removed_img} images from {directory} without annotations")

def remove_labels_without_images(directory):
    img_dir = os.path.join(directory, "images")
    label_dir = os.path.join(directory, "labels")
    total_removed_label = 0

    for label_file in os.listdir(label_dir):
        img_file = label_file.replace(".txt", ".jpg")
        if not os.path.exists(os.path.join(img_dir, img_file)):
            total_removed_label += 1
            os.remove(os.path.join(label_dir, label_file))

    print(f"Found and removed {total_removed_label} labels from {directory} without images")

def preprocess(directory, imgWidth=480, imgHeight=640, box_count_threshold=30, box_size_threshold=0.0015, box_iou_threshold=0.35):
    remove_invalid_box_boundaries(directory, imgWidth, imgHeight)
    remove_boxes_from_images_with_high_box_count(directory, box_count_threshold)
    remove_very_small_boxes(directory, box_size_threshold, imgWidth, imgHeight)
    remove_boxes_with_high_same_class_box_overlap(directory, box_iou_threshold)
    remove_images_without_label(directory)
    remove_labels_without_images(directory)
    print()

def get_super_class_dict(json_path):
    with open(json_path ,"r") as f:
        data = json.loads(f.read())
        nr_categories = len(data['categories'])

        super_class_dict = {}

        for i in range(nr_categories):
          category = data['categories'][i]
          category_name = category['supercategory']
          category_id = category['id']
          if category_name not in super_class_dict.values():
            super_class_dict[len(super_class_dict)] = category_name
    return super_class_dict

def get_class_id_mapping(json_path):
    super_class_dict = get_super_class_dict(json_path)
    with open(json_path, "r") as f:
        data = json.load(f)
        mapping = dict()
        categories = data['categories']
        for i in range(len(categories)):
            cat = categories[i]
            supercategory_name = cat['supercategory']
            for key in super_class_dict.keys():
                if super_class_dict[key] == supercategory_name:
                    mapping[i] = key
                    break
    return mapping

def relabel_annotations(directory, json_path):
    if (json_path is None) or (not os.path.exists(json_path)):
        print("JSON file not found. Downloading from official TACO source (version: 13 Feb 2023)")
        if json_path is None:
            json_path = "official.json"
        gdown.download(id="1TzxsRbWdp3y8Mr6oiRQqynDo_MqkOaQi", output=json_path)
        
    label_dir = os.path.join(directory, "labels")
    class_id_map = get_class_id_mapping(json_path)
    #print(class_id_map)

    for label_file in os.listdir(label_dir):
        label_path = os.path.join(label_dir, label_file)
        annotations = read_label_file(label_path)
        new_annotations = []

        for line in annotations:
            class_id, bbox_x, bbox_y, bbox_xmax, bbox_ymax = line.split()
            new_class_id = class_id_map[int(class_id)]
            new_annotations.append(f"{new_class_id} {bbox_x} {bbox_y} {bbox_xmax} {bbox_ymax}")

        write_label_file(label_path, new_annotations)

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
    parser.add_argument('--useMajorCategory', type=str2bool, required=False, default=False, help="Use the 28 super categories instead of the 60 minor categories")
    parser.add_argument('--json', type=str, help="Path to dataset JSON to relabel annotations (relevant if using --useMajorCategory)")
    parser.add_argument('--no_official', type=str2bool, required=False, default=False, help="Do not preprocess official dataset")
    parser.add_argument('--no_unofficial', type=str2bool, required=False, default=False, help="Do not preprocess unofficial dataset")
    parser.add_argument('--imgWidth', type=int, default=480, help="Image width (default: 480)")
    parser.add_argument('--imgHeight', type=int, default=640, help="Image height (default: 640)")
    parser.add_argument('--maxBoxCount', type=int, default=30, help="Maximum box count per image (default: 30)")
    parser.add_argument('--minBoxSize', type=float, default=0.0015, help="Minimum box size (default: 0.0015)")
    parser.add_argument('--maxIOU', type=float, default=0.35, help="Maximum IoU of boxes from the same class (default: 0.35)")

    args = parser.parse_args()
    data_dir = args.directory
    #print(args.no_official)

    if not args.no_official:
        print("Preprocessing official dataset")
        official_dir = os.path.join(data_dir, "official")
        if args.useMajorCategory:
            relabel_annotations(official_dir, args.json)
        preprocess(official_dir, args.imgWidth, args.imgHeight, args.maxBoxCount, args.minBoxSize, args.maxIOU)
    
    if not args.no_unofficial:
        print("Preprocessing unofficial dataset")
        unofficial_dir = os.path.join(data_dir, "unofficial")
        if args.useMajorCategory:
            relabel_annotations(unofficial_dir, args.json)
        preprocess(unofficial_dir, args.imgWidth, args.imgHeight, args.maxBoxCount, args.minBoxSize, args.maxIOU)

if __name__ == "__main__":
    main()
