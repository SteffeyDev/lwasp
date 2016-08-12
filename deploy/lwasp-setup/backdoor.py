import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w

class BackdoorBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.paths = []
        self.titles = []

        for i in range(0,5):

            label = ""
            extra = None
            label2 = None
            extra2 = None
            if i == 0:
                extra = Gtk.Entry(placeholder_text="e.g. /etc/perl.bash")
                label = "Score for Removing PERL Backdoor, which will be installed at "
            elif i == 1:
                extra = Gtk.Entry(placeholder_text="e.g. /home/.backdoor.php")
                label = "Score for Removing PHP Backdoor, which will be installed at "
            elif i == 2:
                extra = Gtk.Entry(placeholder_text="e.g. /usr/bin/nc")
                label = "Score for Removing Netcat Backdoor, which will be installed at "
            elif i == 3:
                extra2 = Gtk.Entry(placeholder_text="e.g. Media Files")
                label = "Score for Removing "
                label2 = " which are located at "
                extra = Gtk.Entry(placeholder_text="e.g. /home/user/Pictures")
            elif i == 4:
                extra2 = Gtk.Entry(placeholder_text="e.g. Hacking Tools")
                label = "Score for Removing "
                label2 = " which are located at "
                extra = Gtk.Entry(placeholder_text="e.g. /usr/lib/john3.1.1")

            container_box = Gtk.Box(spacing=5)
            check_button = Gtk.CheckButton(label)
            check_button.connect("clicked", self.check_button_clicked)
            check_button.type = i
            container_box.pack_start(check_button, False, False, 0)
            if extra2 is not None:
                container_box.pack_start(extra2, False, False, 0)
            if label2 is not None:
                container_box.pack_start(Gtk.Label(label2), False, False, 0)
            if extra is not None:
                container_box.pack_start(extra, False, False, 0)


            self.paths.append(extra)
            self.titles.append(extra2)

            master_box.pack_start(container_box, False, False, 0)

        note_label = Gtk.Label()
        note_label.set_markup('<span foreground="grey"><small>The first three files are put in place automatically by this scoring engine, the last two are ones that you put on the system. Your custum entries can reference a file or a folder.</small></span>')
        note_label.set_line_wrap(True)
        master_box.pack_end(note_label, False, False, 0)

        self.add_with_viewport(master_box)

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

        path_list = path.split("/")
        filepath = "/".join(path_list[0:(len(path)-2)])
        filename = path_list[len(path_list)-1]

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
