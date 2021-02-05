## Install on Ubuntu 

* STEP1, install python3.6 (can use higher as python3.7).
    ```sh
    sudo add-apt-repository ppa:jonathonf/python-3.6
    sudo apt-get update
    sudo apt-get install python3.6
    sudo apt install python3-pip
    pip3 install --upgrade pip
    ```
    
* STEP2, install needed lib.
    ```sh
        pip install -r requirements.txt
    ```   
    
    
* STEP3, activate web server.
    ```sh
        python Nano_bread/app.py 
    ``` 
    
    
## File configuration

    .
    ├── app.py
    ├── customer
    │   └── root
    │       ├── camera.data
    │       ├── convert_recognition.data
    │       └── recognition.data
    ├── README.md
    ├── requirements.txt
    ├── static
    │   ├── A.png
    │   ├── bread_title.jpg
    │   ├── cameraROI.css
    │   ├── cameraROI.js
    │   ├── camera_set.js
    │   ├── customerProducts.js
    │   ├── EZchainLogo.png
    │   ├── favicon.ico
    │   ├── first_page.css
    │   ├── first_page.js
    │   ├── focus.svg
    │   ├── main_struct.css
    │   ├── recognitionBase.css
    │   ├── recognitionChangePage.js
    │   ├── recognition.css
    │   ├── recognition.js
    │   ├── roi9Recognition.css
    │   ├── settings.svg
    │   ├── style.css
    │   └── x.png
    ├── templates
    │   ├── cameraROI.html
    │   ├── cameraROIInferenceTable.html
    │   ├── cameraROIPercentageTable.html
    │   ├── cameraROITable.html
    │   ├── customerProductImages.html
    │   ├── customerProductImagetable.html
    │   ├── customerProductList.html
    │   ├── customerProductTable.html
    │   ├── editProductProfile.html
    │   ├── first_page.html
    │   ├── login_base.html
    │   ├── recognition.html
    │   ├── roiRecognitionTable.html
    │   ├── setCamera.html
    │   └── tr_tlp.html

/static Configure all static files as .js .css .jpg .png...

/templates Configure all Html files 
 
/customer store all customer data, it will be automatically generated. 
    
    
camera.data Configure customer camera data.

convert_recognition.data Configure all image inference data.

recognition.data Configure Yolo model id mapping customer product ID.