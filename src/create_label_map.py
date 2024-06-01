import json
import argparse
import sys
import os

def get_class_dict(json_path, supercategory=False):
    with open(json_path ,"r") as f:
        data = json.loads(f.read())
        nr_categories = len(data['categories'])

        class_dict = {}

        for i in range(nr_categories):
          category = data['categories'][i]
          if supercategory:
            category_name = category['supercategory']
          else:
            category_name = category['name']
          category_id = category['id']
          if category_name not in class_dict.values():
            class_dict[len(class_dict)] = category_name
    return class_dict

def create_label_map(class_dict, output_path="label_map.txt"):
    label_map = {}

    for id in class_dict:
        category_id = int(id) + 1
        category_name = class_dict[id]
        label_map[category_id] = category_name

    with open(output_path, "w") as f:
        for category_id, category_name in label_map.items():
            f.write(f"{category_id}: {category_name}\n")

    print(f"Label map saved to {output_path}")

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
    parser = argparse.ArgumentParser(description="Create label map.")
    parser.add_argument('--json', type=str, required=True, help="Path to dataset JSON")
    parser.add_argument('--useMajorCategory', type=str2bool, required=False, default=False, help="Use the 28 super categories instead of the 60 minor categories")
    parser.add_argument('--output_path', type=str, required=False, default="label_map.txt", help="Location of label map text file")

    args = parser.parse_args()

    if not os.path.exists(args.json):
        print("JSON file not found. Exiting program.")
        sys.exit(1)
    if os.path.exists(args.output_path):
        os.remove(args.output_path)

    class_dict = get_class_dict(args.json, args.useMajorCategory)
    create_label_map(class_dict,args.output_path)

if __name__ == "__main__":
    main()
