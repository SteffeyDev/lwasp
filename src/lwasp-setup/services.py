# Copyright (C) 2015 Peter Steffey

import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w
from collections import namedtuple
import subprocess
from os.path import isfile
import apt

Item = namedtuple("Items", "name expanded options_box box")

class AppsBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.items = []

        self.master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

        self.entries = []
        for i in range(0,3):
            container_box = Gtk.Box(spacing=5)
            check_button = Gtk.CheckButton('Score for installing software: ')
            check_button.connect("clicked", self.add_check_button_clicked)
            check_button.type = i
            container_box.pack_start(check_button, False, False, 0)
            text_box = Gtk.Entry(placeholder_text="name of package")
            container_box.pack_start(text_box, False, False, 0)
            self.entries.append(text_box)
            self.master_box.pack_start(container_box, False, False, 0)

        title_label_1 = Gtk.Label()
        title_label_1.set_markup('<big>Installed Services</big>')
        self.master_box.pack_start(Gtk.HSeparator(), False, False, 0)
        self.master_box.pack_start(title_label_1, False, False, 0)

        self.apps_list = [app.split(' ')[5] for app in subprocess.check_output(["service", "--status-all"]).split('\n') if len(app.split(' ')) > 5]
        for app in self.apps_list:
				    self.add_row(app)

        self.add_box = Gtk.Box()
        self.add_box.pack_start(Gtk.Label("To install more services, run 'apt-get install' in another terminal and then reload"), False, False, 0)
        add_app = Gtk.Button(label="Reload Services")
        add_app.props.halign = Gtk.Align.END
        add_app.connect("clicked", self.refresh_list)
        self.add_box.pack_end(add_app, False, False, 0)
        self.master_box.pack_end(self.add_box, False, False, 0)

        self.add_with_viewport(self.master_box)

    def add_row(self, app):
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

        for i in range(0,4):

            label = ""
            if i == 0:
                label = "Score for Stopping"
            elif i == 1:
                label = "Score for Uninstalling"
            elif i == 2:
                label = "Penalize for Stopping (Critical Service)"
            elif i == 3:
                label = "Penalize for Uninstalling (Critical Service)"

            check_button = Gtk.CheckButton(label)
            check_button.connect("clicked", self.check_button_clicked)
            check_button.type = i
            check_button.index = len(self.items)
            options_box.pack_start(check_button, True, True, 0)

        self.items.append(Item(name = app, expanded = False, box = user_box, options_box = options_box))

    def delete_app(self, button):
        name = self.items[button.index].name
        toremove = []
        for i in range(0, len(w.commands) - 1):
            if name in w.commands[i]:
                toremove.append(w.commands[i])
        for item in toremove:
            w.commands.remove(item)
        toremove = []
        for i in range(0, len(w.elements) - 1):
            if name in w.elements[i]:
                toremove.append(w.elements[i])
        for item in toremove:
            w.elements.remove(item)
        del self.items[button.index]
        self.master_box.remove(self.master_box.get_children()[len(self.master_box.get_children()) - 2])
        self.master_box.remove(self.master_box.get_children()[len(self.master_box.get_children()) - 2])

    def refresh_list(self, button):
        new_apps_list = [app.split(' ')[5] for app in subprocess.check_output(["service", "--status-all"]).split('\n') if len(app.split(' ')) > 5]
        new_apps = list(set(new_apps_list) - set(self.apps_list))
        for app in new_apps:
            self.add_row(app)
        self.master_box.show_all()
        self.master_box.reorder_child(self.add_box, (len(self.items) * 2) + 5)
        self.apps_list = new_apps_list

    def check_button_clicked(self, button):
        item = self.items[button.index]

        if button.type == 0:
            add(w.elements, 'Service ' + item.name + ' stopped,V,8,Service,' + item.name + ',FALSE,active')
        elif button.type == 1:
            add(w.elements, 'Service ' + item.name + ' is no longer installed,V,10,Service,' + item.name + ',FALSE,loaded')
        elif button.type == 2:
            add(w.elements, 'Service ' + item.name + ' stopped,P,8,Service,' + item.name + ',FALSE,active')
        elif button.type == 3:
            add(w.elements, 'Service ' + item.name + ' is no longer installed,P,10,Service,' + item.name + ',FALSE,loaded')

    def expand_button_clicked(self, button):
        item = self.items[button.index]
        box = item.box

        if item.expanded == True:
            button.set_label("Expand")
            box.remove(item.options_box)
        else:
            button.set_label("Collapse")
            box.pack_end(item.options_box, True, True, 0)
            box.show_all()

        self.items[button.index] = self.items[button.index]._replace(expanded = not item.expanded)

    def add_check_button_clicked(self, button):
        i = button.type

        title = self.entries[i].get_text()

        check = subprocess.Popen(["apt-cache", "search", "--names-only", "^" + title + "$"], stdout=subprocess.PIPE).communicate()[0]

        if title == "" and button.get_active() == True:
            button.set_active(False)
            show_error(self.get_toplevel(), "Value Needed", "Please enter a package name before enabling this")
            return
        elif check == "" and button.get_active() == True:
            button.set_active(False)
            show_error(self.get_toplevel(), "App Does Not Exist", "The service you want the student to install is not available in the apt-get repositories on this system.")
            return
        elif title == "" or check == "": return
        self.entries[i].set_editable(not button.get_active())

        add(w.elements, title + " installed,V,6,Command,dpkg -l,TRUE," + title)
