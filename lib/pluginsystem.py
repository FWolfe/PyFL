# -*- coding: utf-8 -*-
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
    pluginsystem - A simplified way of adding plugin support for your project.

    To create a plugin, each plugin should have its own file (module) in a
    directory python can import from. All thats required in your plugin module:

    import pluginsystem
    class Plugin(pluginsystem.Plugin):
        name = 'my_plugin'
        author = 'me'
        version = '0.01'

        def __init__(self):
            "initial code goes here"

        def start(self):
            "start up code goes here"

        def step(self):
            "loop code goes here"

        def _MY_CUSTOM_EVENT(self, event):
            "custom event code goes here"

    You do not need to create the actual object (ie: plugin = Plugin()), and
    should not have any code outside of the Plugin class (or very minimal code)
    Anything outside should be kept to the __init__ method.

    To send messages to other plugins, your plugin class should call:
    self.sigout("MY_CUSTOM_EVENT", some_data_variable)

    This would trigger the _MY_CUSTOM_EVENT() method in any other plugins.

    Your main project should include:

    import pluginsystem
    plugins = pluginsystem.PluginContainer()
    plugins.load_plugin("my_project.my_plugin", 10) # 10 is priority, can be any int >= 0
    plugins.start() # after all plugins have been loaded

    and in your programs main loop:
    plugins.step()

"""
# pylint: disable=C0301
# pylint: disable=C0103

import importlib
import sys
from collections import namedtuple
import blist
Event = namedtuple('Event', ('sender', 'type', 'data', 'tags'))

def _defaultLogger(plugin, message):
    """_defaultLogger(message)
    Default logging method. Prints the message.
    """
    print message

class NotLoadedError(Exception):
    """NotLoadedError
    Raised when a named plugin isnt loaded.
    """
    pass


class Plugin(object):
    """Plugin()
    """
    name = ''
    author = ''
    version = ''
    parent = None
    config = None
    priority = 50
    __file__ = None
    def __init__(self, parent):
        self.parent = parent

    def start(self):
        """Plugin.start()
        Dummy method to be overwritten, called after all plugins have been loaded
        """
        pass

    def step(self):
        """Plugin.step()
        Dummy method to be overwritten, called each step of the main loop.
        """
        pass

    def sigout(self, event_type, data):
        """Plugin.sigOut(event_type, data)
        Sends a signal to all other plugins, do not overwrite this method.
        """
        self.parent.signal(self, event_type, data)

    def sigin(self, event):
        """sigIn(event)
        Handles signal input, checks if the plugin has a _EVENT_TYPE method,
        and calls it.
        """

        assert isinstance(event, Event)
        try:
            code = getattr(self, '_%s' % event.type)
        except AttributeError:
            return 0
        assert callable(code)
        result = code(event)
        return result


    def root(self):
        """Plugin.root()
        Returns our parents parent, a PluginContainer object.
        """
        return self.parent.parent


    def conf(self, name=None):
        """Plugin.config(name=None)
        Returns the value of the config attribute. If name is specified, returns
        a sibling plugins config attribute or raises a NotLoadedError.
        """
        if name is None:
            return self.config
        try:
            return self.parent[name].config
        except KeyError:
            raise NotLoadedError


    def rel(self, name):
        """Plugin.rel(name)
        Returns a sibling plugin, or raises a NotLoadedError.
        """
        try:
            return self.parent[name]
        except KeyError:
            raise NotLoadedError

    def unload(self):
        """Plugin.unload()
        Dummy method to be overwritten, called when a plugin is unloading.
        """
        pass

#==============================================================================
# 
#==============================================================================
class PluginList(dict):
    """PluginList(parent, plugin_path)
    A dict-like object representing a collection of plugins, keys are plugin
    names, while values are Plugin() objects.
    The plugin_path argument should be in module format ie: 'my_project.plugins'
    and importable by python.
    """
    name = 0
    order = None
    parent = None
    debug = False
    log = _defaultLogger
    logtypes = None
    plugin_path = None
    def __init__(self, parent, plugin_path):
        dict.__init__(self)
        self.order = blist.sortedlist([])
        self.parent = parent
        self.logtypes = {}
        self.plugin_path = plugin_path


    def is_loaded(self, name):
        """PluginList.isLoaded(name)
        Returns True if the plugin is loaded, or False
        """
        if self.has_key(name):
            return True
        return False


    def load_plugin(self, name, priority=None):
        """PluginList.loadPlugin(full_name, priority)
        """
        try:
            full_name = "%s.%s" % (self.plugin_path, name)
            self.log("Loading %s Plugin... (%s)" % (name, full_name))
            lib = importlib.import_module(full_name)
            plugin = lib.Plugin(self)
            plugin.__file__ = full_name
            self[plugin.name] = plugin

            if priority is None:
                priority = plugin.priority
            else:
                plugin.priority = priority
            self.order.add((plugin.priority, plugin.name))
            return plugin

        except Exception as msg:
            self.log("Failed! %s" % msg)
            return None


    def loadlist(self, pending):
        """PluginList.
        """
        while pending:
            priority, full_name = pending.pop(0)
            self.load_plugin(full_name, priority)


    def unload_plugin(self, name):
        """PluginList.
        """
        try:
            plugin = self[name]
        except KeyError:
            raise NotLoadedError
        
        plugin.unload()
        del self[plugin.name]
        del sys.modules[plugin.__file__]

        index = self.order.index((plugin.priority, plugin.name))
        self.order.pop(index)
        return True


    def reload_plugin(self, name):
        """PluginList.
        """
        self.unload_plugin(name)
        plugin = self.load_plugin(name)
        if plugin is None:
            return False
        plugin.start()
        return True


    def start(self):
        """PluginList.start()
        Calls Plugin.start() for all loaded plugins
        """
        for _, p in self.order:
            self[p].start()


    def step(self):
        """PluginList.step()
        Calls Plugin.step() for all loaded plugins
        """
        for _, p in self.order:
            self[p].step()


    def sigout(self, event_type, data):
        """PluginList.sigOut(event_type, data)
        Calls PluginList.signal, with self as the sender.
        """
        return self.signal(self, event_type, data)


    def signal(self, sender, event_type, data):
        """PluginList.signal(sender, event_type, data)
        Triggers a Plugin.sigIn() method call for all loaded plugins.
        Any plugin that returns True will halt processing of the rest of the
        plugins.
        sender should be a Plugin object or self.
        """
        event = Event(sender, event_type, data, {})
        halt = 0
        #C:/Development/PyFL/lib\pluginsystem.py:294: RuntimeWarning: tp_compare didn't return -1 or -2 for exception
        #if self.logtypes.get(event.type, self.debug) != False:
        #    <type 'exceptions.TypeError'>: an integer is required
        try:
            if self.logtypes.get(event.type, self.debug) != False:
                self.log("%s : %s : %s" % (event.sender.name, event.type, event.data))
        except Exception as msg:
            self.log("odd runtime bug: %s" % str(msg))

        for _, name in self.order:
            try:
                halt = self[name].sigin(event)
            except Exception as msg:
                self.log("(%s) %s ERR: %s\n" % (name, str(event), str(msg)))
                #if self.debug:
                #    exit()

            if halt:
                break
        return halt

#==============================================================================
# 
#==============================================================================
class PluginContainer(object):
    """PluginContainer(plugin_path)
    Object class reprenting a collection of plugins. It has a single attribute:
    plugins (a PluginList object). 
    Its methods are mostly conventant wrappers for PluginList methods. A
    PluginContainer is not entirely necessary, as you can create and access a 
    PluginList directly.

    However, this is ment to be a base class your container should inherit.
    
    The plugin_path argument should be in module format ie: 'my_project.plugins'
    and importable by python.
    """

    def __init__(self, plugin_path):
        self.plugins = PluginList(self, plugin_path)

    def is_loaded(self, name):
        """PluginContainer.isLoaded(name)
        Wrapper for PluginList.isLoaded method
        """
        return self.plugins.is_loaded(name)

    def load_plugin(self, name, priority):
        """PluginContainer.loadPlugin(name, priority)
        Wrapper for PluginList.loadPlugin method
        """
        return self.plugins.load_plugin(name, priority)

    def unload_plugin(self, name):
        """PluginContainer.unloadPlugin(name)
        Wrapper for PluginList.unloadPlugin method
        """
        return self.plugins.unload_plugin(name)

    def reload_plugin(self, name):
        """PluginContainer.reloadPlugin(name)
        Wrapper for PluginList.reloadPlugin method
        """
        return self.plugins.reload_plugin(name)

    def loadlist(self, pending):
        """PluginContainer.loadList(pending)
        Wrapper for PluginList.loadList method
        """
        return self.plugins.loadlist(pending)

    def start(self):
        """PluginContainer.start()
        Wrapper for PluginList.start method
        """
        return self.plugins.start()

    def step(self):
        """PluginContainer.step()
        Wrapper for PluginList.step method
        """
        return self.plugins.step()

    def sigout(self, event_type, data):
        """PluginContainer.sigOut(event_type, data)
        Wrapper for PluginList.sigOut method
        """
        self.plugins.sigout(event_type, data)

    def signal(self, sender, event_type, data):
        """PluginContainer.signal(sender, event_type, data)
        Wrapper for PluginList.signal method
        """
        self.plugins.signal(sender, event_type, data)

