"""
This module contains code for determining redundandant accessions for searches
in Goat. Two options are presented to users, 'auto' or 'manual'. In auto mode,
the program determines a likely set of queries to use as redundant accessions,
while in 'manual' mode, the user gets to choose the hits that they consider to
represent redundant.
"""

import urwid
from urwid.canvas import CompositeCanvas
from urwid.canvas import apply_text_layout
from urwid.signals import connect_signal
from urwid.command_map import ACTIVATE
from Bio.Blast import NCBIXML

from searches import search_util

palette = [
    ('reversed', 'black', 'white')
]

def add_redundant_accs_manual(outpath):
    """Allows user to choose which accs are counted as manual"""
    raccs = []
    main_urwid(outpath, raccs)
    return raccs

def get_lines(filepath): #, max_length=82):
    """Gets the lines from the BLAST output"""
    lines = []
    seen = set()
    blast_result = NCBIXML.read(open(filepath))
    for hit in blast_result.descriptions:
        new_title = search_util.remove_blast_header(hit.title)
        if not new_title in seen:
            lines.append([new_title, hit.e])
            seen.add(new_title)
    return lines

def main_urwid(filepath, rlist):
    """Tries to use urwid to display program"""
    lines = get_lines(filepath)
    blast_result = BlastResults(lines)
    chosen_results = ChosenResults([],rlist)
    blast_result.link_screen(chosen_results)
    chosen_results.link_screen(blast_result)
    blast_result.add_results()
    blast_result_frame = urwid.Frame(blast_result,
            header = urwid.Text("Blast results, hit ENTER to select desired entry(ies)\n"))
    chosen_result_frame = urwid.Frame(chosen_results,
            header = urwid.Text("Desired entry(ies), hit ENTER to delete\n"))
    body = urwid.Columns([blast_result_frame, chosen_result_frame])
    loop = urwid.MainLoop(urwid.Frame(body), palette=palette, unhandled_input=quit_filter)
    loop.run()

def quit_filter(key):
    if key == 'q':
        raise urwid.ExitMainLoop()

class BlastColumns(urwid.Columns):
    def __init__(self):
        self.num_columns = self.columns_widths()/2

class ResultScreen(urwid.ListBox):
    def __init__(self, data, other_screen=None, width=0):
        urwid.ListBox.__init__(self, urwid.SimpleListWalker([]))
        self.data = data
        self.other_screen = other_screen
        self.width = width
        self.button_map = {}

    def link_screen(self, other_screen):
        self.other_screen = other_screen

class BlastResults(ResultScreen):
    def add_results(self):
        for line in self.data:
            label = (str(line[0]) + '  ' + str(line[1]))
            button = NewChoiceButton(label, blast_item_chosen, self.other_screen)
            self.body.append(urwid.AttrMap(button, None, focus_map='reversed'))

class ChosenResults(ResultScreen):
    def __init__(self, data, rlist, other_screen=None, width=0):
        self.rlist = rlist
        ResultScreen.__init__(self, data, other_screen=None, width=0)
    def add_result(self, label):
        button = NewChoiceButton(label, result_item_chosen, self)
        decorated_button = urwid.AttrMap(button, None, focus_map='reversed')
        self.body.append(decorated_button)
        self.rlist.append(' '.join(label.split()[:-1]))
        self.button_map[label] = decorated_button

class NewChoiceButton(urwid.SelectableIcon):
    signals = ['click']
    def __init__(self, label, on_press=None, user_data=None):
        self.__super.__init__(label)
        self._original_text = self._text # keep original value pristine, display relies on self._text
        if on_press:
            connect_signal(self, 'click', on_press, user_data)

    def render(self, size, focus=False):
        """Overrides default render activity"""
        (maxcol,) = size
        #self.clip_text(maxcol) # function to change self._text
        string = ' '.join(self._original_text.split()[:-1])
        evalue = self._original_text.split()[-1]
        new_string,evalue,num_pads = calculate_padding(string,evalue,maxcol)
        self.set_text(new_string + (' ' * num_pads) + evalue + ' ')
        text, attr = self.get_text()
        trans = self.get_line_translation(maxcol, (text,attr))
        c = apply_text_layout(text, attr, trans, maxcol)
        if focus:
             c = CompositeCanvas(c)
             c.cursor = self.get_cursor_coords(size)
        return c

    #def clip_text(self, maxcol):
        #"""clips first part of text on screen render"""
        #string = ' '.join(self._original_text.split()[:-1])
        #evalue = self._original_text.split()[-1]
        #new_string,evalue,num_pads = calculate_padding(string,evalue,maxcol)
        #self._text = new_string + (' ' * num_pads) + evalue + '  '

    def keypress(self, size, key):
        """send a signal on 'click'"""
        if self._command_map[key] != ACTIVATE:
            return key
        self._emit('click')

def calculate_padding(instring, evalue, max_size, padding=5):
    """Calculates number of spaces necessary to line up evalue"""
    max_size = int(max_size - 5) # gives some leeway
    length_string = len(instring)
    length_evalue = len(evalue)
    num_pads = 0
    new_string = instring
    if ((length_string + padding + length_evalue) > max_size):
        new_string = instring[:(max_size - (length_evalue+padding))] + '...'
        num_pads = padding - 3 # 3 is length of ellipsis
    else:
        num_pads = max_size - (length_string + length_evalue)
    return (new_string, evalue, num_pads)

def blast_item_chosen(choice, other_screen):
    if choice._original_text not in other_screen.button_map.keys():
        other_screen.add_result(choice._original_text)

def result_item_chosen(choice, result_screen):
    if choice._original_text in result_screen.button_map.keys():
        result_screen.body.remove(result_screen.button_map[choice._original_text])
        del result_screen.button_map[choice._original_text]
        result_screen.rlist.remove(' '.join(choice._original_text.split()[:-1]))
        #result_screen.rlist.remove(choice._original_text)
