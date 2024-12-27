
cmlAddress = "192.168.101.132" # CMLのWebUIアドレス
cmlUsername = "admin" # CMLのユーザ名
cmlPassword = "ciscocisco" # CMLのパスワード(sysadminのパスワードではない)
loginUsername = "cisco" # 作成したノードにログインするためのユーザ名
loginPassword = "cisco" # 作成したノードにログインするためのパスワード
# 以下は特にstaticアドレスを設定する場合に使変更してください
baseArg = dict()
baseArg["mgmtsubnet"]="24" # mgmtのサブネット長
baseArg["mgmtsubnetmask"]="255.255.255.0" # mgmtのサブネットマスク表記
baseArg["mgmtgw"]="192.168.101.1" # mgmtのゲートウェイアドレス
baseArg["loginUsername"]=loginUsername
baseArg["loginPassword"]=loginPassword

title="simpleLab" # Labのタイトル