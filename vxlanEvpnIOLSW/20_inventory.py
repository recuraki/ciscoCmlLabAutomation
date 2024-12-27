import sys
from collections import deque
from virl2_client import ClientLibrary
from ipaddress import IPv4Interface
import yaml
from pathlib import Path
from config import cmlAddress, cmlUsername, cmlPassword, loginUsername, loginPassword
from config import baseArg, title

client = ClientLibrary(f"https://{cmlAddress}/", cmlUsername, cmlPassword, ssl_verify=False)
lab = client.find_labs_by_title(title)[0]

baseYaml = """
# ホスト名定義
all:
  vars:
    ansible_user: cisco
    ansible_password: cisco
    ansible_host_key_checking: false
    ansible_ssh_args: "-C -o ControlMaster=auto -o ControlPersist=60s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    
  children:
    iosxe:
      vars:
        ansible_connection: network_cli
        ansible_network_cli_ssh_type: paramiko
      hosts:
    pc:
      hosts:
"""
dat = yaml.safe_load(baseYaml)
dat["all"]["children"]["iosxe"]["hosts"] = {}
dat["all"]["children"]["pc"]["hosts"] = {}

for node in lab.nodes():
    nodeName = node._label
    for interface in node.interfaces():
        print(f"Node: {nodeName}, Interface: {interface}", interface.discovered_ipv4)
  


for node in lab.nodes():
    nodeName = node._label
    for interface in node.interfaces():
        if "Interface: Ethernet0/0" in str(interface): 
          if len(interface.discovered_ipv4) < 1:
              raise "No IP address is assigned to the interface"
          mgmtAddr = interface.discovered_ipv4[0]
          print(f"Node: {nodeName}, IP address: {mgmtAddr}")
          dat["all"]["children"]["iosxe"]["hosts"][nodeName] = {
              "ansible_host": str(mgmtAddr),
              "ansible_network_os": "ios"
          }
        elif "Interface: eth0" in str(interface):
          if len(interface.discovered_ipv4) < 1:
              raise "No IP address is assigned to the interface"
          mgmtAddr = interface.discovered_ipv4[0]
          print(f"Node: {nodeName}, IP address: {mgmtAddr}")
          dat["all"]["children"]["pc"]["hosts"][nodeName] = {
              "ansible_host": str(mgmtAddr),
          }

print(yaml.dump(dat))
with open('inventory.yaml','w')as fw:
    yaml.dump(dat, fw, default_flow_style=False, allow_unicode=True)