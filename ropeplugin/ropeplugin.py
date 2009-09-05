#-*- coding:utf-8 -*-

import gedit
import gtk
import rope.base.project
import gettext
import os.path

#gettext installation
LOCALES_DIR = os.path.join(os.path.dirname(__file__), '.locales')
gettext.install('ropeplugin', LOCALES_DIR, unicode=True)

#ui strings
file_ui = '''<ui>
    <menubar name="MenuBar">
        <menu name="FileMenu" action="File">
            <placeholder name="FileOps_2">
                <menu action="FileRope">
                    <menuitem action="SetProject" />
                    <menuitem action="ConfigProject" />
                </menu>
            </placeholder>
        </menu>
    </menubar>
</ui>'''


#helper functions
def get_uri_from_path(path):
    '''Converts path string to uri string.'''
    return 'file://' + path


class RopeProjectHelper(object):
    '''A helper class providing rope project management routines.'''
    def __init__(self, window):
        self.project = None
        self.window = window

    def get_or_create_tab_from_uri(self, uri):
        '''Returns the tab from uri. If it doesn't exists, opens it.
        If file doesn't exist, returns nothing.'''
        return self.window.get_tab_from_uri(uri) or \
               self.window.create_tab_from_uri(uri=uri,
                    encoding=gedit.encoding_get_current(),
                    line_pos=0, create=False, jump_to=False)

    def set_project(self, action):
        '''Sets up rope project root folder and creates a rope project.'''
        dlg = gtk.FileChooserDialog(
            title=_(u'Set Project Root Folder...'),
            action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        # if there is an active document, dialog will open its folder
        try:
            uri = self.window.get_active_document().get_uri()
            if uri: #maybe need to initiate save file dialog if uri == None ?
                dlg.set_uri(uri)
        except AttributeError:
            pass
        dlg.set_default_response(gtk.RESPONSE_OK)
        resp = dlg.run()
        if resp == gtk.RESPONSE_OK:
            path = dlg.get_filename()
            self.project = rope.base.project.Project(path)
        dlg.destroy()

    def config_project(self, action):
        '''Opens the current project's config file. If it doesn't exist,
        initiates a 'Set Project Root...' dialog. If config file is already
        open, just switches to its tab.'''
        if not self.project:
            self.set_project(action)
        if self.project: # making sure that project was properly set up
            uri = get_uri_from_path(os.path.join(self.project.root.real_path,
                                                 '.ropeproject', 'config.py'))
            config_tab = self.get_or_create_tab_from_uri(uri)
            self.window.set_active_tab(config_tab)
        else:
            pass # in case project wasn't set up and user canceled initiated
                 # dialog, do nothing.


class RopePlugin(gedit.Plugin):
    '''Main plugin class providing integration with Gedit UI'''
    def __init__(self):
        gedit.Plugin.__init__(self)

    def activate(self, window):
        self.window = window
        self.project_helper = RopeProjectHelper(self.window)
        self.insert_menu()

    def deactivate(self, window):
        self.remove_menu()
        self.window = None
        self.file_action_group = None
        self.project_helper = None

    def update_ui(self, window):
        pass

    def insert_menu(self):
        manager = self.window.get_ui_manager()
        self.file_action_group = gtk.ActionGroup('RopeFileActions')
        file_actions = [
            ('FileRope', None, 'Rope'),
            ('SetProject', None, _(u'Set Project Root Folder...'), None, None,
                self.project_helper.set_project),
            ('ConfigProject', None, _(u'Configure Project'), None, None,
                self.project_helper.config_project)]
        self.file_action_group.add_actions(file_actions)
        manager.insert_action_group(self.file_action_group, -1)
        self.file_ui_id = manager.add_ui_from_string(file_ui)

    def remove_menu(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.file_ui_id)
        manager.remove_action_group(self.file_action_group)
        manager.ensure_update()

