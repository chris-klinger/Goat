"""
New module to take care of settings using new config-based
interface with the open settings file object
"""

from tkinter import *
from tkinter import ttk

from bin.initialize_goat import configs

from gui.util import gui_util

class SettingsFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack(expand=YES, fill=BOTH)
        # Main body of frame is a paned window
        self.notebook = SettingsNotebook(self)
        # Add the toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(
                side=BOTTOM,
                expand=YES,
                fill=X,
                )
        self.buttons = [
                ('Done', self.onSubmit, {'side':RIGHT}),
                ('Cancel', self.onCancel, {'side':RIGHT}),
                ('Add Setting', self.onAdd, {'side':LEFT}),
                ('Modify Setting', self.onModify, {'side':LEFT}),
                ('Remove Setting', self.onRemove, {'side':LEFT}),
                ]
        for (label,action,where) in self.buttons:
            ttk.Button(
                    self.toolbar,
                    text=label,
                    command=action,
                    ).pack(where)


    def onSubmit(self):
        """Commit changes and then close"""
        configs['settings_db'].commit()
        configs['settings_sets'].commit()
        self.onCancel()


    def onCancel(self):
        """Close window"""
        self.parent.destroy()


    def onAdd(self):
        pass

    def onModify(self):
        pass

    def onRemove(self):
        pass


class SettingsNotebook(ttk.Notebook):
    """
    Main body of settings window. Splits between generic settings
    and default settings for each relevant program.

    Modifying settings relies on selected window.
    """
    def __init__(self, parent=None):
        ttk.Notebook.__init__(self, parent)
        self.general = GeneralSettings(self)
        self.blast = BLASTSettings(self)
        self.hmmer = HMMerSettings(self)
        self.add(self.general, text='General')
        self.add(self.blast, text='BLAST')
        self.add(self.hmmer, text='HMMer')
        self.pack(expand=YES, fill=BOTH)


class BasePanedInfo(gui_util.InfoColumnPanel):#gui_util.StackedInfoPanel):
    """
    Baseclass for various other setting panels to inherit from.

    Each subclass instantiates with a different set of values based on
    the settings it is supposed to display
    """
    def __init__(self, parent=None, set_string=''):
        self._values = []
        self._set_string = set_string
        self.get_values()
        # Now can instantiate widget
        gui_util.InfoColumnPanel.__init__(
                self,
                parent,
                self._values,
                )


    def get_values(self):
        """
        Uses the instance-specific value of 'self._set_string' to access
        relevant DBs and retrieve current values of settings for display.
        """
        ssdb = configs['settings_sets']
        sdb  = configs['settings_db']
        target_set = ssdb[self._set_string]
        for setting in target_set.list_entries():
            sobj = sdb[setting]  # Index is by name
            curr_value = sobj.value
            display = "{} : {}".format(setting,sobj.value)
            self._values.append(display)


class GeneralSettings(BasePanedInfo):
    """
    Handles display of general setting options in Goat.
    """
    def __init__(self, parent=None):
        BasePanedInfo.__init__(
                self,
                parent,
                'general',
                )

class BLASTSettings(BasePanedInfo):
    """
    Handles display of BLAST-related settings in Goat
    """
    def __init__(self, parent=None):
        BasePanedInfo.__init__(
                self,
                parent,
                'blast',
                )


class HMMerSettings(BasePanedInfo):
    """
    Handles display of HMMer-related settings in Goat
    """
    def __init__(self, parent=None):
        BasePanedInfo.__init__(
                self,
                parent,
                'hmmer',
                )


