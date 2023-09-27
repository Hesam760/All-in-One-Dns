import ctypes
import subprocess
import json
import re
import os
import sys

def get_interface_info():
    try:
        result = subprocess.run(['netsh', 'interface', 'show', 'interface'], capture_output=True, text=True)
        
        lines = result.stdout.split('\n')
        interface_info = []
        for i in range(3, len(lines)):
            parts = lines[i].strip().split()
            if len(parts) == 4:
                    interface_info.append([parts[1], parts[3]])

        return interface_info
    except Exception as error:
        raise error

    return None

def find_connected_interface(interface_info):
    for interface in interface_info:
        if interface[1] == "Wi-Fi" or interface[1] == "Ethernet" and interface[0].lower() == 'connected':
            return interface[1]
    return None

def set_dns(connected_interface, primary_dns, secondary_dns):
    try:
        primary_cmd = f'netsh interface ipv4 add dnsservers "{connected_interface}" address={primary_dns} index=1'
        secondary_cmd = f'netsh interface ipv4 add dnsservers "{connected_interface}" address={secondary_dns} index=2'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd", f"/c {primary_cmd}", None, 1)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd", f"/c {secondary_cmd}", None, 1)
    except Exception as error:
        raise error

def get_servers():
    with open(get_json_path(), 'r') as file:
        dns_servers = json.load(file)
        
    return dns_servers

def connect_dns(selecte_service):
    interface_info = get_interface_info()
    if interface_info:
        connected_interface = find_connected_interface(interface_info)
        if connected_interface:
            dns_servers = get_servers()
            for key, value in dns_servers.items():
                if selecte_service == key:
                    dns_code = value.split(" ")
                    primary_dns = dns_code[0]
                    secondary_dns = dns_code[1]
                    
            set_dns(connected_interface, primary_dns, secondary_dns)
        else:
            raise Exception("No connected interface found.")
    else:
        raise Exception("Unable to retrieve interface information.")
    
def disconnect_dns():
    interface_info = get_interface_info()
    connected_interface = find_connected_interface(interface_info)
    try:
        reset_cmd = f'netsh interface ip set dns "{connected_interface}" dhcp'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd", f"/c {reset_cmd}", None, 1)
    except Exception as error:
        raise error
        
def add_dns(new_service):
    dns_servers = new_service.values()
    dns_list = [dns.split(" ") for dns in dns_servers]

    if not all(match_dns(dns) for dns in dns_list):
        return "DNS servers not acceptable!"

    if dns_list[0][0] == dns_list[0][1]:
        return "Can't use same dns servers!"
    
    service_name = list(new_service.keys())[0]
    dns_servers = get_servers()
    if service_name in dns_servers:
        return "Can't use the same service name!"

    if len(dns_servers) >= 8:
        return "Can't add more than 8 servers!"
    
    dns_servers.update(new_service)
    with open(get_json_path(), "w") as file:
        json.dump(dns_servers, file, indent=4)
        
    return True

def match_dns(dns_list):
    ipv4_pattern = r'^\d{1,3}(\.\d{1,3}){0,3}$'
        
    for dns in dns_list:
        match = re.match(ipv4_pattern, dns)
        print(match)
        if not bool(match):
            return False
        
    return True

def get_json_path():
    
    if getattr(sys, 'frozen', False):
        executable_directory = os.path.dirname(sys.executable)
        json_path = os.path.join(executable_directory, 'config', 'service.json')
    else:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_directory, 'config', 'service.json')
    
    return json_path

def delete_dns(service_name):
    dns_servers = get_servers()
    
    check = dns_servers.pop(service_name, None)
    if check :
        with open(get_json_path(), "w") as file:
            json.dump(dns_servers, file, indent=4)
        return True
    else :
        return False