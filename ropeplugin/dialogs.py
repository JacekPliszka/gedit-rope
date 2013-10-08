from gi.repository import Gtk
import re

PYTHON_RESERVED = ('and', 'del', 'for', 'is', 'raise', 'assert',
                   'elif', 'from', 'lambda', 'return', 'break',
                   'else', 'global', 'not', 'try', 'class', 'except',
                   'if', 'or', 'while', 'continue', 'exec', 'import',
                   'pass', 'yield', 'def', 'finally', 'in', 'print')

VALID_PYTHON_IDENTIFIER = re.compile(r'^[_A-Za-z][_A-Za-z0-9]*$')

def is_valid_python_identifier(string):
    return string not in PYTHON_RESERVED and \
        VALID_PYTHON_IDENTIFIER.match(string) != None

def on_changed(entry, dlg):
    txt = entry.get_text()
    dlg.set_response_sensitive(Gtk.ResponseType.OK,
                               is_valid_python_identifier(entry.get_text()))
    dlg.set_default_response(Gtk.ResponseType.OK)

def get_python_identifier():
    txt = None
    dlg = Gtk.Dialog(title='Extract variable',
                     buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                              Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
    entry = Gtk.Entry()
    entry.connect('changed', on_changed, dlg)
    hbox = Gtk.HBox()
    hbox.pack_start(Gtk.Label('Name:', True, True, 0), False, 5, 5)
    hbox.pack_end(entry, True, True, 0)
    dlg.vbox.pack_end(hbox, True, True, 0)
    dlg.set_size_request(300, 100)
    dlg.show_all()
    dlg.set_default_response(Gtk.ResponseType.OK)
    dlg.set_response_sensitive(Gtk.ResponseType.OK, False)
    resp = dlg.run()
    if resp == Gtk.ResponseType.OK:
        txt = entry.get_text()
    dlg.destroy()
    return txt

