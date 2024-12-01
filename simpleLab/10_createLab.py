import sys
from collections import deque
from virl2_client import ClientLibrary
from ipaddress import IPv4Interface
import time
from config import cmlAddress, cmlUsername, cmlPassword, loginUsername, loginPassword
from config import baseArg, title

client = ClientLibrary(f"https://{cmlAddress}/", cmlUsername, cmlPassword, ssl_verify=False)

iolxeCfg="""
hostname {hostname}
username {loginUsername} privilege 15 password {loginPassword}
vrf definition management
 address-family ipv4
 address-family ipv6
ip domain name cisco
no ip domain lookup
interface Ethernet 0/0
 no switchport
 vrf forwarding management
 no shutdown
 ip address {mgmtaddr} {mgmtsubnetmask}
ip route vrf management 0.0.0.0 0.0.0.0 {mgmtgw}
line vty 0 4
login local
transport input telnet ssh
ip ssh server algorithm authentication password
crypt key gen rsa mod 2048
do write memory
"""

alpineCfg="""
hostname {hostname}
USERNAME={loginUsername}
PASSWORD={loginPassword}
"""

alpineCfgStatic="""
ip address add {mgmtaddr}/{mgmtsubnet} dev eth0
ip route add default via {mgmtgw}
"""

for lab in client.find_labs_by_title(title):
    lab.stop()
    lab.wipe()
    lab.remove()
lab = client.create_lab(title=title)

x = 0
y = 0
xoffset = 100
yoffset = 100

# ブリッジを作る. bridgeNode.config = "System Bridge" でBridgeモードになる(NATモードにしない)
x += xoffset
y += yoffset
bridgeNode = lab.create_node("bridge", "external_connector", 0, 0)
bridgeNode.config = "System Bridge"
extIntf = bridgeNode.create_interface()

# External Bridge接続用のmgmtswを作る
x += xoffset*0
y += yoffset*1
mgmtsw = lab.create_node("mgmtsw", "unmanaged_switch", 0, 500)
lab.connect_two_nodes(bridgeNode, mgmtsw) # Bridge - mgmtswのリンク作成

def createNode(name, ipaddr, nodeType="iol-xe", pos=[None, None]):
    print(f"Create {name}({nodeType})")
    global x, y
    x += xoffset
    y += yoffset
    assert nodeType in ["iol-xe", "ioll2-xe", "alpine"]
    pos = [x, y] if pos == [None, None] else pos
    node = lab.create_node(name, nodeType, pos[0], pos[1] )
    cfg = baseArg.copy()
    cfg["hostname"] = name
    cfg["mgmtaddr"] = ipaddr
    # nodeの初期設定
    if nodeType == "alpine":
        cfgStr = alpineCfg.format(**cfg)
        if ipaddr != "dhcp":
            # 静的なIPアドレス設定の場合はConfigを追加
            cfgStr += alpineCfgStatic.format(**cfg)
        node.config = cfgStr
    else:
        if ipaddr == "dhcp":
            cfg["mgmtaddr"] = "dhcp"
            cfg["mgmtsubnetmask"] = ""
        node.config = iolxeCfg.format(**cfg) # Render
    # 1つめのInterfaceはmgmtswに接続(Configもこれを前提に作る)
    intf = node.create_interface()
    lab.connect_two_nodes(node, mgmtsw)
    return node

#sw1 = createNode("sw1", "192.168.101.221", "ioll2-xe", (200, 300))
#leaf1 = createNode("rt1", "192.168.101.222", "iol-xe", (400, 200))
#leaf2 = createNode("rt2", "192.168.101.223", "iol-xe", (400, 400))
#pc1 = createNode("pc1", "192.168.101.224", "alpine", (600,200))
#pc2 = createNode("pc2", "192.168.101.225", "alpine", (600, 400))
sw1 = createNode("sw1", "dhcp", "ioll2-xe", (200, 300))
leaf1 = createNode("rt1", "dhcp", "iol-xe", (400, 200))
leaf2 = createNode("rt2", "dhcp", "iol-xe", (400, 400))
pc1 = createNode("pc1", "dhcp", "alpine", (600,200))
pc2 = createNode("pc2", "dhcp", "alpine", (600, 400))


lab.connect_two_nodes(leaf1, sw1) # et0-1.leaf1 - et0-1.sw1
lab.connect_two_nodes(leaf2, sw1) # et0-1.leaf2 - et0-2.sw1
lab.connect_two_nodes(leaf1, pc1) # et0-2.leaf1 - eth1.pc1
lab.connect_two_nodes(leaf2, pc2) # et0-2.leaf2 - eth1.pc2

print("Start lab")
lab.start()

# おまじない。sleepしないとalpineのIPアドレスが取得できないことがある
time.sleep(2)

# ノードの情報を表示
for node in lab.nodes():
    print(node, node.state)
    for interface in node.interfaces():
        if interface.discovered_ipv4 is None: continue
        if len(interface.discovered_ipv4) == 0: continue
        print(" ", interface, interface.discovered_ipv4)