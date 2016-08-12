import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w
from collections import namedtuple
import subprocess
from os.path import isfile
from os.path import expanduser

Item = namedtuple("Items", "text answer box")

class ForensicsBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.items = []

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)

        self.add_box = Gtk.Box()
        add_q = Gtk.Button(label="Add Forensics Question")
        add_q.props.halign = Gtk.Align.END
        add_q.connect("clicked", self.add_q)
        self.add_box.pack_end(add_q, False, False, 0)
        self.master_box.pack_start(self.add_box, False, False, 0)

        note_label = Gtk.Label()
        note_label.set_markup('<span foreground="grey"><small>Don\'t type the "ANSWER:" part, that will be added for you. Just type out the question and the answer.</small></span>')
        note_label.set_line_wrap(True)
        self.master_box.pack_end(note_label, False, False, 0)

        self.add_with_viewport(self.master_box)

    def add_row(self):
        user_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        label = Gtk.Label("Forensics Question #" + str(len(self.items) + 1))
        user_box.pack_start(label, False, False, 0)

        textviewBox = Gtk.Box()
        #scrollWindow = Gtk.ScrolledWindow()
        textviewBox.set_size_request(780, 100)
        #scrollWindow.set_vexpand(True)
        textview = Gtk.TextView()
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        label2 = Gtk.Label("Question: ")
        textviewBox.pack_start(label2, False, False, 0)
        textviewBox.pack_start(textview, True, True, 0)
        user_box.pack_start(textviewBox, False, False, 10)

        answer_entry = Gtk.Entry(placeholder_text="Answer")
        user_box.pack_start(answer_entry, False, False, 0)

        delete_box = Gtk.Box()
        delete_button = Gtk.Button("Remove Forensics Question")
        delete_button.index = len(self.items)
        delete_button.props.halign = Gtk.Align.END
        delete_button.connect("clicked", self.delete_q)
        delete_box.pack_end(delete_button, False, False, 0)
        user_box.pack_start(delete_box, False, False, 0)

        user_box.pack_start(Gtk.HSeparator(), False, False, 0)

        self.master_box.pack_start(user_box, False, True, 0)

        self.items.append(Item(text = textview, answer = answer_entry, box=user_box))

    def delete_q(self, button):
        box = self.items[len(self.items)-1].box
        self.master_box.remove(box)
        del self.items[len(self.items)-1]

    def add_q(self, button):
        self.add_row()
        self.master_box.reorder_child(self.add_box, len(self.items) * 2)
        self.master_box.show_all()

    def finalize(self):
        for i in range(0, len(self.items)):
            self.add_element(i)

    def add_element(self, index):
        item = self.items[index]
        add(w.commands, "sudo printf \"" + item.text.get_buffer().get_text(item.text.get_buffer().get_start_iter(), item.text.get_buffer().get_end_iter(), False) + "\n\nANSWER: \" > " + expanduser("~") + "/Desktop/ForensicsQuestion" + str(index + 1) + ".txt")
        add(w.commands, "sudo chown " + os.environ['SUDO_USER'] + " " + expanduser("~") + "/Desktop/ForensicsQuestion" + str(index + 1) + ".txt")
        add(w.elements, "Forensics question #" + str(index + 1) + " answered correctly,V,10,Forensics," + expanduser("~") + "/Desktop/ForensicsQuestion" + str(index + 1) + ".txt," + item.answer.get_text())
