"""
This module contains code for viewing result objects in Goat. Idea here is to keep
result objects read-only, so no need for code to modify result objects, just to
view them and ensure that searches went as planned. Should still add an option to
remove result objects though.
"""

from tkinter import *
from tkinter import ttk

class ResultFrame(Frame):
    def __init__(self, result_db, search_db, parent=None):
        Frame.__init__(self, parent)
        self.udb = result_db
        self.sdb = search_db
        self.parent = parent
        self.results = ResultGui(result_db, search_db, self)
        self.pack(expand=YES, fill=BOTH)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Remove', self.onRemove, {'side':LEFT}),
                        ('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        """Close associated database and destroy window"""
        self.udb.close()
        self.sdb.close()
        self.parent.destroy()

    def onSubmit(self):
        """Commits any changes and destroys window"""
        self.udb.commit()
        self.sdb.commit()
        self.onClose()

    def onCancel(self):
        """Same as onClose"""
        self.onClose()

class ResultGui(ttk.PanedWindow):
    def __init__(self, result_db, search_db, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.info_frame = ResultInfo(self)
        self.result_tree = ResultTree(result_db, search_db, self.info_frame, self)
        self.add(self.result_tree)
        self.add(self.info_frame)
        self.pack(expand=YES, fill=BOTH)

class ResultTree(ttk.Treeview):
    def __init__(self, result_db, search_db, other_widget, parent=None):
        ttk.Treeview.__init__(self, parent)
        self.udb = result_db
        self.sdb = search_db
        self.info = other_widget
        self.config(selectmode = 'browse') # one item at a time
        self.tag_bind('search', '<Double-1>', # single click does not register properly
                callback=lambda x:self.itemClicked('search'))
        self.tag_bind('result', '<Double-1>',
                callback=lambda x:self.itemClicked('result'))
        self.make_tree()
        self.pack(expand=YES, fill=BOTH)

    def update(self):
        """Update view after removal"""
        for item in self.get_children():
            self.delete(item)
        self.make_tree()

    def make_tree(self):
        """Builds a treeview display of searches/results"""
        for search in self.sdb.list_entries():
            self.insert('','end',search,text=search,tags=('search'))
            sobj = self.sdb[search]
            for result_id in sobj.list_results():
                self.insert(search,'end',result_id,text=result_id,tags=('result'))

    def itemClicked(self, item_type):
        pass

class ResultInfo(ttk.Label):
    def __init__(self, parent=None):
        ttk.Label.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.displayInfo = StringVar()
        self.config(textvariable = self.displayInfo,
                width=-75,
                anchor='center', justify='center')
        self.displayInfo.set('')

    def update_info(self, display_type, *values):
        pass
