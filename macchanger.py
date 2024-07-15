import os
import subprocess
import random
import sys
import ctypes


# check req libs
required_modules = ["psutil"]

def install_packages(packages):
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} was not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages(required_modules)

import psutil

def check_admin():
    """Check if the script is running with admin privileges"""
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

def get_random_mac():
    """Generate a random MAC address"""
    mac = [
        0x00,
        0x16,
        0x3E,
        random.randint(0x00, 0x7F),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
    ]
    return ":".join(map(lambda x: "%02x" % x, mac))

def change_mac(interface, new_mac):
    """Change the MAC address of a given interface"""
    if sys.platform == 'win32':
        try:
            # Disable the network interface
            subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=disable"], capture_output=True, text=True)
            # Change the MAC address
            subprocess.run(["netsh", "interface", "set", "interface", interface, "new", "macaddr=", new_mac], capture_output=True, text=True)
            # Enable the network interface
            subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=enable"], capture_output=True, text=True)
            print(f"MAC address for {interface} changed to {new_mac}")
        except Exception as e:
            print(f"Failed to change MAC address for {interface}: {e}")
    else:
        try:
            # Disable the network interface
            subprocess.call(["sudo", "ifconfig", interface, "down"])
            # Change the MAC address
            subprocess.call(["sudo", "ifconfig", interface, "hw", "ether", new_mac])
            # Enable the network interface
            subprocess.call(["sudo", "ifconfig", interface, "up"])
            print(f"MAC address for {interface} changed to {new_mac}")
        except Exception as e:
            print(f"Failed to change MAC address for {interface}: {e}")

if not check_admin():
    print("Script is not running with admin privileges. Restarting with admin rights...")
    if sys.platform == "win32":
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:
        print("Please run the script with sudo.")
    sys.exit()

# Get list of all network interfaces
interfaces = psutil.net_if_addrs().keys()

for interface in interfaces:
    new_mac = get_random_mac()
    change_mac(interface, new_mac)
