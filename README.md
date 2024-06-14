# List of possible problems
## Inference
### TypeError: YOLOv10.__init_subclass__() takes no keyword arguments
1) Go to `c:\Users\{user}\AppData\Local\Programs\Python\Python39\lib\site-packages\ultralytics\models\yolov10\model.py`. Adjust the user directory based on your computer's username
2) Change `class YOLOv10(Model, PyTorchModelHubMixin, library_name="ultralytics", repo_url="https://github.com/THU-MIG/yolov10", tags=["object-detection", "yolov10"])` into simply `class YOLOv10(Model)`
