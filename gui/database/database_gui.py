"""
This module contains code for dealing with viewing and updating databases
"""

import time

from tkinter import *
from tkinter import ttk, filedialog, messagebox

from bin.initialize_goat import configs

from databases import record_file
from gui.util import input_form, gui_util

# holds a set of types for files
# note, these act as reserved keywords for Goat record attributes
valid_file_types = ['protein','genomic']
default_attrs = ['identity','genus','species','strain','supergroup','files']

class DatabaseFrame(Frame):
    def __init__(self, parent=None): #database, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        #self.db = database
        self.db = configs['record_db']
        #self.db_panel = DatabaseGui(database,self)
        self.db_panel = DatabaseGui(self.db,self)
        self.toolbar = Frame(self)
        self.toolbar.pack(expand=YES, side=BOTTOM, fill=X)

        # override parent window destruction handler to ensure DB integrity
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Remove', self.onRemove, {'side':RIGHT}),
                        ('Modify', self.onModify, {'side':RIGHT}),
                        ('Add', self.onAdd, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        """Signals to close database connection when window is closed, but not
        before to prevent ValueError raises from main_gui code block"""
        self.parent.destroy() # destroy window

    def onSubmit(self):
        """Commits changes to database before closing"""
        self.db.commit()
        self.onClose()

    def onRemove(self):
        """Removes an existing record object"""
        item = self.db_panel.current_item() # first (and only) item in list of tags
        if item['tags'][0] == 'record':
            self.db.remove_record(item['text'])
        elif item['tags'][0] == 'file':
            pass # do we want to be able to remove files directly?

    def onModify(self):
        """Allows user to modify a pre-existing record.

        Current implementation involves retrieving db information and
        passing it to a NewRecordForm, which already contains all the
        methods to deal with adding/removing/changing attributes."""
        item = self.db_panel.current_item()
        if item['tags'][0] == 'record': # first (and only) item in list of tags
            record_obj = self.db[item['text']] # text also holds the ID
            # get default values
            record_list = [('record identity', record_obj.identity),
                ('genus', record_obj.genus), ('species', record_obj.species),
                ('strain', record_obj.strain), ('supergroup', record_obj.supergroup)]
            for k,v in record_obj.__dict__.items():
                if not k in default_attrs:
                    record_list.append((k,v)) # add any other attributes that may be present
            window = Toplevel()
            RecordFrame(record_list, record_obj.files, self.db, self.db_panel, window)
        elif item['tags'][0] == 'file':
            pass # do we want to be able to modify files?

    def onAdd(self):
        """Adds a new record object"""
        window = Toplevel()
        # same as onModify but default values are empty strings
        record_list = [('record identity',''), ('genus',''), ('species',''),
                ('strain',''), ('supergroup','')]
        #RecordFrame(record_list, record_obj.files, self.db, self.db_panel, window)
        RecordFrame(record_list, {}, self.db, self.db_panel, window)

class DatabaseGui(ttk.Panedwindow):
    def __init__(self, database, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        # assign an instance variable, pass in self as the parent to child widgets
        self.info_frame = ttk.Labelframe(self,text='Database Information')
        self.info_panel = InfoPanel(self.info_frame)
        self.db_viewer = DatabaseViewer(database,self.info_panel,self)
        self.add(self.db_viewer)
        self.add(self.info_frame)
        self.pack(expand=YES,fill=BOTH)

        # Set up scrollbars
        #ysb = ttk.Scrollbar(self.db_viewer, orient='vertical', command=self.db_viewer.yview)
        #xsb = ttk.Scrollbar(self.db_viewer, orient='horizontal', command=self.db_viewer.xview)
        #self.db_viewer.configure(yscroll=ysb.set, xscroll=xsb.set)
        #ysb.pack(side=RIGHT, fill=Y)
        #xsb.pack(side=BOTTOM, fill=X)

    def current_item(self):
        """Returns the current item of the db_viewer"""
        item_name = self.db_viewer.focus()
        item = self.db_viewer.item(item_name)
        return item

class DatabaseViewer(ttk.Treeview):
    def __init__(self, database, info_panel, parent=None):
        ttk.Treeview.__init__(self, parent)
        self.db = database
        self.info = info_panel
        self.config(selectmode = 'browse') # select one item at a time only
        self.tag_bind('record', '<Double-1>', # single click doesn't register item properly
                callback=lambda x:self.itemClicked('record'))
        self.tag_bind('file', '<Double-1>',
                callback=lambda x:self.itemClicked('file'))
        self.make_tree()
        self.pack(side=LEFT,expand=YES,fill=BOTH)

    def upate(self):
        """Updates the view upon addition/removal of records"""
        #print('DatabaseViewer update called')
        self.make_tree()

    def make_tree(self):
        """Builds a treeview display of records"""
        #print('Making tree')
        for record in self.db.list_records():
            #print(record)
            record_obj = self.db[record] # should be able to index
            # use record identity as label in tree
            self.insert('','end',record,text=record_obj.identity,tags=('record'))
            # now add files (if present), as subheadings for the record
            for k in record_obj.files.keys():
                self.insert(record,'end',(record + '_' + k),text=k,tags=('file'))

    def itemClicked(self, item_type):
        """Triggered when either records or files are clicked. Builds a list of
        information for display by associated info panel and delegates display
        to that widget"""
        item = self.focus()
        if item_type == 'record':
            rlist = []
            record = self.db[item]
            # genus and species make up header
            rlist.extend([record.genus,record.species])
            for k,v in record.__dict__.items():
                if k != 'files': # skip over files
                    rlist.extend([k,v]) # add other associated information
            self.info.update_info('record', *rlist) # delegates information to display to widget
        elif item_type == 'file':
            flist = []
            record,filename = item.rsplit('_',1)[0], item.rsplit('_',1)[1] # chop back off the name
            record_obj = self.db[record]
            # file ID makes up header
            file_obj = record_obj.files[filename]
            # add additional information
            flist.extend((record_obj.genus, record_obj.species, file_obj.name,
                file_obj.filepath, file_obj.filetype, file_obj.num_entries,
                file_obj.num_lines, file_obj.num_bases))
            self.info.update_info('file', *flist)

class InfoPanel(ttk.Label):
    def __init__(self, parent=None):
        ttk.Label.__init__(self, parent)
        self.pack(side=RIGHT,expand=YES,fill=BOTH)
        self.displayInfo = StringVar() # variable watches for updates
        self.config(textvariable=self.displayInfo, # associate label text with variable
                width=-50, # set a sane minimum width)
                anchor='center',justify='center') # centre and justify label text
        self.displayInfo.set('') # initialize to an empty value

        self._display = ''
        self.bind('<Configure>', self.draw_info)

    def update_info(self,display_type,*values):
        """Takes a list of values and displays it depending on whether the item
        clicked is a record or file"""
        # create a new modified list
        to_display = []
        to_display.append(values[0] + ' ' + values[1])
        if display_type == 'record':
            if len(values) > 2: # additional info present
                for index,value in enumerate(values[2:]):
                    if index % 2 == 0: # even value, key in dictionary
                        temp = ''
                        temp += (values[index+2] + ' ') # +2 compensates for first two list values
                    else: # odd value, value in dictionary
                        temp += (values[index+2])
                        to_display.append(temp)
        else:
            to_display.append('Filename: ' + values[2])
            to_display.append('Filepath: ' + values[3])
            to_display.append('Filetype: ' + values[4])
            to_display.append('Number of entries ' + str(values[5]))
            to_display.append('Number of lines ' + str(values[6]))
            to_display.append('Number of bases ' + str(values[7]))
        self._display = to_display
        self.displayInfo.set('\n'.join([val for val in to_display]))
        self.draw_info()

    def draw_info(self, event=None):
        """Draw on first instantiation"""
        # first ensure root window is updated
        configs['root'].update_idletasks()
        # get current parameters of window
        curr_width = self.winfo_width()
        font_name = self['font']
        # clip any text that is too long
        san = [gui_util.clip_text(curr_width, font_name, val) for val in self._display]
        # join back into a string
        display_string = ''
        if len(san) > 0:
            for line in san:
                display_string += line + '\n'
        self.displayInfo.set(display_string)

class NewAttrForm(input_form.Form):
    def onSubmit(self):
        new_attr = self.content['new attribute'].get()
        new_value = self.content['value'].get()
        self.other.update_attr('add',new_attr,new_value)
        self.parent.destroy()

class NewFileForm(input_form.DefaultValueForm):
    def __init__(self, entry_list, parent=None, other_widget=None, entrysize=40):
        buttons = [('Cancel', self.onCancel, {'side':RIGHT}),
                   ('Submit', self.onSubmit, {'side':RIGHT}),
                   ('Choose file', self.onAdd, {'side':LEFT})]
        input_form.DefaultValueForm.__init__(self, entry_list, parent, buttons, entrysize)
        self.other = other_widget

    def onCancel(self):
        self.parent.destroy()

    def onAdd(self):
        """Pops up file choice dialogue"""
        filepath = filedialog.askopenfilename()
        for entry_row in self.row_list:
            if entry_row.label_text == 'filepath':
                entry_row.entry.insert(0,filepath) # update choice in window

    def onSubmit(self):
        try:
            for key in self.content.keys():
                if self.content[key].get() == '': # no added value
                    raise AttributeError # do not allow submission without info
                if key == 'filename':
                    new_file = self.content[key].get()
                elif key == 'filepath':
                    filepath = self.content[key].get()
                else:
                    filetype = self.content[key].get()
            self.other.add_file(new_file, filepath, filetype)
            self.parent.destroy()
        except(AttributeError):
            # do not allow submission and warn user if values are blank
            messagebox.showwarning('Add File Warning', 'Cannot leave blank entries')

class RemovalFrame(Frame):
    def __init__(self, attrs, attr_widget, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.attr_widget = attr_widget
        self.selected_attr = StringVar()
        self.attr_box = ttk.Combobox(self, textvariable=self.selected_attr)
        self.attr_box['values'] = attrs
        self.attr_box.pack(side=TOP, expand=YES, fill=X)

        self.toolbar = Frame(self)
        self.toolbar.pack(expand=YES, side=BOTTOM, fill=X)

        self.buttons = [('Cancel', self.onCancel, {'side':RIGHT}),
                        ('Submit', self.onSubmit, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onCancel(self):
        self.parent.destroy()

    def onSubmit(self):
        """Signal back to remove attribute"""
        attr = self.selected_attr.get()
        self.attr_widget.update_attr('remove',attr)
        self.parent.destroy()

class RecordFrame(Frame):
    def __init__(self, entry_list, record_files, database, db_widget, parent=None, entrysize=40):
        Frame.__init__(self, parent)
        self.db = database
        self.db_widget = db_widget
        self.parent = parent
        self.pack(expand=YES, fill=BOTH)
        self.record_gui = RecordGui(entry_list, record_files, self)
        self.toolbar = Frame(self)
        self.toolbar.pack(expand=YES, side=BOTTOM, fill=X)

        self.buttons = [('Cancel', self.onCancel, {'side':RIGHT}),
                        ('Submit', self.onSubmit, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onCancel(self):
        self.parent.destroy()

    def onSubmit(self):
        """Adds new or modified record to the database"""
        attrs = self.record_gui.return_attrs()
        record_id = attrs['record identity'].get()
        remaining = {}
        for k in attrs.keys():
            if not (k == 'record identity'):
                remaining[k] = attrs[k].get()
        #if record_id in self.db.keys(): # record is already present
        if record_id in self.db.list_records():
            self.db.update_record(record_id, **remaining)
        else:
            self.db.add_record(record_id, **remaining)
        try:
            for n,p,t in self.record_gui.return_new_files():
                self.db.add_record_file(record_id, n, p, t)
        except(IndexError): # no added files
            pass
        try:
            for n in self.record_gui.return_removed_files():
                self.db.remove_record_file(record_id, n)
        except(IndexError): # no removed files
            pass
        self.db.commit()
        #print(self.db_widget.db_viewer.make_tree)
        self.db_widget.db_viewer.make_tree() # signal back to re-draw tree
        time.sleep(1)
        self.parent.destroy()

class RecordGui(ttk.Panedwindow):
    def __init__(self, entry_list, record_files, parent=None, entrysize=40):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        # assign an instance variable, pass in self as the parent to child widgets
        self.record_frame = ttk.Labelframe(self,text='Record Information')
        self.file_frame = ttk.Labelframe(self,text='File Information')
        self.attr_form = AttributeForm(entry_list,self.record_frame,entrysize)
        self.file_form = FileFrame(record_files,self.file_frame)#.db_frame)
        self.add(self.record_frame)
        self.add(self.file_frame)
        self.pack(expand=YES,fill=BOTH)

    def return_attrs(self):
        """Convenience function to fetch attrs"""
        return self.attr_form.content

    def return_new_files(self):
        """Convenience function"""
        return self.file_form.new_files

    def return_removed_files(self):
        """Convenience function"""
        return self.file_form.removed_files

class AttributeForm(input_form.DefaultValueForm):
    def __init__(self, entry_list, parent=None, entrysize=40):
        buttons = [('Remove Attribute', self.onReAttr, {'side':RIGHT}),
                   ('Add Attribute', self.onAttr, {'side':RIGHT})]
        input_form.DefaultValueForm.__init__(self, entry_list, parent, buttons, entrysize)

    def update_attr(self, update, setting, value=None):
        """Updates window with added entries"""
        if update == 'add':
            new_row = input_form.EntryRow(setting, self.rows, value, self,
                    self.labelsize, self.entrysize)
            self.row_list.append(new_row)
        elif update == 'remove':
            for row in self.row_list:
                if row.label_text == setting:
                    row.destroy()

    def onAttr(self):
        """Adds a new attribute to a record object"""
        window = Toplevel()
        NewAttrForm(('new attribute', 'value'), window, self)

    def onReAttr(self):
        """Removes a record attribute"""
        window = Toplevel()
        RemovalFrame([row.label_text for row in self.row_list],self,window)

class FileFrame(Frame):
    def __init__(self, file_dict, parent=None):
        Frame.__init__(self, parent)
        self.file_dict = file_dict
        self.new_files = [] # keep track of added files
        self.removed_files = [] # keep track of removed files
        self.pack(expand=YES, fill=BOTH)
        self.selected_file = StringVar()
        self.file_box = ttk.Combobox(self, textvariable=self.selected_file)
        # initialize internal values
        self.values = [k for k in self.file_dict.keys()] if self.file_dict.keys() else []
        self.file_box['values'] = self.values
        self.file_box.pack(side=TOP, expand=YES, fill=X)
        self.file_box.bind('<<ComboboxSelected>>', lambda x:self.onSelect())
        self.file_panel = FilePanel(self)

        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, fill=X)

        self.buttons = [('Remove file', self.onReFile, {'side':RIGHT}),
                        ('Add file', self.onAddFile, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSelect(self):
        """Signal to file panel to display associated file information"""
        file_obj = self.file_dict[self.selected_file.get()]
        self.file_panel.update_info(*[file_obj.name, file_obj.filepath,
            file_obj.filetype, str(file_obj.num_entries),
            str(file_obj.num_lines), str(file_obj.num_bases)])

    def _add(self,value):
        """Adds a file to the Combobox
        Because 'values' is represented as a tuple cannot call methods to
        modify it in place; instead update internal list and change tuple
        to represent new contents"""
        self.values.append(value)
        self.file_box['values'] = self.values

    def _remove(self,value):
        """Same as _add but removes the file instead"""
        self.values.remove(value)
        self.file_box['values'] = self.values

    def onReFile(self):
        """Removes a file from a record"""
        curfile = self.file_box.get()
        if curfile == '': # no file selected
            messagebox.showwarning('Remove File Warning', 'No file selected')
        if messagebox.askyesno(
            message = "Are you sure you want to remove {}".format(curfile),
            icon='question', title='Remove File'):
            del self.file_dict[curfile] # remove from the dictionary
            self._remove(curfile) # remove from list box
            # Need to check whether the removed file is new or old
            num_new_files_before = len(self.new_files)
            self.new_files = [l for l in nf if l[0] != curfile] # remove from new_files list
            if len(self.new_files) == num_new_files_before: # we removed a file from before instead
                self.removed_files.append(curfile) # flag for removal from object
            # Finally, clear display for sanity sake
            self.file_panel.clear_display()

    def onAddFile(self):
        """Pops up a new dialog to add a file object"""
        window = Toplevel()
        NewFileForm([('filename',''), ('filepath',''), ('filetype','')], window, self)

    def add_file(self, new_file, filepath, filetype):
        """Adds a file"""
        ff = record_file.FastaFile(new_file, filepath, filetype)
        ff.update_file()
        #self.file_dict[new_file] = record_file.FastaFile(new_file, filepath, filetype)
        self.file_dict[new_file] = ff
        self._add(new_file) # add to temporary selection
        self.new_files.append([new_file, filepath, filetype]) # for permanent addition later

class FilePanel(ttk.Label):
    def __init__(self, parent=None):
        ttk.Label.__init__(self, parent)
        self.pack(expand=YES,fill=BOTH)
        self.displayInfo = StringVar() # variable watches for updates
        self.config(textvariable=self.displayInfo, # associate label text with variable
                width=-80, # set a sane minimum width)
                anchor='center',justify='center') # centre and justify label text
        self.displayInfo.set('File Info') # initialize to an empty value

    def update_info(self, *values):
        """Parses file info for display"""
        display_string = ''
        display_string += ('Filename: ' + values[0] + '\n')
        display_string += ('Filepath: ' + values[1] + '\n')
        display_string += ('Filetype: ' + values[2] + '\n')
        display_string += ('Number of entries ' + str(values[3]) + '\n')
        display_string += ('Number of lines ' + str(values[4]) + '\n')
        display_string += ('Number of bases ' + str(values[5]) + '\n')
        self.displayInfo.set(display_string)

    def clear_display(self):
        """Helper function to clear display"""
        self.displayInfo.set('')
