import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from user_management import UserBox

import w
w.init()

class MyWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="LWASP Setup")
		self.set_default_size(800, 600)
		self.notebook = Gtk.Notebook()
		self.add(self.notebook)


		for i in range(0, 8):
			page = Gtk.Box()
			label = ""

			if i == 0:
				page = UserBox()
				label = "Users"
			elif i == 1:
				label = "Services"
			elif i == 2:
				label = "Forensics ?s"
			elif i == 3:
				label = "Updates"
			elif i == 4:
				label = "Passwd Policy"
			elif i == 5:
				label = "Firewall"
			elif i == 6:
				label = "Sudo Conf."
			elif i == 7:
				label = "Misc"


			page.set_border_width(10)
			self.notebook.append_page(page, Gtk.Label(label))

win = MyWindow()
win.connect('delete-event', Gtk.main_quit)
win.show_all()
Gtk.main()
