# Copyright (C) 2015 Peter Steffey

import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w
from collections import namedtuple

Item = namedtuple("Items", "username expanded options_box box")

class UserBox(Gtk.ScrolledWindow):
    def __init__(self, update_users):
        Gtk.ScrolledWindow.__init__(self)
        self.items = []

        self.update_users = update_users

        self.master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        guest_user_button = Gtk.CheckButton("Score for disabling the guest user account")
        guest_user_button.connect("clicked", self.guest_user_button_changed)
        self.master_box.pack_start(guest_user_button, False, False, 0)
        self.master_box.pack_start(Gtk.HSeparator(), False, False, 0)

        self.autologin_user = "n/a"

        if isfile('/etc/lightdm/lightdm.conf'):
            with open('/etc/lightdm/lightdm.conf', 'r') as lightdm:
                for line in lightdm:
                    if "autologin-user" in line:
                        self.autologin_user = line.rstrip().split("=")[1]
                        break

        self.admins = []
        with open('/etc/group', 'r') as groups:
            for line in groups:
                if 'sudo:' in line:
                    self.admins = line.rstrip().split(":")[3].split(',')
                    break

        users = open('/etc/passwd', 'r')
        number_of_lines = 0
        for line in users:
            if int(line.split(":")[2]) < 1000: continue
            if "nobody" in line: continue

            self.add_row(line)

            number_of_lines += 1

        self.add_box = Gtk.Box()
        self.username_entry = Gtk.Entry(placeholder_text="Username")
        self.username_entry.set_width_chars(11)
        self.name_entry = Gtk.Entry(placeholder_text="Full Name")
        self.password_entry = Gtk.Entry(placeholder_text="Password")
        self.password_entry.set_visibility(False)
        self.add_box.pack_start(self.username_entry, False, False, 0)
        self.add_box.pack_start(self.name_entry, False, False, 0)
        self.add_box.pack_start(self.password_entry, False, False, 0)
        add_label = Gtk.Label("Add as: ")
        add_admin = Gtk.Button(label="Admin")
        add_backdoor = Gtk.Button(label="Backdoor")
        add_user = Gtk.Button(label="User")
        add_backdoor.props.halign = Gtk.Align.END
        add_user.props.halign = Gtk.Align.END
        add_label.props.halign = Gtk.Align.END
        add_admin.props.halign = Gtk.Align.END
        add_backdoor.connect("clicked", self.add_backdoor_user)
        add_user.connect("clicked", self.add_user)
        add_admin.connect("clicked", self.add_admin)
        self.add_box.pack_end(add_backdoor, False, False, 0)
        self.add_box.pack_end(add_admin, False, False, 0)
        self.add_box.pack_end(add_user, False, False, 0)
        self.add_box.pack_end(add_label, False, False, 0)
        self.master_box.pack_start(self.add_box, False, False, 0)

        self.add_with_viewport(self.master_box)

    def guest_user_button_changed(self, button):
        if get_version() > 14.0:
            add(w.elements, "Guest account is disabled,V,6,Command,cat /usr/share/lightdm/lightdm.conf.d/*.conf,TRUE,allow-guest=false")
        else:
            add(w.commands, "sudo printf 'allow-guest=true' >> /etc/lightdm/lightdm.conf")
            add(w.elements, "Guest account is disabled,V,6,FileContents,/etc/lightdm/lightdm.conf,FALSE,allow-guest=true")

    def add_row(self, line, backdoor=False):
        user_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        username = line.split(":")[0]

        w.users.append(username)
        self.update_users()

        full_name = line.split(":")[4].replace(",", "")
        if backdoor:
            username += " - backdoor"

        user_wrapper_box = Gtk.Box(spacing=50)
        label = Gtk.Label(full_name + " (" + username + ")" if full_name != "" else username)
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
                if backdoor: continue
                label = "Score for Password Change"
            if i == 1:
                if backdoor: continue
                if username not in self.admins: continue
                label = "Score for Revoking Admin Access"
            if i == 2:
                label = "Score for Account Deletion"
            if i == 3:
                if username != self.autologin_user: continue
                label = "Score for Turning Off Auto-Login"

            password_changed_check = Gtk.CheckButton(label)
            password_changed_check.connect("clicked", self.check_button_clicked)
            password_changed_check.type = i
            password_changed_check.index = len(self.items)
            if backdoor:
                password_changed_check.set_active(True)
            options_box.pack_start(password_changed_check, True, True, 0)

        if line.split(":")[1] == " ":
            delete_button = Gtk.Button("Remove Account")
            delete_button.index = len(self.items)
            delete_button.connect("clicked", self.delete_user)
            options_box.pack_end(delete_button, False, False, 0)

        self.items.append(Item(username = username, expanded = False, box = user_box, options_box = options_box))

    def delete_user(self, button):
        username = self.items[button.index].username
        w.users.remove(username)
        toremove = []
        for i in range(0, len(w.commands) - 1):
            if username in w.commands[i]:
                toremove.append(w.commands[i])
        for item in toremove:
            w.commands.remove(item)
        toremove = []
        for i in range(0, len(w.elements) - 1):
            if username in w.elements[i]:
                toremove.append(w.elements[i])
        for item in toremove:
            w.elements.remove(item)
        del self.items[button.index]
        self.master_box.remove(self.master_box.get_children()[len(self.master_box.get_children()) - 2])
        self.master_box.remove(self.master_box.get_children()[len(self.master_box.get_children()) - 2])

    def add_user(self, button):
        username = self.username_entry.get_text()
        full_name = self.name_entry.get_text()
        password = self.password_entry.get_text()
        if username == "" or full_name == "" or password == "":
            show_error(self.get_toplevel(), "Insufficient Information", "You must fill out all three fields to create a user")
            return

        self.add_row(self.username_entry.get_text() + ": : : :" + full_name)
        self.refresh_after_add()
        add(w.commands, "sudo useradd -c \"" + full_name + "\" " + username)
        add(w.commands, "echo " + username + ":" + password + " | sudo chpasswd ")

    def add_backdoor_user(self, button):
        username = self.username_entry.get_text()
        full_name = self.name_entry.get_text()
        password = self.password_entry.get_text()
        if username == "" or password == "":
            show_error(self.get_toplevel(), "Insufficient Information", "You must fill out the username and password fields to create a backdoor user")
            return
        self.add_row(username + ": : : :" + full_name, True)
        self.refresh_after_add()
        user_id = 900 + len(self.items)
        add(w.commands, "sudo useradd -M -d / -G sudo -u " + str(user_id) + " -c \"" + full_name + "\" " + username)
        add(w.commands, "echo " + username + ":" + password + " | sudo chpasswd ")
        add(w.commands, "sudo shuf -o /etc/passwd /etc/passwd")
        add(w.commands, "sudo shuf -o /etc/group /etc/group")
        add(w.elements, "Backdoor user " + username + " removed,V,5,FileContents,/etc/passwd,FALSE," + username)
        # add user to system and elements file

    def add_admin(self, button):
        username = self.username_entry.get_text()
        full_name = self.name_entry.get_text()
        password = self.password_entry.get_text()
        if username == "" or full_name == "" or password == "":
            show_error(self.get_toplevel(), "Insufficient Information", "You must fill out all three fields to create a user")
            return
        self.admins.append(username)
        self.add_row(self.username_entry.get_text() + ": : : :" + full_name)
        self.refresh_after_add()
        add(w.commands, "sudo useradd -c \"" + full_name + "\" " + username)
        add(w.commands, "echo " + username + ":" + password + " | sudo chpasswd ")
        add(w.commands, "sudo usermod -aG sudo " + username)


    def refresh_after_add(self):
        self.master_box.show_all()
        self.username_entry.set_text("")
        self.name_entry.set_text("")
        self.password_entry.set_text("")
        self.master_box.reorder_child(self.add_box, (len(self.items) * 2) + 2)

    def check_button_clicked(self, button):
        item = self.items[button.index]
        if button.type == 0:
            add(w.elements, 'Password changed for user ' + item.username + ',V,5,FileContents,/var/log/auth.log,TRUE,password changed for ' + item.username)
        elif button.type == 1:
            add(w.elements, 'User ' + item.username + ' is no longer an administrator,V,5,FileContents,/var/log/auth.log,TRUE,delete \'' + item.username + '\' from group \'sudo\'')
        elif button.type == 2:
            add(w.elements, 'User ' + item.username + ' was deleted,V,5,FileContents,/etc/passwd,FALSE,' + item.username)
        else:
            add(w.elements, 'Auto-Login turned off for user ' + item.username + ',V,7,FileContents,/etc/lightdm/lightdm.conf,FALSE,autologin-user=' + item.username)

    def expand_button_clicked(self, button):
        if button.index >= len(self.items): return
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
