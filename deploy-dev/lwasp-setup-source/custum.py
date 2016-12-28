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

Item = namedtuple("Items", "box title mode points type parameters")

type_list = ['File Contents', 'File Existance', 'Permissions', 'Command']
type_map = {'File Contents': ['Absolute File Path', 'File should contain search string ~ File should NOT contain search string', 'Search String'], 'File Existance': ['Absolute File Path', 'File/directory should exist ~ File/directory should NOT exist'], 'Permissions': ['Absolute File Path', 'Permissions needed (e.g. 745)'], 'Command': ['BASH command to run', 'Output should contain text ~ Output should NOT contain text', 'Text']}

class CustumBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.items = []

        self.master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        title_label_1 = Gtk.Label()
        title_label_1.set_markup('<big>Custum Scoring Elements</big>')
        self.master_box.pack_start(title_label_1, False, False, 0)

        note_label = Gtk.Label()
        note_label.set_markup('<span foreground="grey"><small>These items are not checked for errors, please refer to the Advanced Users Guide PDF for reference</small></span>')
        note_label.set_line_wrap(True)
        self.master_box.pack_start(note_label, False, False, 0)

        self.master_box.pack_start(Gtk.HSeparator(), False, True, 0)

        self.add_box = Gtk.Box()
        add_q = Gtk.Button(label="Add Custom Element")
        add_q.props.halign = Gtk.Align.START
        add_q.connect("clicked", self.add_q)
        self.add_box.pack_start(add_q, False, False, 0)
        self.master_box.pack_start(self.add_box, False, False, 0)

        self.add_with_viewport(self.master_box)

    def add_row(self):
        new_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        new_row = Gtk.Box(spacing=10)

        title_entry = Gtk.Entry(placeholder_text="Title")
        title_entry.set_width_chars(30)

        mode_combo = generateComboBox([["V", "Vulnerability"], ["P", "Penalty"]])

        points_entry = Gtk.Entry(placeholder_text="Points")
        points_entry.set_width_chars(7)

        type_store = []
        for item in type_list:
            type_store.append([item])

        type_combo = self.generateComboBox(type_store)
        type_combo.connect('changed', self.changed_cb, len(self.items))

        new_row.pack_start(title_entry, False, False, 0)
        new_row.pack_start(mode_combo, False, False, 0)
        new_row.pack_start(points_entry, False, False, 0)
        new_row.pack_start(type_combo, False, False, 0)

        new_box.pack_start(new_row, False, False, 0)

        parameters_box = Gtk.Box(spacing=10)
        self.packParameters(type_map['File Contents'], parameters_box)
        new_box.pack_start(parameters_box, False, False, 0)

        self.master_box.pack_start(new_box, False, True, 0)

        self.master_box.pack_start(Gtk.HSeparator(), False, True, 0)

        self.items.append(Item(box = new_box, title = title_entry, mode = mode_combo, points = points_entry, type = type_combo, parameters = parameters_box))

    def packParameters(items, box):
        box.pack_start(Gtk.Label("Parameters: "), False, False, 0)
        for item in items:
            if "~" in item:
                box.pack_start(self.generateComboBox([["True", item.split(" ~ ")[0]], ["False", item.split(" ~ ")[1]]]), True, True, 0)
            else:
                box.pack_start(Gtk.Entry(placeholder_text=item), True, True, 0)

    def generateComboBox(items):
        new_store = Gtk.ListStore(str, str)
        if len(items[0]) == 1:
            new_store = Gtk.ListStore(str)
        for item in items:
            new_store.append(item)

        new_combo = Gtk.ComboBox.new_with_model(new_store)
        new_combo.set_active(0)
        renderer_text = Gtk.CellRendererText()
        new_combo.pack_start(renderer_text, True)
        new_combo.add_attribute(mode_renderer_text, "text", len(items[0]) - 1)
        return new_combo

    def changed_cb(self, type_combo, index):
        tree_iter = type_combo.get_active_iter()
        if tree_iter != None:
            model = type_combo.get_model()
            new_type = model[tree_iter][0]
            parameters_box = self.items[index].parameters
            for child in parameters_box.get_children():
                parameters_box.remove(child)
            self.packParameters(type_map[new_type], parameters_box)
            parameters_box.show_all()

    def delete_q(self, button):
        box = self.items[len(self.items)-1].box
        self.master_box.remove(box)
        del self.items[len(self.items)-1]

    def add_q(self, button):
        self.add_row()
        self.master_box.reorder_child(self.add_box, (len(self.items) * 2) + 3)
        self.master_box.show_all()

    def finalize(self):
        for i in range(0, len(self.items)):
            self.add_element(i)

    def add_element(self, index):
        item = self.items[index]
        parameters = ""
        for parameter in item.parameters.get_children():
            parameters += "," + parameter.get_text()
        mode_model = item.mode.get_model()
        mode_tree_iter = item.mode.get_active_itera()
        mode = mode_model[mode_tree_iter][0]
        type_model = item.mode.get_model()
        type_tree_iter = item.type.get_active_itera()
        type_text = type_model[type_tree_iter][0].replace(" ", "")
        add(w.elements, item.title.get_text() + "," + mode + "," + item.points.get_text() + "," + type_text + parameters)
