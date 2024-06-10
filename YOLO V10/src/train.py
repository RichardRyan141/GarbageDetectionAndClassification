import subprocess

def main():
    parser = argparse.ArgumentParser(description="Preprocess dataset.")
    parser.add_argument('--directory', type=str, required=True, help="Splitted dataset directory name (without 'datasets' parent folder)")
    parser.add_argument('--epochs', type=int, required=True, help="Number of epochs to be trained")
    parser.add_argument('--weight', type=str, required=True, help="Path to model to be fine tuned or checkpoint")
    parser.add_argument('--batch_size', type=int, required=False, default=8, help="Batch size for training")
    args = parser.parse_args()

    train_command = [
        "yolo", "task=detect", "mode=train", f"epochs={args.epochs}", f"batch={args.batch_size}", "plots=True", f"model={args.weight}", f"data={args.directory}/data.yaml"
    ]
    subprocess.run(train_command, check=True)

if __name__ == "__main__":
    main()