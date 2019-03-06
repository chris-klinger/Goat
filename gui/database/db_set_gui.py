"""
This module contains code for interacting with database sets. Similar to query
sets, no interaction with records is supported. Unlike query sets, interface is
simpler because no alternative sets need to be considered.
"""

from tkinter import *
from tkinter import ttk, messagebox

from bin.initialize_goat import configs

from util import util
from gui.util import gui_util, input_form
from gui.queries import main_query_gui
from databases import sets

class RecordSetFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.rdb = configs['record_db']
        self.rsdb = configs['record_sets']
        self.pack(expand=YES, fill=BOTH)
        self.paned_window = RecordSetWindow(self)
        # Add the toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT}),
                        ('Add Record Set', self.onAdd, {'side': LEFT}),
                        ('Modify Record Set', self.onModify, {'side': LEFT}),
                        ('Remove Record Set', self.onRemove, {'side': LEFT})]
        for (label, action, where) in self.buttons:
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        self.rsdb.commit()
        self.parent.destroy()

    def onCancel(self):
        self.parent.destroy()

    def onAdd(self):
        """Pops up a new window to add relevant information for a new set"""
        window = Toplevel()
        ModifySetFrame(window, self) # add is just modify without object

    def add_db_set(self, set_name, set_obj):
        """Adds set object and then re-draws the tree"""
        self.rsdb.add_entry(set_name, set_obj)
        self.paned_window.redraw_tree()

    def onModify(self):
        """Gets the selected object and then modifies it"""
        item = self.paned_window.curr_item()
        try:
            if item['tags'][0] == 'set':
                set_obj = self.rsdb[item['text']]
                window = Toplevel()
                ModifySetFrame(window, self, set_obj)
        except KeyError:
            pass

    def onRemove(self):
        """Gets the selected object and removes it after asking user"""
        item = self.paned_window.curr_item()
        if item['tags'][0] == 'set':
            sname = item['text']
            if messagebox.askyesno(
                    message="Delete set {}?".format(sname),
                    icon='question', title='Remove Set'):
                self.rsdb.remove_entry(sname)
                self.paned_window.redraw_tree()

class RecordSetWindow(ttk.Panedwindow):
    def __init__(self, parent):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.info_frame = SetInfo(self)
        self.set_tree = SetTree(self, self.info_frame)
        self.add(self.set_tree)
        self.add(self.info_frame)
        self.pack(expand=YES, fill=BOTH)

    def redraw_tree(self):
        self.set_tree.update()

    def curr_item(self):
        item_id = self.set_tree.focus()
        return self.set_tree.item(item_id)

class SetTree(ttk.Treeview):
    def __init__(self, parent, other_widget):
        ttk.Treeview.__init__(self, parent)
        self.rdb = configs['record_db']
        self.rsdb = configs['record_sets']
        self.other = other_widget
        self.config(selectmode = 'browse')
        self.tag_bind('set', '<Double-1>',
                callback=lambda x:self.itemClicked('set'))
        self.tag_bind('record', '<Double-1>',
                callback=lambda x:self.itemClicked('record'))
        self.tag_bind('file', '<Double-1>',
                callback=lambda x:self.itemClicked('file'))
        self.make_tree()
        self.pack(expand=YES, fill=BOTH)

    def update(self):
        for item in self.get_children():
            self.delete(item)
        self.make_tree()

    def make_tree(self):
        """Builds treeview spanning set-record-files"""
        counter = util.IDCounter()
        # first add sets
        for rsid in self.rsdb.list_entries():
            uniq_s = str(counter.get_new_id())
            set_obj = self.rsdb[rsid]
            self.insert('','end',uniq_s,text=rsid,tags=('set'))
            # for each set, add all records
            for rid in set_obj.list_entries():
                uniq_r = str(counter.get_new_id())
                robj = self.rdb[rid]
                self.insert(uniq_s,'end',uniq_r,text=rid,tags=('record'))
                for fid in robj.files.keys():
                    uniq_f = str(counter.get_new_id())
                    self.insert(uniq_r,'end',uniq_f,text=fid,tags=('file'))

    def itemClicked(self, tag):
        """
        Triggers on item click. Uses recursion to obtain correct object from
        correct database and then builds up a list of information for the
        associated info panel widget to display.
        """
        item_id = self.focus()
        parent_list = self.get_ancestors(item_id,[])
        db_obj = self.get_item_from_db(parent_list)
        to_display = []
        if tag == 'set':
            to_display.extend([
                ('Database Set Information' + '\n'),
                ('Set Name: ' + db_obj.name),
                ('Number of Entries: ' + str(db_obj.num_entries))])
        elif tag == 'record':
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
        self.other.update_info(to_display)

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

    def get_item_from_db(self, item_list, obj=None, index=0):
        """Uses the length of item_list to choose appropriate object from nested
        database objects"""
        item = item_list[0]
        if index == 0:
            new_obj = self.rsdb[item]
        elif index == 1:
            new_obj = self.rdb[item]
        elif index == 2:
            new_obj = obj.files[item]
        if len(item_list) == 1:
            return new_obj
        else:
            item_list.remove(item)
            index += 1
            return self.get_item_from_db(item_list, new_obj, index) # recur

class SetInfo(gui_util.InfoPanel):
    def __init__(self, parent):
        gui_util.InfoPanel.__init__(self, parent)

class ModifySetFrame(Frame):
    def __init__(self, parent, other_widget, set_obj=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.parent = parent
        self.other = other_widget
        self.set_obj = set_obj
        self.rdb = configs['record_db']
        self.rsdb = configs['record_sets']
        # input for set name
        sname = self.set_obj.name if set_obj else ''
        self.name = input_form.DefaultValueForm(
                [('Name',sname)],self)
        # use GUI from main query implementation
        self.columns = main_query_gui.QueryColumns(self,
                p_text='Possible Databases',
                a_text='To be Added')
        # add a toolbar
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

        # add possibilities
        present = list(set_obj.entries) if set_obj else []
        db_list = []
        added_list = []
        for rid in self.rdb.list_entries():
            robj = self.rdb[rid]
            if rid in present:
                added_list.append([rid,robj])
            else:
                db_list.append([rid,robj])
        self.columns.add_queries(added_list)
        self.columns.add_possibilities(db_list)

    def onSubmit(self):
        """Either adds or modifies a query object"""
        add_new = False
        sname = self.name.get('Name')
        if not self.set_obj:
            self.set_obj = sets.DBSet(sname)
            add_new = True
        else:
            self.set_obj.name = sname
        to_add = []
        for entry in (self.columns.get_to_add()).keys():
            to_add.append(entry)
        self.set_obj.add_entries(to_add)
        if add_new: # also re-draws
            self.other.add_db_set(sname, self.set_obj)
        else: # still re-draw
            self.other.paned_window.redraw_tree()
        self.parent.destroy()

    def onCancel(self):
        self.parent.destroy()
