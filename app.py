import ctypes
import subprocess
import json
import wmi
import re
import os
import sys


class DNS:

    def __init__(self) -> None:
        pass

    def get_interface_info(self) -> list:
        try:
            result = subprocess.run(
                ["netsh", "interface", "show", "interface"],
                capture_output=True,
                text=True,
            )
            lines = result.stdout.split("\n")
            interface_info = []
            for i in range(3, len(lines)):
                parts = lines[i].strip().split()
                if len(parts) == 4:
                    interface_info.append([parts[1], parts[3]])
                elif len(parts) == 5:
                    interface_info.append([parts[1], parts[3] + " " + parts[4]])

            return interface_info
        except Exception as error:
            raise error

        return None

    def find_connected_interface(self, interface_info) -> any:
        for interface in interface_info:
            if (
                interface[1] == "Wi-Fi"
                or str(interface[1]).startswith("Ethernet")
                and interface[0].lower() == "connected"
            ):
                return interface[1]
        return None

    def check_dns_status(self) -> bool:
        c = wmi.WMI()
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if (
                interface.DNSServerSearchOrder is not None
                and len(interface.DNSServerSearchOrder) > 0
                and not interface.DNSServerSearchOrder[0].startswith("192.168")
            ):
                return interface.DNSServerSearchOrder[0], True
        return None, False

    def run_hidden(self, cmd) -> None:
        ps_cmd = [
            "powershell",
            "-Command",
            f"Start-Process cmd -ArgumentList '/c {cmd}' -Verb RunAs -WindowStyle Hidden",
        ]
        subprocess.run(ps_cmd, creationflags=subprocess.CREATE_NO_WINDOW)

    def set_dns(self, connected_interface, primary_dns, secondary_dns) -> None:
        try:
            interface_quoted = f'"{connected_interface}"'
            primary_cmd = f"netsh interface ipv4 set dnsservers name={interface_quoted} source=static address={primary_dns}"
            secondary_cmd = f"netsh interface ipv4 add dnsservers name={interface_quoted} address={secondary_dns} index=2"

            self.run_hidden(primary_cmd)
            self.run_hidden(secondary_cmd)

        except Exception as error:
            raise error

    def get_servers(self) -> dict:
        with open(self.get_json_path(), "r") as file:
            dns_servers = json.load(file)
        return dns_servers

    def connect_dns(self, selecte_service) -> None:
        interface_info = self.get_interface_info()
        if interface_info:
            connected_interface = self.find_connected_interface(interface_info)
            if connected_interface:
                dns_servers = self.get_servers()
                for key, value in dns_servers.items():
                    if selecte_service == key:
                        dns_code = value.split(" ")
                        primary_dns = dns_code[0]
                        secondary_dns = dns_code[1]

                self.set_dns(connected_interface, primary_dns, secondary_dns)
            else:
                raise Exception("No connected interface found.")
        else:
            raise Exception("Unable to retrieve interface information.")

    def disconnect_dns(self) -> None:
        interface_info = self.get_interface_info()
        connected_interface = self.find_connected_interface(interface_info)
        try:
            interface_quoted = f'"{connected_interface}"'
            reset_cmd = f'netsh interface ip set dns "{connected_interface}" dhcp'
            self.run_hidden(reset_cmd)
        except Exception as error:
            raise error

    def add_dns(self, new_service) -> any:
        dns_servers = new_service.values()
        dns_list = [dns.split(" ") for dns in dns_servers]

        if not all(self.match_dns(dns) for dns in dns_list):
            return "DNS servers not acceptable!", False

        if dns_list[0][0] == dns_list[0][1]:
            return "Can't use same dns servers!", False

        service_name = list(new_service.keys())[0]
        dns_servers = self.get_servers()
        if service_name in dns_servers:
            return "Can't use the same service name!", False

        if len(dns_servers) >= 8:
            return "Can't add more than 8 servers!", False

        dns_servers.update(new_service)
        with open(self.get_json_path(), "w") as file:
            json.dump(dns_servers, file, indent=4)

        return "add DNS successfully!", True

    def match_dns(self, dns_list) -> bool:
        ipv4_pattern = r"^\d{1,3}(\.\d{1,3}){0,3}$"

        for dns in dns_list:
            match = re.match(ipv4_pattern, dns)
            if not bool(match):
                return False

        return True

    def get_json_path(self) -> str:

        if getattr(sys, "frozen", False):
            executable_directory = os.path.dirname(sys.executable)
            json_path = os.path.join(executable_directory, "config", "service.json")
        else:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(script_directory, "config", "service.json")

        return json_path

    def delete_dns(self, service_name) -> bool:
        dns_servers = self.get_servers()
        if len(dns_servers) > 2:
            check = dns_servers.pop(service_name, None)
            if check:
                with open(self.get_json_path(), "w") as file:
                    json.dump(dns_servers, file, indent=4)
                return "Delete DNS Successfully!", True
            else:
                return "Failed to delete DNS!", False
        else:
            return "You have to include 2 services!", False

    def get_ping(self, host):
        try:
            output = subprocess.check_output(
                ["ping", "-n", "1", host],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            for line in output.splitlines():
                if "time=" in line:
                    return line.split("time=")[-1].split()[0]
            return "No response"
        except Exception:
            return "Error"
