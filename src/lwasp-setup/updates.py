# Copyright (C) 2015 Peter Steffey

import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w
from collections import namedtuple

Item = namedtuple("Items", "name box")

class UpdatesBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.items = []

        self.master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        for i in range(0,5):

            label = ""
            if i == 0: label = "Score for Enabling Auto-install Security Updates"
            elif i == 1: label = "Score for Enabling Auto-download Security Updates"
            elif i == 2: label = "Score for Enabling Check for Updates Daily"
            elif i == 3: label = "Score for Performing All Security Updates"
            elif i == 4: label = "Score for Performing All Updates"

            check_button = Gtk.CheckButton(label)
            check_button.connect("clicked", self.check_button_clicked)
            check_button.type = i
            self.master_box.pack_start(check_button, False, False, 0)

        # time consuming
        updates_string = subprocess.Popen(["/usr/lib/update-notifier/apt-check", "-p"], stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[1]
        self.updates = updates_string.split('\n')

        for update in self.updates:
            self.add_row(update)

        self.add_with_viewport(self.master_box)

    def add_row(self, app):
        update_row = Gtk.Box(spacing=5)

        label = Gtk.Label(app)
        update_row.pack_start(label, False, True, 0)

        check_button = Gtk.CheckButton("Score for Updating")
        check_button.connect("clicked", self.update_button_clicked)
        check_button.props.halign = Gtk.Align.END
        check_button.index = len(self.items)
        update_row.pack_end(check_button, False, True, 0)

        separator = Gtk.HSeparator()
        self.master_box.pack_start(separator, False, True, 0)

        self.master_box.pack_start(update_row, False, True, 0)

        self.items.append(Item(name = app, box = update_row))

    def update_button_clicked(self, button):
        item = self.items[button.index]
        dpkg_update_step1 = subprocess.Popen(["apt-cache", "policy", item.name], stdout=subprocess.PIPE)
        dpkg_update = subprocess.check_output(["grep", "Candidate"], stdin=dpkg_update_step1.stdout)
        version = dpkg_update.strip().split(' ')[1]
        add(w.elements, 'Service ' + item.name + ' is updated,V,7,Package,' + item.name + ',updated,' + version)

    def check_button_clicked(self, button):
        i = button.type

        if i == 0:
            if get_version() > 15:
                add(w.elements, "Auto-Install Security Updates Enabled,V,7,FileContents,/etc/apt/apt.conf.d/20auto-upgrades,TRUE,APT::Periodic::Unattended-Upgrade \"1\"")
            else:
                add(w.elements, "Auto-Install Security Updates Enabled,V,7,FileContents,/etc/apt/apt.conf.d/10periodic,TRUE,APT::Periodic::Unattended-Upgrade \"1\"")
        elif i == 1: add(w.elements, "Auto-Download Security Updates Enabled,V,7,FileContents,/etc/apt/apt.conf.d/10periodic,TRUE,APT::Periodic::Download-Upgradeable-Packages \"1\"")
        elif i == 2: add(w.elements, "Check for Updates Daily Enabled,V,7,FileContents,/etc/apt/apt.conf.d/10periodic,TRUE,APT::Periodic::Update-Package-Lists \"1\"")
        elif i == 3: add(w.elements, "All Security Updates Complete,V,4,Command,/usr/lib/update-notifier/apt-check,TRUE,;0")
        elif i == 4: add(w.elements, "All Updates Complete,V,4,Command,/usr/lib/update-notifier/apt-check,TRUE,0;0")
