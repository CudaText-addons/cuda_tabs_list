from cudatext import *
import cudatext_cmd
import re

class Command:
    title = 'Tabs'
    h_tree = None
    busy_update = False
    
    def open(self):
        if app_api_version()<'1.0.127':
            msg_box('Tabs List needs newer app', MB_OK or MB_ICONERROR)
            return
    
        ed.cmd(cudatext_cmd.cmd_ShowSidePanelAsIs)
        app_proc(PROC_SIDEPANEL_ADD, self.title+",-1,tree")
        app_proc(PROC_SIDEPANEL_ACTIVATE, self.title)
        
        app_proc(PROC_MENU_CLEAR, 'side:'+self.title)
        app_proc(PROC_MENU_ADD, 'side:'+self.title+';cuda_tabs_list,menu_close_sel;Close;-1')
        app_proc(PROC_MENU_ADD, 'side:'+self.title+';cuda_tabs_list,menu_close_others;Close others;-1')
        app_proc(PROC_MENU_ADD, 'side:'+self.title+';0;-;-1')
        app_proc(PROC_MENU_ADD, 'side:'+self.title+';cuda_tabs_list,menu_copy_file_name;Copy filename only;-1')
        app_proc(PROC_MENU_ADD, 'side:'+self.title+';cuda_tabs_list,menu_copy_file_path;Copy full filepath;-1')
        
        self.h_tree = app_proc(PROC_SIDEPANEL_GET_CONTROL, self.title)
        tree_proc(self.h_tree, TREE_PROP_SHOW_ROOT, 0, 0, '0')
        self.update()
        
    def on_focus(self, ed_self):
        self.update()

    def on_open(self, ed_self):
        self.update()

    def on_tab_move(self, ed_self):
        self.update()

    def clear_tree(self):
        tree_proc(self.h_tree, TREE_ITEM_DELETE, 0)

    def update(self):
        if self.h_tree is None: return
        self.busy_update = True
        self.clear_tree()
        
        ed.set_prop(PROP_TAG, 'tag')
        handles = ed_handles()
        for h in handles:
            edit = Editor(h)
            prefix = '[%d] '%(h-handles[0]+1)
            name = prefix + edit.get_prop(PROP_TAB_TITLE)
            h_item = tree_proc(self.h_tree, TREE_ITEM_ADD, 0, -1, name, -1)
            if edit.get_prop(PROP_TAG)=='tag':
                tree_proc(self.h_tree, TREE_ITEM_SELECT, h_item) 
        ed.set_prop(PROP_TAG, '')

        self.busy_update = False
        
    def on_panel(self, ed_self, id_control, id_event):
        if self.h_tree is None: return
        if self.h_tree!=id_control: return
        if self.busy_update: return
        
        if id_event=='on_sel':
            e = self.ed_of_sel()
            e.focus()

    def ed_of_sel(self):
        h_item = tree_proc(self.h_tree, TREE_ITEM_GET_SELECTED)
        prop = tree_proc(self.h_tree, TREE_ITEM_GET_PROP, h_item)
        if prop is None: return
        s = prop[0]
        s = re.findall('\d+', s)[0]
        index = int(s)-1
        h = ed_handles()[index]
        e = Editor(h)
        return e

    def menu_close_sel(self):
        e = self.ed_of_sel()
        e.cmd(cudatext_cmd.cmd_FileClose)
        
    def menu_close_others(self):
        e = self.ed_of_sel()
        e.cmd(cudatext_cmd.cmd_FileCloseOtherAll)

    def menu_copy_file_path(self):
        e = self.ed_of_sel()
        e.cmd(cudatext_cmd.cmd_CopyFilenameFull)

    def menu_copy_file_name(self):
        e = self.ed_of_sel()
        e.cmd(cudatext_cmd.cmd_CopyFilenameName)
