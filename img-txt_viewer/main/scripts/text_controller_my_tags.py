#region Imports


# Standard Library
import os


# Standard Library - GUI
from tkinter import (
    ttk, Tk, messagebox, TclError,
    BooleanVar,
    Frame, Menu,
    Listbox
)
from tkinter import colorchooser
import tkinter.font as tkfont


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as Tip
import yaml


# Custom Libraries
import main.scripts.custom_simpledialog as custom_dialog
from main.scripts import HelpText
from main.scripts.help_window import HelpWindow
import main.scripts.entry_helper as EntryHelper


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region MyTags


class MyTags:
    def __init__(self, app: 'Main', root: 'Tk'):
        self.app = app
        self.root = root

        # UI state
        self.show_all_tags_var = BooleanVar(value=True)
        self.hide_mytags_controls_var = BooleanVar(value=True)
        self.hide_alltags_controls_var = BooleanVar(value=False)

        # UI widgets (set during create_tab8)
        self.custom_dictionary_treeview = None
        self.alltags_listbox = None
        self.list_btn_frame = None
        self.alltags_btn_frame = None
        self.alltags_frame = None
        self.text_frame = None
        self.tag_entry = None

        # DnD state
        self._drag_state = {
            'active': False,
            'selected_iids': tuple(),
            'start_iid': None,
            'placeholder_iid': None,
            'prev_cursor': None,
        }
        self._placeholder_bg = '#dbeafe'

        # Font style state for MyTags (applied to Treeview tags)
        # Items
        self._style_items = {
            'family': '',
            'size': 9,
            'weight': 'normal',
            'slant': 'roman',
            'underline': False,
            'overstrike': False,
            'foreground': '',
            'background': '',
        }
        # Groups (folders)
        self._style_groups = {
            'family': '',
            'size': 9,
            'weight': 'bold',
            'slant': 'roman',
            'underline': False,
            'overstrike': False,
            'foreground': '',
            'background': '',
        }
        # Tk Font objects (created lazily)
        self._font_items = None
        self._font_groups = None
        self._ttk_style = None
        self._tree_style_name = 'MyTags.Treeview'

        # Toggle vars for style flags (for menu checkbuttons)
        self.items_bold_var = BooleanVar(value=self._style_items['weight'] == 'bold')
        self.items_italic_var = BooleanVar(value=self._style_items['slant'] == 'italic')
        self.items_underline_var = BooleanVar(value=self._style_items['underline'])
        self.items_overstrike_var = BooleanVar(value=self._style_items['overstrike'])

        self.groups_bold_var = BooleanVar(value=self._style_groups['weight'] == 'bold')
        self.groups_italic_var = BooleanVar(value=self._style_groups['slant'] == 'italic')
        self.groups_underline_var = BooleanVar(value=self._style_groups['underline'])
        self.groups_overstrike_var = BooleanVar(value=self._style_groups['overstrike'])

        # Help Window
        self.help_window = HelpWindow(self.root)


    #region UI Build


    def create_tab8(self):
        # Context menu (handles both tree and listbox)
        def show_context_menu(event):
            widget: 'ttk.Treeview' | 'Listbox' = event.widget
            if widget == self.custom_dictionary_treeview:
                iid = widget.identify_row(event.y)
                # normalize selection to clicked row if needed
                if iid:
                    if iid not in widget.selection():
                        widget.selection_set(iid)
                else:
                    # clicked on empty area
                    widget.selection_remove(widget.selection())

                def _all_node_iids():
                    def walk(parent=''):
                        for child in widget.get_children(parent):
                            try:
                                tags = widget.item(child, 'tags') or ()
                            except Exception:
                                tags = ()
                            # skip transient placeholder rows
                            if 'placeholder' in tags:
                                continue
                            yield child
                            yield from walk(child)
                    return tuple(walk(''))

                def select_all():
                    try:
                        all_iids = _all_node_iids()
                        if all_iids:
                            widget.selection_set(*all_iids)
                        else:
                            widget.selection_remove(widget.selection())
                    except Exception:
                        pass

                def invert_selection():
                    try:
                        all_iids = set(_all_node_iids())
                        current = set(widget.selection() or ())
                        inverted = tuple(all_iids - current)
                        if current:
                            widget.selection_remove(*tuple(current))
                        if inverted:
                            widget.selection_set(*inverted)
                    except Exception:
                        pass

                def select_all_groups():
                    try:
                        groups = []
                        for nid in _all_node_iids():
                            try:
                                if 'folder' in (widget.item(nid, 'tags') or ()):
                                    groups.append(nid)
                            except Exception:
                                continue
                        if groups:
                            widget.selection_set(*tuple(groups))
                        else:
                            widget.selection_remove(widget.selection())
                    except Exception:
                        pass

                def select_all_items():
                    try:
                        items = []
                        for nid in _all_node_iids():
                            try:
                                if 'item' in (widget.item(nid, 'tags') or ()):
                                    items.append(nid)
                            except Exception:
                                continue
                        if items:
                            widget.selection_set(*tuple(items))
                        else:
                            widget.selection_remove(widget.selection())
                    except Exception:
                        pass

                is_folder = False
                if iid:
                    try:
                        is_folder = 'folder' in widget.item(iid, 'tags')
                    except Exception:
                        is_folder = False

                # any selected rows (items or folders)
                selected_rows_exist = False
                try:
                    selected_rows_exist = bool(widget.selection())
                except Exception:
                    selected_rows_exist = False

                def context_parent_for_new_group():
                    # Right-click root -> root
                    # Right-click on folder -> inside that folder
                    # Right-click on item -> inside that item's parent (same group)
                    if not iid:
                        return None
                    try:
                        if 'folder' in (widget.item(iid, 'tags') or ()):
                            return iid
                    except Exception:
                        pass
                    try:
                        return widget.parent(iid)
                    except Exception:
                        return None

                def build_groups_submenu(parent_menu):
                    sub = Menu(parent_menu, tearoff=0)
                    sub.add_command(label="(Root)", command=lambda: self.move_selection_to_folder(None))

                    tree = widget

                    def add_folder_entries(menu, parent_iid):
                        for gid in tree.get_children(parent_iid):
                            try:
                                if 'folder' in (tree.item(gid, 'tags') or ()):
                                    name = tree.item(gid)['text']
                                else:
                                    continue
                            except Exception:
                                continue
                            # submenu for this folder
                            child_sub = Menu(menu, tearoff=0)
                            # entry to move directly into this folder
                            child_sub.add_command(label="(Here)", command=lambda fid=gid: self.move_selection_to_folder(fid))
                            # recurse into children
                            add_folder_entries(child_sub, gid)
                            menu.add_cascade(label=name, menu=child_sub)

                    add_folder_entries(sub, '')
                    # If no folders exist at all
                    if not sub.index('end'):
                        sub.add_command(label="No groups", state='disabled')
                    return sub

                def add_selection_commands(menu: 'Menu'):
                    selection_submenu = Menu(menu, tearoff=0)
                    selection_submenu.add_command(label="All", command=select_all)
                    selection_submenu.add_command(label="Invert", command=invert_selection)
                    selection_submenu.add_command(label="Select All Groups", command=select_all_groups)
                    selection_submenu.add_command(label="Select All Tags", command=select_all_items)
                    menu.add_cascade(label="Selection", menu=selection_submenu)

                menu = Menu(widget, tearoff=0)
                # Always visible
                menu.add_command(label="New Group...", command=lambda: self.add_group_via_prompt(context_parent_for_new_group()))
                if not iid: # On empty area
                    menu.add_command(label="New Tag...", command=lambda: self.add_item_to_folder('', None))
                    menu.add_separator()
                    add_selection_commands(menu)
                else:
                    parent_for_new_tag = iid if is_folder else widget.parent(iid)
                    menu.add_command(label="New Tag...", command=lambda: self.add_item_to_folder(parent_for_new_tag, None))
                    if is_folder: # On folder
                        menu.add_command(label="Sort Tags", command=lambda iid=iid: self.sort_group_items(iid))
                    menu.add_separator()
                    menu.add_command(label="Rename...", command=lambda: self.rename_node(iid))
                    menu.add_command(label="Remove", command=self.remove_selected_tags)
                    # Always visible
                    menu.add_separator()
                    if selected_rows_exist:
                        menu.add_cascade(label="Move to...", menu=build_groups_submenu(menu))
                    menu.add_command(label="Move Up", command=lambda: self.move_selection(widget, 'up'))
                    menu.add_command(label="Move Down", command=lambda: self.move_selection(widget, 'down'))
                    menu.add_separator()
                    if not is_folder: # On item
                        menu.add_command(label="Prefix to Text", command=lambda: self.insert_selected_tags(widget, 'start'))
                        menu.add_command(label="Append to Text", command=lambda: self.insert_selected_tags(widget, 'end'))
                        menu.add_separator()
                    add_selection_commands(menu)
                menu.tk_popup(event.x_root, event.y_root)

            elif widget == self.alltags_listbox:
                index = widget.nearest(event.y)
                if not widget.curselection():
                    widget.selection_clear(0, 'end')
                    widget.selection_set(index)
                elif index not in widget.curselection():
                    widget.selection_clear(0, 'end')
                    widget.selection_set(index)

                def select_all():
                    widget.selection_set(0, 'end')

                def invert_selection():
                    current = set(widget.curselection())
                    all_indices = set(range(widget.size()))
                    inverted = all_indices - current
                    widget.selection_clear(0, 'end')
                    for i in inverted:
                        widget.selection_set(i)

                menu = Menu(widget, tearoff=0)
                if widget.curselection():
                    menu.add_command(label="Prefix to Text", command=lambda: self.insert_selected_tags(widget, 'start'))
                    menu.add_command(label="Append to Text", command=lambda: self.insert_selected_tags(widget, 'end'))
                    menu.add_separator()
                    menu.add_command(label="Add to MyTags", command=self.add_selected_alltags_to_mytags)
                    menu.add_separator()
                    menu.add_command(label="Refresh", command=self.refresh_all_tags_listbox)
                    menu.add_separator()
                    menu.add_command(label="Selection: All", command=select_all)
                    menu.add_command(label="Selection: Invert", command=invert_selection)
                else:
                    menu.add_command(label="Refresh", command=self.refresh_all_tags_listbox)
                menu.tk_popup(event.x_root, event.y_root)

        # Interface
        self.create_custom_dictionary(refresh=False)
        self.app.tab8.grid_rowconfigure(1, weight=1)
        self.app.tab8.grid_columnconfigure(0, weight=1)

        # Top Row
        top_frame = Frame(self.app.tab8)
        top_frame.grid(row=0, column=0, sticky='ew')

        help_btn = ttk.Button(top_frame, text="?", takefocus=False, width=2, command=self.show_my_tags_help)
        help_btn.pack(side='left')

        # Options Menu
        menubutton = ttk.Menubutton(top_frame, text="Options", takefocus=False)
        menubutton.pack(side='left')
        menu = Menu(menubutton, tearoff=0)
        menubutton.config(menu=menu)
        menu.add_checkbutton(label="Use: MyTags", variable=self.app.use_mytags_var, command=self.refresh_custom_dictionary)
        menu.add_checkbutton(label="Show: All Tags", variable=self.show_all_tags_var, command=self.toggle_all_tags_listbox)
        menu.add_separator()
        menu.add_command(label="Refresh: My Tags", command=self.load_my_tags_file)
        menu.add_command(label="Refresh: All Tags", command=self.refresh_all_tags_listbox)
        menu.add_separator()
        menu.add_checkbutton(label="Hide: My Tags - Controls", variable=self.hide_mytags_controls_var, command=self.toggle_mytags_controls)
        menu.add_checkbutton(label="Hide: All Tags - Controls", variable=self.hide_alltags_controls_var, command=self.toggle_alltags_controls)
        menu.add_separator()
        menu.add_command(label="Sort MyTags Tags", command=self.sort_all_groups_items)
        menu.add_command(label="Sort MyTags Groups", command=self.sort_all_groups)
        menu.add_separator()

        # MyTags Font Style submenu
        font_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="MyTags Font Style", menu=font_menu)

        # Groups Style submenu
        groups_menu = Menu(font_menu, tearoff=0)
        font_menu.add_cascade(label="Groups", menu=groups_menu)
        groups_menu.add_command(label="Font...", command=lambda: self._prompt_font_family('groups'))
        groups_menu.add_command(label="Size...", command=lambda: self._prompt_font_size('groups'))
        groups_menu.add_separator()
        groups_menu.add_checkbutton(label="Bold", variable=self.groups_bold_var, command=lambda: self._toggle_style_flags('groups'))
        groups_menu.add_checkbutton(label="Italic", variable=self.groups_italic_var, command=lambda: self._toggle_style_flags('groups'))
        groups_menu.add_checkbutton(label="Underline", variable=self.groups_underline_var, command=lambda: self._toggle_style_flags('groups'))
        groups_menu.add_checkbutton(label="Overstrike", variable=self.groups_overstrike_var, command=lambda: self._toggle_style_flags('groups'))
        groups_menu.add_separator()
        groups_menu.add_command(label="Foreground...", command=lambda: self._choose_color('groups', 'foreground'))
        groups_menu.add_command(label="Background...", command=lambda: self._choose_color('groups', 'background'))
        groups_menu.add_separator()
        groups_menu.add_command(label="Reset", command=lambda: self._reset_font_style('groups'))

        # Items Style submenu
        items_menu = Menu(font_menu, tearoff=0)
        font_menu.add_cascade(label="Items", menu=items_menu)
        items_menu.add_command(label="Font...", command=lambda: self._prompt_font_family('items'))
        items_menu.add_command(label="Size...", command=lambda: self._prompt_font_size('items'))
        items_menu.add_separator()
        items_menu.add_checkbutton(label="Bold", variable=self.items_bold_var, command=lambda: self._toggle_style_flags('items'))
        items_menu.add_checkbutton(label="Italic", variable=self.items_italic_var, command=lambda: self._toggle_style_flags('items'))
        items_menu.add_checkbutton(label="Underline", variable=self.items_underline_var, command=lambda: self._toggle_style_flags('items'))
        items_menu.add_checkbutton(label="Overstrike", variable=self.items_overstrike_var, command=lambda: self._toggle_style_flags('items'))
        items_menu.add_separator()
        items_menu.add_command(label="Foreground...", command=lambda: self._choose_color('items', 'foreground'))
        items_menu.add_command(label="Background...", command=lambda: self._choose_color('items', 'background'))
        items_menu.add_separator()
        items_menu.add_command(label="Reset", command=lambda: self._reset_font_style('items'))
        menu.add_separator()
        menu.add_command(label="Cleanup MyTags", command=self.cleanup_custom_dictionary)
        menu.add_command(label="Open MyTags File...", command=lambda: self.app.open_textfile(self.app.my_tags_yml))

        # Tag entry + Add + Save
        entry_frame = Frame(top_frame)
        entry_frame.pack(side='left', fill='x', expand=True, pady=4)

        self.tag_entry = ttk.Entry(entry_frame)
        self.tag_entry.pack(side='left', fill='x', expand=True)
        self.tag_entry.bind('<Return>', lambda event: (self.add_tag(self.tag_entry.get()), self.tag_entry.delete(0, 'end')))
        EntryHelper.bind_helpers(self.tag_entry)

        add_btn = ttk.Button(entry_frame, text="Add", command=lambda: (self.add_tag(self.tag_entry.get()), self.tag_entry.delete(0, 'end')))
        add_btn.pack(side='left')
        Tip.create(widget=add_btn, text="Add tag to 'My Tags'")

        self.save_btn = ttk.Button(top_frame, text="Save Tags", takefocus=False, command=self.save_my_tags_file)
        self.save_btn.pack(side='right')
        self.save_btn_tooltip = Tip.create(widget=self.save_btn, text="Save changes to 'My Tags' file")

        # Middle Row
        self.text_frame = ttk.PanedWindow(self.app.tab8, orient='horizontal')
        self.text_frame.grid(row=1, column=0, sticky='nsew')

        # My Tags section
        my_tags_frame = Frame(self.text_frame)
        self.text_frame.add(my_tags_frame, weight=1)
        my_tags_frame.grid_rowconfigure(1, weight=1)
        my_tags_frame.grid_columnconfigure(0, weight=1)

        top_frame = Frame(my_tags_frame)
        top_frame.grid(row=0, column=0, sticky='ew', padx=2, pady=(2, 0))
        ttk.Label(top_frame, text="My Tags:").pack(side='left', padx=(0, 5))

        self.custom_dictionary_treeview = ttk.Treeview(my_tags_frame, show='tree', selectmode='extended', height=12)
        self.custom_dictionary_treeview.column('#0', anchor='w')
        self.custom_dictionary_treeview.grid(row=1, column=0, sticky='nsew')
        self._apply_treeview_styles()
        # Ensure Treeview uses the custom style
        try:
            self.custom_dictionary_treeview.configure(style=self._tree_style_name)
        except Exception:
            pass

        self.custom_dictionary_treeview.bind("<Button-3>", show_context_menu)
        self.custom_dictionary_treeview.bind("<Double-Button-1>", lambda event: self.insert_selected_tags(self.custom_dictionary_treeview, 'end'))

        # Drag & Drop (middle mouse)
        self.custom_dictionary_treeview.bind("<Button-2>", self._dnd_start)
        self.custom_dictionary_treeview.bind("<B2-Motion>", self._dnd_motion)
        self.custom_dictionary_treeview.bind("<ButtonRelease-2>", self._dnd_drop)

        # My Tags buttons
        self.list_btn_frame = Frame(my_tags_frame)
        self.list_btn_frame.grid(row=2, column=0, sticky='ew', pady=(2, 0))
        self.list_btn_frame.grid_columnconfigure(0, weight=1)
        self.list_btn_frame.grid_columnconfigure(1, weight=1)

        prefix_btn = ttk.Button(self.list_btn_frame, text="Prefix", command=lambda: self.insert_selected_tags(self.custom_dictionary_treeview, 'start'))
        prefix_btn.grid(row=0, column=0, sticky='ew', padx=2)
        append_btn = ttk.Button(self.list_btn_frame, text="Append", command=lambda: self.insert_selected_tags(self.custom_dictionary_treeview, 'end'))
        append_btn.grid(row=0, column=1, sticky='ew', padx=2)
        edit_btn = ttk.Button(self.list_btn_frame, text="Edit", command=self.edit_selected_tag_to_entry)
        edit_btn.grid(row=2, column=0, sticky='ew', padx=2)
        remove_btn = ttk.Button(self.list_btn_frame, text="Remove", command=self.remove_selected_tags)
        remove_btn.grid(row=2, column=1, sticky='ew', padx=2)
        up_btn = ttk.Button(self.list_btn_frame, text="Move Up", command=lambda: self.move_selection(self.custom_dictionary_treeview, 'up'))
        up_btn.grid(row=4, column=0, sticky='ew', padx=2)
        down_btn = ttk.Button(self.list_btn_frame, text="Move Down", command=lambda: self.move_selection(self.custom_dictionary_treeview, 'down'))
        down_btn.grid(row=4, column=1, sticky='ew', padx=2)

        # Apply initial visibility for MyTags controls based on the default-enabled hide option
        self.toggle_mytags_controls()

        # All Tags section
        self.alltags_frame = Frame(self.text_frame)
        self.text_frame.add(self.alltags_frame, weight=1)
        self.alltags_frame.grid_rowconfigure(1, weight=1)
        self.alltags_frame.grid_columnconfigure(0, weight=1)

        alltags_lbl = ttk.Label(self.alltags_frame, text="All Tags")
        alltags_lbl.grid(row=0, column=0, sticky='w', padx=2, pady=(2, 0))

        self.alltags_listbox = Listbox(self.alltags_frame, selectmode='extended')
        self.alltags_listbox.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.alltags_listbox.bind("<Button-3>", show_context_menu)
        self.alltags_listbox.bind("<Double-Button-1>", lambda event: self.insert_selected_tags(self.alltags_listbox, 'end'))

        # All Tags buttons
        self.alltags_btn_frame = Frame(self.alltags_frame)
        self.alltags_btn_frame.grid(row=2, column=0, sticky='ew', pady=(2, 0))
        self.alltags_btn_frame.grid_columnconfigure(0, weight=1)
        self.alltags_btn_frame.grid_columnconfigure(1, weight=0)
        self.alltags_btn_frame.grid_columnconfigure(2, weight=1)

        prefix_btn = ttk.Button(self.alltags_btn_frame, text="Prefix", command=lambda: self.insert_selected_tags(self.alltags_listbox, 'start'))
        prefix_btn.grid(row=0, column=0, sticky='ew', padx=2)
        add_btn = ttk.Button(self.alltags_btn_frame, text="<", command=self.add_selected_alltags_to_mytags, width=2)
        add_btn.grid(row=0, column=1)
        Tip.create(widget=add_btn, text="Add selected tags to 'My Tags'")
        append_btn = ttk.Button(self.alltags_btn_frame, text="Append", command=lambda: self.insert_selected_tags(self.alltags_listbox, 'end'))
        append_btn.grid(row=0, column=2, sticky='ew', padx=2)

        self.load_my_tags_file()
        self.refresh_custom_dictionary()
        self._apply_treeview_styles()


    def show_my_tags_help(self):
        self.help_window.open_window(geometry="600x700", help_text=HelpText.MY_TAGS_HELP)


    #endregion
    #region UI toggles


    def toggle_all_tags_listbox(self):
        if self.show_all_tags_var.get():
            self.text_frame.add(self.alltags_frame, weight=1)
        else:
            self.text_frame.remove(self.alltags_frame)


    def toggle_mytags_controls(self):
        if self.hide_mytags_controls_var.get():
            self.list_btn_frame.grid_remove()
        else:
            self.list_btn_frame.grid(row=2, column=0, sticky='ew', pady=(2,0))


    def toggle_alltags_controls(self):
        if self.hide_alltags_controls_var.get():
            self.alltags_btn_frame.grid_remove()
        else:
            self.alltags_btn_frame.grid(row=2, column=0, sticky='ew', pady=(2,0))


    #endregion
    #region Data ops


    def load_my_tags_file(self):
        if not self.custom_dictionary_treeview:
            return
        self.custom_dictionary_treeview.delete(*self.custom_dictionary_treeview.get_children())
        data = self._read_mytags_data()
        self._populate_tree_from_data(data)
        self.check_unsaved_changes()


    def save_my_tags_file(self):
        if not self.custom_dictionary_treeview:
            return
        data = self._collect_tree_data()
        try:
            self._write_mytags_data(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save MyTags (YAML):\n{e}")
            return
        self.root.after(100, self.refresh_custom_dictionary)
        self.check_unsaved_changes()


    def add_tag(self, tag_text: str):
        if not self.custom_dictionary_treeview:
            return
        tag = (tag_text or '').strip()
        if not tag:
            return
        tree = self.custom_dictionary_treeview
        sel = tree.selection()
        # If exactly one folder is selected, add to that folder
        folder_iid = None
        if len(sel) == 1:
            try:
                if 'folder' in tree.item(sel[0], 'tags'):
                    folder_iid = sel[0]
            except Exception:
                folder_iid = None
        changed = False
        if folder_iid:
            # ensure no duplicate within that folder
            existing = set(tree.item(i)['text'] for i in tree.get_children(folder_iid) if 'item' in tree.item(i, 'tags'))
            if tag not in existing:
                tree.insert(folder_iid, 'end', text=tag, tags=('item',))
                changed = True
        else:
            # add to root if not duplicate in root
            existing = set(tree.item(i)['text'] for i in tree.get_children('') if 'folder' not in tree.item(i, 'tags'))
            if tag not in existing:
                tree.insert('', 'end', text=tag, tags=('item',))
                changed = True
        if changed:
            self.check_unsaved_changes()


    def remove_selected_tags(self):
        if not self.custom_dictionary_treeview:
            return
        selected = self.custom_dictionary_treeview.selection()
        changed = False
        for iid in selected:
            self.custom_dictionary_treeview.delete(iid)
            changed = True
        if changed:
            self.check_unsaved_changes()


    def edit_selected_tag_to_entry(self):
        if not self.custom_dictionary_treeview or not self.tag_entry:
            return
        selected = self.custom_dictionary_treeview.selection()
        if not selected:
            return
        iid = selected[0]
        self.rename_node(iid)


    def move_selection(self, treeview: 'ttk.Treeview', direction: str):
        selected = treeview.selection()
        if not selected:
            return
        delta = -1 if direction == 'up' else 1
        # Move each selected within its parent
        order = selected if direction == 'up' else tuple(reversed(selected))
        changed = False
        for iid in order:
            parent = treeview.parent(iid)
            siblings = list(treeview.get_children(parent))
            idx = siblings.index(iid) if iid in siblings else -1
            if idx == -1:
                continue
            new_idx = idx + delta
            if 0 <= new_idx < len(siblings):
                treeview.move(iid, parent, new_idx)
                treeview.selection_set(iid)
                changed = True
        if changed:
            self.check_unsaved_changes()


    def add_selected_alltags_to_mytags(self):
        if not self.alltags_listbox or not self.custom_dictionary_treeview:
            return
        selected_indices = self.alltags_listbox.curselection()
        if not selected_indices:
            return
        tree = self.custom_dictionary_treeview
        sel = tree.selection()
        folder_iid = None
        if len(sel) == 1:
            try:
                if 'folder' in tree.item(sel[0], 'tags'):
                    folder_iid = sel[0]
            except Exception:
                folder_iid = None
        changed = False
        if folder_iid:
            existing = set(tree.item(i)['text'] for i in tree.get_children(folder_iid) if 'item' in tree.item(i, 'tags'))
            for idx in selected_indices:
                tag = self.alltags_listbox.get(idx)
                if tag not in existing:
                    tree.insert(folder_iid, 'end', text=tag, tags=('item',))
                    changed = True
        else:
            existing = set(tree.item(i)['text'] for i in tree.get_children('') if 'folder' not in tree.item(i, 'tags'))
            for idx in selected_indices:
                tag = self.alltags_listbox.get(idx)
                if tag not in existing:
                    tree.insert('', 'end', text=tag, tags=('item',))
                    changed = True
        if changed:
            self.check_unsaved_changes()


    def refresh_all_tags_listbox(self, tags=None):
        if tags is None:
            self.app.stat_calculator.calculate_file_stats()
            tags = self.app.stat_calculator.sorted_captions
        self.alltags_listbox.delete(0, 'end')
        for tag, count in tags:
            t = (tag or '').strip()
            if not t:
                continue
            self.alltags_listbox.insert('end', t)


    def insert_selected_tags(self, widget, position: str = 'start'):
        tags = self._get_selected_tags(widget)
        if not tags:
            return
        current_text = self.app.text_box.get('1.0', 'end-1c').strip()
        existing = self._split_csv(current_text) if current_text else []
        new_parts = tags + existing if position == 'start' else existing + tags
        new_text = self._join_csv(new_parts)
        self.app.text_box.delete('1.0', 'end')
        self.app.text_box.insert('1.0', new_text)


    def refresh_custom_dictionary(self):
        data = self._read_mytags_data()
        treeview = self.custom_dictionary_treeview
        # Clear existing items
        for item in treeview.get_children():
            treeview.delete(item)
        # Insert folders and items
        self._populate_tree_from_data(data)
        self.app.autocomplete.update_autocomplete_dictionary()
        self.check_unsaved_changes()


    def create_custom_dictionary(self, reset=False, refresh=True):
        try:
            filename = self.app.my_tags_yml
            if reset or not os.path.isfile(filename):
                csv_path = self._csv_legacy_path()
                if os.path.isfile(csv_path):
                    try:
                        with open(csv_path, 'r', encoding='utf-8') as f:
                            lines = f.read().splitlines()
                        tags = [line.strip() for line in lines if line.strip() and not line.strip().startswith('###')]
                        # Write structured data to preserve grouping (no flat list)
                        self._write_mytags_data({'items': tags, 'groups': []})
                    except Exception:
                        self._write_mytags_data({'items': [], 'groups': []})
                else:
                    self._write_mytags_data({'items': [], 'groups': []})
                if refresh:
                    self.refresh_custom_dictionary()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: create_custom_dictionary()", f"An error occurred while creating the MyTags file:\n\n{filename}\n\n{e}")


    def remove_extra_newlines(self, text: "str"):
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if line.strip() != '']
        result = '\n'.join(cleaned_lines)
        if not result.endswith('\n'):
            result += '\n'
        return result


    def cleanup_custom_dictionary(self):
        # Initial warning messagebox
        msg = (
            "Cleanup MyTags will:\n"
            "• Remove duplicate tags (case-sensitive)\n"
            "• Remove empty tags\n"
            "• Remove quotes from tags\n"
            "• Remove empty groups\n\n"
            "This operation cannot be undone.\n"
            "Do you want to continue?"
        )
        if not messagebox.askokcancel("Cleanup MyTags", msg):
            return
        try:
            data = self._read_mytags_data()
            seen = set()

            def clean_items(lst):
                cleaned = []
                for tag in lst or []:
                    cleaned_tag = str(tag).replace('"', '').replace("'", "").strip()
                    if cleaned_tag and cleaned_tag not in seen:
                        seen.add(cleaned_tag)
                        cleaned.append(cleaned_tag)
                return cleaned

            def clean_group(grp: dict):
                name = str(grp.get('name', '')).strip() or 'Group'
                items = clean_items(grp.get('items') or [])
                cleaned_children = []
                for child in grp.get('groups') or []:
                    cg = clean_group(child)
                    if cg is not None:
                        cleaned_children.append(cg)
                # keep group if it has items or non-empty children
                if items or cleaned_children:
                    return {'name': name, 'items': items, 'groups': cleaned_children}
                return None

            cleaned_items = clean_items(data.get('items') or [])
            cleaned_groups = []
            for grp in data.get('groups') or []:
                cg = clean_group(grp)
                if cg is not None:
                    cleaned_groups.append(cg)

            self._write_mytags_data({'items': cleaned_items, 'groups': cleaned_groups})
            self.refresh_custom_dictionary()
            self.check_unsaved_changes()
            messagebox.showinfo("Success", "MyTags has been cleaned.")
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: cleanup_custom_dictionary()", f"An error occurred while cleaning MyTags:\n\n{e}")


    def add_to_custom_dictionary(self, origin):
        try:
            if origin == "text_box":
                selected_text = self.app.text_box.get("sel.first", "sel.last")
            elif origin == "auto_tag":
                selected_text = self.app.text_controller.autotag_listbox.get("active")
                selected_text = selected_text.split(':', 1)[-1].strip()
            else:
                selected_text = ""
            if selected_text:
                # Update structured data, preserving existing groups
                data = self._read_mytags_data()
                existing = set(data.get('items', []))
                for grp in data.get('groups', []):
                    for it in grp.get('items', []):
                        existing.add(it)
                if selected_text not in existing:
                    data.setdefault('items', []).append(selected_text)
                    self._write_mytags_data(data)
            self.refresh_custom_dictionary()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: add_to_custom_dictionary()", f"An error occurred while saving the selection to 'my_tags.yaml'.\n\n{e}")


    #endregion
    #region Helpers


    def is_treeview_synced_with_yaml(self) -> bool:
        try:
            yaml_data = self._read_mytags_data()
            tree_data = self._collect_tree_data()
        except Exception:
            return False
        try:
            synced = (yaml_data == tree_data)
        except Exception:
            return False
        return synced


    def check_unsaved_changes(self):
        if self.is_treeview_synced_with_yaml():
            self.save_btn.config(style="TButton")
            self.save_btn_tooltip.config(text="No changes to save")
        else:
            self.save_btn.config(style="Red.TButton")
            self.save_btn_tooltip.config(text="There are unsaved changes")


    #region Font Style


    def _ensure_fonts(self):
        if self._font_items is None:
            self._font_items = tkfont.Font(self.root, name='MyTagsItemFont', family=tkfont.nametofont('TkDefaultFont').cget('family'), size=9)
        if self._font_groups is None:
            self._font_groups = tkfont.Font(self.root, name='MyTagsGroupFont', family=tkfont.nametofont('TkDefaultFont').cget('family'), size=9, weight='bold')


    def _apply_treeview_styles(self):
        if not self.custom_dictionary_treeview:
            return
        self._ensure_fonts()
        # Ensure ttk.Style exists and our style is configured
        if self._ttk_style is None:
            try:
                self._ttk_style = ttk.Style(self.root)
            except Exception:
                self._ttk_style = ttk.Style()
        try:
            self._ttk_style.configure(self._tree_style_name)
        except Exception:
            pass
        # Items font
        items_style = self._style_items
        fam_i = items_style['family'] or tkfont.nametofont('TkDefaultFont').cget('family')
        try:
            size_i = int(items_style['size'])
        except Exception:
            size_i = 9
        self._font_items.configure(
            family=fam_i,
            size=size_i,
            weight=items_style['weight'],
            slant=items_style['slant'],
            underline=bool(items_style['underline']),
            overstrike=bool(items_style['overstrike'])
        )
        # Groups font
        groups_style = self._style_groups
        fam_g = groups_style['family'] or tkfont.nametofont('TkDefaultFont').cget('family')
        try:
            size_g = int(groups_style['size'])
        except Exception:
            size_g = 9
        self._font_groups.configure(
            family=fam_g,
            size=size_g,
            weight=groups_style['weight'],
            slant=groups_style['slant'],
            underline=bool(groups_style['underline']),
            overstrike=bool(groups_style['overstrike'])
        )
        # Apply to Treeview tags
        try:
            self.custom_dictionary_treeview.tag_configure('item', font=self._font_items, foreground=(items_style['foreground'] or ''), background=(items_style['background'] or ''))
        except Exception:
            pass
        try:
            self.custom_dictionary_treeview.tag_configure('folder', font=self._font_groups, foreground=(groups_style['foreground'] or ''), background=(groups_style['background'] or ''))
        except Exception:
            pass
        # Compute and apply rowheight using larger of items/groups font line space
        try:
            metrics_items = self._font_items.metrics()
            metrics_groups = self._font_groups.metrics()
            font_h_items = metrics_items.get('linespace', 0)
            font_h_groups = metrics_groups.get('linespace', 0)
        except Exception:
            font_h_items = 0
            font_h_groups = 0
        row_h = max(16, font_h_items, font_h_groups)
        try:
            self._ttk_style.configure(self._tree_style_name, rowheight=row_h)
            self.custom_dictionary_treeview.configure(style=self._tree_style_name)
        except Exception:
            pass


    def _toggle_style_flags(self, which: str):
        if which == 'items':
            self._style_items['weight'] = 'bold' if self.items_bold_var.get() else 'normal'
            self._style_items['slant'] = 'italic' if self.items_italic_var.get() else 'roman'
            self._style_items['underline'] = bool(self.items_underline_var.get())
            self._style_items['overstrike'] = bool(self.items_overstrike_var.get())
        else:
            self._style_groups['weight'] = 'bold' if self.groups_bold_var.get() else 'normal'
            self._style_groups['slant'] = 'italic' if self.groups_italic_var.get() else 'roman'
            self._style_groups['underline'] = bool(self.groups_underline_var.get())
            self._style_groups['overstrike'] = bool(self.groups_overstrike_var.get())
        self._apply_treeview_styles()


    def _prompt_font_family(self, which: str):
        try:
            families = sorted(set(tkfont.families(self.root)))
        except Exception:
            families = []
        current = self._style_items['family'] if which == 'items' else self._style_groups['family']
        name = custom_dialog.askcombo("Font Family", "Select font", values=families, initialvalue=current or '', parent=self.root, icon_image=self.app.blank_image)
        if name is None:
            return
        name = name.strip()
        if which == 'items':
            self._style_items['family'] = name
        else:
            self._style_groups['family'] = name
        self._apply_treeview_styles()


    def _prompt_font_size(self, which: str):
        current = self._style_items['size'] if which == 'items' else self._style_groups['size']
        val = custom_dialog.askstring("Font Size", "Enter font size (e.g., 9)", initialvalue=str(current), parent=self.root, icon_image=self.app.blank_image)
        if val is None:
            return
        try:
            size = max(6, min(96, int(str(val).strip())))
        except Exception:
            return
        if which == 'items':
            self._style_items['size'] = size
        else:
            self._style_groups['size'] = size
        self._apply_treeview_styles()

    # Removed row height manual controls; auto-calculated from font metrics


    def _choose_color(self, which: str, field: str):
        style = self._style_items if which == 'items' else self._style_groups
        initial = style.get(field) or None
        try:
            _rgb, hexval = colorchooser.askcolor(initialcolor=initial, parent=self.root, title=("Choose " + field.capitalize()))
        except Exception:
            hexval = None
        if not hexval:
            return
        style[field] = hexval
        self._apply_treeview_styles()


    def _reset_font_style(self, which: str):
        if which == 'items':
            self._style_items = {
                'family': '', 'size': 9, 'weight': 'normal', 'slant': 'roman',
                'underline': False, 'overstrike': False, 'foreground': '', 'background': ''
            }
            self.items_bold_var.set(False)
            self.items_italic_var.set(False)
            self.items_underline_var.set(False)
            self.items_overstrike_var.set(False)
        else:
            self._style_groups = {
                'family': '', 'size': 9, 'weight': 'bold', 'slant': 'roman',
                'underline': False, 'overstrike': False, 'foreground': '', 'background': ''
            }
            self.groups_bold_var.set(True)
            self.groups_italic_var.set(False)
            self.groups_underline_var.set(False)
            self.groups_overstrike_var.set(False)
        self._apply_treeview_styles()


    #endregion
    #region Treeview helpers


    def _split_csv(self, text: str):
        return [t.strip() for t in text.split(',') if t.strip()]


    def _join_csv(self, parts):
        return ', '.join([p for p in parts if p])


    def _get_selected_tags(self, widget):
        # Treeview
        if hasattr(widget, 'selection') and callable(getattr(widget, 'selection')):
            selected = widget.selection()
            # Only return item texts, skip folders
            out = []
            for iid in selected or []:
                try:
                    if 'folder' in widget.item(iid, 'tags'):
                        continue
                except Exception:
                    pass
                out.append(widget.item(iid)['text'])
            return out
        # Listbox
        if hasattr(widget, 'curselection') and callable(getattr(widget, 'curselection')):
            indices = widget.curselection()
            return [widget.get(i) for i in indices] if indices else []
        return []


    # YAML storage helpers
    def _csv_legacy_path(self) -> str:
        # my_tags.yaml path stored in self.app.my_tags_csv; legacy CSV lives alongside
        yaml_path = self.app.my_tags_yml
        base_dir = os.path.dirname(yaml_path)
        return os.path.join(base_dir, "my_tags.csv")


    def _read_mytags_list(self):
        # Flatten hierarchical data for consumers needing a flat list
        data = self._read_mytags_data()

        def flatten_groups(groups):
            out = []
            for g in groups or []:
                out.extend(g.get('items') or [])
                out.extend(flatten_groups(g.get('groups') or []))
            return out

        flat = list(data.get('items', []) or [])
        flat.extend(flatten_groups(data.get('groups') or []))
        if flat:
            return flat
        return []


    def _read_mytags_data(self):
        path = self.app.my_tags_yml

        def normalize_group_entry(entry):
            if not isinstance(entry, dict):
                return None
            name = str(entry.get('name', '')).strip() or 'Group'
            # normalize items
            items = []
            if isinstance(entry.get('items'), list):
                items = [str(x).strip() for x in entry['items'] if str(x).strip()]
            # normalize children groups (supports list or dict legacy)
            raw_children = entry.get('groups') or []
            children = []
            if isinstance(raw_children, dict):
                for n, lst in raw_children.items():
                    lst2 = [str(x).strip() for x in (lst or []) if str(x).strip()]
                    children.append({'name': str(n).strip() or 'Group', 'items': lst2, 'groups': []})
            elif isinstance(raw_children, list):
                for sub in raw_children:
                    sg = normalize_group_entry(sub)
                    if sg:
                        children.append(sg)
            open_state = entry.get('open', True)
            return {'name': name, 'items': items, 'groups': children, 'open': bool(open_state)}

        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if not data:
                    return {'items': [], 'groups': []}
                if isinstance(data, dict) and ('items' in data or 'groups' in data):
                    items = []
                    groups = []
                    # items
                    if isinstance(data.get('items'), list):
                        items = [str(x).strip() for x in data['items'] if str(x).strip()]
                    # groups could be list[dict{name,items,groups}] or dict[name] -> list (legacy)
                    g = data.get('groups') or []
                    if isinstance(g, dict):
                        for name, lst in g.items():
                            lst2 = [str(x).strip() for x in (lst or []) if str(x).strip()]
                            groups.append({'name': str(name).strip() or 'Group', 'items': lst2, 'groups': [], 'open': True})
                    elif isinstance(g, list):
                        for entry in g:
                            ng = normalize_group_entry(entry)
                            if ng:
                                groups.append(ng)
                    return {'items': items, 'groups': groups}
                # Legacy dict with 'tags'
                if isinstance(data, dict) and 'tags' in data and isinstance(data['tags'], list):
                    items = [str(x).strip() for x in data['tags'] if str(x).strip()]
                    return {'items': items, 'groups': []}
                # Legacy list
                if isinstance(data, list):
                    items = [str(x).strip() for x in data if str(x).strip()]
                    return {'items': items, 'groups': []}
            except Exception:
                pass
        # Fallback CSV migration
        csv_path = self._csv_legacy_path()
        if os.path.isfile(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    lines = f.read().splitlines()
                items = [line.strip() for line in lines if line.strip() and not line.strip().startswith('###')]
                try:
                    self._write_mytags_data({'items': items, 'groups': []})
                except Exception:
                    pass
                return {'items': items, 'groups': []}
            except Exception:
                return {'items': [], 'groups': []}
        return {'items': [], 'groups': []}


    def _write_mytags_list(self, tags):
        # Never write a flat list. Preserve existing groups and update only root 'items'.
        data = self._read_mytags_data()
        data['items'] = [str(t).strip() for t in tags if str(t).strip()]
        self._write_mytags_data(data)


    def _write_mytags_data(self, data: dict):
        # Store structured data: {'items': [...], 'groups': [{'name':..., 'items':[...], 'groups':[...], 'open': bool}]}
        path = self.app.my_tags_yml
        os.makedirs(os.path.dirname(path), exist_ok=True)

        def sanitize_group(g: dict):
            name = str(g.get('name', '')).strip() or 'Group'
            lst = [str(t).strip() for t in (g.get('items') or []) if str(t).strip()]
            subs = []
            for sub in g.get('groups') or []:
                if isinstance(sub, dict):
                    subs.append(sanitize_group(sub))
            open_state = bool(g.get('open', True))
            return {'name': name, 'items': lst, 'groups': subs, 'open': open_state}

        items = [str(t).strip() for t in (data.get('items') or []) if str(t).strip()]
        groups = []
        for g in data.get('groups') or []:
            if isinstance(g, dict):
                groups.append(sanitize_group(g))

        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump({'items': items, 'groups': groups}, f, allow_unicode=True, sort_keys=False)


    def _populate_tree_from_data(self, data: dict):
        tree = self.custom_dictionary_treeview

        def insert_group(parent_iid, grp: dict):
            folder_iid = tree.insert(parent_iid, 'end', text=grp.get('name', 'Group'), tags=('folder',))
            for item in grp.get('items', []) or []:
                tree.insert(folder_iid, 'end', text=item, tags=('item',))
            for child in grp.get('groups', []) or []:
                insert_group(folder_iid, child)
            tree.item(folder_iid, open=bool(grp.get('open', True)))

        # Root items
        for tag in data.get('items', []) or []:
            tree.insert('', 'end', text=tag, tags=('item',))
        # Groups (recursive)
        for grp in data.get('groups', []) or []:
            insert_group('', grp)


    def _collect_tree_data(self) -> dict:
        tree = self.custom_dictionary_treeview

        def collect(parent_iid):
            items = []
            groups = []
            for iid in tree.get_children(parent_iid):
                text = tree.item(iid)['text']
                tags = tree.item(iid, 'tags') or ()
                if 'folder' in tags:
                    sub_items, sub_groups = collect(iid)
                    is_open = tree.item(iid, 'open')
                    groups.append({'name': text, 'items': sub_items, 'groups': sub_groups, 'open': bool(is_open)})
                elif 'item' in tags:
                    items.append(text)
                else:
                    # skip placeholders or unknown tags
                    continue
            return items, groups

        items, groups = collect('')
        return {'items': items, 'groups': groups}


    # Convenience actions for folders/items
    def add_group_via_prompt(self, parent_iid=None):
        name = custom_dialog.askstring("New Group", "Enter group name:", parent=self.root, icon_image=self.app.blank_image)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        parent = parent_iid or ''
        self.custom_dictionary_treeview.insert(parent, 'end', text=name, tags=('folder',))
        self.check_unsaved_changes()

    def add_item_to_folder(self, folder_iid: str | None, name: str | None = None):
        if folder_iid is None:
            folder_iid = ''
        tree = self.custom_dictionary_treeview
        if not tree:
            return
        if name is None:
            name = custom_dialog.askstring("New Item", "Enter item name:", parent=self.root, icon_image=self.app.blank_image)
            if name is None:
                return
            name = name.strip()
            if not name:
                return
        existing = set(tree.item(i)['text'] for i in tree.get_children(folder_iid) if 'item' in (tree.item(i, 'tags') or ()))
        if name not in existing:
            tree.insert(folder_iid, 'end', text=name, tags=('item',))
            self.check_unsaved_changes()


    def rename_node(self, iid):
        if not iid:
            return
        tree = self.custom_dictionary_treeview
        text = tree.item(iid)['text']
        is_folder = False
        try:
            is_folder = 'folder' in tree.item(iid, 'tags')
        except Exception:
            is_folder = False
        title = "Rename Group" if is_folder else "Rename Item"
        new_name = custom_dialog.askstring(title, "Enter new name:", initialvalue=text, parent=self.root, icon_image=self.app.blank_image)
        if new_name is None:
            return
        new_name = new_name.strip()
        if not new_name:
            return
        tree.item(iid, text=new_name)
        self.check_unsaved_changes()


    def move_selection_to_folder(self, folder_iid):
        tree = self.custom_dictionary_treeview
        if not tree:
            return
        selected = tuple(tree.selection() or ())
        if not selected:
            return
        dest_parent = folder_iid or ''
        selected_set = set(selected)

        def ancestor_selected(node):
            parent = tree.parent(node)
            while parent:
                if parent in selected_set:
                    return True
                parent = tree.parent(parent)
            return False

        def is_descendant(node, ancestor):
            while node:
                if node == ancestor:
                    return True
                node = tree.parent(node)
            return False

        def existing_names(parent):
            item_names, folder_names = set(), set()
            for child in tree.get_children(parent):
                try:
                    tags = tree.item(child, 'tags') or ()
                    if 'placeholder' in tags:
                        continue
                    name = tree.item(child)['text']
                except Exception:
                    continue
                (folder_names if 'folder' in tags else item_names).add(name)
            return item_names, folder_names

        dest_item_names, dest_folder_names = existing_names(dest_parent)
        moved = []
        for iid in selected:
            if ancestor_selected(iid):
                continue
            try:
                tags = tree.item(iid, 'tags') or ()
                if 'placeholder' in tags:
                    continue
                name = tree.item(iid)['text']
            except Exception:
                continue
            if tree.parent(iid) == dest_parent:
                continue
            if 'folder' in tags:
                if dest_parent and (iid == dest_parent or is_descendant(dest_parent, iid)):
                    continue
                if name in dest_folder_names:
                    continue
                target_names = dest_folder_names
            else:
                if name in dest_item_names:
                    continue
                target_names = dest_item_names
            try:
                tree.move(iid, dest_parent, 'end')
            except Exception:
                continue
            moved.append(iid)
            target_names.add(name)
        if not moved:
            return
        try:
            tree.selection_set(moved)
            tree.focus(moved[0])
        except Exception:
            pass
        self.check_unsaved_changes()


    def _sort_items_and_folders(self, tree, parent_iid):
        """Sort items alphabetically, keep folders after items (preserve folder order)."""
        items, folders = self.get_items_and_folders(tree, parent_iid)
        sorted_items = sorted(items, key=lambda cid: tree.item(cid)['text'].lower())
        for idx, cid in enumerate(sorted_items):
            tree.move(cid, parent_iid, idx)
        for idx, cid in enumerate(folders, start=len(sorted_items)):
            tree.move(cid, parent_iid, idx)
        return folders


    def _sort_folders_recursively(self, tree, parent_iid):
        """Sort folders alphabetically, keep items before folders (preserve item order)."""
        items, folders = self.get_items_and_folders(tree, parent_iid)
        sorted_folders = sorted(folders, key=lambda cid: tree.item(cid)['text'].lower())
        for idx, cid in enumerate(items):
            tree.move(cid, parent_iid, idx)
        for idx, cid in enumerate(sorted_folders, start=len(items)):
            tree.move(cid, parent_iid, idx)
            self._sort_folders_recursively(tree, cid)


    def get_items_and_folders(self, tree, parent_iid):
        children = list(tree.get_children(parent_iid))
        items = [cid for cid in children if 'item' in (tree.item(cid, 'tags') or ())]
        folders = [cid for cid in children if 'folder' in (tree.item(cid, 'tags') or ())]
        return items,folders


    def sort_group_items(self, iid):
        tree = self.custom_dictionary_treeview
        if not tree or not iid:
            return
        self._sort_items_and_folders(tree, iid)
        self.check_unsaved_changes()


    def sort_all_groups_items(self):
        tree = self.custom_dictionary_treeview
        if not tree:
            return

        def sort_items_in_group(parent_iid):
            folders = self._sort_items_and_folders(tree, parent_iid)
            for folder_cid in folders:
                sort_items_in_group(folder_cid)

        sort_items_in_group('')
        self.check_unsaved_changes()


    def sort_all_groups(self):
        tree = self.custom_dictionary_treeview
        if not tree:
            return
        self._sort_folders_recursively(tree, '')
        self.check_unsaved_changes()


    #endregion
    #region DnD


    def _compute_insert_index(self, tree: 'ttk.Treeview', y: int, parent) -> int:
        items = list(tree.get_children(parent))
        ph_iid = self._drag_state.get('placeholder_iid')
        items_wo = [iid for iid in items if iid != ph_iid]
        size = len(items_wo)
        if size <= 0:
            return 0
        over_iid = tree.identify_row(y)
        # if hovered row not in our sibling set, fallback to top/bottom by position
        if not over_iid or over_iid not in items_wo + ([ph_iid] if ph_iid else []):
            first_bbox = tree.bbox(items_wo[0])
            last_bbox = tree.bbox(items_wo[-1])
            if last_bbox and y >= (last_bbox[1] + last_bbox[3]):
                return size
            if first_bbox and y <= first_bbox[1]:
                return 0
            return size
        # hovering placeholder
        if ph_iid and over_iid == ph_iid:
            bbox = tree.bbox(over_iid)
            idx = tree.index(over_iid)
            if bbox and y > (bbox[1] + bbox[3] / 2):
                return min(idx + 1, len(items)) - (1 if ph_iid in items and tree.index(ph_iid) < idx + 1 else 0)
            else:
                return idx - (1 if ph_iid in items and tree.index(ph_iid) <= idx else 0)
        # normal row
        try:
            base_idx = items_wo.index(over_iid)
        except ValueError:
            base_idx = 0
        bbox = tree.bbox(over_iid)
        insert_idx = base_idx
        if bbox is not None and y > (bbox[1] + bbox[3] / 2):
            insert_idx = base_idx + 1
        return max(0, min(insert_idx, size))


    def _remove_placeholder(self, tree: 'ttk.Treeview'):
        ph_iid = self._drag_state.get('placeholder_iid')
        if ph_iid:
            try:
                tree.delete(ph_iid)
            except Exception:
                pass
        self._drag_state['placeholder_iid'] = None


    def _insert_placeholder(self, tree: 'ttk.Treeview', parent, insert_idx: int):
        self._remove_placeholder(tree)
        items = list(tree.get_children(parent))
        size = len([iid for iid in items if iid != self._drag_state.get('placeholder_iid')])
        try:
            tree.tag_configure('placeholder', background=self._placeholder_bg)
        except Exception:
            pass
        if insert_idx >= size:
            ph_iid = tree.insert(parent, 'end', text='', tags=('placeholder',))
        else:
            ph_iid = tree.insert(parent, insert_idx, text='', tags=('placeholder',))
        self._drag_state['placeholder_iid'] = ph_iid


    def _move_placeholder(self, tree: 'ttk.Treeview', parent, insert_idx: int):
        items = list(tree.get_children(parent))
        ph_iid = self._drag_state.get('placeholder_iid')
        items_wo = [iid for iid in items if iid != ph_iid]
        size = len(items_wo)
        target_idx = insert_idx if insert_idx < size else size
        if ph_iid and ph_iid in items:
            current_idx = tree.index(ph_iid)
            if (target_idx == size and current_idx == len(items) - 1) or current_idx == target_idx:
                return
            try:
                tree.move(ph_iid, parent, target_idx)
                return
            except Exception:
                pass
        self._insert_placeholder(tree, parent, target_idx)


    def _dnd_start(self, event):
        tree: 'ttk.Treeview' = event.widget
        if tree is not self.custom_dictionary_treeview:
            return
        over_iid = tree.identify_row(event.y)
        if not over_iid:
            return 'break'
        if over_iid not in tree.selection():
            tree.selection_set(over_iid)
        parent = tree.parent(over_iid)
        # Order only selected items within same parent
        sel_set = set(tree.selection())
        ordered = [iid for iid in tree.get_children(parent) if iid in sel_set]
        if not ordered:
            return 'break'
        self._drag_state['active'] = True
        self._drag_state['selected_iids'] = tuple(ordered)
        self._drag_state['start_iid'] = over_iid
        self._drag_state['parent'] = parent
        tree.focus(over_iid)
        self._drag_state['prev_cursor'] = tree.cget('cursor')
        try:
            tree.config(cursor='hand2')
        except Exception:
            pass
        insert_idx = self._compute_insert_index(tree, event.y, parent)
        self._move_placeholder(tree, parent, insert_idx)
        return 'break'


    def _dnd_motion(self, event):
        if not self._drag_state['active']:
            return 'break'
        tree: 'ttk.Treeview' = event.widget
        parent = self._drag_state.get('parent')
        height = tree.winfo_height()
        margin = 12
        if event.y < margin:
            tree.yview_scroll(-1, 'units')
        elif event.y > height - margin:
            tree.yview_scroll(1, 'units')
        insert_idx = self._compute_insert_index(tree, event.y, parent)
        self._move_placeholder(tree, parent, insert_idx)
        return 'break'


    def _dnd_drop(self, event):
        if not self._drag_state['active']:
            return 'break'
        tree: 'ttk.Treeview' = event.widget
        self._drag_state['active'] = False
        parent = self._drag_state.get('parent')
        selected = list(self._drag_state.get('selected_iids') or ())
        if not selected:
            return 'break'
        all_items = list(tree.get_children(parent))
        ph_iid = self._drag_state.get('placeholder_iid')
        if ph_iid and ph_iid in all_items:
            drop_idx_original = tree.index(ph_iid)
        else:
            drop_idx_original = self._compute_insert_index(tree, event.y, parent)
        sel_set = set(selected)
        ordered_selected = [iid for iid in all_items if iid in sel_set]
        others = [iid for iid in all_items if iid not in sel_set and iid != ph_iid]
        index_map = {iid: idx for idx, iid in enumerate(all_items)}
        offset_before = sum(1 for iid in ordered_selected if index_map[iid] < drop_idx_original)
        drop_idx_others = max(0, min(len(others), drop_idx_original - offset_before))
        self._remove_placeholder(tree)
        changed = False
        if ordered_selected:
            sel_start = min(index_map[iid] for iid in ordered_selected)
            start_in_others = sum(1 for iid in others if index_map[iid] < sel_start)
            if drop_idx_others == start_in_others:
                try:
                    tree.config(cursor=self._drag_state.get('prev_cursor') or '')
                except Exception:
                    pass
                self._drag_state['selected_iids'] = tuple()
                self._drag_state['start_iid'] = None
                self._drag_state['parent'] = None
                return 'break'
        anchor_iid = None
        if drop_idx_others < len(others):
            anchor_iid = others[drop_idx_others]
        try:
            if anchor_iid is None:
                for iid in ordered_selected:
                    tree.move(iid, parent, 'end')
                    changed = True
            else:
                for iid in ordered_selected:
                    tree.move(iid, parent, tree.index(anchor_iid))
                    changed = True
        except Exception:
            pass
        try:
            tree.selection_set(ordered_selected)
            tree.focus(ordered_selected[0])
        except Exception:
            pass
        try:
            tree.config(cursor=self._drag_state.get('prev_cursor') or '')
        except Exception:
            pass
        self._drag_state['selected_iids'] = tuple()
        self._drag_state['start_iid'] = None
        self._drag_state['parent'] = None
        if changed:
            self.check_unsaved_changes()
        return 'break'


    #endregion


#endregion
