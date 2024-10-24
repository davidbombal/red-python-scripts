########################################
##   THE SCRIPT MUST BE RUN AS SUDO   ##
########################################

#    Import subprocess so we can use system commands.
import subprocess

#    Import the re module so we can make use of regular expressions. 
import re

#    Python allows us to run system commands using the function 
#    provided by the subprocess module; 
#    (subprocess.run(<list of command line arguments go here>, <specify the second argument if you want to capture the output>)).
#
#    This script is a parent process that creates a child process which 
#    runs a system command and will only continue once the child process 
#    is completed.
#
#    To save the contents that get sent to the standard output stream 
#    (the terminal), we must first specify that we want to capture the output.
#    To do this we specify the second argument as capture_output = True. 
#    This information gets stored in the stdout attribute as bytes and 
#    needs to be decoded before being used as a String in Python.
#    /etc/NetworkManager/system-connections/ is the directory where wifi
#    profiles in linux are stored
directory = "/etc/NetworkManager/system-connections/"
profile_names = subprocess.run(["ls", directory], capture_output = True).stdout.decode()

#     We parse the profile names from profile_names string using
#     splitlines() since each profile name is on a separate line
profile_names_parsed = profile_names.splitlines( )

#    We create an empty list outside of the loop where dictionaries 
#    containing all the wifi usernames and passwords will be saved.

wifi_list = []

#    If any profile names are not found this means that wifi connections 
#    have also not been found. So we run this part to check the 
#    details of the wifi and see whether we can get their passwords.

if len(profile_names_parsed) != 0:
    for name in profile_names_parsed:
        #    We put the profile names that have spaces in them inside
        #    single quotes so that they can be an accessible file names
        if " " in name:
            name = f"'{name}'"
        #    Every wifi connection will need its own dictionary which 
        #    will be appended to the variable wifi_list.
        wifi_profile = {}
        #    We can now run a more specific command to see the information 
        #    about the wifi connection and if the Security key
        #    is not absent it may be possible to get the password.
        profile_info = subprocess.run(["cat", directory + name], capture_output = True).stdout.decode()
        password = re.search("psk=(.*)\n", profile_info)
        
        #    We use the regular expression to only look for the absent cases so we can ignore them.
        if re.search("psk=(.*)\n", profile_info) == None:
            continue
        else:
            #    Assign the ssid of the wifi profile to the dictionary.
            wifi_profile["ssid"] = name 
            #    Some wifi connections may not have passwords.
            if password == None:
                wifi_profile["password"] = None
            else:
                #    We assign the grouping (where the password is contained) that 
                #    we are interested in to the password key in the dictionary.
                wifi_profile["password"] = password[1]
            #    We append the wifi information to the variable wifi_list.
            wifi_list.append(wifi_profile) 

for x in range(len(wifi_list)):
    print(wifi_list[x])