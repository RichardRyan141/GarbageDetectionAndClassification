import os
import sys
import argparse
import json

def get_categories(label_map):
  categories = []
  with open(label_map, "r") as f:
    for line in f:
      cat_name = line.split(": ")[1].split('\n')[0]
      categories.append(cat_name)
  return categories

def get_new_annotations(categories, label_dir, width, height):
  new_annotations = []
  for label_file in os.listdir(label_dir):
    label_path = os.path.join(label_dir, label_file)
    img_name = label_file.replace(".txt", ".jpg")
    with open(label_path, "r") as f:
      annot = dict()
      annot['filename'] = img_name
      annot['width'] = width
      annot['height'] = height
      bboxes = []
      for line in f:
        class_id, x_min, y_min, x_max, y_max = line.split()
        bbox = dict()
        bbox['x_min'] = float(x_min) / width
        bbox['y_min'] = float(y_min) / height
        bbox['x_max'] = float(x_max) / width
        bbox['y_max'] = float(y_max) / height
        bbox['class_name'] = categories[int(class_id)]
        bbox['classes'] = int(class_id)
        bboxes.append(bbox)
      annot['bboxes'] = bboxes
      new_annotations.append(annot)
  return new_annotations

def write_annotations(label_map, label_dir, width, height):
  categories = get_categories(label_map)
  new_annot = get_new_annotations(categories, label_dir, width, height)
  img_dir = label_dir.replace("/labels", "/images")
  json_path = os.path.join(img_dir, "annotation.json")

  if os.path.exists(json_path):
    os.remove(json_path)
  
  with open(json_path, "w") as f:
    json.dump(new_annot, f, indent=4)
  
  print(f"new annotations for {label_dir} created")


def main():
    parser = argparse.ArgumentParser(description="Create new annotations.")
    parser.add_argument('--label_map', type=str, required=True, help="Path to label map text file")
    parser.add_argument('--data_dir', type=str, required=True, help="Path to dataset directory")
    parser.add_argument('--imgWidth', type=int, required=False, default=480, help="Image width")
    parser.add_argument('--imgHeight', type=int, required=False, default=640, help="Image height")

    args = parser.parse_args()

    if not os.path.exists(args.label_map):
        print("label map text file not found. Exiting program.")
        sys.exit(1)
  
    official_label_dir = os.path.join(args.data_dir, "official", "labels")
    unofficial_label_dir = os.path.join(args.data_dir, "unofficial", "labels")

    write_annotations(args.label_map, official_label_dir, args.imgWidth, args.imgHeight)
    write_annotations(args.label_map, unofficial_label_dir, args.imgWidth, args.imgHeight)

if __name__ == "__main__":
    main()
