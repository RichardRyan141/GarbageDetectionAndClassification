[![Open In Colab](https://img.shields.io/badge/Colab-F9AB00?style=for-the-badge&logo=googlecolab&color=525252)](https://colab.research.google.com/drive/1WM_fMhhBQdD2c3ZiKFxPVy5aExniy62y?usp=sharing)


# Installation tutorial
1) Clone this repository  
2) Do `pip install -q git+https://github.com/THU-MIG/yolov10.git`  
3) Do `pip install -r requirement.txt`

# YOLO v10 pre trained weights
COCO
| Model | Test Size | #Params | FLOPs | AP<sup>val</sup> | Latency |
|:---------------|:----:|:---:|:--:|:--:|:--:|
| [YOLOv10-N](https://huggingface.co/jameslahm/yolov10n) |   640  |     2.3M    |   6.7G   |     38.5%     | 1.84ms |
| [YOLOv10-S](https://huggingface.co/jameslahm/yolov10s) |   640  |     7.2M    |   21.6G  |     46.3%     | 2.49ms |
| [YOLOv10-M](https://huggingface.co/jameslahm/yolov10m) |   640  |     15.4M   |   59.1G  |     51.1%     | 4.74ms |
| [YOLOv10-B](https://huggingface.co/jameslahm/yolov10b) |   640  |     19.1M   |  92.0G |     52.5%     | 5.74ms |
| [YOLOv10-L](https://huggingface.co/jameslahm/yolov10l) |   640  |     24.4M   |  120.3G   |     53.2%     | 7.28ms |
| [YOLOv10-X](https://huggingface.co/jameslahm/yolov10x) |   640  |     29.5M    |   160.4G   |     54.4%     | 10.70ms |

or  
```
!mkdir -p weights
!wget -P weights -q https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10n.pt
!wget -P weights -q https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10s.pt
!wget -P weights -q https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10m.pt
!wget -P weights -q https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10b.pt
!wget -P weights -q https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10x.pt
!wget -P weights -q https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10l.pt
!ls -lh weights
```

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
This model is a fine tuned YOLO v10-M on the TACO roboflow dataset for 700 epochs  
[Model](https://huggingface.co/Ryan404/taco_yolo_v10/tree/main)  
mAP50 = 51%  
mAP50-95 = 40%  

# Inference tutorial
1) Clone this repository
2) Do the installation process above
3) Run `inference.py`

# To-do list
- [x] Add a code to download and preprocess data
- [x] Add a code to train the model
- [x] Add a code for inference
- [x] Add a full jupyter notebook demo from start (download data) to finish (custom inference)
- [ ] Create a web ui for ease of training and inference

# Acknowledgements
1) TACO dataset by Divya - [dataset](https://universe.roboflow.com/divya-lzcld/taco-mqclx)
2) TACO dataset by Kneroma - [dataset](https://www.kaggle.com/datasets/kneroma/tacotrashdataset)
3) YOLO v10 model - [github](https://github.com/THU-MIG/yolov10)
