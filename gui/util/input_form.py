"""
This module implements a reusable input form class
"""

from tkinter import *

class Form:
    def __init__(self, labels, parent=None, other_widget=None, entrysize=40):
        labelsize = max(len(x) for x in labels) + 2
        box = Frame(parent)
        box.pack(expand=YES, fill=X)
        rows = Frame(box, bd=2, relief=GROOVE)
        rows.pack(side=TOP, expand=YES, fill=X)
        self.content = {}
        self.parent = parent
        self.other = other_widget

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

class DefaultValueForm(Frame):
    """Like Form, but each entry has a default value"""
    def __init__(self, entry_list, parent=None, buttons=None, entrysize=40):
        Frame.__init__(self, parent)
        self.labelsize = max(len(x) for x,y in entry_list) + 2
        self.entrysize = entrysize
        self.pack(expand=YES, fill=X)
        self.rows = Frame(self, bd=2, relief=GROOVE)
        self.rows.pack(side=TOP, expand=YES, fill=X)
        self.row_list = [] # stores all instances
        if not buttons: # default values
            self.buttons = [('Cancel', self.onCancel, {'side':RIGHT}),
                        ('Submit', self.onSubmit, {'side':RIGHT})]
        else:
            self.buttons = buttons
        self.content = {}
        self.parent = parent

        for label,value in entry_list:
            row = EntryRow(label, self.rows, value, self,
                    self.labelsize, self.entrysize)
            self.row_list.append(row) # allows access to entry rows for changing

        if self.buttons:
            for (label, action, where) in self.buttons:
                Button(self, text=label, command=action).pack(where)

    def onSubmit(self):
        pass

    def onCancel(self):
        self.parent.destroy()

class EntryRow(Frame):
    """Holds onto references"""
    def __init__(self, label_text, parent=None, entry_value='',
            other_widget=None, labelsize=40, entrysize=40):
        Frame.__init__(self, parent)
        self.label_text = label_text # holds onto instance attributes
        self.pack(fill=X)
        Label(self, text=label_text, width=labelsize).pack(side=LEFT)
        entry = Entry(self, width=entrysize)
        entry.pack(side=RIGHT, expand=YES, fill=X)
        entry.insert(0,entry_value)
        other_widget.content[label_text] = entry

class DynamicForm(Form):
    def __init__(self, labels=None):
        labels = input('Enter field names: ').split()
        Form.__init__(self, labels)
    def onSubmit(self):
        print('Field values...')
        Form.onSubmit(self)
        self.onCancel()
