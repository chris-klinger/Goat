"""
This module contains code for dealing with viewing and updating databases
"""

from tkinter import *
from tkinter import ttk, filedialog, messagebox

from bin.initialize_goat import configs

from util import util
from records import record_file, record_obj
from gui.util import input_form, gui_util

# holds a set of types for files
# note, these act as reserved keywords for Goat record attributes
valid_filetypes = ['protein','genomic']
default_attrs = ['identity','genus','species','strain','supergroup','files']
valid_supergroups = ['Opisthokonta','Amoebozoa','Archaeplastida','Excavata','SAR',
                    'CTH','incertae sedis'] # these last two not really SGs...

class DatabaseFrame(Frame):
    def __init__(self, parent=None): #database, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack(expand=YES, fill=BOTH)
        self.rdb = configs['record_db']
        self.db_panel = DatabaseGui(self)
        self.toolbar = Frame(self)
        self.toolbar.pack(expand=YES, side=BOTTOM, fill=X)

        #self.parent = parent
        #self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT}),
                        ('Remove', self.onRemove, {'side':LEFT}),
                        ('Modify', self.onModify, {'side':LEFT}),
                        ('Add', self.onAdd, {'side':LEFT})]
        for (label, action, where) in self.buttons:
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Commits changes to database before closing"""
        self.rdb.commit()
        self.onCancel()

    def onCancel(self):
        self.parent.destroy()

    def onRemove(self):
        """Removes an existing record object"""
        item = self.db_panel.current_item() # first (and only) item in list of tags
        if item['tags'][0] == 'record':
            if messagebox.askyesno(
                    message = "Do you really want to delete {}?".format(
                        item['text']), icon='question',
                        title='Remove Record'):
                self.rdb.remove_entry(item['text'])
        elif item['tags'][0] == 'file':
            pass # do we want to be able to remove files directly?

    def onModify(self):
        """Allows user to modify a pre-existing record.

        Current implementation involves retrieving db information and
        passing it to a NewRecordForm, which already contains all the
        methods to deal with adding/removing/changing attributes."""
        item = self.db_panel.current_item()
        if item['tags'][0] == 'record': # first (and only) item in list of tags
            robj = self.rdb[item['text']] # text also holds the ID
            # get default values
            record_list = [('record identity', robj.identity),
                ('genus', robj.genus), ('species', robj.species),
                ('strain', robj.strain)]
            for k,v in robj.__dict__.items():
                if not k in default_attrs:
                    record_list.append((k,v)) # add any other attributes that may be present
            window = Toplevel()
            RecordFrame(record_list, robj.supergroup, robj.files, self.db_panel, window)
        elif item['tags'][0] == 'file':
            pass # do we want to be able to modify files?

    def onAdd(self):
        """Adds a new record object"""
        window = Toplevel()
        # same as onModify but default values are empty strings
        record_list = [('record identity',''), ('genus',''), ('species',''),
                ('strain','')]
        RecordFrame(record_list, '', {}, self.db_panel, window)

class DatabaseGui(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        # assign an instance variable, pass in self as the parent to child widgets
        self.info_frame = ttk.Labelframe(self,text='Database Information')
        self.info_panel = InfoPanel(self.info_frame)
        self.db_viewer = DatabaseViewer(self.info_panel,self)
        self.add(self.db_viewer)
        self.add(self.info_frame)
        self.pack(expand=YES,fill=BOTH)

    def current_item(self):
        """Returns the current item of the db_viewer"""
        item_name = self.db_viewer.focus()
        item = self.db_viewer.item(item_name)
        return item

class DatabaseViewer(ttk.Treeview):
    def __init__(self, info_panel, parent=None):
        ttk.Treeview.__init__(self, parent)
        self.rdb = configs['record_db']
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
        for item in self.get_children():
            self.delete(item)
        self.make_tree()

    def make_tree(self):
        """Builds a treeview display of records/files"""
        counter = util.IDCounter()
        for rid in self.rdb.list_entries():
            uniq_r = str(counter.get_new_id())
            robj = self.rdb[rid]
            self.insert('','end',uniq_r,text=rid,tags=('record'))
            # now add files (if present), as subheadings for the record
            for fid in robj.files.keys():
                uniq_f = str(counter.get_new_id())
                self.insert(uniq_r,'end',uniq_f,text=fid,tags=('file'))

    def itemClicked(self, tag):
        """
        Triggered when either records or files are clicked. Builds a list of
        information for display by associated info panel and delegates display
        to that widget
        """
        item_id = self.focus()
        parent_list = self.get_ancestors(item_id,[])
        db_obj = self.get_item_from_db(parent_list, self.rdb)
        to_display = []
        if tag == 'record':
            # genus and species make up header
            to_display.extend([
                    ('Database Record Information' + '\n'),
                    ('Record: ' + db_obj.genus + ' ' + db_obj.species + '\n')])
            # now add other associated information
            for k,v in sorted(db_obj.__dict__.items()):
                if k != 'files': # skip over files
                    str_key = str(k)
                    title = str_key.title()
                    to_display.append((title + ': ' + str(v)))
        elif tag == 'file':
            # add additional information
            to_display.extend([
                ('Record File Information' + '\n'),
                ('Filename: ' + db_obj.name),
                ('Filepath: ' + db_obj.filepath),
                ('Filetype: ' + db_obj.filetype + '\n'),
                ('Number of Entries: ' + str(db_obj.num_entries)),
                ('Number of Lines: ' + str(db_obj.num_lines)),
                ('Number of Bases: ' + str(db_obj.num_bases))])
        self.info.update_info(to_display)

    def get_ancestors(self, item_name, item_list=[]):
        """Recurs until root node to return a list of ancestors"""
        parent = self.parent(item_name)
        item = self.item(item_name)
        item_id = item['text']
        if item_name == '': # hit root node
            return item_list[::-1]
        else:
            item_list.append(item_id)
            return self.get_ancestors(parent, item_list) # recur

    def get_item_from_db(self, item_list, obj, index=0, db_obj=None):
        """Uses the length of item_list to choose appropriate object from nested
        database objects"""
        item = item_list[0]
        if index == 0:
            new_obj = self.rdb[item]
        elif index == 1:
            new_obj = obj.files[item]
        if len(item_list) == 1:
            return new_obj
        else:
            item_list.remove(item)
            index += 1
            return self.get_item_from_db(item_list, new_obj, index, db_obj) # recur

class InfoPanel(gui_util.InfoPanel):
    def __init__(self, parent=None):
        gui_util.InfoPanel.__init__(self, parent)

class RecordFrame(Frame):
    def __init__(self, entry_list, supergroup, record_files, db_widget, parent=None):
        Frame.__init__(self, parent)
        self.rdb = configs['record_db']
        self.db_widget = db_widget
        self.parent = parent
        self.pack(expand=YES, fill=BOTH)
        self.record_gui = RecordGui(entry_list, supergroup, record_files, self)
        self.toolbar = Frame(self)
        self.toolbar.pack(expand=YES, side=BOTTOM, fill=X)

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

    def onCancel(self):
        self.parent.destroy()

    def onSubmit(self):
        """Adds new or modified record to the database"""
        attrs = self.record_gui.return_attrs()
        #print(attrs)
        record_id = attrs['record identity']
        remaining = {}
        for k in attrs.keys():
            if not (k == 'record identity'):
                remaining[k] = attrs[k]
        #if record_id in self.db.keys(): # record is already present
        if record_id in self.rdb.list_entries():
            #self.db.update_record(record_id, **remaining)
            db_obj = self.rdb[record_id]
        else:
            db_obj = record_obj.Record(record_id)
            self.rdb[record_id] = db_obj
        # either way, update record object with new info
        db_obj.update(**remaining)
        try:
            for n,p,t in self.record_gui.return_new_files():
                db_obj.add_file(n, p, t)
        except(IndexError): # no added files
            pass
        try:
            for n in self.record_gui.return_removed_files():
                db_obj.remove_file(n)
        except(IndexError): # no removed files
            pass
        #self.db.commit()
        #print(self.db_widget.db_viewer.make_tree)
        #self.db_widget.db_viewer.make_tree() # signal back to re-draw tree
        self.db_widget.db_viewer.update()
        self.parent.destroy()

class RecordGui(ttk.Panedwindow):
    def __init__(self, entry_list, supergroup, record_files, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        # assign an instance variable, pass in self as the parent to child widgets
        self.record_frame = ttk.Labelframe(self,text='Record Information')
        self.file_frame = ttk.Labelframe(self,text='File Information')
        self.attr_form = AttributeFrame(entry_list, supergroup, self.record_frame)
        self.file_form = FileFrame(record_files,self.file_frame)#.db_frame)
        self.add(self.record_frame)
        self.add(self.file_frame)
        self.pack(expand=YES,fill=BOTH)

    def return_attrs(self):
        """Convenience function to fetch attrs"""
        return self.attr_form.return_attrs()

    def return_new_files(self):
        """Convenience function"""
        return self.file_form.new_files

    def return_removed_files(self):
        """Convenience function"""
        return self.file_form.removed_files

class AttributeFrame(Frame):
    def __init__(self, entry_list, supergroup, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.parent = parent
        self.form = input_form.DefaultValueForm(entry_list, self)
        self.sgroup = gui_util.ComboBoxFrame(self,
                choices=valid_supergroups,
                labeltext='Supergroup')
        self.sgroup.set(supergroup) # sets to current value
        # toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=BOTH)
        self.buttons = [('Remove Attribute', self.onReAttr, {'side':RIGHT}),
                        ('Add Attribute', self.onAttr, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

    def update_attr(self, update, setting, value=None):
        """Updates window with added entries"""
        if update == 'add':
            new_row = input_form.EntryRow(setting, self.rows, value, self,
                    self.labelsize, self.entrysize)
            self.form.row_list.append(new_row)
        elif update == 'remove':
            for row in self.form.row_list:
                if row.label_text == setting:
                    row.destroy()

    def onAttr(self):
        """Adds a new attribute to a record object"""
        window = Toplevel()
        NewAttrForm(('New Attribute', 'Value'), window, self)

    def onReAttr(self):
        """Removes a record attribute"""
        window = Toplevel()
        RemovalFrame([row.label_text for row in self.form.row_list],self,window)

    def return_attrs(self):
        """Returns all attributes"""
        attr_dict = {}
        for row in self.form.row_list:
            label = row.label_text
            attr_dict[label] = row.entry.get()
        attr_dict['supergroup'] = self.sgroup.get()
        return attr_dict

class NewAttrForm(input_form.Form):
    def onSubmit(self):
        new_attr = self.content['New Attribute'].get()
        new_value = self.content['Value'].get()
        self.other.update_attr('add',new_attr,new_value)
        self.parent.destroy()

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

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

    def onCancel(self):
        self.parent.destroy()

    def onSubmit(self):
        """Signal back to remove attribute"""
        attr = self.selected_attr.get()
        self.attr_widget.update_attr('remove',attr)
        self.parent.destroy()

class FileFrame(Frame):
    def __init__(self, file_dict, parent=None):
        Frame.__init__(self, parent)
        self.file_dict = file_dict
        self.new_files = [] # keep track of added files
        self.removed_files = [] # keep track of removed files
        self.pack(expand=YES, fill=BOTH)
        #self.file_box = ttk.Combobox(self, textvariable=self.selected_file)
        self.file_box = gui_util.ComboBoxFrame(self,
                ([k for k in self.file_dict.keys()] if self.file_dict.keys() else []), # choices
                'Record Files', self.onSelect)
        self.file_panel = FilePanel(self)

        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, fill=X)

        self.buttons = [('Remove file', self.onReFile, {'side':RIGHT}),
                        ('Add file', self.onAddFile, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

    def onSelect(self):
        """Signal to file panel to display associated file information"""
        db_obj = self.file_dict[self.file_box.get()]
        to_display = []
        to_display.extend([
                ('Record File Information' + '\n'),
                ('Filename: ' + db_obj.name),
                ('Filepath: ' + db_obj.filepath),
                ('Filetype: ' + db_obj.filetype + '\n'),
                ('Number of Entries: ' + str(db_obj.num_entries)),
                ('Number of Lines: ' + str(db_obj.num_lines)),
                ('Number of Bases: ' + str(db_obj.num_bases))])
        self.file_panel.update_info(to_display)

    def _add(self, values):
        """
        Adds a file to the Combobox; Because 'values' is represented as a tuple
        cannot call methods to modify it in place; instead update internal list
        and change tuple to represent new contents
        """
        self.file_box.add_items(values)

    def _remove(self, values):
        """Same as _add but removes the file instead"""
        self.file_box.remove_items(values)

    def onReFile(self):
        """Removes a file from a record"""
        curfile = self.file_box.get()
        if curfile == '': # no file selected
            messagebox.showwarning('Remove File Warning', 'No file selected')
        if messagebox.askyesno(
            message = "Are you sure you want to remove {}".format(curfile),
            icon='question', title='Remove File'):
            del self.file_dict[curfile] # remove from the dictionary
            self._remove((curfile,)) # remove from list box
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
        NewFileFrame(window, self)

    def add_file(self, new_file, filepath, filetype):
        """Adds a file"""
        ff = record_file.FastaFile(new_file, filepath, filetype)
        ff.update_file()
        self.file_dict[new_file] = ff
        self._add((new_file,)) # add to temporary selection
        self.new_files.append([new_file, filepath, filetype]) # for permanent addition later

class NewFileFrame(Frame):
    def __init__(self, parent=None, other_widget=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.parent = parent
        self.other = other_widget
        self.name = input_form.DefaultValueForm(
                [('Filename','')], self)
        self.cfile = input_form.FileValueForm(self)
        self.ftype = gui_util.ComboBoxFrame(self,
                valid_filetypes, 'Filetype')
        # toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

    def onCancel(self):
        self.parent.destroy()

    def onSubmit(self):
        #try:
        fname = self.name.get('Filename')
        fpath = self.cfile.get()
        ftype = self.ftype.get()
        for val in (fname,fpath,ftype):
            if val == '':
                raise AttributeError
        self.other.add_file(fname, fpath, ftype)
        self.parent.destroy()
        #except(AttributeError):
        #    # do not allow submission and warn user if values are blank
        #    messagebox.showwarning('Add File Warning', 'Cannot leave blank entries')

class FilePanel(gui_util.InfoPanel):
    def __init__(self, parent=None):
        gui_util.InfoPanel.__init__(self, parent)
