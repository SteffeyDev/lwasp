# Copyright (C) 2015 Peter Steffey

import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w
from collections import namedtuple

class PasswdBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.entries = []

        for i in range(0,9):

            label = ""
            extra = None
            if i == 0: label = "Score for Creating Password History File"
            elif i == 1: label = "Score for Disallowing Null Passwords"
            elif i == 2: label = "Score for Aditing failed password attempts"
            elif i == 3:
                extra = Gtk.Entry(placeholder_text="Min Length")
                label = "Score for Setting a Minimum Password Length"
            elif i == 4:
                extra = Gtk.Entry(placeholder_text="Max Age")
                label = "Score for Setting a Maximum Password Age"
            elif i == 5:
                extra = Gtk.Entry(placeholder_text="Warn Age")
                label = "Score for Setting a Password Warn Age"
            elif i == 6: label = "Score for Storing Passwords with SHA-512 Encryption"
            elif i == 7: label = "Score for Setting Password Complexity Requirements"
            elif i == 8: label = "Score for Enforcing Password History"

            container_box = Gtk.Box(spacing=20)
            check_button = Gtk.CheckButton(label)
            check_button.connect("clicked", self.check_button_clicked)
            check_button.type = i

            self.entries.append(extra)
            if extra is not None:
                container_box.pack_start(extra, False, False, 0)
            container_box.pack_start(check_button, False, False, 0)

            master_box.pack_start(container_box, False, False, 0)

        self.add_with_viewport(master_box)

    def check_button_clicked(self, button):
        i = button.type
        text = ""

        if i in range(3,6):
            text = self.entries[i].get_text()
            if text == "" and button.get_active() == True:
                button.set_active(False)
                show_error(self.get_toplevel(), "Value Needed", "Please an integer value before enabling this")
                return
            elif text == "": return
            self.entries[i].set_editable(not button.get_active())

        if i == 0:
            add(w.commands, "sudo rm /etc/security/opasswd")
            add(w.elements, "Created a password history file,V,6,FileExistance,/etc/security/opasswd,TRUE")
        elif i == 1: add(w.elements, "Null passwords are no longer allowed,V,7,FileContents,/etc/pam.d/common-auth,FALSE,nullok_secure")
        elif i == 2: add(w.elements, "Auditing for failed password attempts is enabled,V,7,FileContents,/etc/pam.d/common-auth,TRUE,pam_tally.so~audit")
        elif i == 3: add(w.elements, "A Minimum password length is set,V,7,FileContents,/etc/pam.d/common-password,TRUE,pam_cracklib.so~minlen=" + text)
        elif i == 4: add(w.elements, "A Maximum password age is set,V,7,FileContents,/etc/login.defs,TRUE,PASS_MAX_DAYS " + text)
        elif i == 5: add(w.elements, "A Password warn age is set,V,7,FileContents,/etc/login.defs,TRUE,PASS_WARN_AGE " + text)
        elif i == 6:
            add(w.commands, "sudo sed -i.bak s/sha512/''/g /etc/pam.d/common-password")
            add(w.commands, "sudo rm /etc/pam.d/common-password.bak")
            add(w.elements, "Passwords are stored with SHA-512 Encryption,V,7,FileContents,/etc/pam.d/common-password,TRUE,pam_unix.so~sha512")
        elif i == 7: add(w.elements, "Password complexity requirement are set,V,7,FileContents,/etc/pam.d/common-password,TRUE,pam_cracklib.so~dcredit,pam_cracklib.so~ucredit,pam_cracklib.so~lcredit,pam_crachlib.so~ocredit")
        elif i == 8: add(w.elements, "Password history is enforced,V,7,FileContents,/etc/pam.d/common-password,TRUE,pam_pwhistory.so~remember=" + text)
