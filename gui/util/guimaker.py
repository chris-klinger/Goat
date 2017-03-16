"""
Extended Frame to make window menus and toolbars automatically
"""

import sys
from tkinter import *
from tkinter.messagebox import showinfo

class GuiMaker(Frame):
    # class variable
    menuBar = []
    toolBar = []
    helpButton = True

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH) # frame can stretch/resize
        self.start() # for subclass: set menu/toolBar
        self.makeMenuBar()
        self.makeToolBar()
        self.makeWidgets()

    def start(self):
        """Override in subclass: set menu/toolBar with self"""
        pass

    def makeMenuBar(self):
        """Make menu bar at top"""
        menubar = Frame(self, relief=RAISED, bd=2)
        menubar.pack(side=TOP, fill=X)

        for (name, key, items) in self.menuBar:
            mbutton = Menubutton(menubar, text=name, underline=key)
            mbutton.pack(side=LEFT)
            pulldown = Menu(mbutton)
            self.addMenuItems(pulldown, items)
            mbutton.config(menu=pulldown)

        if self.helpButton:
            Button(menubar, text = 'Help',
                    cursor = 'gumby',
                    relief = FLAT,
                    command = self.help).pack(side=RIGHT)

    def addMenuItems(self, menu, items):
        for item in items:
            if item == 'separator':
                menu.add_separator({})
            elif type(item) == list:
                for num in item: # list: disable item list
                    menu.entryconfig(num, state=DISABLED)
            elif type(item[2]) != list:
                menu.add_command(label = item[0],
                                underline = item[1],
                                command = item[2])
            else:
                pullover = Menu(menu)
                self.addMenuItems(pullover, item[2]) # sublist
                menu.add_cascade(label = item[0],
                                underline = item[1],
                                menu = pullover)

    def makeToolBar(self):
        """Makes tool bar at bottom"""
        if self.toolBar:
            toolbar = Frame(self, cursor='hand2', relief=SUNKEN, bd=2)
            toolbar.pack(side=BOTTOM, fill=X)
            for (name, action, where) in self.toolBar:
                Button(toolbar, text=name, command=action).pack(where)

    def makeWidgets(self):
        """Makes 'middle' part last so top/bottom is clipped last"""
        name = Label(self,
                width=40, height=10,
                relief=SUNKEN, bg='white',
                text = self.__class__.__name__,
                cursor = 'crosshair')
        name.pack(expand=YES, fill=BOTH, side=TOP)

    def help(self):
        """Override in subclass"""
        showinfo('Help', 'Sorry, no help for ' + self.__class__.__name__)

if __name__ == '__main__':
    menuBar = [
        ('File', 0,
            [('Open', 0, lambda:0),
            ('Quit', 0, sys.exit)]),
        ('Edit', 0,
            [('Cut', 0, lambda:0),
            ('Paste', 0, lambda:0)]) ]
    toolBar = [('Quit', sys.exit, {'side':LEFT})]

    class TestAppFrameMenu(GuiMaker):
        def start(self):
            self.menuBar = menuBar
            self.toolBar = toolBar

    root = Tk()
    TestAppFrameMenu(Toplevel())
    root.mainloop()
