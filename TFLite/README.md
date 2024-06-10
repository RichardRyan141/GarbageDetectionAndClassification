# Installation tutorial
1) Clone this repository  
2) Clone tensorflow repository  `!git clone https://github.com/tensorflow/examples`  
3) Go to `examples/tensorflow_examples/lite/model_maker/requirements.txt` and modify `scann==1.2.6` into 'scann>=1.2.6`, this is due to scann no longer supporting download of version 1.2.6  
4) Go to `examples/tensorflow_examples/lite/model_maker/pip_package` and do `pip install -e .`