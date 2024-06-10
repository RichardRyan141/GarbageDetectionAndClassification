import argparse
import os
import shutil
import sys
from PIL import Image
import json

def dict_to_xml(image_info, annotation_list, category_list, split_type):
    xml = "<annotation>\n"
    xml += f"\t<folder>{split_type}</folder>\n"
    xml += f"\t<filename>{image_info['file_name']}</filename>\n"
    xml += f"\t<path>{image_info['file_path']}</path>\n"
    xml += "\t<source>\n"
    xml += "\t\t<database>Unspecified</database>\n"
    xml += "\t</source>\n"
    xml += f"\t<size>\n"
    xml += f"\t\t<width>{image_info['width']}</width>\n"
    xml += f"\t\t<height>{image_info['height']}</height>\n"
    xml += "\t\t<depth>3</depth>\n"
    xml += "\t</size>\n"
    xml += "\t<segmented>0</segmented>\n"
    for annot in annotation_list:
        xml += "\t<object>\n"
        xml += f"\t\t<name>{category_list[annot['category_id']]}</name>\n"
        xml += "\t\t<pose>Unspecified</pose>\n"
        xml += "\t\t<truncated>0</truncated>\n"
        xml += "\t\t<difficult>0</difficult>\n"
        xml += "\t\t<bndbox>\n"
        xml += f"\t\t\t<xmin>{round(annot['bbox'][0])}</xmin>\n"
        xml += f"\t\t\t<ymin>{round(annot['bbox'][1])}</ymin>\n"
        xml += f"\t\t\t<xmax>{round(annot['bbox'][0] + annot['bbox'][2])}</xmax>\n"
        xml += f"\t\t\t<ymax>{round(annot['bbox'][1] + annot['bbox'][3])}</ymax>\n"
        xml += "\t\t</bndbox>\n"
        xml += "\t</object>\n"
    xml += "</annotation>"
    return xml

def get_category_list(split_directory):
    json_path = os.path.join(split_directory, "annotations.json")
    if not os.path.exists(json_path):
        print(f"Annotation json ({json_path}) not found")
        sys.exit(1)
    
    with open(json_path, "r") as f:
        data = json.loads(f.read())

    categories = data['categories']
    category_list = []

    for cat in categories:
        cat['supercategory'] = cat['supercategory'].replace('&', 'and')

        if cat['supercategory'] in ['Plastic glooves', 'Plastic utensils', 'Lid']:
            cat['supercategory'] = 'Other plastic'
        if cat['supercategory'] in ['Scrap metal', 'Food waste', 'Shoe', 'Rope and strings', 'Squeezable tube', 'Blister pack', 'Battery', 'Aluminium foil', 'Pop tab', 'Glass jar', 'Unlabeled litter']:
            cat['supercategory'] = 'Miscelaneous'
        if cat['supercategory'] == 'Paper bag':
            cat['supercategory'] = 'Paper'
        
        category_list.append(cat['supercategory'])
    return category_list

def get_xml(split_directory, split_type):
    img_annot_list = []
    image_dir = os.path.join(split_directory, split_type, "images")
    label_dir = os.path.join(split_directory, split_type, "labels")
    xml_dir = os.path.join(split_directory, split_type, "xml_labels")
    category_list = get_category_list(split_directory)

    if os.path.exists(xml_dir):
        shutil.rmtree(xml_dir)
    os.makedirs(xml_dir)

    for img_name in os.listdir(image_dir):
        img_path = os.path.join(image_dir, img_name)
        image = Image.open(img_path)
        width, height = image.size

        image_info = {
            "file_name": img_name,
            "file_path": os.path.join(image_dir, img_name),
            "width": width,
            "height": height
        }

        label_name = img_name.replace(".jpg", ".txt")
        label_path = os.path.join(label_dir, label_name)
        annot_list = []
        with open(label_path, "r") as f:
            for line in f:
                category_id, bbox_x1, bbox_y1, bbox_w, bbox_h = line.strip().split()
                annot = {
                    "category_id": int(category_id),
                    "bbox": [float(bbox_x1), float(bbox_y1), float(bbox_w), float(bbox_h)]
                }
                annot_list.append(annot)
        xml = dict_to_xml(image_info, annot_list, category_list, split_type)

        xml_name = img_name.replace(".jpg", ".xml")
        xml_path = os.path.join(xml_dir, xml_name)
        with open(xml_path, "w") as f:
            f.write(xml)

def main():
    parser = argparse.ArgumentParser(description="Change JSON and TXT labels into XML for training")
    parser.add_argument('--split_directory', type=str, required=True, help="Directory of splitted dataset")
    args = parser.parse_args()
    
    train_image_dir = os.path.join(args.split_directory, "train", "images")
    train_label_dir = os.path.join(args.split_directory, "train", "labels")
    if not os.path.exists(train_image_dir):
        print(f"Train image directory ({train_image_dir}) not found")
        sys.exit(1)
    if not os.path.exists(train_label_dir):
        print(f"Train label directory ({train_label_dir}) not found")
        sys.exit(1)

    val_image_dir = os.path.join(args.split_directory, "val", "images")
    val_label_dir = os.path.join(args.split_directory, "val", "labels")
    if not os.path.exists(val_image_dir):
        print(f"Validation image directory ({val_image_dir}) not found")
        sys.exit(1)
    if not os.path.exists(val_label_dir):
        print(f"Validation label directory ({val_label_dir}) not found")
        sys.exit(1)

    if os.path.exists(os.path.join(args.split_directory, "test")):
        test_image_dir = os.path.join(args.split_directory, "test", "images")
        test_label_dir = os.path.join(args.split_directory, "test", "labels")
        if not os.path.exists(test_image_dir):
            print(f"Test image directory ({test_image_dir}) not found")
            sys.exit(1)
        if not os.path.exists(test_label_dir):
            print(f"Test label directory ({test_label_dir}) not found")
            sys.exit(1)
    
    get_xml(args.split_directory, "train")
    get_xml(args.split_directory, "val")
    if os.path.exists(os.path.join(args.split_directory, "test")):
        get_xml(args.split_directory, "test")

if __name__ == "__main__":
    main()
