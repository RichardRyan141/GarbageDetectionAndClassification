import argparse
import os
import shutil
import json
import random
import sys

def move_and_rename_images(directory):
    orig_data_directory = os.path.join(directory, "data")
    new_data_directory = "new_data_dir_asasfasdasd"

    if os.path.exists(new_data_directory):
        shutil.rmtree(new_data_directory)
    os.makedirs(new_data_directory)
    os.makedirs(os.path.join(new_data_directory, "images"))
    os.makedirs(os.path.join(new_data_directory, "labels"))

    annot_json_path = os.path.join(directory, "data", "annotations.json")
    with open(annot_json_path, "r") as f:
        data = json.loads(f.read())

    images = data['images']
    annotations = data['annotations']

    img_annotation_list = []
    for i in range(len(images)):
        image = images[i]
        old_filename = image['file_name']
        new_filename = old_filename.replace("/", "_")
        
        old_filepath = os.path.join(directory, "data", old_filename)
        new_filepath = os.path.join(new_data_directory, "images", new_filename)
        if os.path.exists(old_filepath):
            shutil.copy(old_filepath, new_filepath)
        
        image['file_name'] = new_filename
        image['folder'] = new_data_directory
        
        annots = [annot for annot in annotations if int(annot['image_id']) == int(image['id'])]
        
        img_annotation_list.append((image, annots))
    
    new_json_path = os.path.join(new_data_directory, "annotations.json")
    shutil.copy(annot_json_path, new_json_path)

    shutil.rmtree(directory)
    os.rename(new_data_directory, directory)
    return img_annotation_list

def remove_invalid_boxes(annotations):
    new_annotations = []
    invalid_box_count = 0
    
    for annot in annotations:
        bbox = annot['bbox']
        try:
            x = float(bbox[0])
            y = float(bbox[1])
            w = float(bbox[2])
            h = float(bbox[3])
            new_annotations.append(annot)
        except:
            invalid_box_count += 1
            
    return new_annotations, invalid_box_count

def reduce_box_count(annotations, max_box_count = 30):
    if len(annotations) < max_box_count:
        return annotations, 0
    return random.sample(annotations, max_box_count), len(annotations) - max_box_count

def remove_very_small_boxes(image, annotations, min_box_size = 0.00015):
    new_annotations = []
    small_box_count = 0
    for annot in annotations:
        bbox = annot['bbox']
        area_ratio = (bbox[2] * bbox[3]) / (image['height'] * image['width'])
        if area_ratio >= min_box_size:
            new_annotations.append(annot)
        else:
            small_box_count += 1
    return new_annotations, small_box_count

def remove_boxes_with_high_same_class_box_overlap(annotations, max_iou = 0.35):
    if len(annotations) < 2:
        return annotations, 0
        
    removed_boxes = set()
    for i in range(len(annotations) - 1):
        for j in range(i + 1, len(annotations)):
            if i in removed_boxes or j in removed_boxes:
                continue

            (x1, y1, w1, h1) = annotations[i]['bbox']
            (x2, y2, w2, h2) = annotations[j]['bbox']

            if annotations[i]['category_id'] != annotations[j]['category_id']:
                continue

            x_overlap = max(0, min(x1+w1, x2+w2) - max(x1, x2))
            y_overlap = max(0, min(y1+h1, y2+h2) - max(y1, y2))

            intersect = x_overlap * y_overlap
            area1 = w1 * h1
            area2 = w2 * h2
            union = area1 + area2 - intersect
            IoU = intersect / union
            if IoU > max_iou:
                removed_boxes.add(i if area1 < area2 else j)

    new_annotations = [annotations[i] for i in range(len(annotations)) if i not in removed_boxes]

    return new_annotations, len(removed_boxes)

def create_label_file(directory, img_annot):
    img, annots = img_annot
    image_filename = img['file_name']
    label_filename = image_filename.replace(".jpg", ".txt")
    
    new_label_path = os.path.join(directory, "labels", label_filename)
    with open(new_label_path, "w") as f:
        for annot in annots:
            class_id = annot['category_id']
            bbox = annot['bbox']
            x_center = (float(bbox[0]) - float(bbox[2]) / 2) / img['width']
            y_center = (float(bbox[1]) - float(bbox[3]) / 2) / img['height']
            line = f"{class_id} {x_center} {y_center} {bbox[2]} {bbox[3]}\n"
            f.write(line)

def preprocess(args):
    image_annotation_list = move_and_rename_images(args.directory)
    print("Moved all images to 1 directory")

    total_invalid_box_count = 0
    total_high_box_count = 0
    total_small_boxes_count = 0
    total_high_iou_box_count = 0
    remaining_boxes = 0
    new_img_annotation_list = []

    for img_annot in image_annotation_list:
        image, annotations = img_annot
        
        new_annotations, invalid_box_count = remove_invalid_boxes(annotations)
        new_annotations, high_box_count = reduce_box_count(new_annotations, args.max_box_count)
        new_annotations, small_boxes_count = remove_very_small_boxes(image, new_annotations, args.min_box_size)
        new_annotations, high_iou_box_count = remove_boxes_with_high_same_class_box_overlap(new_annotations, args.max_iou)
        
        total_invalid_box_count += invalid_box_count
        total_high_box_count += high_box_count
        total_small_boxes_count += small_boxes_count
        total_high_iou_box_count += high_iou_box_count
        
        new_img_annotation_list.append((image, new_annotations))
        remaining_boxes += len(new_annotations)

    print(f"Invalid boxes removed : {total_invalid_box_count}")
    print(f"High count boxes removed : {total_high_box_count}")
    print(f"Small size boxes removed: {total_small_boxes_count}")
    print(f"High iou boxes removed : {total_high_iou_box_count}")
    print()
    print(f"Remaining boxes : {remaining_boxes}")

    for img_annot in new_img_annotation_list:
        create_label_file(args.directory, img_annot)

def main():
    parser = argparse.ArgumentParser(description="Preprocess dataset from kaggle.")
    parser.add_argument('--directory', type=str, required=True, help="Original dataset directory")
    parser.add_argument('--max_box_count', type=int, required=False, default=30, help="Maximum number of boxes in an image")
    parser.add_argument('--min_box_size', type=float, required=False, default=0.00015, help="Minimum box size ratio")
    parser.add_argument('--max_iou', type=float, required=False, default=0.35, help="Max IoU overlap between boxes of the same class")
    args = parser.parse_args()

    args.directory = os.path.join("datasets", args.directory)

    if not os.path.exists(args.directory):
        print(f"Data directory ({args.directory}) not found")
        sys.exit(1)

    preprocess(args)

if __name__ == "__main__":
    main()
