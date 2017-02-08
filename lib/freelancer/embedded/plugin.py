# -*- coding: utf-8 -*-

# pylint: disable=C0301
# pylint: disable=C0103

import pluginsystem
from FLHook import PrintUserCmdText
from freelancer.embedded import DEFAULT_RETURNCODE, SKIPPLUGINS_NOFUNCTIONCALL

class Plugin(pluginsystem.Plugin):
    _user_commands = None
    def __init__(self, parent):
        pluginsystem.Plugin.__init__(self, parent)
        self._user_commands = [item[9:] for item in dir(self) if item.startswith('_UserCmd_') and not item in ('_UserCmd_Help', '_UserCmd_Process')]


    def _UserCmd_Help(self, event):
        iClientID, text = event.data
        if text and text in self._user_commands:
            try:
                code = getattr(self, "_UserCmd_%s" % text)
                text = code.__doc__

            except AttributeError:
                PrintUserCmdText(iClientID, "Error! Command code is missing, or has no help")
                return SKIPPLUGINS_NOFUNCTIONCALL
            
            for line in text.split('\n'):
                PrintUserCmdText(iClientID, line.lstrip())
            return SKIPPLUGINS_NOFUNCTIONCALL
        
        for item in self._user_commands:
            PrintUserCmdText(iClientID, "/%s" % item)
        return DEFAULT_RETURNCODE


    def _UserCmd_Process(self, event):
        iClientID, text = event.data
        if not text[0] == '/':
            return DEFAULT_RETURNCODE
        try:
            cmd, text = text[1:].split(' ',1)
        except ValueError:
            cmd, text = text[1:], ''
        cmd = cmd.lower()
        if cmd == 'help':
            # create a new event, type UserCmd_Help and new text
            event = pluginsystem.Event(event.sender, 'UserCmd_Help', (iClientID, text), event.tags)
            return self._UserCmd_Help(event)

        if cmd and cmd in self._user_commands:
            try:
                code = getattr(self, "_UserCmd_%s" % cmd)
            except AttributeError:
                PrintUserCmdText(iClientID, "Error! Command code is missing")
                return SKIPPLUGINS_NOFUNCTIONCALL
            try:
                code(iClientID, text)
            except FLHook.Error as msg:
                PrintUserCmdText(iClientID, "Error! %s" % msg)
            return SKIPPLUGINS_NOFUNCTIONCALL
        return DEFAULT_RETURNCODE
