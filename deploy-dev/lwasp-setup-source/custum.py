# Copyright (C) 2015 Peter Steffey

#work in progress

import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w
from collections import namedtuple
import subprocess
from os.path import isfile

Item = namedtuple("Items", "title mode points type parameters")

type_map = {'FileContents': ['Absolute File Path', '(T/F) Whether the file should contain the search string(s)', 'Search String 1'], 'FileExistance': ['Absolute File Path', '(T/F) Whether the file/directory should exist'], 'Permissions': ['Absolute File Path', 'Permissions Needed in numerical form (e.g. 745)'], 'Command': ['BASH command to run', '(T/F) Whether the output should contain the text', 'Text to look for in output of command']}

class CustumBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.items = []

        self.master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

        self.add_box = Gtk.Box()
        add_q = Gtk.Button(label="Add")
        add_q.props.halign = Gtk.Align.END
        add_q.connect("clicked", self.add_q)
        self.add_box.pack_end(add_q, False, False, 0)
        self.master_box.pack_start(self.add_box, False, False, 0)

        title_label_1 = Gtk.Label()
        title_label_1.set_markup('<big>Installed Services</big>')
        self.master_box.pack_start(Gtk.HSeparator(), False, False, 0)
        self.master_box.pack_start(title_label_1, False, False, 0)

        self.add_box = Gtk.Box()
        self.name_entry = Gtk.Entry(placeholder_text="Package Name")
        self.add_box.pack_start(Gtk.Label("Install Software: "), False, False, 0)
        self.add_box.pack_start(self.name_entry, False, False, 0)
        add_app = Gtk.Button(label="Install")
        add_app.props.halign = Gtk.Align.END
        add_app.connect("clicked", self.add_app)
        self.add_box.pack_end(add_app, False, False, 0)
        self.master_box.pack_end(self.add_box, False, False, 0)

        self.add_with_viewport(self.master_box)

    def add_row(self, item):
        user_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        user_wrapper_box = Gtk.Box(spacing=5)

        label = Gtk.Label(app)
        user_wrapper_box.pack_start(label, False, True, 0)
        button = Gtk.Button(label="Expand")
        button.props.halign = Gtk.Align.END
        button.index = len(self.items)
        button.connect("clicked", self.expand_button_clicked)
        user_wrapper_box.pack_end(button, False, True, 0)

        user_box.pack_start(user_wrapper_box, False, False, 0)
        self.master_box.pack_start(user_box, False, True, 0)

        separator = Gtk.HSeparator()
        self.master_box.pack_start(separator, False, True, 0)

        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.items.append(Item(name = app, expanded = False, box = user_box, options_box = options_box))

    def delete_q(self, button):
        box = self.items[len(self.items)-1].box
        self.master_box.remove(box)
        del self.items[len(self.items)-1]

    def add_q(self, button):
        self.add_row()
        self.master_box.reorder_child(self.add_box, len(self.items) * 2)
        self.master_box.show_all()
