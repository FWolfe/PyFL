# -*- coding: utf-8 -*-

import FLHook
from freelancer.files.character import CharFile
class Player(object):
    id = None
    user_data = None
    def __init__(self, client_id):
        try :
            self.id = int(client_id)
        except ValueError: # client_id is a character name
            self.id = FLHook.HkGetClientIdFromCharname(client_id)

    def printText(self, text):
        FLHook.PrintUserCmdText(self.id, text)

    def saveData(self):
        FLHook.SaveUserData(self.id)

    def getData(self, key=None, default=None):
        if key is None:
            return self.user_data
        data = self.user_data.get(key, default)
        self.user_data[key] = data
        return data

    def getName(self):
        return FLHook.HkGetCharnameFromClientId(self.id)

    def getClientInfo(self):
        return FLHook.GetClientInfo(self.id)
        
    def getShipId(self):
        return FLHook.GetClientInfo(self.id).iShip
        
#==============================================================================
#   HkFuncPlayers
#==============================================================================

    def addCash(self, amount):
        FLHook.HkAddCash(self.getName(), amount)

    def getCash(self):
        return FLHook.HkGetCash(self.getName())

    def kick(self, reason=None):
        if reason is None:
            FLHook.HkKick(self.getName())
        else:
            FLHook.HkKickReason(self.getName(), reason)

    def ban(self):
        FLHook.HkBan(self.getName(), True)

    def unban(self):
        FLHook.HkBan(self.getName(), False)

    def beam(self, base):
        FLHook.HkBeam(self.getName(), base)

    def getRep(self, faction):
        return FLHook.HkGetRep(self.getName(), faction)

    def setRep(self, faction, value):
        return FLHook.HkSetRep(self.getName(), faction, value)

    def getCharFileName(self):
        return FLHook.HkGetCharFileName(self.getName())

    def getAccountDirName(self):
        return FLHook.HkGetAccountDirName(self.getName())

    def getCharFile(self):
        return CharFile(self.getAccountDirName(), "%s.fl" % self.getCharFileName())

#==============================================================================
# 
#==============================================================================

    def inMenu(self):
        return FLHook.HkIsInCharSelectMenu(self.id)

    def enumcargo(self):
        return FLHook.HkEnumCargo(self.getName())