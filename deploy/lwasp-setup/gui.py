import os
import sys

try:
	import gi
except:
	os.system('sudo apt-get install python-gi -y')
	import gi

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

class MyWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="LWASP Setup")
		self.set_default_size(800, 600)

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

		self.set_icon_from_file(get_resource_path("icon.png"))

		for i in range(0, 8):
			page = Gtk.Box()
			label = ""

			if i == 0:
				page = UserBox()
				label = "Users"
			elif i == 1:
				page = AppsBox()
				label = "Services"
			elif i == 2:
				page = ForensicsBox()
				self.forensics_box = page
				label = "Forensics ?s"
			elif i == 3:
				page = UpdatesBox()
				label = "Updates"
			elif i == 4:
				page = PasswdBox()
				label = "Passwd Policy"
			elif i == 5:
				page = FirewallBox()
				label = "Firewall"
			elif i == 6:
				page = BackdoorBox()
				label = "Bad Files"
			elif i == 7:
				page = MiscBox()
				label = "Other"


			page.set_border_width(10)
			self.notebook.append_page(page, Gtk.Label(label))

		dialog = IntroDialog(self)
		dialog.run()
		dialog.destroy()

	def done_button_pressed(self, button):
		self.forensics_box.finalize()
		with open('elements.csv', 'w') as elements:
			for item in w.elements:
				elements.write(item + '\n')
		with open('commands.bash', 'w') as commands:
			for item in w.commands:
				commands.write(item + '\n')
		os.system('sudo mv elements.csv ../lwasp-install/')
		os.system('sudo chmod +x commands.bash')

		Gtk.main_quit()

win = MyWindow()
win.connect('delete-event', Gtk.main_quit)
win.show_all()
Gtk.main()

win.destroy()
win = None

to_run = ""

class interWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="LWASP Setup")
		self.set_default_size(200, 200)

		master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
		master_box.set_border_width(10)

		self.set_icon_from_file(get_resource_path("icon.png"))

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
		to_run = "cd ..; /bin/bash install"
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
