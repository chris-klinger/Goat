"""
This module contains code to implement an entry-form style widget that also links
in with an instance of SettingsFile to support dynamic re-assignment of settings
within Goat.
"""

from tkinter import *

from gui.util import input_form
from settings import settings_config

class SettingsForm(input_form.DefaultValueForm):
    def __init__(self, entry_list, parent=None, entrysize=40):
        buttons = [('Cancel', self.onCancel, {'side':RIGHT}),
                    ('Submit', self.onSubmit, {'side':RIGHT}),
                    ('Add', self.onAdd, {'side':RIGHT})]
        input_form.DefaultValueForm.__init__(self, entry_list, parent, buttons, entrysize)

    def onSubmit(self):
        """Re-binds settings to values entered in form"""
        for key in self.content:
            settings_config.change_setting(key,self.content[key].get())
        self.parent.destroy()

    def onAdd(self):
        """Adds a new setting to the settings file"""
        pass
