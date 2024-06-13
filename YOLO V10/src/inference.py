import subprocess
import argparse
import os
import sys
import shutil

def is_image(file_path):
    return file_path.lower().endswith(('.png', '.jpg', '.jpeg'))

def is_video(file_path):
    return file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))

def main():
    parser = argparse.ArgumentParser(description="Preprocess dataset.")
    parser.add_argument('--source', type=str, required=True, choices=['image', 'video', 'folder'], help='Do you want to infer an image, a video or an entire directory?')
    parser.add_argument('--image', type=str, required=False, help="Path to an image to infer on")
    parser.add_argument('--video', type=str, required=False, help="Path to a video to infer on")
    parser.add_argument('--directory', type=str, required=False, help="Path to directory to infer on")
    parser.add_argument('--result_directory', type=str, required=True, help="Path to directory to store inference image result")
    parser.add_argument('--weight', type=str, required=True, help="Path to model to be fine tuned or checkpoint")
    parser.add_argument('--conf', type=float, required=False, default=0.35, help="Minimum confidence level of a detection to be recognized")
    args = parser.parse_args()

    if args.source == 'image':
        if not args.image:
            print("Image flag must be used if the source is an image")
            sys.exit(1)
        if not os.path.exists(args.image):
            print(f"Image ({args.image}) not found")
            sys.exit(1)
        if not is_image(args.image):
            print(f"{args.image} is not an image, it should end with .png, .jpg or .jpeg")
            sys.exit(1)
    elif args.source == 'video':
        if not args.video:
            print("Video flag must be used if the source is a video")
            sys.exit(1)
        if not os.path.exists(args.video):
            print(f"Video ({args.video}) not found")
            sys.exit(1)
        if not is_video(args.video):
            print(f"{args.video} is not a video, it should end with .mp4, .avi, .mov, or .mkv")
            sys.exit(1)
    else:
        if not args.directory:
            print("directory flag must be used if the source is a folder")
            sys.exit(1)
        if not os.path.exists(args.directory):
            print(f"Directory ({args.directory}) not found")
            sys.exit(1)

    if not os.path.exists(args.result_directory):
        os.makedirs(args.result_directory)

    if (args.source == "image") or (args.source == "video"):
        infer_command = [
            "yolo", "task=detect", "mode=predict", f"conf={args.conf}", "save=True", f"model={args.weight}", f"source={args.image}"
        ]
        subprocess.run(infer_command , check=True)

        orig_result_dir = "runs/detect/predict"
        orig_result_path = os.path.join(orig_result_dir, os.listdir(orig_result_dir)[0])
        dest_result_path = os.path.join(args.result_directory,os.listdir(orig_result_dir)[0])
        shutil.copy(orig_result_path,dest_result_path)

        shutil.rmtree(orig_result_dir)
    else:
        for file_name in os.listdir(args.directory):
            file_path = os.path.join(args.directory, file_name)
            if (not is_image(file_path)) and (not is_video(file_path)):
                continue

            infer_command = [
                "yolo", "task=detect", "mode=predict", f"conf={args.conf}", "save=True", f"model={args.weight}", f"source={file_path}"
            ]
            subprocess.run(infer_command , check=True)

            orig_result_dir = "runs/detect/predict"

            if (not os.path.exists(orig_result_dir)) or (len(os.listdir(orig_result_dir)) == 0):
                print(f"No results found in the prediction directory for {file_path}.")
                continue

            orig_result_path = os.path.join(orig_result_dir, os.listdir(orig_result_dir)[0])
            dest_result_path = os.path.join(args.result_directory, os.listdir(orig_result_dir)[0])
            shutil.copy(orig_result_path, dest_result_path)
            shutil.rmtree(orig_result_dir)

if __name__ == "__main__":
    main()
