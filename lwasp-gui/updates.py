import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w
from collections import namedtuple

class UpdatesBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

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
            master_box.pack_start(check_button, False, False, 0)

        self.add(master_box)

    def check_button_clicked(self, button):
        i = button.type
        if i == 0: add(w.elements, "Auto-Install Security Updates Enabled,V,7,FileContents,/etc/apt/apt.conf.d/10periodic,APT::Periodic::Unattended-Upgrade \"1\"")
        elif i == 1: add(w.elements, "Auto-Install Security Updates Enabled,V,7,FileContents,/etc/apt/apt.conf.d/10periodic,APT::Periodic::Download-Upgradeable-Packages \"1\"")
        elif i == 2: add(w.elements, "Auto-Install Security Updates Enabled,V,7,FileContents,/etc/apt/apt.conf.d/10periodic,APT::Periodic::Update-Package-Lists \"7\"")
        elif i == 3: add(w.elements, "All Security Updates Complete,V,4,Command,/usr/lib/update-notifier/apt-check,;0")
        elif i == 4: add(w.elements, "All Updates Complete,V,4,Command,/usr/lib/update-notifier/apt-check,0;0")
        print w.elements
