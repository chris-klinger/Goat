"""
This module contains various multi-use tools for constructing GUI interfaces.
"""

from tkinter import *

class ComboBoxFrame(Frame):
    def __init__(self, parent=None, choices=None, labeltext=None):
        Frame.__init__(self, parent)
        self.choices = choices
        self.pack()
        if labeltext:
            Label(self, text=labeltext).pack()
        self.selected = StringVar()
        self.combobox = ttk.Combobox(self, textvariable=self.selected)
        self.combobox['values'] = (choices if choices else [])
        self.combobox.pack()

class RadioBoxFrame(Frame):
    def __init__(self, parent=None, choices=None, labeltext=None):
        Frame.__init__(self, parent)
        self.choices = choices
        self.pack()
        if labeltext:
            Label(self, text=labeltext).pack()
        self.selected = StringVar()
        for text,var in self.choices:
            ttk.Radiobutton(self, text=text, variable=self.selected,
                            value=var).pack(side=LEFT)
        self.selected.set(var) # set to last value

class CheckBoxFrame(Frame):
    def __init__(self, parent=None, labeltext=None):
        Frame.__init__(self, parent)
        self.pack()
        if labeltext:
            Label(self, text=labeltext).pack()
        self.checked = IntVar()
        self.checkbutton = ttk.Checkbutton(self, text='Yes',
                        variable=self.checked).pack()

class ScrollBoxFrame(Frame):
    def __init__(self, parent=None, text=None, items=None,
            other_widget=None, mode='extended'):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.other = other_widget
        if text:
            Label(self, text=text).pack(side=TOP)
        self.item_list = [] # internal list mapping to listbox list
        self.item_dict = {} # hashtable for listbox items
        self.listbox = Listbox(self, height=20, selectmode=mode)
        self.listbox.bind('<<ListboxSelect>>', self.onSelect)
        self.listbox.pack(side=LEFT, expand=YES, fill=BOTH)
        vs = ttk.Scrollbar(self, orient=VERTICAL, command=self.listbox.yview)
        vs.pack(side=RIGHT)
        self.listbox['yscrollcommand'] = vs.set
        if items:
            self.add_items(items)

    def add_items(self, items, mode='end'):#item_dict):
        """General case addition of items"""
        if mode == 'end': # add each item to end of list
            for item,value in items: #item_dict.items():
                if not item in self.item_list: # do not add duplicate items
                    self.listbox.insert('end', item)
                    self.item_list.append(item)
                    self.item_dict[item] = value
        elif mode == 'index': # add back into old place in list
            for item,value,index in items:
                if not item in self.item_list:
                    self.listbox.insert(index, item)
                    self.item_list.insert(index,item) # keep inherent index in list
                    self.item_dict[item] = value

    def remove_items(self, *indices):
        """General case removal of items - note that removal is by index so
        must account for different length of list upon each subsequent item
        removal otherwise remove incorrect item(s) and risk ValueError"""
        num_removals = 0
        for index in indices:
            index -= num_removals # account for removing previous items
            item = self.listbox.get(index)
            self.listbox.delete(index)
            self.item_list.remove(item)
            del self.item_dict[item]
            num_removals += 1

    def onSelect(self, *args):
        pass # implement in other subclasses?
