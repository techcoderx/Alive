from PySide6 import QtCore
from beem import Hive
from beemgraphenebase import account
import requests

class HiveLoginBridge(QtCore.QObject):
    startSignal = QtCore.Signal(str, str)
    hiveLoginResult = QtCore.Signal(int, arguments=['result'])

    def __init__(self, obj, parent=None):
        super().__init__(parent)
        self.m_obj = obj
        self.m_obj.hiveLoginResult.connect(self.hiveLoginResult)
        self.startSignal.connect(self.m_obj.auth)

class HiveLogin(QtCore.QObject):
    hiveLoginResult = QtCore.Signal(int)

    @QtCore.Slot(str, str)
    def auth(self, username, private_key):
        try:
            hive_pubkey = account.PrivateKey(wif=private_key,prefix='STM').get_public_key()
        except:
            return self.hiveLoginResult.emit(3)
        hive_accreq = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'condenser_api.get_accounts',
            'params': [[username]]
        }
        # support posting authorities from other accounts?
        hive_accresp = requests.post("https://techcoderx.com",json=hive_accreq)
        if hive_accresp.status_code != 200:
            return self.hiveLoginResult.emit(1)
        hive_accresult = hive_accresp.json()['result']
        if len(hive_accresult) == 0:
            return self.hiveLoginResult.emit(2)
        hive_acckeys = hive_accresult[0]['posting']
        for i in range(len(hive_acckeys['key_auths'])):
            if hive_acckeys['key_auths'][i][0] == str(hive_pubkey):
                return self.hiveLoginResult.emit(0)
        return self.hiveLoginResult.emit(3)

class HivePowerBridge(QtCore.QObject):
    startSignal = QtCore.Signal(str)
    hivePowerResult = QtCore.Signal(float, arguments=['result'])

    def __init__(self, obj, parent=None):
        super().__init__(parent)
        self.m_obj = obj
        self.m_obj.hivePowerResult.connect(self.hivePowerResult)
        self.startSignal.connect(self.m_obj.getHP)

class HiveRcBridge(QtCore.QObject):
    startSignal = QtCore.Signal(str)
    hiveRcResult = QtCore.Signal(str, arguments=['result'])

    def __init__(self, obj, parent=None):
        super().__init__(parent)
        self.m_obj = obj
        self.m_obj.hiveRcResult.connect(self.hiveRcResult)
        self.startSignal.connect(self.m_obj.getRC)

class HiveAccount(QtCore.QObject):
    hivePowerResult = QtCore.Signal(float)
    hiveRcResult = QtCore.Signal(str)

    @QtCore.Slot(str)
    def getHP(self,username):
        hive_accreq = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'condenser_api.get_accounts',
            'params': [[username]]
        }
        hive_propsreq = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'condenser_api.get_dynamic_global_properties',
            'params': []
        }
        account = requests.post('https://techcoderx.com',json=hive_accreq)
        props = requests.post('https://techcoderx.com',json=hive_propsreq)
        if account.status_code != 200:
            return self.hivePowerResult.emit("Error")
        elif props.status_code != 200:
            return self.hivePowerResult.emit("Error")
        self.hivePowerResult.emit(float(props.json()['result']['total_vesting_fund_hive'][:-5]) / float(props.json()['result']['total_vesting_shares'][:-6]) * float(account.json()['result'][0]['vesting_shares'][:-6]))

    @QtCore.Slot(str)
    def getRC(self,username):
        hive_rcreq = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'rc_api.find_rc_accounts',
            'params': {
                'accounts': [username]
            }
        }
        rc = requests.post('https://techcoderx.com',json=hive_rcreq)
        if rc.status_code != 200:
            self.hiveRcResult.emit("Error")
        else:
            self.hiveRcResult.emit(rc.text)