import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w

class MiscBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.extras = []

        title_label_1 = Gtk.Label()
        title_label_1.set_markup('<big>Sudo Configuration</big>')
        master_box.pack_start(title_label_1, False, False, 0)

        for i in range(0,2):

            if i == 0:
                users = w.users
                extra = Gtk.ComboBoxText()
                extra.set_entry_text_column(0)
                for user in users:
                    extra.append_text(user)
                label = "Score for deleting an insecure entry in the sudoers file that gives this user root access*: "
            elif i == 1:
                label = "Score for deleting insecure file in the /etc/sudoers.d/ directory"

            container_box = Gtk.Box(spacing=5)
            check_button = Gtk.CheckButton(label)
            check_button.connect("clicked", self.check_button_clicked)
            check_button.type = i
            container_box.pack_start(check_button, False, False, 0)
            if extra is not None:
                container_box.pack_start(extra, False, False, 0)


            self.extras.append(extra)

            master_box.pack_start(container_box, False, False, 0)

        master_box.pack_start(Gtk.HSeparator(), False, False, 0)

        note_label = Gtk.Label()
        note_label.set_markup('<span foreground="grey"><small>* root access without needing to be an administrator or use a password.</small></span>')
        note_label.set_line_wrap(True)
        master_box.pack_end(note_label, False, False, 0)

        self.add(master_box)

    def check_button_clicked(self, button):
        i = button.type

        title = ""

        path = self.paths[i].get_text()
        if path == "" and button.get_active() == True:
            button.set_active(False)
            show_error(self.get_toplevel(), "Value Needed", "Please enter a file path before enabling this")
            return
        elif path == "": return
        self.paths[i].set_editable(not button.get_active())

        filepath = "/".join(path.split("/")[0:(len(path)-2)])
        filename = path.split("/")[len(path)-1]

        if i in range(3,5):
            title = self.titles[i].get_text()
            if title == "" and button.get_active() == True:
                button.set_active(False)
                show_error(self.get_toplevel(), "Value Needed", "Please a title before enabling this")
                return
            elif title == "": return
            self.titles[i].set_editable(not button.get_active())

        if i == 0:
            add(w.commands, "sudo mkdir -p " + filepath)
            add(w.commands, "sudo mv backdoors/perl " + path)
            add(w.elements, "PERL Backdoor removed,V,10,FileExistance," + path + ",FALSE")
        elif i == 1:
            add(w.commands, "sudo mkdir -p " + filepath)
            add(w.commands, "sudo mv backdoors/php " + path)
            add(w.elements, "PHP Backdoor removed,V,10,FileExistance," + path + ",FALSE")
        elif i == 2:
            add(w.commands, "sudo mkdir -p " + filepath)
            add(w.commands, "sudo mv backdoors/netcat " + path)
            add(w.elements, "Netcat Backdoor removed,V,10,FileExistance," + path + ",FALSE")
        elif i == 3 or i == 4:
            add(w.elements, title + " removed,V,10,FileExistance," + path + ",FALSE")


        print w.elements
