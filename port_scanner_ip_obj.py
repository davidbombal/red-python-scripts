#!/usr/bin/env python3
# The socket module in Python is an interface to the Berkeley sockets API.
import socket
# We import the ipaddress module. We want to use the ipaddress.ip_address(address) 
# method to see if we can instantiate a valid ip address to test.
import ipaddress
# We need to create regular expressions to ensure that the input is correctly formatted.
import re

# Regular Expression Pattern to extract the number of ports you want to scan. 
# You have to specify <lowest_port_number>-<highest_port_number> (ex 10-100)
port_range_pattern = re.compile("([0-9]+)-([0-9]+)")
# Initialising the port numbers, will be using the variables later on.
port_min = 0
port_max = 65535

# This script uses the socket api to see if you can connect to a port on a specified ip address. 
# Once you've successfully connected a port is seen as open.
# This script does not discriminate the difference between filtered and closed ports.

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

open_ports = []
# Ask user to input the ip address they want to scan.
while True:
    ip_add_entered = input("\nPlease enter the ip address that you want to scan: ")
    # If we enter an invalid ip address the try except block will go to the except block and say you entered an invalid ip address.
    try:
        ip_address_obj = ipaddress.ip_address(ip_add_entered)
        # The following line will only execute if the ip is valid.
        print("You entered a valid ip address.")
        break
    except:
        print("You entered an invalid ip address")
    

while True:
    # You can scan 0-65535 ports. This scanner is basic and doesn't use multithreading so scanning all
    # the ports is not advised.
    print("Please enter the range of ports you want to scan in format: <int>-<int> (ex would be 60-120)")
    port_range = input("Enter port range: ")
    # We pass the port numbers in by removing extra spaces that people sometimes enter. 
    # So if you enter 80 - 90 instead of 80-90 the program will still work.
    port_range_valid = port_range_pattern.search(port_range.replace(" ",""))
    if port_range_valid:
        # We're extracting the low end of the port scanner range the user want to scan.
        port_min = int(port_range_valid.group(1))
        # We're extracting the upper end of the port scanner range the user want to scan.
        port_max = int(port_range_valid.group(2))
        break

# Basic socket port scanning
for port in range(port_min, port_max + 1):
    # Connect to socket of target machine. We need the ip address and the port number we want to connect to.
    try:
        # Create a socket object
        # You can create a socket connection similar to opening a file in Python. 
        # We can change the code to allow for domain names as well.
        # With socket.AF_INET you can enter either a domain name or an ip address 
        # and it will then continue with the connection.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # You want to set a timeout for the socket to try and connect to the server. 
            # If you make the duration longer it will return better results. 
            # We put it at 0.5s. So for every port it scans it will allow 0.5s 
            # for a successful connection.
            s.settimeout(0.5)
            # We use the socket object we created to connect to the ip address we entered and the port number. 
            # If it can't connect to this socket it will cause an exception and the open_ports list will not 
            # append the value.
            s.connect((ip_add_entered, port))
            # If the following line runs then then it was successful in connecting to the port.
            open_ports.append(port)

    except:
        # We don't need to do anything here. If we were interested in the closed ports we'd put something here.
        pass

# We only care about the open ports.
for port in open_ports:
    # We use an f string to easily format the string with variables so we don't have to do concatenation.
    print(f"Port {port} is open on {ip_add_entered}.")
