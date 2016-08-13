# Copyright (C) 2015 Peter Steffey

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import os

import w

class IntroDialog(Gtk.Dialog):
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "Welcome to LWASP", parent, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK))

		self.set_default_size(300, 50)
		self.set_modal(True)

		box = self.get_content_area()
		box.set_spacing(20)
		box.set_border_width(20)

		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale('icon.png', width=200, height=200,
                                                 preserve_aspect_ratio=False)
		image = Gtk.Image()
		image.set_from_pixbuf(pixbuf)
		box.pack_start(image, False, False, 0)

		label = Gtk.Label("This Linux Watchful Adaptive Security Profiler is designed to create vulnerabilities on a Linux image and then score cyber security students on how well they fix those vulnerabilites.  LWASP is designed to work on an unconfigured image, but advanced users can pre-configure their images and allow scoring for more difficult vulnerabilites.")
		label.set_line_wrap(True)
		box.pack_start(label, False, False, 0)

		self.show_all()
