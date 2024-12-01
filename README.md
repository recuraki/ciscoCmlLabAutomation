# setup
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# 設定変更

config.pyの以下を環境に合わせて書き換えてください。
```
cmlAddress = "192.168.101.132" # CMLのWebUIアドレス
cmlUsername = "admin" # CMLのユーザ名
cmlPassword = "ciscocisco" # CMLのパスワード(sysadminのパスワードではない)
baseArg["mgmtsubnet"]="24" # mgmtのサブネット長
baseArg["mgmtsubnetmask"]="255.255.255.0" # mgmtのサブネットマスク表記
baseArg["mgmtgw"]="192.168.101.1" # mgmtのゲートウェイアドレス
```

# 設定変更(固定アドレスを使いたい場合)

このスクリプトは各ノードのmgmtをホストインタフェースにBridgeします。各mgmtのアドレスを静的に割り当てたい場合は以下の`dhcp`を静的なアドレスに書き換えてください。
```
sw1 = createNode("sw1", "dhcp", "ioll2-xe", (200, 300))
leaf1 = createNode("rt1", "dhcp", "iol-xe", (400, 200))
leaf2 = createNode("rt2", "dhcp", "iol-xe", (400, 400))
pc1 = createNode("pc1", "dhcp", "alpine", (600,200))
pc2 = createNode("pc2", "dhcp", "alpine", (600, 400))
```

# 実行
以下を実行すると"title"で設定したラボ名称のラボが存在されると削除されることに注意します。

```
cd simpleLab
python 10_createLab.py
python 20_inventory.py
ansible-playbook -i inventory.yaml 30_setconfig.yaml
ansible-playbook -i inventory.yaml 40_testping.yaml 
```

最後の`40`はOSPFのstatusがFULlになっていないとFailします。時間を空けてから実行してみてください。

