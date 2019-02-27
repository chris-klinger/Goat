"""
This module contains various multi-use tools for constructing GUI interfaces.
"""

from tkinter import *
import tkinter.font as tkf


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

    def set(self, value):
        """Sets value of combobox"""
        self.combobox.set(value)

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

    def remove_items(self, items):
        """Convenience function"""
        values = self.combobox['values']
        new_values = []
        for item in values:
            if not item in items:
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

    def get(self):
        """Convenience function"""
        return self.selected.get()

class CheckBoxFrame(Frame):
    def __init__(self, parent=None, labeltext=None, place=None,
            button_text='Yes'):
        Frame.__init__(self, parent)
        if place == 'LEFT':
            self.pack(side=LEFT)
        else:
            self.pack()
        if labeltext:
            Label(self, text=labeltext).pack()
        self.checked = IntVar()
        if button_text:
            self.checkbutton = ttk.Checkbutton(self, text=button_text,
                    variable=self.checked).pack()
        else:
            self.checkbutton = ttk.Checkbutton(self,
                    variable=self.checked).pack()

    def button_checked(self):
        """Returns True if checked, False otherwise"""
        if self.checked.get() == 1:
            return True
        else:
            return False

class CheckBoxGroup(Frame):
    def __init__(self, parent, labels=None, labeltext=None):
        """
        Utility widget to group numerous check boxes together into a single frame
        arrayed across like a RadioBox. Main difference is that any number of
        these may be checked.
        """
        Frame.__init__(self, parent)
        self.pack()
        if labeltext:
            Label(self, text=labeltext).pack()
        self.buttons = []
        self.button_frame = Frame(self)
        self.button_frame.pack()
        if labels:
            self.add_buttons(labels)

    def add_buttons(self, labels):
        """Adds buttons"""
        for label in labels:
            button = CheckBoxFrame(self.button_frame, labeltext=label,
                    place='LEFT', button_text=None)
            self.buttons.append([label,button]) # keep track of instance variables

    def get(self):
        """Returns a dict with button label/checked pairs"""
        bdict = {}
        for label,button in self.buttons:
            bdict[label] = button.button_checked() # True/False
        return bdict

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
        self.item_index = {} # hashtable for item index in other widget
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

    def add_items(self, items, mode='end'): #, index_dict=None):
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
                    #print('index before: ' + str(index))
                    new_index = self.get_new_index(item,index) #,index_dict)
                    #print('index after: ' + str(index))
                    self.listbox.insert(new_index,item)
                    self.item_list.insert(new_index,item) # keep inherent index in list
                    self.item_dict[item] = value

    def get_new_index(self, item, index): #, index_dict):
        """Subtracts from index for every value missing before it"""
        new_index = index
        for sitem,sindex in sorted(self.item_index.items(), key=lambda x: x[1]):
            #print(sitem)
            #print(sindex)
            if sindex > index:
                return new_index
            else:
                if not item == sitem:
                    if sitem not in self.item_list:
                        #print('decrementing index')
                        new_index -= 1
        return new_index # last element

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

    def clear(self):
        """Removes all entries"""
        indices = list(range(len(self.item_list)))
        self.remove_items(indices)

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


class InfoColumnPanel(ttk.Label):#ttk.Entry):
    """
    Provides a simple "label-like" interface to display text with. This
    widget should determine, based on the values profided and the size of
    the parent frame, how to stack rows and then space values.
    """
    def __init__(
            self,
            parent,
            values,
            width=50,
            justify='left',
            gap=3,
            max_cols=4,
            #values=[],
            textvariable='',
            #state='readonly',
            ):
        ttk.Label.__init__(self, parent) #, width)
        self._parent = parent
        self._width = width
        self._values = values
        self._gap = gap  # desired spacing between values
        self._max_cols = max_cols # user-specified number of cols to display
        # Values that are calculated for drawing
        #self._max_length = 1  # maximum length of all values
        self._char_width = 0  # Actual width of a character
        self._gap_width = 0  # Actual width of a gap
        self._real_max = 0    # Actual width of the maximum value
        self._real_gap = 0   # Width of the specified number of gaps
        self._num_cols = 1  # number of columns to display
        self._to_display = StringVar()
        self.config(
                textvariable=self._to_display,
                width=width,
                justify=justify,
                #state=state,
                )
        self.pack(expand=YES, fill=BOTH)
        # Configure actual text display
        self.bind('<Configure>', self._draw_info) # re-draw on window resizes

        # Draw on intial instantiation
        self._display = self._values
        self._draw_info()


    def update_info(self, values):
        """Updates internal list and forces re-draw"""
        self._display = values
        self._draw_info()


    def _draw_info(self, event=None):
        """
        Determines own width and then uses that to calculate, from the
        list of values, the maximum number of columns and required
        spacing for each row
        """
        # First ensure root window is updated
        configs['root'].update_idletasks()
        # get current parameters of window
        curr_width = self.winfo_width()
        font_name = self['font']
        # Figure out parameters from values
        self._determine_num_cols(curr_width, font_name)
        # Create formatted string
        display_string = self._create_display_string()
        # Finally, update linked variable
        self._to_display.set(display_string)


    def _determine_num_cols(self, width, font):
        """
        Given the desired width of the window, determine how many columns
        could be used to display the values and update two private instance
        variables accordingly
        """
        # Determine values based on font
        f = tkf.Font(family=font)  # name of the font
        self._char_width = f.measure('0')  # standard char for avg width
        self._gap_width = f.measure(' ')   # actual width of a gap
        # Now determine how many columns are needed
        sorted_vals = sorted(
                self._values,
                reverse = True,  # largest values first
                key=lambda x: len(x),
                )
        self._real_max = len(sorted_vals[0]) * self._char_width
        self._real_gap = self._gap_width * self._gap  # Actual width of the gap
        total_length = 0
        num_cols = 1
        for value in sorted_vals:
            val_length = len(value) * self._char_width
            max_required = total_length + val_length + (num_cols * self._real_gap)
            if max_required >= width:  #self._width:  # too wide
                print("breaking due to max length")
                break
            else:
                total_length += val_length  # keep track
                num_cols += 1
                if num_cols >= self._max_cols:
                    print("Currently want {} columns".format(num_cols))
                    print("breaking due to max cols")
                    break  # reached cutoff
        self._num_cols = num_cols


    def _create_display_string(self):
        """
        Given the desired width of the window and the number of values
        expected for each row, create a formatted string.

        A single value per row is easy, but may require clipping (check).

        If num_vals > 1, then this means that no clipping is required,
        but that the length of the gap will need to be calculated for
        each row to ensure that subsequent columns line up
        """
        num_vals = len(self._values)
        num_rows = num_vals//self._num_cols  # rounds down
        if num_vals%self._num_cols != 0:  # i.e. does not perfectly divide it
            num_rows += 1
        rows = [self._values[(i*self._num_cols):(i*self._num_cols+self._num_cols)]
                for i in range(num_rows)]
        # Iterate over rows to create display string
        display_string = ''
        for row in rows:
            row_string = self._create_row_string(row)
            display_string += row_string + '\n'
        return display_string


    def _create_row_string(self, row):
        """
        Given a row with an arbitrary number of values, create a
        single formatted string such that all values will be properly
        spaced when multiple rows are created.
        """
        row_string = ''
        column_width = self._real_max + self._real_gap  # All entries must add up to this!
        if len(row) == 1:  # Single value, nothing to do
            row_string += row[0]
        else:
            for i,value in enumerate(row):  # Enumerate is 0-indexed
                if i == 0:
                    row_string += value
                else:
                    num_gaps = ((column_width - (
                    (len(row[i-1]) * self._char_width) + # Previous value
                    (self._real_gap)  # Gap width
                    )) //  # Round down
                    (self._gap_width))
                    row_string += (' ' * num_gaps)
                    row_string += (' ' * self._gap)
                    row_string += value
        return row_string



####################
# Helper Functions #
####################

def clip_text(width, font, string):
    """
    Calculates the approximate character width of a window (in pixels) and
    then clips the desired display string to fit within that window
    """
    import tkinter.font as tkf
    f = tkf.Font(family=font) # here font is the name
    char_width = f.measure('0') # 0 is a standard measure for width
    num_chars = width/char_width
    if len(string) < num_chars:
        return string
    else:
        return (''.join([char for i,char in enumerate(string) if i < (num_chars-4)]) + '...')
