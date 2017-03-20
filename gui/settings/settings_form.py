"""
This module contains code to implement an entry-form style widget that also links
in with an instance of SettingsFile to support dynamic re-assignment of settings
within Goat.
"""

from tkinter import *

from gui import main_gui
from gui.util import input_form
from settings import settings_config

class NewSettingsForm(input_form.Form):
    def onSubmit(self):
        new_setting = self.content['new setting'].get()
        new_value = self.content['value'].get()
        settings_config.add_setting(**{new_setting:new_value})
        self.parent.destroy()

class RemoveSettingsForm(input_form.Form):
    def onSubmit(self):
        setting_to_remove = self.content['setting to remove'].get()
        settings_config.remove_setting(setting_to_remove)
        self.parent.destroy()

class SettingsForm(input_form.DefaultValueForm):
    def __init__(self, entry_list, parent=None, entrysize=40):
        buttons = [('Cancel', self.onCancel, {'side':RIGHT}),
                    ('Submit', self.onSubmit, {'side':RIGHT}),
                    ('Apply', self.onApply, {'side':RIGHT}),
                    ('Add', self.onAdd, {'side':RIGHT}),
                    ('Remove', self.onRemove, {'side':RIGHT})]
        input_form.DefaultValueForm.__init__(self, entry_list, parent, buttons, entrysize)

    def change_settings(self):
        """Function to change settings"""
        for key in self.content:
            if settings_config.get_setting(key) != self.content[key].get():
                settings_config.change_setting(key,self.content[key].get())

    def onSubmit(self):
        """Re-binds settings to values entered in form"""
        self.change_settings()
        self.parent.destroy()

    def onApply(self):
        """Applies settings"""
        self.change_settings()
        self.parent.destroy()
        main_gui.settings_popup() # refresh after changes

    def onAdd(self):
        """Adds a new setting to the settings file"""
        window = Toplevel()
        NewSettingsForm(('new setting', 'value'),window)
        window.wait_window() # blocks execution of following code until new settings added
        self.parent.destroy()
        main_gui.settings_popup() # refreshes settings window with changes

    def onRemove(self):
        """Removes a setting from the settings file"""
        window = Toplevel()
        RemoveSettingsForm(('setting to remove',),window)
        window.wait_window()
        self.parent.destroy()
        main_gui.settings_popup() # refresh after removal too
