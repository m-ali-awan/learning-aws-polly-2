#!bin/bash
yum install -y gcc openssl-devel bzip2-devel git zip unzip wget sqlite-devel
mkdir polly_libraries
cd polly_libraries
wget https://github.com/Miserlou/lambda-packages/files/1425358/_sqlite3.so.zip
unzip _sqlite3.so.zip 
python3.6 -m venv pollyenv
source pollyenv/bin/activate
python3.6 -m pip install -U textblob pyssml
python3.6 -m textblob.download_corpora punkt
cd
zip -r9 ~/repo/sam-config/lambda.zip nltk_data/tokenizers
cd  ~/repo/polly_libraries/pollyenv/lib/python3.6/site-packages/
zip -r9 ~/repo/sam-config/lambda.zip *
cd  ~/repo/polly_libraries/pollyenv/lib64/python3.6/site-packages/
zip -r9 ~/repo/sam-config/lambda.zip *
cd ~/repo/polly_libraries
zip -g ~/repo/sam-config/lambda.zip _sqlite3.so


