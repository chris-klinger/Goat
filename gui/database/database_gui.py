"""
This module contains code for dealing with viewing and updating databases
"""

from tkinter import *
from tkinter import ttk

from databases import database_records
from gui.util import input_form

# holds a set of types for files
# note, these act as reserved keywords for Goat record attributes
valid_file_types = {'protein','genomic'}

class DatabaseFrame(Frame):
    def __init__(self, database, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.db = database
        self.db_panel = DatabaseGui(database,self)
        self.db_panel.pack()
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, fill=X)

        self.buttons = [('Remove', self.onRemove, {'side':RIGHT}),
                        ('Modify', self.onModify, {'side':RIGHT}),
                        ('Add', self.onAdd, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onRemove(self):
        pass

    def onModify(self):
        pass

    def onAdd(self):
        """Adds a new record object"""
        window = Toplevel()
        record_list = [('record identity',''), ('genus',''), ('species',''),
                ('strain',''), ('supergroup','')]
        NewRecordForm(record_list, self.db, self.db_panel, window)

class DatabaseGui(ttk.Panedwindow):
    def __init__(self, database, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        # assign an instance variable, pass in self as the parent to child widgets
        self.info_frame = ttk.Labelframe(self,text='Database Information')
        #self.info_frame.pack(expand=YES,fill=BOTH)
        self.info_panel = InfoPanel(self.info_frame)
        self.db_viewer = DatabaseViewer(database,self.info_panel,self)#.db_frame)
        self.add(self.db_viewer)
        self.add(self.info_frame)
        self.pack(expand=YES,fill=BOTH)

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
        self.make_tree()

    def make_tree(self):
        for record in self.db.list_records():
            print(record)
            #record_obj = self.db.fetch_record(record)
            record_obj = self.db[record] # should be able to index
            #for k,v in record_obj.items():
                #print(k + ' ' + v)
            record_name = record_obj.genus + ' ' + record_obj.species
            self.insert('','end',record,text=record_name,tags=('record'))
            #for k,v in self.db.list_record_info(record):
            for k in record_obj.files.keys():
                #if k in valid_file_types:
                self.insert(record,'end',(record + '_' + k),text=k,tags=('file'))

    def itemClicked(self, item_type):
        item = self.focus()
        if item_type == 'record':
            rlist = []
            record = self.db.fetch_record(item)
            rlist.extend((record.genus,record.species))
            for k,v in record.__dict__.items():
                if k not in valid_file_types:
                    rlist.extend((k,v))
            self.info.update_info('record', *rlist) # delegates information to display to widget
        elif item_type == 'file':
            flist = []
            record,filename = item.rsplit('_',1)[0], item.rsplit('_',1)[1] # chop back off the name
            #record = self.db.fetch_record(record_name)
            record_obj = self.db.record
            record_file = record_obj.files[filename]
            #flist.extend((record.genus,record.species,file_type,
                #getattr(record,file_type)))
            flist.extend((record_obj.genus, record_obj.species, record_file.name,
                record_file.filepath, record_file.filetype, record_file.num_entries,
                record_file.num_lines, record_file.num_bases))
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

    def update_info(self,display_type,*values):
        display_string = ''
        display_string += (values[0] + ' ' + values[1] + '\n\n\n\n')
        if display_type == 'record':
            if len(values) > 2:
                for index,value in enumerate(values[2:]):
                    if index % 2 == 0: # even value
                        display_string += (values[index+2] + ' ') # +2 compensates for first two list values
                    else: # odd value
                        display_string += (values[index+2] + '\n')
        else:
            display_string += ('Filename: ' + values[2] + '\n')
            display_string += ('Filepath: ' + values[3] + '\n')
            display_string += ('Filetype: ' + values[4] + '\n')
            display_string += ('Number of entries ' + str(values[5]) + '\n')
            display_string += ('Number of lines ' + str(values[6]) + '\n')
            display_string += ('Number of bases ' + str(values[7]) + '\n')
        self.displayInfo.set(display_string)

class NewAttrForm(input_form.Form):
    def onSubmit(self):
        new_attr = self.content['new attribute'].get()
        new_value = self.content['value'].get()
        self.other.update_view('add',new_attr,new_value)
        self.parent.destroy()

class NewFileForm(input_form.Form):
    def onSubmit(self):
        remaining = {}
        for key in self.content.keys():
            if key == 'filename':
                new_file = self.content[key].get()
            elif key == 'filepath':
                filepath = self.content[key].get()
            else:
                remaining[key] = self.content[key].get()
        self.other.update_view('add',new_file,filepath)
        self.files.extend(new_file, filepath, remaining) # keep track of all info!
        self.parent.destroy()

class RemovalForm(input_form.Form):
    def onSubmit(self):
        item_to_remove = self.content['item to remove'].get()
        self.other.update_view('remove', item_to_remove)
        self.parent.destroy()

class NewRecordForm(input_form.DefaultValueForm):
    def __init__(self, entry_list, database, db_widget, parent=None, entrysize=40):
        buttons = [('Cancel', self.onCancel, {'side':RIGHT}),
                    ('Submit', self.onSubmit, {'side':RIGHT}),
                    ('Add Entry', self.onAttr, {'side':RIGHT}),
                    ('Add File', self.onAddfile, {'side':RIGHT}),
                    ('Remove Entry', self.onReAttr, {'side':LEFT}),
                    ('Remove File', self.onReFile, {'side':LEFT})]
        input_form.DefaultValueForm.__init__(self, entry_list, parent, buttons, entrysize)
        self.db = database
        self.db_widget = db_widget # communicate changes back to parent
        self.files = [] # keep track of all file info

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

    def onCancel(self):
        """Cancels without actually adding entry"""
        self.parent.destroy()

    def onSubmit(self):
        """Actually adds the record to the database"""
        record_id = self.content['record identity'].get()
        attrs = {}
        for k in self.content.keys():
            if not (k == 'filename' or k == 'record identity'): # avoid redundancy
                attrs[k] = self.content[k].get()
        self.db.add_record(record_id, **attrs)
        if len(self.files) != 0: # we have files
            for name,path,remaining in files:
                self.db.add_record_file(record_id, name, path, **remaining)
        self.db_widget.update() # signal back to re-draw tree
        self.parent.destroy()

    def onAttr(self):
        """Adds a new attribute to a record object"""
        window = Toplevel()
        NewAttrForm(('new attribute', 'value'), window, self).pack()

    def onAddfile(self):
        """Pops up a new dialog to add a file object"""
        window = Toplevel()
        NewFileForm(('filename', 'filepath', 'filetype'), window, self).pack()

    def onReAttr(self):
        """Removes a record attribute"""
        window = Toplevel()
        RemovalForm('attribute to remove', window, self).pack()

    def onReFile(self):
        """Removes a file from a record"""
        window = Toplevel()
        RemovalForm('file to remove', window, self).pack()
