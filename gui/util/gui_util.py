"""
This module contains various multi-use tools for constructing GUI interfaces.
"""

from tkinter import *

from bin.initialize_goat import configs

##################
# Helper Classes #
##################

class ComboBoxFrame(Frame):
    def __init__(self, parent=None, choices=None, labeltext=None,
            select_function=None):
        Frame.__init__(self, parent)
        self.choices = choices
        self.pack()
        if labeltext:
            Label(self, text=labeltext).pack()
        self.selected = StringVar()
        self.combobox = ttk.Combobox(self, textvariable=self.selected)
        self.combobox['values'] = (choices if choices else [])
        self.combobox.pack()
        if select_function: # for combobox selection
            self.select_function = select_function
            self.combobox.bind('<<ComboboxSelected>>',
                    lambda x: self.onSelect()) # lambda prevents passing the event object

    def get(self):
        """Convenience function"""
        return self.combobox.get()

    def onSelect(self):
        """Triggers built-in function"""
        self.select_function()

    def add_items(self, items):
        """Convenience function"""
        values = self.combobox['values']
        new_values = []
        if values != '': # either empty string or tuple
            for val in values:
                new_values.append(val) # if tuple, need to add back to list
        for item in items:
            new_values.append(item)
        self.combobox['values'] = new_values

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

    def onSelect(self, *args):
        pass # implement in other subclasses?

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

    def remove_items(self, indices):
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

    def selection(self):
        """Returns current selection"""
        return self.listbox.curselection()

    def get(self, index):
        """Returns item corresponding to index"""
        return self.listbox.get(index)

class InfoPanel(ttk.Label):
    def __init__(self, parent=None, width=-50, anchor='center', justify='center'):
        ttk.Label.__init__(self, parent)
        self.pack(expand=YES,fill=BOTH)
        self.displayInfo = StringVar() # variable watches for updates
        self.config(textvariable=self.displayInfo, # associate label text with variable
                width=width, # set a sane minimum width)
                anchor=anchor,justify=justify) # centre and justify label text
        self.displayInfo.set('') # initialize to an empty value

        self._display = ''
        self.bind('<Configure>', self.draw_info) # re-draw on window resizes

    def update_info(self, values):
        """Implement in sublcass"""
        self._display = values
        self.draw_info()

    def draw_info(self, event=None):
        """Draw on first instantiation"""
        # first ensure root window is updated
        configs['root'].update_idletasks()
        # get current parameters of window
        curr_width = self.winfo_width()
        font_name = self['font']
        # clip any text that is too long
        san = [clip_text(curr_width, font_name, val) for val in self._display]
        # join back into a string
        display_string = ''
        if len(san) > 0:
            for line in san:
                display_string += line + '\n'
        self.displayInfo.set(display_string)

####################
# Helper Functions #
####################

def clip_text(width, font, string):
    """Calculates the approximate character width of a window (in pixels) and
    then clips the desired display string to fit within that window"""
    import tkinter.font as tkf
    f = tkf.Font(family=font) # here font is the name
    char_width = f.measure('0') # 0 is a standard measure for width
    num_chars = width/char_width
    if len(string) < num_chars:
        return string
    else:
        return (''.join([char for i,char in enumerate(string) if i < (num_chars-4)]) + '...')
