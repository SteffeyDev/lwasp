import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os


from user_management import UserBox
from services import AppsBox
from forensics import ForensicsBox
from updates import UpdatesBox
from passwd import PasswdBox
from firewall import FirewallBox
from backdoor import BackdoorBox
from misc import MiscBox

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

		self.set_icon_from_file(self.get_resource_path("icon.png"))

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

	def get_resource_path(self, rel_path):
	    dir_of_py_file = os.path.dirname(__file__)
	    rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
	    abs_path_to_resource = os.path.abspath(rel_path_to_resource)
	    return abs_path_to_resource

	def done_button_pressed(self, button):
		hh = ""
		#need to create forensics questions on desktop

win = MyWindow()
win.connect('delete-event', Gtk.main_quit)
win.show_all()
Gtk.main()
