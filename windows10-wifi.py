######################################
#Copyright of David Bombal, 2021     #
#https://www.davidbombal.com         #
#https://www.youtube.com/davidbombal #
######################################

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
command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output = True).stdout.decode()

#    We imported the re module to make use of regular expressions. 
#    We want to find all the wifi names which are listed after 
#    "ALL User Profile     :". Using regular expressions we can create 
#    a group of all characters until the return escape sequence (\r) appears.
profile_names = (re.findall("All User Profile     : (.*)\r", command_output))

#    We create an empty list outside of the loop where dictionaries 
#    containing all the wifi usernames and passwords will be saved.
wifi_list = []

#    If any profile names are not found this means that wifi connections 
#    have also not been found. So we run this part to check the 
#    details of the wifi and see whether we can get their passwords.
if len(profile_names) != 0:
    for name in profile_names:
        #    Every wifi connection will need its own dictionary which 
        #    will be appended to the variable wifi_list.
        wifi_profile = {}
        #    We can now run a more specific command to see the information 
        #    about the wifi connection and if the Security key
        #    is not absent it may be possible to get the password.
        profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output = True).stdout.decode()
        #    We use the regular expression to only look for the absent cases so we can ignore them.
        if re.search("Security key           : Absent", profile_info):
            continue
        else:
            #    Assign the ssid of the wifi profile to the dictionary.
            wifi_profile["ssid"] = name
            #    These cases aren't absent and we should run the 
            #    "key=clear" command part to get the password.
            profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"], capture_output = True).stdout.decode()
            #    Again run the regular expression to capture the 
            #    group after the : (which is the password).
            password = re.search("Key Content            : (.*)\r", profile_info_pass)
            #    Check if we found a password using the regular expression. 
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

