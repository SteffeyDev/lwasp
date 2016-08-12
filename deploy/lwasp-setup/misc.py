import gi
from os.path import isfile
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w

class MiscBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.extras = []

        title_label_1 = Gtk.Label()
        title_label_1.set_markup('<big>Sudo Configuration</big>')
        master_box.pack_start(title_label_1, False, False, 0)

        for i in range(0,2):

            extra = None

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

        note_label = Gtk.Label()
        note_label.set_markup('<span foreground="grey"><small>* root access without needing to be an administrator or use a password.</small></span>')
        note_label.set_line_wrap(True)
        master_box.pack_start(note_label, False, False, 0)

        master_box.pack_start(Gtk.HSeparator(), False, False, 0)

        title_label_2 = Gtk.Label()
        title_label_2.set_markup('<big>Scheduled Tasks</big>')
        master_box.pack_start(title_label_2, False, False, 0)

        for i in range(2,6):

            extra = None

            if i == 2:
                label = "Score for removing task that turns off the firewall every 5 mins"
            elif i == 3:
                label = "Score for removing task that launches a netcat backdoor every minute"
            elif i == 4:
                label = "Score for removing task that taunts the user with this message every 3 mins: "
                extra = Gtk.Entry(placeholder_text="Taunt")
            elif i == 5:
                label = "Score for removing custum scheduled task that runs every minute: "
                extra = Gtk.Entry(placeholder_text="BASH Command")

            container_box = Gtk.Box(spacing=5)
            check_button = Gtk.CheckButton(label)
            check_button.connect("clicked", self.check_button_clicked)
            check_button.type = i
            container_box.pack_start(check_button, False, False, 0)
            if extra is not None:
                container_box.pack_start(extra, False, False, 0)


            self.extras.append(extra)

            master_box.pack_start(container_box, False, False, 0)

        note_label_3 = Gtk.Label()
        note_label_3.set_markup('<span foreground="grey"><small>Scheduled tasks are put in place in the root crontab by LWASP.  In your custum command, avoid using quotation marks</small></span>')
        note_label_3.set_line_wrap(True)
        master_box.pack_start(note_label_3, False, False, 0)

        master_box.pack_start(Gtk.HSeparator(), False, False, 0)

        title_label_3 = Gtk.Label()
        title_label_3.set_markup('<big>Miscellaneous</big>')
        master_box.pack_start(title_label_3, False, False, 0)

        for i in range(6,8):

            extra = None

            if i == 6:
                label = "Score for disabling IP Spoofing"
            elif i == 7:
                label = "Score for hiding users from the login screen"

            container_box = Gtk.Box(spacing=5)
            check_button = Gtk.CheckButton(label)
            check_button.connect("clicked", self.check_button_clicked)
            check_button.type = i
            container_box.pack_start(check_button, False, False, 0)
            if extra is not None:
                container_box.pack_start(extra, False, False, 0)


            self.extras.append(extra)

            master_box.pack_start(container_box, False, False, 0)

        note_label_2 = Gtk.Label()
        note_label_2.set_markup('<span foreground="grey"><small>Email <a href="mailto:steffeydev@icloud.com">steffeydev@icloud.com</a> to request additional scoring items</small></span>')
        note_label_2.set_line_wrap(True)
        master_box.pack_end(note_label_2, False, False, 0)

        self.add_with_viewport(master_box)

    def update_users(self):
        users = w.users
        self.extras[0].remove_all()
        for user in users:
            self.extras[0].append_text(user)

    def check_button_clicked(self, button):
        i = button.type

        text = ""

        if i in range(4,6):
            text = self.extras[i].get_text()
            if text == "" and button.get_active() == True:
                button.set_active(False)
                show_error(self.get_toplevel(), "Value Needed", "Please enter the needed information before enabling this")
                return
            elif text == "": return
            self.extras[i].set_editable(not button.get_active())

        if i == 0:
            user = ""
            tree_iter = self.extras[i].get_active_iter()
            if tree_iter != None:
                model = self.extras[i].get_model()
                user = model[tree_iter][0]
            if user == "" and button.get_active() == True:
                button.set_active(False)
                show_error(self.get_toplevel(), "Value Needed", "Please select a user before enabling this")
                return
            elif user == "": return

            add(w.commands, "sudo echo \"" + user + "  ALL=(ALL:ALL) ALL\" >> /etc/sudoers")
            add(w.elements, "Insecure sudo configuration fixed,V,12,FileContents,/etc/sudoers,FALSE," + user + "  ALL=(ALL:ALL) ALL")
        elif i == 1:
            add(w.commands, "sudo echo \"" + os.environ['SUDO_USER'] + "  ALL=(ALL) NOPASSWD:ALL\" > /etc/sudoers.d/extra")
            add(w.commands, "sudo chmod 440 /etc/sudoers.d/extra")
            add(w.elements, "Insecure sudo configuration file removed,V,12,FileExistance,/etc/sudoers.d/extra,FALSE")
        elif i == 2:
            add(w.commands, "sudo crontab -l > mycron; echo \"*/5 * * * * sudo ufw disable\" >> mycron; sudo crontab mycron; rm mycron")
            add(w.elements, "Scheduled task that turns off firewall removed,V,8,Command,sudo crontab -l,FALSE,sudo ufw disable")
        elif i == 3:
            add(w.commands, "sudo crontab -l > mycron; echo \"*/2 * * * * nc -l -v 9999\" >> mycron; sudo crontab mycron; rm mycron")
            add(w.elements, "Scheduled task that launches netcat backdoor removed,V,8,Command,sudo crontab -l,FALSE,nc -l")
        elif i == 4:
            add(w.commands, "sudo crontab -l > mycron; echo \'*/3 * * * * notify-send \"Taunt\" \"" + text + "\"\' >> mycron; sudo crontab mycron; rm mycron")
            add(w.elements, "Scheduled task that launches taunt removed,V,8,Command,sudo crontab -l,FALSE,notify-send")
        elif i == 5:
            text = text.replace("\"", "")
            add(w.commands, "sudo crontab -l > mycron; echo '*/1 * * * * " + text + "' >> mycron; sudo crontab mycron; rm mycron")
            add(w.elements, "Bad scheduled task removed,V,8,Command,sudo crontab -l,FALSE," + text)
        elif i == 6:
            add(w.elements, "IP Spoofing is disabled,V,7,FileContents,/etc/host.conf,TRUE,nospoof on")
        elif i == 7:
            add(w.elements, "Usernames are hidden from the login screen,V,8,FileContents,/etc/lightdm/lightdm.conf,TRUE,greeter-hide-users=true")
