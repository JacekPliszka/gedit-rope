#-*- coding:utf-8 -*-
import gedit
import gtk
import rope.base.project
from rope.base import libutils
from rope.refactor.extract import ExtractVariable
import gettext
import os.path
import config
import dialogs

#gettext installation
LOCALES_DIR = os.path.join(os.path.dirname(__file__), '.locales')
gettext.install('ropeplugin', LOCALES_DIR, unicode=True)

#ui strings
rope_ui ='''   <menubar name="MenuBar">
        <menu name="RopeMenu" action="Rope">
            <placeholder name="RopeOps_1">
                <menu name="RopeProjectMenu" action="RopeProject">
                    <menuitem action="RopeSetProject" />
                    <menuitem action="RopeConfigProject" />
                </menu>
                <menu name="RopeRefactorMenu" action="RopeRefactor">
                    <menuitem action="RopeExtractVariable" />
                </menu>
                <separator />
                <menuitem action="RopeConfigPlugin" />
            </placeholder>
        </menu>
    </menubar>''' # may distribute them across several menus (File, Edit, etc.)
                  # later but for now I prefer them to be in one place

#helper functions
def get_uri_from_path(path):
    'Converts absolute path string to uri string.'
    return 'file://' + path

def get_or_create_tab_from_uri(window, uri):
    '''Returns the tab from uri. If it doesn't exists, opens it.
    If the file doesn't exist, returns nothing.'''
    return window.get_tab_from_uri(uri) or \
           window.create_tab_from_uri(uri=uri,
                encoding=gedit.encoding_get_current(),
                line_pos=0, create=False, jump_to=False)

def reload_doc(doc):
    'Reloads document from disk'
    doc.load(uri=doc.get_uri(),
             encoding=doc.get_encoding(),
             line_pos=0, create=False) # it works, but spits out all sorts of
                                       # failed assertions. there must be a
                                       # better way

def get_selected_text(buffer):
    start, end = buffer.get_selection_bounds()
    return buffer.get_text(start, end)


class RopeProjectHelper(object):
    'A helper class providing rope project management routines.'
    def __init__(self, window):
        self.project = None
        self.window = window

    def set_project(self, action):
        'Sets up rope project root folder and creates a rope project.'
        dlg = gtk.FileChooserDialog(
            title=_(u'Set Project Root Folder...'),
            action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))        
        try: # if there is an active document, dialog will open its folder
            uri = self.window.get_active_document().get_uri()
            if uri: # maybe need to initiate save file dialog if uri == None ?
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
            config_tab = get_or_create_tab_from_uri(self.window, uri)
            self.window.set_active_tab(config_tab)


class RefactorHelper(object):
    'Helper class providing refactoring routines'
    def __init__(self, window, project_helper):
        self.window = window
        self.project_helper = project_helper
        
    @property
    def project(self):
        return self.project_helper.project   
        
    def validate_project(self):
        try:
            self.project.validate()
        except:
            self.project_helper.set_project(action=None)
            self.project.validate()    
    
    def rename(self, action):
        'Renames a variable'
        self.validate_project()
    
    def reload_modified_documents(self, changes):
        'Reloads all opened docs marked as modified in changes'

    def extract_variable(self, action):
        'Extracts a variable from expression selected in a document'
        self.validate_project()
        doc = self.window.get_active_document()
        start, end = doc.get_selection_bounds()
        resource = libutils.path_to_resource(self.project,
                                             doc.get_uri_for_display())   
        extractor = ExtractVariable(self.project, resource,
                                    start.get_offset(), end.get_offset())
        txt = dialogs.get_python_identifier()
        if txt:
            changes = extractor.get_changes(txt)
            self.apply_changes(changes)
    
    def apply_changes(self, changes):
        print changes.get_description() # TODO: actual preview/apply dialog
        self.project.do(changes)
        # maybe reloading everything isn't such a good idea...
        for doc in self.window.get_documents():
            reload_doc(doc)
        

class RopePlugin(gedit.Plugin):
    'Main plugin class providing integration with Gedit UI'
    def __init__(self):
        gedit.Plugin.__init__(self)

    def activate(self, window):
        self.window = window
        self.project_helper = RopeProjectHelper(self.window)
        self.refactor_helper = RefactorHelper(self.window,
                                              self.project_helper)
        self.insert_menu()

    def deactivate(self, window):
        self.remove_menu()
        self.window = None
        self.rope_action_group = None
        self.project_helper = None

    def update_ui(self, window):
        manager = window.get_ui_manager()
        manager.ensure_update()
        
        
    def config_plugin(self, action):
        config_path = os.path.join(os.path.dirname(__file__), 'config.py')
        config_uri = get_uri_from_path(config_path)
        config_tab = get_or_create_tab_from_uri(self.window, config_uri)
        self.window.set_active_tab(config_tab)
        
    def insert_menu(self):
        uimanager = self.window.get_ui_manager()
        self.rope_action_group = gtk.ActionGroup('RopeActions')
        rope_actions = [('Rope', None, 'Rope'),
            ('RopeProject', None, _(u'Project')),          
            ('RopeSetProject', None, _(u'Set Project Root Folder...'),
                config.SET_PROJECT_SHORTCUT, None,
                self.project_helper.set_project),
            ('RopeConfigProject', None, _(u'Configure Project'), 
                config.CONFIG_PROJECT_SHORTCUT, None,
                self.project_helper.config_project),    
            
            ('RopeRefactor', None, _(u'Refactoring')),
            ('RopeExtractVariable', None, _(u'ExtractVariable'),
                config.EXTRACT_VARIABLE_SHORTCUT, None,
                self.refactor_helper.extract_variable),
            
            ('RopeConfigPlugin', None, _(u'Configure Plugin'),
                config.CONFIG_PLUGIN_SHORTCUT, None,
                self.config_plugin)]

        self.rope_action_group.add_actions(rope_actions)
        uimanager.insert_action_group(self.rope_action_group, -1)
        self.rope_ui_id = uimanager.add_ui_from_string(rope_ui)

    def remove_menu(self):
        uimanager = self.window.get_ui_manager()
        uimanager.remove_ui(self.rope_ui_id)
        uimanager.remove_action_group(self.rope_action_group)
        uimanager.ensure_update()

