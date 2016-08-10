import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w
from collections import namedtuple
import subprocess
from os.path import isfile

Item = namedtuple("Items", "name expanded options_box box")

services = {'telnet':'telnetd', 'wireshark': 'wireshark', 'wordpress': 'wordpress', 'apparmor': 'apparmor', 'apache2': 'apache2', 'atom': 'atom', 'couchbase-server': 'sync_gateway', 'dovecot-core': 'dovecot', 'vsftpd': 'vsftpd', 'fail2ban': 'fail2ban', 'openssh-server':'sshd', 'php5': 'php5-fpm', 'postfix': 'postfix', 'mysql-server': 'mysqld', 'postgresql': 'postgres', 'nginx': 'nginx', 'thunderbird': 'thunderbird', 'ruby': 'ruby', 'firefox': 'firefox', 'cups': 'cupsd', 'remmina': 'remmina', 'python': 'python', 'nmap': 'nmap', 'wireshark': 'wireshark', 'vsftpd': 'vsftpd', 'netcat-openbsd': 'nc', 'nodejs': 'node', 'oodo': 'oodo', 'openssh-server': 'sshd', 'perl': 'perl', 'xrdp': 'xrdp', 'ufw': 'ufw', 'chkrootkit': 'chkrootkit', 'logwatch': 'logwatch', 'bum': 'bum', 'denyhosts': 'denyhosts', 'psad': 'psad', 'rkhunter': 'rkhunter', 'snort': 'snort', 'openssl': 'openssl'}

class AppsBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.items = []

        self.master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

        self.valid_services = []
        for service in services:
            self.valid_services.append(service)

        # time consuming
        updates_string = subprocess.Popen(["/usr/lib/update-notifier/apt-check", "-p"], stderr=subprocess.PIPE).communicate()[1]
        self.updates = updates_string.rstrip()

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

        apps = subprocess.Popen(["dpkg", "-l"], stdout=subprocess.PIPE).communicate()[0]
        apps_list = apps.split('\n')
        for app in apps_list:
            if len(app.split(" ")) > 2:
                app_name = app.split(" ")[2]
                if app_name in self.valid_services:
                    self.add_row(app_name)

        self.add_box = Gtk.Box()
        self.name_entry = Gtk.Entry(placeholder_text="Package Name")
        self.add_box.pack_start(Gtk.Label("Install Software: "), False, False, 0)
        self.add_box.pack_start(self.name_entry, False, False, 0)
        add_app = Gtk.Button(label="Install")
        add_app.props.halign = Gtk.Align.END
        add_app.connect("clicked", self.add_app)
        self.add_box.pack_end(add_app, False, False, 0)
        self.master_box.pack_end(self.add_box, False, False, 0)



        self.add(self.master_box)

    def add_row(self, app, removeable = False):
        user_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        user_wrapper_box = Gtk.Box(spacing=5)

        label = Gtk.Label(app)
        user_wrapper_box.pack_start(label, False, True, 0)
        button = Gtk.Button(label="Expand")
        button.props.halign = Gtk.Align.END
        button.index = len(self.items)
        button.connect("clicked", self.expand_button_clicked)
        user_wrapper_box.pack_end(button, False, True, 0)
        if app in self.updates:
            note_label = Gtk.Label()
            note_label.set_markup('<span foreground="grey"><small>Updates Available</small></span>')
            note_label.set_line_wrap(True)
            note_label.props.halign = Gtk.Align.END
            user_wrapper_box.pack_end(note_label, False, False, 0)
        user_box.pack_start(user_wrapper_box, False, False, 0)
        self.master_box.pack_start(user_box, False, True, 0)

        separator = Gtk.HSeparator()
        self.master_box.pack_start(separator, False, True, 0)

        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        for i in range(0,5):

            label = ""
            if i == 0:
                label = "Score for Stopping"
            elif i == 1:
                label = "Score for Uninstalling"
            elif i == 2:
                label = "Penalize for Stopping (Critical Service)"
            elif i == 3:
                label = "Penalize for Uninstalling (Critical Service)"
            elif i == 4:
                print app
                if app not in self.updates: break
                label = "Score for Updating"

            check_button = Gtk.CheckButton(label)
            check_button.connect("clicked", self.check_button_clicked)
            check_button.type = i
            check_button.index = len(self.items)
            options_box.pack_start(check_button, True, True, 0)

        if removeable:
            delete_button = Gtk.Button("Uninstall App")
            delete_button.index = len(self.items)
            delete_button.connect("clicked", self.delete_app)
            options_box.pack_end(delete_button, False, False, 0)

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

    def add_app(self, button):
        app = self.name_entry.get_text()
        for item in self.items:
            if app == item.name:
                show_error(self.get_toplevel(), "App Exists", "This service is already installed on your system.")
                return
        if app == "":
            show_error(self.get_toplevel(), "Insufficient Information", "You must provide the name of the service to install")
            return
        check = subprocess.Popen(["apt-cache", "search", "--names-only", "^" + app + "$"], stdout=subprocess.PIPE).communicate()[0]
        if check == "":
            show_error(self.get_toplevel(), "App Does Not Exist", "The service you want to add is not available in the apt-get repositories on this system.")
            return
        self.add_row(app, True)
        self.refresh_after_add()
        add(w.commands, "sudo apt-get install " + app + " -y")

    def refresh_after_add(self):
        self.master_box.show_all()
        self.name_entry.set_text("")
        self.master_box.reorder_child(self.add_box, (len(self.items) * 2) + 5)

    def check_button_clicked(self, button):
        item = self.items[button.index]
        filename = ""

        if button.type == 1 or button.type == 3:
            if isfile('/etc/init.d/' + item.name):
                filename = "/etc/init.d/" + item.name
            elif isfile('/usr/bin/' + services[item.name]):
                filename = '/usr/bin/' + services[item.name]
            elif isfile('/usr/sbin/' + services[item.name]):
                filename = '/usr/sbin/' + services[item.name]
            elif isfile('/bin/' + services[item.name]):
                filename = '/bin/' + services[item.name]
            elif isfile('/sbin/' + services[item.name]):
                filename = '/sbin/' + services[item.name]

        if button.type == 0:
            add(w.elements, 'Service ' + item.name + ' stopped,V,8,Service,' + services[item.name] + ',FALSE')
        elif button.type == 1:
            add(w.elements, 'Service ' + item.name + ' is no longer installed,V,10,FileExistance,' + filename + ',FALSE')
        elif button.type == 2:
            add(w.elements, 'Service ' + item.name + ' stopped,P,8,Service,' + services[item.name] + ',FALSE')
        elif button.type == 3:
            add(w.elements, 'Service ' + item.name + ' is no longer installed,P,10,FileExistance,' + filename + ',FALSE')
        elif button.type == 4:

            dpkg_update = subprocess.Popen(["apt-cache", "policy", item.name], stdout=subprocess.PIPE).communicate()[0]
            dpkg_update_list = dpkg_update.split('\n')
            version = ""
            for line in dpkg_update_list:
                if "Candidate:" in line:
                    version = line.split(" ")[3]

            print version
            add(w.elements, 'Service ' + item.name + ' is updated,V,7,Updates,' + item.name + ',' + version)

        print w.elements

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

        add(w.elements, title + " installed and running,V,6,Command,dpkg -l,TRUE," + title)
