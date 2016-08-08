import gi
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def add(array, line):
    if line in array:
        array.remove(line)
    else:
        array.append(line)

def show_error(top, title, message):
    dialog = Gtk.MessageDialog(top, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, title)
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()
