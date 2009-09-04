#-*- coding:utf-8 -*-

import gedit
import gtk
import rope.base.project
from gettext import gettext as _
import os.path

#helper functions
def get_uri_from_path(path):
    return 'file://' + path


class RopeProjectHelper(object):

    def __init__(self, window):
        self.project = None
        self.window = window

    def get_or_create_tab_from_uri(self, uri):
        return self.window.get_tab_from_uri(uri) or \
               self.window.create_tab_from_uri(uri=uri,
                    encoding=gedit.encoding_get_current(),
                    line_pos=0, create=False, jump_to=False)

    def set_project(self, action):
        dlg = gtk.FileChooserDialog(
            title=_('Set Project Root Folder...'),
            action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dlg.set_uri(self.window.get_active_document().get_uri())
        dlg.set_default_response(gtk.RESPONSE_OK)
        resp = dlg.run()
        if resp == gtk.RESPONSE_OK:
            path = dlg.get_filename()
            self.project = rope.base.project.Project(path)
        dlg.destroy()

    def config_project(self, action):
        if not self.project:
            self.set_project(action)
        uri = get_uri_from_path(os.path.join(self.project.root.real_path,
                                               '.ropeproject', 'config.py'))
        config_tab = self.get_or_create_tab_from_uri(uri)
        self.window.set_active_tab(config_tab)


class RopePlugin(gedit.Plugin):

    def __init__(self):
        gedit.Plugin.__init__(self)

    def activate(self, window):
        self.window = window
        self.project_helper = RopeProjectHelper(self.window)
        self.insert_menu()

    def deactivate(self, window):
        self.remove_menu()
        self.window = None
        self.action_group = None
        self.project_helper = None

    def update_ui(self, window):
        self.action_group.set_sensitive(
            self.window.get_active_document() != None)

    def insert_menu(self):
        manager = self.window.get_ui_manager()
        self.action_group = gtk.ActionGroup('RopeActions')
        actions = [
            ('FileRope', None, _('Rope')),
            ('SetProject', None, _('Set Project Root Folder...'), None, None,
                self.project_helper.set_project),
            ('ConfigProject', None, _('Configure Project'), None, None,
                self.project_helper.config_project),
            ('EditRope', None, _('Rope')),
            ('Rename', None, _('Rename'))]
        self.action_group.add_actions(actions)
        manager.insert_action_group(self.action_group, -1)
        ui_file = os.path.join(os.path.dirname(__file__), 'ui')
        self.ui_id = manager.add_ui_from_file(ui_file)

    def remove_menu(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.ui_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()

