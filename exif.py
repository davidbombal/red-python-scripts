# Disclaimer: This script is for educational purposes only.  
# Do not use against any photos that you don't own or have authorization to test. 

#!/usr/bin/env python3

# Please note: 
# This program is for .JPG and .TIFF format files. The program could be extended to support .HEIC, .PNG and other formats.
# Installation and usage instructions:
# 1. Install Pillow (Pillow will not work if you have PIL installed):
# python3 -m pip install --upgrade pip
# python3 -m pip install --upgrade Pillow
# 2. Add .jpg images downloaded from Flickr to subfolder ./images from where the script is stored. 
# Try the following Flickr account: https://www.flickr.com/photos/194419969@N07/? (Please don't use other Flickr accounts).
# Note most social media sites strip exif data from uploaded photos.

import os
import sys
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


# Helper function
def create_google_maps_url(gps_coords):            
    # Exif data stores coordinates in degree/minutes/seconds format. To convert to decimal degrees.
    # We extract the data from the dictionary we sent to this function for latitudinal data.
    dec_deg_lat = convert_decimal_degrees(float(gps_coords["lat"][0]),  float(gps_coords["lat"][1]), float(gps_coords["lat"][2]), gps_coords["lat_ref"])
    # We extract the data from the dictionary we sent to this function for longitudinal data.
    dec_deg_lon = convert_decimal_degrees(float(gps_coords["lon"][0]),  float(gps_coords["lon"][1]), float(gps_coords["lon"][2]), gps_coords["lon_ref"])
    # We return a search string which can be used in Google Maps
    return f"https://maps.google.com/?q={dec_deg_lat},{dec_deg_lon}"


# Converting to decimal degrees for latitude and longitude is from degree/minutes/seconds format is the same for latitude and longitude. So we use DRY principles, and create a seperate function.
def convert_decimal_degrees(degree, minutes, seconds, direction):
    decimal_degrees = degree + minutes / 60 + seconds / 3600
    # A value of "S" for South or West will be multiplied by -1
    if direction == "S" or direction == "W":
        decimal_degrees *= -1
    return decimal_degrees
        

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


# Choice whether to keep output in the Terminal or redirect to a file.
while True:
    output_choice = input("How do you want to receive the output:\n\n1 - File\n2 - Terminal\nEnter choice here: ")
    try:
        conv_val = int(output_choice)
        if conv_val == 1:
            # We redirect the standard output stream to a file instead of the screen.
            sys.stdout = open("exif_data.txt", "w")
            break
        elif conv_val == 2:
            # The standard output stream is the screen so we don't need to redirect and just need to break the while loop.
            break
        else:
            print("You entered an incorrect option, please try again.")
    except:
        print("You entered an invalid option, please try again.")


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
        # Open the image file. We open the file in binary format for reading.
        image = Image.open(file)
        print(f"_______________________________________________________________{file}_______________________________________________________________")
        # The ._getexif() method returns a dictionary. .items() method returns a list of all dictionary keys and values.
        gps_coords = {}
        # We check if exif data are defined for the image. 
        if image._getexif() == None:
            print(f"{file} contains no exif data.")
        # If exif data are defined we can cycle through the tag, and value for the file.
        else:
            for tag, value in image._getexif().items():
                # If you print the tag without running it through the TAGS.get() method you'll get numerical values for every tag. We want the tags in human-readable form. 
                # You can see the tags and the associated decimal number in the exif standard here: https://exiv2.org/tags.html
                tag_name = TAGS.get(tag)
                if tag_name == "GPSInfo":
                    for key, val in value.items():
                        # Print the GPS Data value for every key to the screen.
                        print(f"{GPSTAGS.get(key)} - {val}")
                        # We add Latitude data to the gps_coord dictionary which we initialized in line 110.
                        if GPSTAGS.get(key) == "GPSLatitude":
                            gps_coords["lat"] = val
                        # We add Longitude data to the gps_coord dictionary which we initialized in line 110.
                        elif GPSTAGS.get(key) == "GPSLongitude":
                            gps_coords["lon"] = val
                        # We add Latitude reference data to the gps_coord dictionary which we initialized in line 110.
                        elif GPSTAGS.get(key) == "GPSLatitudeRef":
                            gps_coords["lat_ref"] = val
                        # We add Longitude reference data to the gps_coord dictionary which we initialized in line 110.
                        elif GPSTAGS.get(key) == "GPSLongitudeRef":
                            gps_coords["lon_ref"] = val   
                else:
                    # We print data not related to the GPSInfo.
                    print(f"{tag_name} - {value}")
            # We print the longitudinal and latitudinal data which has been formatted for Google Maps. We only do so if the GPS Coordinates exists. 
            if gps_coords:
                print(create_google_maps_url(gps_coords))
            # Change back to the original working directory.
    except IOError:
        print("File format not supported!")

if output_choice == "1":
    sys.stdout.close()
os.chdir(cwd)
