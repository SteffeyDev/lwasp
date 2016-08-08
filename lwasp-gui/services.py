import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_utility import *
import w
from collections import namedtuple
import subprocess

Item = namedtuple("Items", "name expanded options_box box")

services = {'telnet':'telnetd', 'wireshark': 'wireshark', 'wordpress': 'wordpress', 'apparmor': 'apparmor', 'apache2': 'apache2', 'atom': 'atom', 'couchbase-server': 'sync_gateway', 'dovecot-core': 'dovecot', 'vsftpd': 'vsftpd', 'fail2ban': 'fail2ban', 'openssh-server':'sshd', 'php5': 'php5-fpm', 'postfix': 'postfix', 'mysql-server': 'mysqld', 'postgresql': 'postgres', 'nginx': 'nginx', 'thunderbird': 'thunderbird', 'ruby': 'ruby', 'firefox': 'firefox', 'cups': 'cupsd', 'remmina': 'remmina', 'python': 'python', 'nmap': 'nmap', 'wireshark': 'wireshark', 'vsftpd': 'vsftpd', 'netcat-openbsd': 'nc', 'nodejs': 'node', 'oodo': 'oodo', 'openssh-server': 'sshd', 'perl': 'perl', 'xrdp': 'xrdp', 'ufw': 'ufw'}

class AppsBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.items = []

        self.master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        valid_services = []
        for service in services:
            valid_services.append(service)

        # time consuming
        self.updates = subprocess.Popen(["/usr/lib/update-notifier/apt-check", "-p"], stdout=subprocess.PIPE).communicate()[0]

        apps = subprocess.Popen(["dpkg", "-l"], stdout=subprocess.PIPE).communicate()[0]
        apps_list = apps.split('\n')
        for app in apps_list:
            if len(app.split(" ")) > 2:
                app_name = app.split(" ")[2]
                if app_name in valid_services:
                    self.add_row(app_name)

        self.add_box = Gtk.Box()
        self.name_entry = Gtk.Entry(placeholder_text="Package Name")
        self.add_box.pack_start(self.name_entry, False, False, 0)
        add_app = Gtk.Button(label="Install")
        add_app.props.halign = Gtk.Align.END
        add_app.connect("clicked", self.add_app)
        self.add_box.pack_end(add_app, False, False, 0)
        self.master_box.pack_end(self.add_box, False, False, 0)

        self.add(self.master_box)

    def add_row(self, app, removeable = False):
        user_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        user_wrapper_box = Gtk.Box(spacing=50)
        label = Gtk.Label(app)
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
        if app == "": return
        check = subprocess.Popen(["apt-cache", "search", "--names-only", "^" + app + "$"], stdout=subprocess.PIPE).communicate()[0]
        if check == "": return
        self.add_row(app, True)
        self.refresh_after_add()
        add(w.commands, "sudo apt-get install " + app + " -y")

    def refresh_after_add(self):
        self.master_box.show_all()
        self.name_entry.set_text("")
        self.master_box.reorder_child(self.add_box, len(self.items) * 2)

    def check_button_clicked(self, button):
        item = self.items[button.index]
        filename = ""

        if button.type == 1 or button.type == 3:
            if isFile('/etc/init.d/' + item.name):
                filename = "/etc/init.d/" + item.name
            elif isFile('/usr/bin/' + services[item.name]):
                filename = '/usr/bin/' + services[item.name]
            elif isFile('/usr/sbin/' + services[item.name]):
                filename = '/usr/sbin/' + services[item.name]
            elif isFile('/bin/' + services[item.name]):
                filename = '/bin/' + services[item.name]
            elif isFile('/sbin/' + services[item.name]):
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
                    version = line.split(" ")[2]

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
