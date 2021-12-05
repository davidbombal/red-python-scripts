# Disclaimer: This script is for educational purposes only.  
# Do not use against any photos that you don't own or have authorization to test. 

#!/usr/bin/env python3

# This program is for .JPG and .TIFF format files.
# Installation and usage instructions:
# 1. Install Pillow (Pillow will not work if you have PIL installed):
# python3 -m pip install --upgrade pip
# python3 -m pip install --upgrade Pillow
# 2. Add .jpg images downloaded from Flickr to subfolder ./images from where the script is stored. 
# Try the following Flickr account: https://www.flickr.com/photos/194419969@N07/? (Please don't use other Flickr accounts).
# Note most social media sites strip exif data from uploaded photos.


# Print Logo
print("""
______            _     _  ______                 _           _ 
|  _  \          (_)   | | | ___ \               | |         | |
| | | |__ ___   ___  __| | | |_/ / ___  _ __ ___ | |__   __ _| |
| | | / _` \ \ / / |/ _` | | ___ \/ _ \| '_ ` _ \| '_ \ / _` | |
| |/ / (_| |\ V /| | (_| | | |_/ / (_) | | | | | | |_) | (_| | |
|___/ \__,_| \_/ |_|\__,_| \____/ \___/|_| |_| |_|_.__/ \__,_|_|
                                                                
                                                                

 _______   _____________   _____ _____  _____ _     
|  ___\ \ / /_   _|  ___| |_   _|  _  ||  _  | |    
| |__  \ V /  | | | |_      | | | | | || | | | |    
|  __| /   \  | | |  _|     | | | | | || | | | |    
| |___/ /^\ \_| |_| |       | | \ \_/ /\ \_/ / |____
\____/\/   \/\___/\_|       \_/  \___/  \___/\_____/
                                                    
                                                    
""")


import os
from PIL import Image

# Add files to the folder ./images
# We assign the cwd to a variable. We will refer to it to get the path to images.
cwd = os.getcwd()
# Change the current working directory to the one where you keep your images.
os.chdir(os.path.join(cwd, "images"))
# Get a list of all the files in the images directory.
files = os.listdir()

# Check if you have any files in the ./images folder.
if len(files) == 0:
    print("You don't have have files in the ./images folder.")
    exit()
# Loop through the files in the images directory.
for file in files:
    # We add try except black to handle when there are wrong file formats in the ./images folder.
    try:
        img = Image.open(file)
        # We get the exif data from the which we'll overwrite
        img_data = list(img.getdata())
        # We create a new Image object. We initialise it with the same mode and size as the original image.
        img_no_exif = Image.new(img.mode, img.size)
        # We copy the pixel data from img_data. 
        img_no_exif.putdata(img_data)
        # We save the new image without exif data. The keyword argument exif would've been used with the exif data if you wanted to save any. We overwrite the original image.
        img_no_exif.save(file)
    except IOError:
        print("File format not supported!")
