# Upload NFTs to OpenSea

Credits to [@lukeprelic](https://github.com/lukaprelic) for his code on [gist](https://gist.github.com/lukaprelic/2a2dc408e841039d341b66cc893dab54).


## Installation Instructions

Before installation, please create a collection with the same name as you would put in the `project_name` variable.

1. Open the project folder and type the following command:

        pip install -r requirements.txt

2. Download `ChromeDriver.exe` from [this link](https://chromedriver.chromium.org/downloads) matching it with the version of Chrome browser you have installed.

3. Move the downloaded `ChromeDriver.exe` file to system PATH (preferably to PYTHONPATH i.e. where `python.exe` file is situated).

4. Run the code using:

        python openseaupload.py


**Note:** It is recommended to run the `pip install` command in a Python virtual environment.


## Metamask Password and Passphrase
Create a `.env` file in the root of project folder and the following environment variables inside it:

    METAMASK_PASSPHRASE="<seedphrase>"
    METAMASK_PASSWORD="<password>"

Make sure to replace `<seedphrase>` and `<password>` with you Metamask seed phrase and wallet password respectively.

Alternatively, you can also define these two as system environment variables.


## Changes Required to be Made

* Make sure all your images are in the `Generated` folder and are named as `1.png`, `2.png` and so on. This is from the *Edition* column in the `metadata.csv` file and can be changed.
* The `metadata.csv` file should be structured as per sample in the `Generated` folder. This will make sure that no change is required in the code.
* Value of `start_count_id` variable shows from which value the images will be loaded from. This can be useful if if the program stops and needs to be run again.
* Value of `total_count` variable shows the total number of images to be uploaded. This will not change even when continued from an error state.
* If extra metadata is to be added, the lines 49, 61-62, 76-77, 102-103, 139-140 in `openseaupload.py` will need to be modified as per columns in `metadata.csv` file.
