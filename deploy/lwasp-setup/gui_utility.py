import gi, os
from os.path import isfile
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def add(array, line):
    if line in array:
        array.remove(line)
    else:
        array.append(line)

def show_error(top, title, message, type=Gtk.MessageType.ERROR):
    dialog = Gtk.MessageDialog(top, 0, type, Gtk.ButtonsType.OK, title)
    dialog.format_secondary_text(message)
    dialog.set_modal(True)
    dialog.run()
    dialog.destroy()

def get_resource_path(rel_path):
    dir_of_py_file = os.path.dirname(__file__)
    rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
    abs_path_to_resource = os.path.abspath(rel_path_to_resource)
    return abs_path_to_resource
