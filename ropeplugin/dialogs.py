import gtk
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
    dlg.set_response_sensitive(gtk.RESPONSE_OK, 
                               is_valid_python_identifier(entry.get_text()))
    dlg.set_default_response(gtk.RESPONSE_OK)
    
def get_python_identifier():
    txt = None
    dlg = gtk.Dialog(title='Extract variable', 
                     buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                              gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    entry = gtk.Entry()
    entry.connect('changed', on_changed, dlg)
    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label('Name:'), False, 5, 5)
    hbox.pack_end(entry)
    dlg.vbox.pack_end(hbox, True, True, 0)
    dlg.set_size_request(300, 100)
    dlg.show_all()
    dlg.set_default_response(gtk.RESPONSE_OK)
    dlg.set_response_sensitive(gtk.RESPONSE_OK, False)
    resp = dlg.run()
    if resp == gtk.RESPONSE_OK:
        txt = entry.get_text()
    dlg.destroy()
    return txt

