import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w

class UserBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.expanded = []
        self.options_boxes = []
        self.boxes = []

        self.master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        print "master: ", self.master_box

        self.autologin_user = "n/a"

        if isfile('/etc/lightdm/lightdm.conf'):
            with open('/etc/lightdm/lightdm.conf') as lightdm:
                for line in lightdm:
                    if "autologin-user" in line:
                        self.autologin_user = line.split("=")[1]
                        break

        users = open('/etc/passwd', 'r')
        number_of_lines = 0
        for line in users:
            if int(line.split(":")[2]) < 1000: continue

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
        add_backdoor = Gtk.Button(label="Add as Backdoor User")
        add_user = Gtk.Button(label="Add as Normal User")
        add_backdoor.props.halign = Gtk.Align.END
        add_user.props.halign = Gtk.Align.END
        add_backdoor.connect("clicked", self.add_backdoor_user)
        add_user.connect("clicked", self.add_user)
        self.add_box.pack_end(add_backdoor, False, False, 0)
        self.add_box.pack_end(add_user, False, False, 0)
        self.master_box.pack_start(self.add_box, False, False, 0)

        self.add(self.master_box)

    def add_row(self, line, backdoor=False):
        print line
        user_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        username = line.split(":")[0]
        full_name = line.split(":")[4].replace(",", "")
        if backdoor:
            username += " (backdoor)"

        user_wrapper_box = Gtk.Box(spacing=50)
        label = Gtk.Label(full_name + " (" + username + ")" if full_name != "" else username)
        user_wrapper_box.pack_start(label, False, True, 0)
        button = Gtk.Button(label="Expand")
        button.props.halign = Gtk.Align.END
        button.index = len(self.expanded)
        button.connect("clicked", self.expand_button_clicked)
        user_wrapper_box.pack_end(button, False, True, 0)
        user_box.pack_start(user_wrapper_box, False, False, 0)
        self.master_box.pack_start(user_box, False, True, 0)

        separator = Gtk.HSeparator()
        self.master_box.pack_start(separator, False, True, 0)

        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        option_range = range(0, 3)
        if backdoor:
            option_range = range(2, 3)
        if username == self.autologin_user:
            option_range = range(0, 4)
        for i in option_range:

            label = ""
            if i == 0: label = "Score for Password Change"
            if i == 1: label = "Score for Revoking Admin Acess"
            if i == 2: label = "Score for Account Deletion"
            if i == 3: label = "Score for Turning Off Auto-Login"

            password_changed_check = Gtk.CheckButton(label)
            password_changed_check.connect("clicked", self.check_button_clicked)
            password_changed_check.type = i
            if backdoor:
                password_changed_check.set_active(True)
            options_box.pack_start(password_changed_check, True, True, 0)

        self.options_boxes.append(options_box)
        self.boxes.append(user_box)
        self.expanded.append(False)

    def add_user(self, button):
        username = self.username_entry.get_text()
        full_name = self.name_entry.get_text()
        password = self.password_entry.get_text()
        if username == "" or full_name == "" or password == "": return
        self.add_row(self.username_entry.get_text() + ":")
        self.refresh_after_add()
        add(w.commands, "sudo useradd -c \"" + full_name + "\" " + username)
        add(w.commands, "echo " + username + ":" + password + " | sudo chpasswd ")

    def add_backdoor_user(self, button):
        username = self.username_entry.get_text()
        full_name = self.name_entry.get_text()
        password = self.password_entry.get_text()
        self.add_row(username + ":", True)
        self.refresh_after_add()
        user_id = 900 + len(self.expanded)
        add(w.commands, "sudo useradd -M -d / -G sudo -u " + str(user_ID) + " -c \"" + full_name + "\" " + username)
        add(w.commands, "echo " + username + ":" + password + " | sudo chpasswd ")
        add(w.commands, "sudo shuf -o /etc/passwd /etc/passwd")
        add(w.elements, "Backdoor user " + username + " removed,V,5,FileContents,/etc/passwd,FALSE" + username)
        # add user to system and elements file

    def refresh_after_add(self):
        self.master_box.show_all()
        self.username_entry.set_text("")
        self.master_box.reorder_child(self.add_box, len(self.expanded) * 2)

    def check_button_clicked(self, button):
        if button.type == 0:
            #elements add item
            hh = ''
        elif button.type == 1:
            #same
            hh = ''
        elif button.type == 2:
            #same
            hh = ''
        else:
            #same
            hh = ''

    def expand_button_clicked(self, button):

        box = self.boxes[button.index]

        if self.expanded[button.index] == True:
            button.set_label("Expand")
            box.remove(self.options_boxes[button.index])
        else:
            button.set_label("Collapse")
            box.pack_end(self.options_boxes[button.index], True, True, 0)
            box.show_all()

        self.expanded[button.index] = not self.expanded[button.index]
