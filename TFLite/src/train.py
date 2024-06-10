import argparse
import numpy as np
import os
import json
from tflite_model_maker import model_spec
from tflite_model_maker import object_detector
from tflite_support import metadata
import tensorflow as tf
assert tf.__version__.startswith('2')

tf.get_logger().setLevel('ERROR')
from absl import logging
logging.set_verbosity(logging.ERROR)

def get_category_set(split_directory):
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
    return category_set

def main():
    parser = argparse.ArgumentParser(description="Preprocess dataset.")
    parser.add_argument('--split_directory', type=str, required=True, help="Splitted dataset directory")
    parser.add_argument('--model_version', type=int, required=True, help="Efficientdet Lite model version (0-4)")
    parser.add_argument('--epochs', type=int, required=True, help="Number of epochs to be trained")
    parser.add_argument('--batch_size', type=int, required=False, default=8, help="Batch size for training")
    parser.add_argument('--full_model_train', action='store_true', help="Use if you want to train the entire model and not just the head")
    parser.add_argument('--model_save_name', type=str, required=False, help="Model's name for saving (no extensions)")
    args = parser.parse_args()

    train_image_dir = os.path.join(args.split_directory, "train", "images")
    train_xml_label_dir = os.path.join(args.split_directory, "train", "xml_labels")
    if not os.path.exists(train_image_dir):
        print(f"Train image directory ({train_image_dir}) not found")
        sys.exit(1)
    if not os.path.exists(train_xml_label_dir):
        print(f"Train xml label directory ({train_xml_label_dir}) not found")
        sys.exit(1)

    val_image_dir = os.path.join(args.split_directory, "val", "images")
    val_xml_label_dir = os.path.join(args.split_directory, "val", "xml_labels")
    if not os.path.exists(val_image_dir):
        print(f"Validation image directory ({val_image_dir}) not found")
        sys.exit(1)
    if not os.path.exists(val_xml_label_dir):
        print(f"Validation xml label directory ({val_xml_label_dir}) not found")
        sys.exit(1)
    
    if (args.model_version < 0) or (args.model_version > 4):
        print(f"Model version must be between 0 and 4, but found {args.model_version} instead")
        sys.exit(1)

    category_set = get_category_set(args.split_directory)
    category_list = list(category_set)

    train_data = object_detector.DataLoader.from_pascal_voc(
        train_image_dir,
        train_xml_label_dir,
        category_list
    )

    print("Train data loaded")

    val_data = object_detector.DataLoader.from_pascal_voc(
        val_image_dir,
        val_xml_label_dir,
        category_list
    )
    print("Val data loaded")
    
    spec = model_spec.get(f"efficientdet_lite{args.model_version}")
    model = object_detector.create(train_data, model_spec=spec, batch_size=args.batch_size, train_whole_model=False, epochs=args.epochs, validation_data=val_data)

    if not args.model_save_name:
        if args.full_model_train:
            model_save_name = f"taco_v{args.model_version}_full_{args.epochs}epoch"
        else:
            model_save_name = f"taco_v{args.model_version}_head_{args.epochs}epoch"
    else:
        model_save_name = args.model_save_name
    model.export(export_dir='.', tflite_filename=model_save_name + ".tflite")

if __name__ == "__main__":
    main()
