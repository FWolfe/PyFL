# =============================================================================
#
#    Copyright (C) 2015  Fenris_Wolf, YSPStudios
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =============================================================================
"""
    freelancer.embedded.classes - FLHooks embedded classes and structs


    Adding classes to the converter:
    In C++, the basic logic is this:
    
    You need to define a ToPython(class* pointer) function, this is very basic
    PyObject* ToPython(DamageList* hkInfo)
    {
        return pyClassConverter("DamageList", hkInfo);
    };
    
    pyClassConverter takes 2 args, the first is a string of our class name defined
    in the CLASSES dict defined at the bottom of this file.
    The second arg is our pointer. 
    pyClassConverter will call freelancer.embedded._convertClass, with those same
    2 args (but as python objects). The name is looked up in the CLASSES dict and
    mapped to a python class which you will need to create here.
    
    class DamageList(CppClass)

    All classes should be subclasses of CppClass, this will handle all __init__()
    __getattr__(), __setattr__() and __delattr__() methods. There is no need to 
    overload them.

    Your class should have several static attributes defined:
    
    _cname = string name for exception messages
    
    _attr = tuple object containing attribute names, so we can index them by 
        number (this will be important in C++)

    _get_method = a function in the embedded FLHookClasses module you will need
        to create for fetching attribute values

    _set_method = a function in the embedded FLHookClasses module you will need
        to create for setting attribute values

    _func_method = a function in the embedded FLHookClasses module you will need
        to create for calling this classes methods
    
    if your class is ment to be 'readonly' you can skip _set_method, likewise
    if your class has no callable methods you can skip _func_method.
    Thanks to the CppClass inheritance, nothing else needs to be done for handling
    attributes.
    Mapping our python class methods to C++ class functions is almost as easy:
    
    def get_inflictor_id(self):
        return self._func_method(self._ptr, 5, (None,))

    Note our _func_method takes 3 args, first is the pointer (self._ptr), second
    is a int value (in this case 5) so your C++ knows with function to call, third
    is a tuple object which is any extra args C++ should be calling the function with.
    
    Thats all that needs to be done in python, C++ is a bit more work but not much.
    First lets start with the function called by _get_method:
    
    static PyObject* emb_DamageList_GetAttr(PyObject *self, PyObject *pArgs)
    {
        // GET_CAPSULE_DATA is a macro that takes the C++ class our pointer is
        // it will convert it into the 'ptr' variable, and create the iFuncID
        // variable (the index number assigned to the function or attribute we 
        // want), it also creates a PyObject* pFuncArgs, which is the tuple
        // we passed in pythons _func_method
        GET_CAPSULE_DATA(DamageList);
        switch (iFuncID) {
            case 0:
                return Py_BuildValue("I", ptr->iDunno1);
            case 1:
                return Py_BuildValue("N", ptr->damageentries);
            case 2:
                return Py_BuildValue("b", ptr->bDestroyed);
            case 3:
                return Py_BuildValue("I", ptr->iDunno2);
            case 4:
                return Py_BuildValue("I", ptr->iInflictorID);
            case 5:
                return Py_BuildValue("I", ptr->iInflictorPlayerID);
            default:
                return Py_BuildValue("O", Py_None);
        }
    }

    The functions you need to create for _set_method and _func_method are essentially
    the same, except on what it does inbetween the different 'case #' blocks and 
    what its going to return.
    Under all the various class functions theres a block you'll need to add your
    new functions to:
    
    static PyMethodDef FLHookClassesMethods[] = {
        { "DamageList_GetAttr", emb_DamageList_GetAttr, METH_VARARGS, "" },
        .....
        .....
        { NULL, NULL, 0, NULL }
    };

    The first string is the python name for the function, which is called as
    FLHookClasses.DamageList_GetAttr
    
    Easy stuff :)
    
    
"""
import FLHookClasses
from collections import namedtuple

def nullFunc(self, ptr, index, value):
    return None
    
class CppClass(object):
    _ptr = None # pointer to our C++ object
    _cname = 'CppClass' 
    _attr = (None,) # a tuple of attributes in our C++ class
    _get_method = None # embedded function we call for attribute get
    _set_method = None # embedded function we call for attribute set
    _func_method = None # embedded function we call object methods
    
    def __init__(self, ptr):
        # set self._ptr without calling self.__setattr__
        super(CppClass, self).__setattr__('_ptr', ptr)
        #if is_constant:
        #    super(self.__class__, self).__setattr__('_set_method', None)

    def __setattr__ (self, key, value) :
        """override"""
        if hasattr(CppClass, key): # check our default attributes, these cannot be changed after creation
            raise AttributeError('%s.%s attribute can not be changed.' % (self._cname, key))
        try:
            index = self._attr.index(key)
            return self._set_method(self._ptr, index, (value,))
        except ValueError:
            raise AttributeError("'%s' object has no attribute '%s'" % (self._cname, key))
        except TypeError:
            raise AttributeError("'%s' object has no 'set' method (C++ const?)" % self._cname)

    def __getattr__ (self, key) :
        """override"""
        try:
            index = self._attr.index(key)
            if self._get_method:            
                return self._get_method(self._ptr, index, (None,))
        except ValueError:
            raise AttributeError("'%s' object has no attribute '%s'" % (self._cname, key) )

    def __delattr__(self, item) :
        """override"""
        raise AttributeError("'%s' attributes can not be deleted." % self._cname)

# =============================================================================

class Vector(CppClass):
    _cname = 'Vector'
    _attr = ('x', 'y', 'z')
    _get_method = FLHookClasses.Vector_GetAttr
    _set_method = FLHookClasses.Vector_SetAttr


class Quaternion(CppClass):
    _cname = 'Quaternion'
    _attr = ('w', 'x', 'y', 'z')
    _get_method = FLHookClasses.Quaternion_GetAttr
    _set_method = FLHookClasses.Quaternion_SetAttr

#==============================================================================
# 
# class SSPObjUpdateInfo(CppClass):
#     _cname = 'SSPObjUpdateInfo'
#     _attr = ('iShip', 'vDir', 'vPos', 'fTimestamp', 'fDunno', 'throttle', 'cState')
#     _get_method = FLHookClasses.SSPObjUpdateInfo_GetAttr
#     # this class should be constant    
#     _set_method = FLHookClasses.SSPObjUpdateInfo_SetAttr
# 
# 
# class SSPObjCollisionInfo(CppClass):
#     _cname = 'SSPObjCollisionInfo'
#     _attr = ('iColliderObjectID', 'iColliderSubObjID', 'iDamagedObjectID', 'iDamagedSubObjID', 'fDamage')
#     _get_method = FLHookClasses.SSPObjCollisionInfo_GetAttr
#     # this class should be constant    
#     _set_method = FLHookClasses.SSPObjCollisionInfo_SetAttr
# 
# 
# 
#==============================================================================



class DamageList(CppClass):
    _cname = 'DamageList'
    _attr = ('iDunno1', 'damageentries', 'bDestroyed', 'iDunno2', 'iInflictorID', 'iInflictorPlayerID')
    _get_method = FLHookClasses.DamageList_GetAttr
    _set_method = nullFunc
    _func_method = FLHookClasses.DamageList_Functions
    
    def DmgCauseToString(self):
        "static char const *  DmgCauseToString(enum DamageCause);"
        return self._func_method(self._ptr, 1, (None,))

    def add_damage_entry(self, subobj, health, fate):
        "void add_damage_entry(unsigned short,float,enum DamageEntry::SubObjFate);"
        return self._func_method(self._ptr, 2, (subobj, health, fate))
        
    def get_cause(self):
        "enum DamageCause  get_cause(void)const ;"
        return self._func_method(self._ptr, 3, (None,))
        
    def get_hit_pts_left(self, subobj): # not sure about subobj
        "float get_hit_pts_left(unsigned short)const ;"
        return self._func_method(self._ptr, 4, (subobj,))
        
    def get_inflictor_id(self):
        "unsigned int get_inflictor_id(void)const ;"
        return self._func_method(self._ptr, 5, (None,))

    def get_inflictor_owner_player(self):
        "unsigned int get_inflictor_owner_player(void)const ;"
        return self._func_method(self._ptr, 6, (None,))
        
    def is_destroyed(self):
        "bool is_destroyed(void)const ;"
        return self._func_method(self._ptr, 7, (None,))
        
    def is_inflictor_a_player(self):
        "bool is_inflictor_a_player(void)const ;"
        return self._func_method(self._ptr, 8, (None,))

    def set_cause(self, cause):
        "void set_cause(enum DamageCause);"
        return self._func_method(self._ptr, 9, (cause,))
    
    def set_destroyed(self, destroyed):
        "void set_destroyed(bool);"
        return self._func_method(self._ptr, 10, (destroyed,))
    
    def set_inflictor_id(self, obj_id):
        "void set_inflictor_id(unsigned int);"
        return self._func_method(self._ptr, 11, (obj_id,))
    
    def set_inflictor_owner_player(self, client_id):
        "void set_inflictor_owner_player(unsigned int);"
        return self._func_method(self._ptr, 12, (client_id,))

class ClientInfo(CppClass):
    _cname = 'ClientInfo'
    _attr = (
        'iShip', 'iShipOld', 'tmSpawnTime', 'dmgLast', 'lstMoneyFix', 'iTradePartner',
        'bCruiseActivated', 'bThrusterActivated', 'bEngineKilled', 'bTradelane', 
        'iBaseEnterTime', 'iCharMenuEnterTime', 'tmKickTime', 'iLastExitedBaseID',
        'bDisconnected', 'bCharSelected', 'tmF1Time', 'tmF1TimeDisconnect', 'lstIgnore',
        'dieMsg','dieMsgSize', 'dieMsgStyle', 'chatSize', 'chatStyle',
        'bAutoBuyMissiles', 'bAutoBuyMines', 'bAutoBuyTorps', 'bAutoBuyCD', 'bAutoBuyCM',
        'bAutoBuyReload', 'iKillsInARow',
        'iConnects', 'wscHostname', 'bSpawnProtected', 'bUseServersideHitDetection', 
        'unused_data',
    )
    _get_method = FLHookClasses.ClientInfo_GetAttr
    
    
    
# =============================================================================
CONSTS = {
    'Vector' : namedtuple('Vector', ('x', 'y', 'z')),
    'Quaternion' : namedtuple('Quaternion', ('w', 'x', 'y', 'z')),
    'SSPObjUpdateInfo' : namedtuple('SSPObjUpdateInfo', ('iShip', 'vDir', 'vPos', 'fTimestamp', 'fDunno', 'throttle', 'cState')),
    'SSPObjCollisionInfo' : namedtuple('SSPObjCollisionInfo', ('iColliderObjectID', 'iColliderSubObjID', 'iDamagedObjectID', 'iDamagedSubObjID', 'fDamage')),
    'SLoginInfo' : namedtuple('SLoginInfo', ("wszAccount",)),
    'SStartupInfo' : namedtuple('SStartupInfo', ('iDunno', "iMaxPlayers",)),
    'SCreateCharacterInfo' : namedtuple('SCreateCharacterInfo', ('wszCharname', 'iNickName', 'iBase', 'iPackage', 'iPilot', 'iDunno')),
    'XFireWeaponInfo' : namedtuple('XFireWeaponInfo', ('iDunno1', 'vDirection', 'iDunno2', 'sArray1', 'sArray2', 's3')),
    'XActivateEquip' : namedtuple('XActivateEquip', ("iSpaceID", "sID", "bActivate")),
    'XActivateCruise' : namedtuple('XActivateCruise', ("iShip", "bActivate")),
    'XActivateThrusters' : namedtuple('XActivateThrusters', ("iShip", "bActivate")),
    'XSetTarget' : namedtuple('XSetTarget', ("iShip", "iSlot", "iSpaceID", "iSubObjID")),
    'XGoTradelane' : namedtuple('XGoTradelane', ("iShip", "iTradelaneSpaceObj1", "iTradelaneSpaceObj2")),
    'XJettisonCargo' : namedtuple('XJettisonCargo', ("iShip", "iSlot", "iCount")),
    'XSetManeuver' : namedtuple('XSetManeuver', ("iShipFrom", "IShipTo", "iFlag")),
    'SGFGoodSellInfo' : namedtuple('SGFGoodSellInfo', ("l1", "iArchID", "iCount")),
    'SGFGoodBuyInfo' : namedtuple('SGFGoodBuyInfo', ("iBaseID", "lNull", "iGoodID", "iCount")),
    'SSPMunitionCollisionInfo' : namedtuple('SSPMunitionCollisionInfo', ("iProjectileArchID", "dw2", "dwTargetShip", "s1")),
    'EquipDesc' : namedtuple('EquipDesc', ("iDunno", "sID", "iArchID", "bMounted", "fHealth", "iCount", "bMission", "iOwner")),
    'CHARACTER_ID' : namedtuple('CHARACTER_ID', ("szCharFilename")),
    'CARGO_INFO' : namedtuple('CARGO_INFO', ("iID", "iCount", "iArchID", "fStatus", "bMission", "bMounted")),
    'MONEY_FIX' : namedtuple('MONEY_FIX', ("wscCharname", "iAmount")),

    'IGNORE_INFO' : namedtuple('IGNORE_INFO', ("wscCharname", "wscFlags")),
    'RESOLVE_IP' : namedtuple('RESOLVE_IP', ("iClientID", "iConnects", "wscIP", "wscHostname")),
    'CLIENT_INFO' : namedtuple('CLIENT_INFO', ('iShip', 'iShipOld', 'iTradePartner', 'bCruiseActivated', 'bThrusterActivated', 'bEngineKilled', 
        'bTradelane', 'iBaseEnterTime', 'iCharMenuEnterTime', 'iLastExitedBaseID', 'bDisconnected', 'bCharSelected',
        'bAutoBuyMissiles', 'bAutoBuyMines', 'bAutoBuyTorps', 'bAutoBuyCD', 'bAutoBuyCM', 'bAutoBuyReload',
        'iKillsInARow', 'iConnects', 'wscHostname', 'bSpawnProtected', 'bUseServersideHitDetection')),
    'HKPLAYERINFO' : namedtuple('HKPLAYERINFO', ("iClientID", "wscCharname",  "wscBase", "wscSystem", "iSystem", "iShip", "wscIP", "wscHostname")),

    'DamageEntry' : namedtuple('DamageEntry', ('subobj', 'health', 'fate')),
    'DamageList' : namedtuple('DamageList', ('iDunno1', 'damageentries', 'bDestroyed', 'iDunno2', 'iInflictorID', 'iInflictorPlayerID')),
    'SSPUseItem' : namedtuple('SSPUseItem', ('object', 'hpid', 'quantity')),
}

CLASSES = {
    'Vector' : Vector,
    'Quaternion' : Quaternion,
    #'SSPObjUpdateInfo' : SSPObjUpdateInfo,
    #'SSPObjCollisionInfo' : SSPObjCollisionInfo,
    'DamageList' : DamageList,
    'ClientInfo' : ClientInfo,
}




def convertConst(struct_type, args):
    """_convertStruct(struct_type, args)
    internal function called from C++, pyConverter() function. converts a struct to a namedtuple
    """
    return CONSTS[struct_type](*args)

def convertClass(class_type, ptr):
    """_convertClass(class_type, args)
    internal function called from C++, pyConverter() function.
    """
    return CLASSES[class_type](ptr)

