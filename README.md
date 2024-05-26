# GarbageDetectionAndClassification
## Download
First of all, clone this repository with the following command  
```git clone https://github.com/RichardRyan141/GarbageDetectionAndClassification.git```  
After that, navigate to the cloned directory and install the library requirements with  
```pip install -r requirements.txt```  
Here are the flags that are used to run the download script 
1) `--source`, this is a required field and denotes whether you will be downloading from a JSON or a Google Drive. Typically, downloading from Google Drive is faster
2) `--directory`, this is a required field and denotes where the dataset will be stored
3) `--officialJSON`, this is not a required field and is used to specify a custom JSON path where the TACO official data is downloaded from. If not used, it will use the latest JSON as of this project's creation (13 Feb 2023)
4)  `--unofficialJSON`, this is not a required field and is used to specify a custom JSON path where the TACO unofficial data is downloaded from. If not used, it will use the latest JSON as of this project's creation (19 Dec 2019)
5)  `--maxWorker`, this is not a required field and is used to specify the number of concurrent workers to speed up the download process. Only relevant if you are downloading from JSON and not from Google Drive
6)  `--GDriveID`, this is not a required field and is used to specify the ID of the zip containing the dataset. If not used, it will use the ID of a zip containing the latest version of the dataset as of this project's creation (22 May 2024)
7)  `--officialDL`, this is not a required field and is used to specify if you would like to download the official dataset or not. Default is set to **True**
8)  `--unofficialDL`, this is not a required field and is used to specify if you would like to download the unofficial dataset or not. Default is set to **True**

One example of downloading it is with the following command  
```python src/download.py --source JSON --directory data```  
This will download both official and unofficial dataset from TACO's JSON and place the downloaded dataset into a directory called **data**  
Another example is  
```python src/download.py --source JSON --directory data --officialJSON official.json --unofficialJSON unofficial.json --maxWorker 6"```  
This will download both official and unofficial dataset from the provided JSON files and using at most 6 workers to download the dataset  

After the download, the dataset's directory should look something like this
```
data
----/official
--------/images
------------batch_1-000000.jpg
------------batch_1-000001.jpg
------------...
--------/labels
------------batch_1-000000.txt
------------batch_1-000001.txt
------------...
----unofficial
--------/images
------------000000.jpg
------------000001.jpg
------------...
--------/labels
------------000000.txt
------------000001.txt
------------...
```

# Acknowledgements
- Pedro F Proença and Pedro Simões. "TACO: Trash Annotations in Context for Litter Detection." arXiv:2003.06975 (2020). [Link](https://arxiv.org/abs/2003.06975) [Github](https://github.com/pedropro/TACO)
