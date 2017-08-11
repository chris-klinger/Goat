"""
This module contains updated code for interacting with queries sets, without
worrying about individual queries themselves. Idea here is to separate query sets
by their type and provide separate treeview widgets to interact with each set.
Generic buttons for adding/modifying/removing sets will also be present to make
changes that can either be committed to the underlying db (or not).
"""

from tkinter import *
from tkinter import ttk

from bin.initialize_goat import configs

from util import util
from queries import query_sets
from gui.queries import main_query_gui
from gui.util import gui_util, input_form

class SetFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.qdb = configs['query_db']
        self.qsdb = configs['query_sets']
        self.pack(expand=YES, fill=BOTH)
        self.paned_window = SplitSetWindow(self)
        # Add the toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT}),
                        ('Add Query(ies)', self.onAdd, {'side': LEFT}),
                        ('Modify Query', self.onModify, {'side': LEFT}),
                        ('Remove Query(ies)', self.onRemove, {'side': LEFT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        self.qsdb.commit()
        self.parent.destroy()

    def onCancel(self):
        self.parent.destroy()

    def onAdd(self):
        """
        Determines which window is selected in the associated notebook widget and
        then provide an interface to add queries of the selected type.
        """
        qtype = self.paned_window.notebook_tab()
        window = Toplevel()
        AddSetFrame(window, self, qtype)

    def add_query_set(self, set_name, qtype, set_obj):
        """Adds set_obj to db and then re-draws the relevant tree"""
        self.qsdb.add_entry(set_name, set_obj)
        self.paned_window.redraw_tree(qtype)

    def onModify(self):
        """
        Determines which window is selected in the associated notebook widget and
        then provide an interface to add queries of the selected type.
        """
        item = self.paned_window.notebook_item()
        try:
            if item['tags'][0] == 'set': # set, not query
                set_obj = self.qsdb[item['text']]
                window = Toplevel()
                ModifySetFrame(window, set_obj)
        except KeyError:
            pass

    def onRemove(self):
        pass

class SplitSetWindow(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.info_frame = SetInfo(self)
        self.notebook = SetNotebook(self, self.info_frame) # link widget to display info
        self.add(self.notebook)
        self.add(self.info_frame)
        self.pack(expand=YES, fill=BOTH)

    def notebook_tab(self):
        """Returns value of selected notebook window"""
        return self.notebook.selected_tab()

    def notebook_item(self):
        """Returns a specific item name from the list"""
        return self.notebook.get_item()

    def redraw_tree(self, qtype):
        """Signals to notebook to re-draw tree for selected widget"""
        self.notebook.redraw_tree(qtype)

class SetNotebook(ttk.Notebook):
    def __init__(self, parent=None, other_widget=None):
        ttk.Notebook.__init__(self, parent)
        self.seqs = SeqTree(self, other_widget)
        self.hmms = HMMTree(self, other_widget)
        self.msas = MSATree(self, other_widget)
        self.add(self.seqs, text='Seq Query Sets')
        self.add(self.hmms, text='HMM Query Sets')
        self.add(self.msas, text='MSA Query Sets')
        self.pack(expand=YES, fill=BOTH)

    def selected_tab(self):
        """Returns the type associated with the chosen window"""
        curr_tab = self.select()
        if curr_tab == str(self.seqs):
            return 'seq'
        elif curr_tab == str(self.hmms):
            return 'hmm'
        else:
            return 'msa' # has to be one of the three

    def get_item(self):
        """Returns the current item of the widget"""
        tab = self.selected_tab()
        if tab == 'seq':
            return self.seqs.item(self.seqs.focus())
        elif tab == 'hmm':
            return self.hmms.item(self.seqs.focus())
        else:
            return self.msas.item(self.seqs.focus())

    def redraw_tree(self, qtype):
        """Forces update() on relevant child widget"""
        if qtype == 'seq':
            self.seqs.update()
        elif qtype == 'hmm':
            self.hmms.update()
        else:
            self.msas.update()

class SetTree(ttk.Treeview):
    """
    Generic superclass for set-based tree objects; make_tree() must be defined by
    each subclass to use a different selection from the query_db; similarly,
    itemClicked() must also be defined by each subclass
    """
    def __init__(self, parent, other_widget):
        ttk.Treeview.__init__(self, parent)
        self.qdb = configs['query_db']
        self.qsdb = configs['query_sets']
        self.info = other_widget
        self.config(selectmode = 'browse') # one item at a time
        self.tag_bind('set', '<Double-1>', # single click does not register properly
                callback=lambda x:self.itemClicked('set'))
        self.tag_bind('query', '<Double-1>',
                callback=lambda x:self.itemClicked('query'))
        self.make_tree()
        self.pack(expand=YES, fill=BOTH)

    def update(self):
        """Update view after removal"""
        for item in self.get_children():
            self.delete(item)
        self.make_tree()

    def make_tree(self, qtype=None):
        """Builds a treeview display of searches/results"""
        counter = util.IDCounter()
        for qset in self.qsdb.list_entries():
            set_obj = self.qsdb[qset]
            if set_obj.qtype == qtype:
                uniq_s = str(counter.get_new_id())
                self.insert('','end',uniq_s,text=qset,tags=('set'))
                for qid in set_obj.list_queries():
                    uniq_q = str(counter.get_new_id())
                    self.insert(uniq_s,'end',uniq_q,text=qid,tags=('query'))

    def itemClicked(self, item_type):
        """Builds a list of information for display by ResultInfo panel for
        either searches or results; delegates formatting/display to panel"""
        raise NotImplementedError # must be defined in subclass

class SeqTree(SetTree):
    """Subclass specific for sequence-based queries"""
    def make_tree(self):
        """Call super method with right argument"""
        super(SeqTree,self).make_tree('seq')

    def itemClicked(self, item_type):
        """Builds info based on the item clicked and send to display widget"""
        item_id = self.focus()
        item = self.item(item_id)
        display_list = []
        if item_type == 'set':
            set_obj = self.qsdb[item['text']]
            display_list.extend([
                ('Sequence Query Set Information' + '\n'),
                ('Set Name: ' + set_obj.name)]) # add more stuff later
        else: # item_type == 'query'
            pass

class HMMTree(SetTree):
    """Subclass specific for HMM-based queries"""
    def make_tree(self):
        """Call super method with right argument"""
        super(HMMTree,self).make_tree('hmm')

    def itemClicked(self, item_type):
        pass

class MSATree(SetTree):
    """Subclass specific for MSA-based queries"""
    def make_tree(self):
        """Call super method with right argument"""
        super(MSATree,self).make_tree('msa')

    def itemClicked(self, item_type):
        pass

class SetInfo(gui_util.InfoPanel):
    def __init__(self, parent=None):
        gui_util.InfoPanel.__init__(self, parent)

class AddSetFrame(Frame):
    def __init__(self, parent, other_widget, qtype):
        Frame.__init__(self, parent)
        self.parent = parent
        self.other = other_widget
        self.qtype = qtype
        self.qdb = configs['query_db']
        self.pack(expand=YES, fill=BOTH)
        # input for set name
        self.name = input_form.DefaultValueForm(
                [('Name','')],self)
        # use GUI from main query implementation
        self.columns = main_query_gui.QueryColumns(self)
        # add a toolbar
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

        # add query possibilities
        query_list = []
        for qid in self.qdb.list_entries():
            qobj = self.qdb[qid]
            if qobj.search_type == self.qtype:
                query_list.append([qid,qobj])
        self.columns.add_possibilities(query_list)

    def onSubmit(self):
        """Adds a query set object"""
        sname = self.name.get('Name')
        qids = []
        qdict = self.columns.get_to_add()
        for qid in qdict.keys():
            qids.append(qid)
        query_set = query_sets.QuerySet(sname, self.qtype)
        query_set.add_qids(qids)
        self.other.add_query_set(sname, self.qtype, query_set)
        self.parent.destroy()

    def onCancel(self):
        self.parent.destroy()

class ModifySetFrame(Frame):
    def __init__(self, parent, set_obj):
        Frame.__init__(self, parent)
