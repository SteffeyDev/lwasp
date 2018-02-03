# Copyright (C) 2015 Peter Steffey

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import os

import w

class IntroductionBox(Gtk.ScrolledWindow):
		def __init__(self):
				Gtk.ScrolledWindow.__init__(self)
		
				box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
				
				path = str(os.path.join(os.path.dirname(os.path.abspath(__file__))))
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path[:-5] + 'install/icon.png', width=200, height=200,
																										 preserve_aspect_ratio=False)
				image = Gtk.Image()
				image.set_from_pixbuf(pixbuf)
				box.pack_start(image, False, False, 0)
				
				label = Gtk.Label("The Linux Watchful Adaptive Security Profiler is designed to create vulnerabilities on a Linux image and then score cyber security students on finding and fixing those vulnerabilites.  LWASP is designed to work on an unconfigured image, but advanced users can pre-configure their images and allow scoring for more difficult vulnerabilites.")
				label.set_line_wrap(True)
				box.pack_start(label, False, False, 10)

				label2 = Gtk.Label("Explore the tabs at the top to set up scoring on this image, and then press the button at the bottom right when you are done.")
				label2.set_line_wrap(True)
				box.pack_start(label2, False, False, 10)


				self.add_with_viewport(box)
