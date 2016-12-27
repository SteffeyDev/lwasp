# Copyright (C) 2015 Peter Steffey

import os
import sys
import apt

cache = apt.cache.Cache()
cache.update()

try:
	import gi
except:
	cache['python-gi'].mark_install()
	cache.commit()

	import gi

cache['update-notifier'].mark_install()
cache.commit()

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from user_management import UserBox
from services import AppsBox
from forensics import ForensicsBox
from updates import UpdatesBox
from passwd import PasswdBox
from firewall import FirewallBox
from backdoor import BackdoorBox
from misc import MiscBox
from intro import IntroDialog
from gui_utility import *

import w
w.init()

continue_on = False
sudo_user = os.environ['SUDO_USER']

if sudo_user == "root":
	print " * This application cannot be run as root, please run as the main user account on the VM."
	sys.exit()

class MyWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="LWASP Setup")
		self.set_default_size(800, 600)
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

		self.misc_box = None

		master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

		self.notebook = Gtk.Notebook()
		master_box.pack_start(self.notebook, True, True, 0)
		master_box.add(Gtk.HSeparator())

		bottom_box = Gtk.Box()
		done_button = Gtk.Button(label="Finalize & Generate Scoring Files")
		done_button.props.halign = Gtk.Align.END
		done_button.connect("clicked", self.done_button_pressed)
		bottom_box.pack_end(done_button, False, False, 0)
		master_box.add(bottom_box)

		self.add(master_box)
		path = str(os.path.join(os.path.dirname(os.path.abspath(__file__))))
		self.set_icon_from_file(path[:-5] + 'install/icon.png')

		for i in range(0, 8):
			page = Gtk.Box()
			label = ""

			if i == 0:
				page = UserBox(self.update_users)
				label = "Users"
			elif i == 1:
				page = AppsBox()
				label = "Services"
			elif i == 2:
				page = ForensicsBox()
				self.forensics_box = page
				label = "Forensics"
			elif i == 3:
				page = UpdatesBox()
				label = "Updates"
			elif i == 4:
				page = PasswdBox()
				label = "Password Policy"
			elif i == 5:
				page = FirewallBox()
				label = "Firewall"
			elif i == 6:
				page = BackdoorBox()
				label = "Bad Files"
			elif i == 7:
				page = MiscBox()
				self.misc_box = page
				label = "Other"


			page.set_border_width(10)
			self.notebook.append_page(page, Gtk.Label(label))

		dialog = IntroDialog(self)
		dialog.run()
		dialog.destroy()

	def update_users(self):
		if self.misc_box is not None:
			self.misc_box.update_users()

	def done_button_pressed(self, button):
		self.forensics_box.finalize()
		with open('elements.csv', 'w') as elements:
			with open('/home/' + sudo_user + '/Desktop/LWASP-Elements-Export.csv', 'w') as export:
				export.write("Scoring Item,Points,Type\n")
				for item in w.elements:
					elements.write(item + '\n')
					export.write(item.split(",")[0] + "," + item.split(",")[2] + "," + ("*" if item.split(",")[1] == "Penalty" else "Vulnerability") + "\n")
				export.close()
			elements.close()
		with open('commands.bash', 'w') as commands:
			for item in w.commands:
				commands.write(item + '\n')
			commands.close()
		path = str(os.path.join(os.path.dirname(os.path.abspath(__file__))))
		os.system('sudo mv elements.csv ' + path[:-5] + 'install/')
		os.system('sudo mv commands.bash ' + path[:-5] + 'install/')
		os.system('sudo chmod +x ' + path[:-5] + 'install/commands.bash')

		show_error(self, "Elements Export", "A copy of what scores has been created on the Desktop for your reference.  If you do not remove this, it will be deleted automatically at next reboot.", Gtk.MessageType.INFO)

		global continue_on
		continue_on = True

		Gtk.main_quit()
		self.destroy()

win = MyWindow()
win.connect('delete-event', Gtk.main_quit)
win.show_all()
Gtk.main()

win.destroy()
win = None

if continue_on:

	to_run = ""

	class interWindow(Gtk.Window):
		def __init__(self):
			Gtk.Window.__init__(self, title="LWASP Setup")
			self.set_default_size(200, 200)
			self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

			master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
			master_box.set_border_width(10)

			path = str(os.path.join(os.path.dirname(os.path.abspath(__file__))))
			self.set_icon_from_file(path[:-5] + 'install/icon.png')

			label = Gtk.Label("Do you want to continue on to the installation (simple) or stop so you can modify the scoring items in the elements.csv file (advanced)?")
			label.set_line_wrap(True)
			button1 = Gtk.Button(label="Continue to Installation")
			button1.connect("clicked", self.launch_install)
			button2 = Gtk.Button(label="End & Modify")
			button2.connect("clicked", self.end)
			master_box.pack_start(label, False, False, 0)
			master_box.pack_start(button1, False, False, 0)
			master_box.pack_start(button2, False, False, 0)

			self.add(master_box)

		def launch_install(self, button):
			global to_run
			path = str(os.path.join(os.path.dirname(os.path.abspath(__file__))))
			to_run = "/bin/bash " + path[:-11] + 'install ' + sudo_user
			Gtk.main_quit()
			self.destroy()

		def end(self, button):
			show_error(self, "Modification", "Feel free to modify this image and the elements.csv file in the lwasp-install folder to change names, point values, and score advanced items.  Run ./install to continue with the installation", Gtk.MessageType.INFO)
			Gtk.main_quit()
			self.destroy()

	win2 = interWindow()
	win2.connect('delete-event', Gtk.main_quit)
	win2.show_all()
	Gtk.main()

	win2.destroy()
	win2 = None

	os.system(to_run)
