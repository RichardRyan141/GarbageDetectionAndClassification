import os
import argparse
import json
import random
import yaml
import sys

def read_label_file(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f]

def write_label_file(file_path, lines):
    with open(file_path, "w") as f:
        for line in lines:
            f.write(line + "\n")

def remove_invalid_box_boundaries(directory):
    label_dir = os.path.join(directory, "labels")
    invalid_boxes = 0

    for file_name in os.listdir(label_dir):
        file_path = os.path.join(label_dir, file_name)
        annotations = read_label_file(file_path)
        new_annotations = []

        for line in annotations:
            try:
                class_id, bbox_xcenter, bbox_ycenter, bbox_w, bbox_h = map(float, line.split())
                bbox_x = bbox_xcenter - bbox_w / 2
                bbox_y = bbox_ycenter - bbox_h / 2
                if bbox_x < 0 or bbox_x + bbox_w > 1 or bbox_y < 0 or bbox_y + bbox_h > 1:
                    invalid_boxes += 1
                else:
                    new_annotations.append(line)
            except:
                invalid_boxes += 1

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

def remove_very_small_boxes(directory, threshold):
    label_dir = os.path.join(directory, "labels")
    total_removed_boxes = 0

    for label_file in os.listdir(label_dir):
        label_path = os.path.join(label_dir, label_file)
        annotations = read_label_file(label_path)
        new_annotations = []

        for line in annotations:
            class_id, bbox_xcenter, bbox_ycenter, bbox_w, bbox_h = map(float, line.strip().split())
            bbox_area = bbox_w * bbox_h
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

                class1, xc1, yc1, w1, h1 = map(float, boxes[i].split())
                class2, xc2, yc2, w2, h2 = map(float, boxes[j].split())

                x1 = xc1 - w1/2
                y1 = yc1 - h1/2
                x2 = xc2 - w2/2
                y2 = yc2 - h2/2

                if class1 != class2:
                    continue

                x_overlap = max(0, max(x1, x2) - min(x1+w1, x2+w2))
                y_overlap = max(0, max(y1, y2) - min(y1+w1, y2+h2))

                intersect = x_overlap * y_overlap
                area1 = w1 * h1
                area2 = w2 * h2
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

def preprocess(directory, args):
    remove_invalid_box_boundaries(directory)
    remove_boxes_from_images_with_high_box_count(directory, args.max_box_count)
    remove_very_small_boxes(directory, args.min_box_size)
    remove_boxes_with_high_same_class_box_overlap(directory, args.max_iou)
    remove_images_without_label(directory)
    remove_labels_without_images(directory)

def get_labels(directory):
    yaml_path = os.path.join(directory, "data.yaml")
    if not os.path.exists(yaml_path):
        print(f"YAML path not found ({yaml_path})")
        sys.exit(1)
    with open(yaml_path, "r") as f:
        yaml_content = yaml.safe_load(f)
        class_labels = yaml_content.get("names", [])
    return class_labels

def group_labels(directory, class_labels, class_grouped):
    rev_class_labels = {v: k for k, v in enumerate(class_labels)}

    old_to_new_map = {rev_class_labels[v]: k for k, v in class_grouped}

    label_dir = os.path.join(directory, "labels")
    for label_file in os.listdir(label_dir):
        if not label_file.endswith(".txt"):
            continue

        new_lines = []
        with open(os.path.join(label_dir, label_file), "r") as lines:
            for line in lines:
                parts = line.split()
                original_class_id = int(parts[0])
                new_class_id = old_to_new_map[original_class_id]
                new_line = f"{new_class_id} {' '.join(parts[1:])}\n"
                new_lines.append(new_line)

        with open(os.path.join(label_dir, label_file), "w") as f:
            f.writelines(new_lines)

    print(f"Grouped labels for {directory}")    

def update_yaml(directory, new_labels):
    yaml_path = os.path.join(directory, "data.yaml")
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    new_names = [new_labels[i] for i in range(len(new_labels))]

    data["names"] = new_names
    data["nc"] = len(new_names)
    data['train'] = '../train/images'
    data['val'] = '../valid/images'

    with open(f"{yaml_path}", "w") as f:
        yaml.safe_dump(data, f)
    with open(f"{yaml_path}", "r") as f:
        print(f.read())

def main():
    parser = argparse.ArgumentParser(description="Preprocess dataset from roboflow.")
    parser.add_argument('--directory', type=str, required=True, help="Original dataset directory")
    parser.add_argument('--max_box_count', type=int, required=False, default=30, help="Maximum number of boxes in an image")
    parser.add_argument('--min_box_size', type=float, required=False, default=0.00015, help="Minimum box size ratio")
    parser.add_argument('--max_iou', type=float, required=False, default=0.35, help="Max IoU overlap between boxes of the same class")
    args = parser.parse_args()

    args.directory = os.path.join("datasets", args.directory)

    if not os.path.exists(args.directory):
        print(f"Data directory ({args.directory}) not found")
        sys.exit(1)
    
    class_labels = get_labels(args.directory)
    class_labels_grouped = [
        (3, "Aluminium foil"),
        (2, "Bottle"),
        (2, "Bottle cap"),
        (3, "Broken glass"),
        (5, "Can"),
        (6, "Carton"),
        (0, "Cigarette"),
        (4, "Cup"),
        (4, "Lid"),
        (3, "Other litter"),
        (3, "Other plastic"),
        (1, "Paper"),
        (1, "Plastic bag - wrapper"),
        (3, "Plastic container"),
        (5, "Pop tab"),
        (3, "Straw"),
        (6, "Styrofoam piece"),
        (3, "Unlabeled litter"),
    ]

    train_dir = os.path.join(args.directory, "train")
    preprocess(train_dir, args)
    group_labels(train_dir, class_labels, class_labels_grouped)

    val_dir = os.path.join(args.directory, "valid")
    preprocess(val_dir, args)
    group_labels(val_dir, class_labels, class_labels_grouped)

    test_dir = os.path.join(args.directory, "test")
    preprocess(test_dir, args)
    group_labels(test_dir, class_labels, class_labels_grouped)

    new_labels = [
        "Cigarette",
        "Bag - wrapper",
        "Bottle",
        "Other litter",
        "Cup",
        "Can",
        "Carton and Styrofoam",
    ]

    update_yaml(args.directory, new_labels)

if __name__ == "__main__":
    main()
