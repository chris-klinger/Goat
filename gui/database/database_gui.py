"""
This module contains code for dealing with viewing and updating databases
"""

from tkinter import *
from tkinter import ttk

from databases import database_records

# holds a set of types for files
# note, these act as reserved keywords for Goat record attributes
valid_file_types = {'protein','genomic'}

class DatabaseGui(ttk.Panedwindow):
    def __init__(self, database, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        # assign an instance variable, pass in self as the parent to child widgets
        self.info_frame = ttk.Labelframe(self,text='Database Information')
        self.info_frame.pack(expand=YES,fill=BOTH)
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

    def make_tree(self):
        for record in self.db.list_records():
            #print(record)
            record_obj = self.db.fetch_record(record)
            record_name = record_obj.genus + ' ' + record_obj.species
            self.insert('','end',record,text=record_name,tags=('record'))
            for k,v in self.db.list_record_info(record):
                if k in valid_file_types:
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
            record_name,file_type = item.rsplit('_',1)[0], item.rsplit('_',1)[1] # chop back off the name
            record = self.db.fetch_record(record_name)
            flist.extend((record.genus,record.species,file_type,
                getattr(record,file_type)))
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
            display_string += ('Filetype: ' + values[2] + '\n')
            display_string += ('Filepath: ' + values[3] + '\n')
        self.displayInfo.set(display_string)
