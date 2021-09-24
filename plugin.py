# Verisure Python Plugin
#
# Author: flopp999
#
"""
<plugin key="Verisure" name="Verisure 0.13" author="flopp999" version="0.13" wikilink="https://github.com/flopp999/Verisure-Domoticz" externallink="https://www.verisure.com">
    <description>
        <h2>Support me with a coffee &<a href="https://www.buymeacoffee.com/flopp999">https://www.buymeacoffee.com/flopp999</a></h2><br/>
        <h3>Configuration</h3>
        <h4>Use Username and Password from mypages.verisure.com &<a href="https://mypages.verisure.com">https://mypages.verisure.com</a></h4><br/>
    </description>
    <params>
        <param field="Mode1" label="Username" width="320px" required="true" default="Id"/>
        <param field="Mode2" label="Password" password="true" width="350px" required="true" default="Secret"/>
        <param field="Mode6" label="Debug to file (Verisure.log)" width="70px">
            <options>
                <option label="Yes" value="Yes" />
                <option label="No" value="No" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import verisure

Package = True

try:
    import requests, json, os, logging
except ImportError as e:
    Package = False

try:
    from logging.handlers import RotatingFileHandler
except ImportError as e:
    Package = False

try:
    from datetime import datetime, timedelta
except ImportError as e:
    Package = False

dir = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger("Verisure")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(dir+'/Verisure.log', maxBytes=1000000, backupCount=5)
logger.addHandler(handler)


class BasePlugin:
    enabled = False

    def __init__(self):
        self.Count = 6
        self.LoggedIn = False
        return

    def onStop(self):
        self.session.logout()

    def onStart(self):
#        Domoticz.Debugging(128)
        WriteDebug("===onStart===")
        self.Username = Parameters["Mode1"]
        self.Password = Parameters["Mode2"]

        if len(self.Username) <= 6:
            Domoticz.Log("Username too short")
            WriteDebug("Username too short")

        if len(self.Password) < 4:
            Domoticz.Log("Password too short")
            WriteDebug("Password too short")

        if os.path.isfile(dir+'/Verisure.zip'):
            if 'Verisure' not in Images:
                Domoticz.Image('Verisure.zip').Create()
            self.ImageID = Images["Verisure"].ID

        self.session = verisure.Session(self.Username,self.Password)
        try:
            self.session.login()
            self.LoggedIn = True
        except verisure.session.LoginError as error:
            Domoticz.Error(str(error))
            return

    def onHeartbeat(self):
        if self.Count >= 1 and self.LoggedIn == True:
            try:
                overview = self.session.get_lock_state()
                for Name,Value in overview[0].items():
                    UpdateDevice(Name,str(Value))
                Domoticz.Log("Data updated")
                self.Count = 0

            except verisure.session.RequestError as error:
                Domoticz.Error(str(error))
                return

        self.Count += 1

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def UpdateDevice(Name,sValue):
    if Name == "zone":
        ID = 1
        Unit = ""
    elif Name == "deviceLabel":
        ID = 2
        Unit = ""
    elif Name == "area":
        ID = 3
        Unit = ""
    elif Name == "userIndex":
        ID = 4
        Unit = ""
    elif Name == "userString":
        ID = 5
        Unit = ""
    elif Name == "method":
        ID = 6
        if sValue == "AUTO":
            sValue = 1
        elif sValue == "THUMB":
            sValue = 2
        elif sValue == "REMOTE":
            sValue = 3
        elif sValue == "CODE":
            sValue = 4
        elif sValue == "STAR":
            sValue = 5
        elif sValue == "TAG":
            sValue = 6
        else:
            Domoticz.Error("Verisure method")
            Domoticz.Error(str(sValue))
            sValue = -1
        Unit = ""
    elif Name == "lockedState":
        ID = 7
        if sValue == "LOCKED":
            sValue = 1
        elif sValue == "UNLOCKED":
            sValue = 0
        else:
            Domoticz.Error("Verisure lockedState")
            Domoticz.Error(str(sValue))
            sValue = -1
        Unit = ""
    elif Name == "currentLockState":
        ID = 8
        if sValue == "LOCKED":
            sValue = 1
        elif sValue == "UNLOCKED":
            sValue = 0
        else:
            Domoticz.Error("Verisure currentLockedState")
            Domoticz.Error(str(sValue))
            sValue = -1
        Unit = ""
    elif Name == "pendingLockState":
        ID = 9
        Unit = ""
    elif Name == "eventTime":
        ID = 10
        Unit = ""
    elif Name == "secureModeActive":
        ID = 11
        if sValue == "True":
            sValue = 1
        elif sValue == "False":
            sValue = 0
        Unit = ""
    elif Name == "motorJam":
        ID = 12
        if sValue == "True":
            sValue = 1
        elif sValue == "False":
            sValue = 0
        Unit = ""
    elif Name == "paired":
        ID = 13
        if sValue == "True":
            sValue = 1
        elif sValue == "False":
            sValue = 0
        Unit = ""

    if (ID not in Devices):
        if sValue == "-32768":
            Used = 0
        else:
            Used = 1
        if ID == 2 or ID == 3 or ID == 5 or ID == 10:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Text", Options={"Custom": "0;"+Unit}, Used=1, Image=(_plugin.ImageID)).Create()
        else:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Options={"Custom": "0;"+Unit}, Used=1, Image=(_plugin.ImageID)).Create()
    if (ID in Devices):
        if Devices[ID].sValue != str(sValue):
            Devices[ID].Update(0, str(sValue))

def CheckInternet():
    WriteDebug("Entered CheckInternet")
    try:
        WriteDebug("Ping")
        requests.get(url='https://verisure.com/', timeout=2)
        WriteDebug("Internet is OK")
        return True
    except:
        WriteDebug("Internet is not available")
        return False

def WriteDebug(text):
    if Parameters["Mode6"] == "Yes":
        timenow = (datetime.now())
        logger.info(str(timenow)+" "+text)

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    _plugin.onMessage(Connection, Data)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def onStop():
    global _plugin
    _plugin.onStop()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
