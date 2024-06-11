# Installation tutorial
1) Clone this repository  
2) Do `pip install -q git+https://github.com/THU-MIG/yolov10.git`  
3) Do `pip install -r requirement.txt`

# Training tutorial
1) Clone this repository
2) Do the installation process above
3) Run `download.py` and choose the dataset source (roboflow or kaggle). You will need to get an API key from either of them to download the dataset. Tutorial on how to get the API key can be found [here for roboflow](https://docs.roboflow.com/api-reference/authentication) and [here for kaggle](https://www.kaggle.com/docs/api)
4) Run the respective `preprocess_{source}.py` code, and then if you are using kaggle dataset it needs to be split first by running the `split_kaggle.py` code
5) Run the `train.py` code

## Extra training notes
1) On kaggle notebook with accelerator P100, using the YOLO v10-M, when training with the roboflow dataset it takes approximately 3 minutes per epoch assuming batch size of 20
2) If you want to continue training, just change the model path when running `train.py` to the latest / best model from the last training, take note that it will start the epoch count from 0 and will not continue the last session although the weights used will already be fine tuned from the previous session(s)

# Model
This model is a fine tuned YOLO v10-M on the roboflow dataset for 700 epochs
[700 epoch](https://huggingface.co/Ryan404/taco_yolo_v10/tree/main)

# Inference tutorial
1) Clone this repository
2) Do the installation process above
3) Run `inference.py`

# To-do list
- [x] Add a code to download and preprocess data
- [x] Add a code to train the model
- [ ] Add a code for inference
- [ ] Add a full jupyter notebook demo from start (download data) to finish (custom inference)

# Acknowledgements
1) TACO dataset by Divya - [dataset](https://universe.roboflow.com/divya-lzcld/taco-mqclx)
2) TACO dataset by Kneroma - [dataset](https://www.kaggle.com/datasets/kneroma/tacotrashdataset)
3) YOLO v10 model - [github](https://github.com/THU-MIG/yolov10)
