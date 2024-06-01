import tensorflow as tf
from object_detection.utils import dataset_util
import json
import os
import argparse
import sys

def create_tf_example(example, image_dir):
    img_path = os.path.join(image_dir, example['filename'])
    with tf.io.gfile.GFile(img_path, 'rb') as fid:
        encoded_image_data = fid.read()

    image_format = b'jpeg' if example['filename'].lower().endswith('.jpg') else b'png'
    height = example['height']
    width = example['width']
    filename = example['filename'].encode('utf8')

    xmins = [bbox['x_min'] / width for bbox in example['bboxes']]
    xmaxs = [bbox['x_max'] / width for bbox in example['bboxes']]
    ymins = [bbox['y_min'] / height for bbox in example['bboxes']]
    ymaxs = [bbox['y_max'] / height for bbox in example['bboxes']]
    classes_text = [bbox['class_name'].encode('utf8') for bbox in example['bboxes']]
    classes = [bbox['class_id'] for bbox in example['bboxes']]

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_image_data),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example

def main():
    parser = argparse.ArgumentParser(description='Create TFRecord from JSON annotations.')
    parser.add_argument('--output_path', required=True, help='Path to output TFRecord')
    parser.add_argument('--image_dir', required=True, help='Path to the image directory')
    args = parser.parse_args()

    writer = tf.io.TFRecordWriter(args.output_path)
    json_input = os.path.join(args.image_dir, "annotation.json")
    if not os.path.exists(json_input):
        print(f"{json_input} not found. Exiting program")
        sys.exit(1)

    with open(json_input) as f:
        examples = json.load(f)
    
    for example in examples:
        tf_example = create_tf_example(example, args.image_dir)
        writer.write(tf_example.SerializeToString())

    writer.close()
    
    print(f"TFrecord for {args.image_dir} created\n")

if __name__ == '__main__':
    main()
