# Qiagen Upload

This repository contains the scripts required for use in uploading TSO500 samples to QCII for analysis, via the API. The project contains two modules, get_user_code and qiagen_upload. The repository has a logger script which provides logging functionality to both modules. It contains a Dockerfile and a Makefile for use in building a dockerised version and pushing this dockerised version to Docker Hub. It also contains an XML template which is used to create the XML metadata file used for each sample upload.

### get_user_code

This script can be run to generate the user_code required to register the device in QCII, and to generate the device_code and code_verifier required for use when running the qiagen_upload module.

#### Inputs

The inputs are as follows:
```bash
usage: Generate user code required to register the device in QCII, and device code and code_verifier required for use when running the qiagen_upload module

Generate user code required to register the device in QCII, and device code and code_verifier required for use when running the qiagen_upload module

options:
  -h, --help            show this help message and exit

Required named arguments:
  -CI CLIENT_ID, --client_id CLIENT_ID
                        Client ID provided by Qiagen
```

The script can be run as follows:
```bash
python3 -m get_user_code -CI $CLIENT_ID
```

#### Outputs

The script has 4 output files:
* Logfile - ```outputs/get_user_code_YYYYMMDD_HHMMSS.log``` - Contains log messages documenting script logic
* Code verifier file - ```outputs/qiagen_code_verifier_YYYYMMDD_HHMMSS``` - Contains the code_verifier generated by the script. A high-entropy cryptographic random string
* Device code file - ```outputs/qiagen_device_code_YYYYMMDD_HHMMSS``` - Contains the device_code generated by the script. This code authorises the device.
* User code file - ```outputs/qiagen_user_code_YYYYMMDD_HHMMSS``` - Contains the user code generated by the script. This can be used to register the device in QiaOAuth

### qiagen_upload

This module contains the qiagen_upload script, which can be used to uplaod the sample zip file to QCII. It contains 3 classes:
* CreateZIP - Class to create the final ZIP file for upload to QCI
* CreateXML - Class to create the XML for the QCI sample upload. QCII requires an XML metadata file for every sample uploaded via the API
* UploadToQiagen - Class to upload the created zip file to QCII using the API     

#### Inputs

The inputs are as follows:
```bash
usage: Create sample ZIP and XML, generate access token, and upload sample ZIP file to QCII

Create sample ZIP and XML, generate access token, and upload sample ZIP file to QCII

options:
  -h, --help            show this help message and exit
  -S SAMPLE_NAME, --sample_name SAMPLE_NAME
                        Sample name string
  -Z SAMPLE_PATH, --sample_path SAMPLE_PATH
                        Zipped folder containing variant files
  -CI CLIENT_ID, --client_id CLIENT_ID
                        Client ID provided by Qiagen
  -CS CLIENT_SECRET, --client_secret CLIENT_SECRET
                        Client secret provided by Qiagen
  -C CODE_VERIFIER, --code_verifier CODE_VERIFIER
                        Code verifier generated when obtaining the user code
  -D DEVICE_CODE, --device_code DEVICE_CODE
                        Device code generated when obtaining the user code
```

The script can be run as follows:
```bash
python3 -m qiagen_upload -S $SAMPLE_NAME -Z /qiagen_upload/$SAMPLE_ZIP.zip -CI $CLIENT_ID -CS $CLIENT_SECRET -C $CODE_VERIFIER -D $DEVICE_CODE
```
#### Outputs

The script has 2 output files:
* Sample zip - ```$SAMPLE_NAME.zip``` - sample zip file containing only the files required for upload, plus the created XML metadata file
* Logfile - ```outputs/qiagen_upload_YYYYMMDD_HHMMSS.log``` - Contains log messages documenting script logic

## Docker image

The docker image is built, tagged and saved as a .tar.gz file using the Makefile as follows:

```bash
sudo make build
```

The docker image can be pushed to Docker Hub as follows:
```bash
sudo make push
```

The current and all previous versions of the tool are stored as dockerised versions in 001_ToolsReferenceData project as .tar.gz files. They are also stored in the seglh Docker Hub.

### get_user_code

get_user_code can be run as follows:

```bash
sudo docker run -it --rm -v $PATH_TO_OUTDIR:/outputs/ seglh/qiagen_upload:$TAG get_user_code -CI $CLIENT_ID
```

### qiagen_upload

qiagen_upload can be run as follows:

```bash
sudo docker run -it --rm -v $PATH_TO_OUTDIR:/qiagen_upload/outputs/ -v $PATH_TO_SAMPLE_ZIP:/qiagen_upload/$SAMPLE_ZIP.zip seglh/qiagen_upload:$TAG qiagen_upload -S $SAMPLE_NAME -Z /qiagen_upload/$SAMPLE_ZIP.zip -CI $CLIENT_ID -CS $CLIENT_SECRET -C $CODE_VERIFIER -D $DEVICE_CODE
```

### Developed by the Synnovis Genome Informatics Team
