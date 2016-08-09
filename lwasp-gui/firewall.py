import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w

class FirewallBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.entries = []


        for i in range(0,5):

            label = ""
            extra = None
            if i == 0: label = "Score for Enabling UFW"
            elif i == 1: label = "Score for Enabling Verbose Logging for UFW"
            elif i == 2:
                extra = Gtk.Entry(placeholder_text="Port #")
                label = "Score for Configuring Firewall to Block Port "
            elif i == 3:
                extra = Gtk.Entry(placeholder_text="Port #")
                label = "Score for Configuring Firewall to Block Port "
            elif i == 4:
                extra = Gtk.Entry(placeholder_text="Port #")
                label = "Score for Configuring Firewall to Block Port "

            container_box = Gtk.Box(spacing=20)
            check_button = Gtk.CheckButton(label)
            check_button.connect("clicked", self.check_button_clicked)
            check_button.type = i
            container_box.pack_start(check_button, False, False, 0)
            self.entries.append(extra)
            if extra is not None:
                container_box.pack_start(extra, False, False, 0)

            master_box.pack_start(container_box, False, False, 0)

        self.add(master_box)

    def check_button_clicked(self, button):
        i = button.type

        port = ""

        if i in range(2,5):
            port = self.entries[i].get_text()
            if port == "" and button.get_active() == True:
                button.set_active(False)
                show_error(self.get_toplevel(), "Value Needed", "Please enter a port number before enabling this")
                return
            elif port == "": return
            self.entries[i].set_editable(not button.get_active())

        if i == 0: add(w.elements, "Firewall is active,V,6,Command,sudo ufw status,FALSE,inactive")
        elif i == 1: add(w.elements, "Firewall logging is on High,V,7,FileContents,/etc/ufw/ufw.conf,TRUE,LOGLEVEL=high")
        elif i == 2: add(w.elements, "Firewall in configured to block port " + port + ",V,7,FileContents,/lib/ufw/user.rules,TRUE," + port + " -j DROP")
        elif i == 3: add(w.elements, "Firewall in configured to block port " + port + ",V,7,FileContents,/lib/ufw/user.rules,TRUE," + port + " -j DROP")
        elif i == 4: add(w.elements, "Firewall in configured to block port " + port + ",V,7,FileContents,/lib/ufw/user.rules,TRUE," + port + " -j DROP")

        print w.elements
