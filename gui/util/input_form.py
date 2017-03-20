"""
This module implements a reusable input form class
"""

from tkinter import *

class Form:
    def __init__(self, labels, parent=None, entrysize=40):
        labelsize = max(len(x) for x in labels) + 2
        box = Frame(parent)
        box.pack(expand=YES, fill=X)
        rows = Frame(box, bd=2, relief=GROOVE)
        rows.pack(side=TOP, expand=YES, fill=X)
        self.content = {}
        self.parent = parent

        for label in labels:
            row = Frame(rows)
            row.pack(fill=X)
            Label(row, text=label, width=labelsize).pack(side=LEFT)
            entry = Entry(row, width=entrysize)
            entry.pack(side=RIGHT, expand=YES, fill=X)
            self.content[label] = entry
        Button(box, text='Cancel', command=self.onCancel).pack(side=RIGHT)
        Button(box, text='Submit', command=self.onSubmit).pack(side=RIGHT)
        box.master.bind('<Return>', (lambda event: self.onSubmit()))

    def onSubmit(self): # override in subclass
        for key in self.content:
            print(key, '\t=>\t', self.content[key].get())

    def onCancel(self): # override if necessary
        self.parent.destroy()

class DefaultValueForm:
    """Like Form, but each entry has a default value"""
    def __init__(self, entry_list, parent=None, buttons=None, entrysize=40):
        labelsize = max(len(x) for x,y in entry_list) + 2
        box = Frame(parent)
        box.pack(expand=YES, fill=X)
        rows = Frame(box, bd=2, relief=GROOVE)
        rows.pack(side=TOP, expand=YES, fill=X)
        if not buttons: # default values
            self.buttons = [('Cancel', self.onCancel, {'side':RIGHT}),
                        ('Submit', self.onSubmit, {'side':RIGHT})]
        else:
            self.buttons = buttons
        self.content = {}
        self.parent = parent

        for label,value in entry_list:
            row = Frame(rows)
            row.pack(fill=X)
            Label(row, text=label, width=labelsize).pack(side=LEFT)
            entry = Entry(row, width=entrysize)
            entry.pack(side=RIGHT, expand=YES, fill=X)
            entry.insert(0,value)
            self.content[label] = entry

        if self.buttons:
            for (label, action, where) in self.buttons:
                Button(box, text=label, command=action).pack(where)

    def onSubmit(self):
        pass

    def onCancel(self):
        self.parent.destroy()

class DynamicForm(Form):
    def __init__(self, labels=None):
        labels = input('Enter field names: ').split()
        Form.__init__(self, labels)
    def onSubmit(self):
        print('Field values...')
        Form.onSubmit(self)
        self.onCancel()
