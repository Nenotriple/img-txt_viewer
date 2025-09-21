#region Imports


# Standard Library - GUI
from tkinter import (
    ttk, Tk, messagebox,
    BooleanVar,
    Frame, Menu,
    Listbox
)


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


class MyTags:
    def __init__(self, app: 'Main', root: 'Tk'):
        self.app = app
        self.root = root

        # UI state variables
        self.show_all_tags_var = BooleanVar(value=True)
        self.hide_mytags_controls_var = BooleanVar(value=False)
        self.hide_alltags_controls_var = BooleanVar(value=False)

        # UI widgets (set during create_tab8)
        self.custom_dictionary_listbox = None
        self.alltags_listbox = None
        self.list_btn_frame = None
        self.alltags_btn_frame = None
        self.alltags_frame = None
        self.text_frame = None
        self.tag_entry = None

        # DnD state
        self._drag_state = {
            'active': False,
            'indices': tuple(),
            'start_index': None,
            'placeholder_index': None,
            'prev_cursor': None,
        }
        self._placeholder_bg = '#dbeafe'


    # --------------------
    # Data operations
    # --------------------


    def load_my_tags_file(self):
        if not self.custom_dictionary_listbox:
            return
        self.custom_dictionary_listbox.delete(0, 'end')
        try:
            with open(self.app.my_tags_csv, 'r', encoding='utf-8') as file:
                content = self.app.remove_extra_newlines(file.read())
        except Exception:
            content = ''
        for line in content.split('\n'):
            tag = line.strip()
            if tag:
                self.custom_dictionary_listbox.insert('end', tag)


    def save_my_tags_file(self):
        if not self.custom_dictionary_listbox:
            return
        tags = self.custom_dictionary_listbox.get(0, 'end')
        content = '\n'.join(tags) + ('\n' if tags else '')
        with open(self.app.my_tags_csv, 'w', encoding='utf-8') as file:
            file.write(content)
        self.root.after(100, self.app.refresh_custom_dictionary)


    def add_tag(self, tag_text: str):
        if not self.custom_dictionary_listbox:
            return
        tag = (tag_text or '').strip()
        if tag:
            self.custom_dictionary_listbox.insert('end', tag)


    def remove_selected_tags(self):
        if not self.custom_dictionary_listbox:
            return
        listbox = self.custom_dictionary_listbox
        selected = listbox.curselection()
        if not selected:
            return
        for idx in reversed(selected):
            listbox.delete(idx)


    def edit_selected_tag_to_entry(self):
        if not self.custom_dictionary_listbox or not self.tag_entry:
            return
        listbox = self.custom_dictionary_listbox
        selected = listbox.curselection()
        if not selected:
            return
        index = selected[0]
        tag = listbox.get(index)
        self.tag_entry.delete(0, 'end')
        self.tag_entry.insert(0, tag)
        listbox.delete(index)


    def move_selection(self, listbox: 'Listbox', direction: str):
        selected_indices = listbox.curselection()
        if not selected_indices:
            return
        delta = -1 if direction == 'up' else 1
        order = (selected_indices if direction == 'up' else reversed(selected_indices))
        for index in order:
            new_index = index + delta
            if 0 <= new_index < listbox.size():
                tag = listbox.get(index)
                listbox.delete(index)
                listbox.insert(new_index, tag)
                listbox.selection_set(new_index)


    def add_selected_alltags_to_mytags(self):
        if not self.alltags_listbox or not self.custom_dictionary_listbox:
            return
        selected_indices = self.alltags_listbox.curselection()
        if not selected_indices:
            return
        existing = set(self.custom_dictionary_listbox.get(0, 'end'))
        for idx in selected_indices:
            tag = self.alltags_listbox.get(idx)
            if tag not in existing:
                self.custom_dictionary_listbox.insert('end', tag)


    def _split_csv(self, text: str):
        # Simple CSV split by comma, trimming whitespace; assumes tags do not contain commas
        return [t.strip() for t in text.split(',') if t.strip()]


    def _join_csv(self, parts):
        return ', '.join([p for p in parts if p])


    def insert_selected_tags(self, listbox: 'Listbox', position: str = 'start'):
        # Efficiently insert all selected tags at once
        selected_indices = listbox.curselection()
        if not selected_indices:
            return
        tags = [listbox.get(i) for i in selected_indices]
        current_text = self.app.text_box.get('1.0', 'end-1c').strip()
        existing = self._split_csv(current_text) if current_text else []
        if position == 'start':
            new_parts = tags + existing
        else:
            new_parts = existing + tags
        new_text = self._join_csv(new_parts)
        self.app.text_box.delete('1.0', 'end')
        self.app.text_box.insert('1.0', new_text)


    def create_tab8(self):
        # DRAG & DROP (Middle Mouse)
        def dnd_start(event):
            return self._dnd_start(event)

        def dnd_motion(event):
            return self._dnd_motion(event)

        def dnd_drop(event):
            return self._dnd_drop(event)

        # CONTEXT MENU
        def show_context_menu(event):
            listbox: 'Listbox' = event.widget
            index = listbox.nearest(event.y)
            if not listbox.curselection():
                listbox.selection_clear(0, 'end')
                listbox.selection_set(index)
            elif index not in listbox.curselection():
                listbox.selection_clear(0, 'end')
                listbox.selection_set(index)

            # ALL
            def select_all():
                listbox.selection_set(0, 'end')

            # INVERT
            def invert_selection():
                current = set(listbox.curselection())
                all_indices = set(range(listbox.size()))
                inverted = all_indices - current
                listbox.selection_clear(0, 'end')
                for i in inverted:
                    listbox.selection_set(i)

            # MENU
            if listbox.curselection():
                menu = Menu(listbox, tearoff=0)
                if listbox == self.custom_dictionary_listbox:
                    menu.add_command(label="Prefix", command=lambda: self.insert_selected_tags(listbox, 'start'))
                    menu.add_command(label="Append", command=lambda: self.insert_selected_tags(listbox, 'end'))
                    menu.add_separator()
                    menu.add_command(label="Edit", command=self.edit_selected_tag_to_entry)
                    menu.add_command(label="Remove", command=self.remove_selected_tags)
                    menu.add_separator()
                    menu.add_command(label="Move Up", command=lambda: self.move_selection(listbox, 'up'))
                    menu.add_command(label="Move Down", command=lambda: self.move_selection(listbox, 'down'))
                else:
                    menu.add_command(label="Prefix", command=lambda: self.insert_selected_tags(listbox, 'start'))
                    menu.add_command(label="Append", command=lambda: self.insert_selected_tags(listbox, 'end'))
                    menu.add_separator()
                    menu.add_command(label="Add to MyTags", command=self.add_selected_alltags_to_mytags)
                    menu.add_separator()
                    menu.add_command(label="Refresh", command=self.refresh_all_tags_listbox)
                menu.add_separator()
                menu.add_command(label="Selection: All", command=select_all)
                menu.add_command(label="Selection: Invert", command=invert_selection)
                menu.tk_popup(event.x_root, event.y_root)

        # INTERFACE
        self.app.create_custom_dictionary(refresh=False)
        tab_frame = Frame(self.app.tab8)
        tab_frame.pack(side='top', fill='both', expand=True)
        tab_frame.grid_rowconfigure(1, weight=1)
        tab_frame.grid_columnconfigure(0, weight=1)
        # Top Row - Row 0
        top_frame = Frame(tab_frame)
        top_frame.grid(row=0, column=0, sticky='ew')
        help_btn = ttk.Button(top_frame, text="?", takefocus=False, width=2, command=self.show_my_tags_help)
        help_btn.pack(side='left')
        menubutton = ttk.Menubutton(top_frame, text="Options", takefocus=False)
        menubutton.pack(side='left')
        menu = Menu(menubutton, tearoff=0)
        menubutton.config(menu=menu)
        menu.add_checkbutton(label="Use: MyTags", variable=self.app.use_mytags_var, command=self.app.refresh_custom_dictionary)
        menu.add_checkbutton(label="Show: All Tags", variable=self.show_all_tags_var, command=self.toggle_all_tags_listbox)
        menu.add_separator()
        menu.add_command(label="Refresh: My Tags", command=self.load_my_tags_file)
        menu.add_command(label="Refresh: All Tags", command=self.refresh_all_tags_listbox)
        menu.add_separator()
        menu.add_checkbutton(label="Hide: My Tags - Controls", variable=self.hide_mytags_controls_var, command=self.toggle_mytags_controls)
        menu.add_checkbutton(label="Hide: All Tags - Controls", variable=self.hide_alltags_controls_var, command=self.toggle_alltags_controls)
        menu.add_separator()
        menu.add_command(label="Cleanup MyTags", command=self.app.cleanup_custom_dictionary)
        menu.add_command(label="Open MyTags File...", command=lambda: self.app.open_textfile(self.app.my_tags_csv))
        # entry_frame
        entry_frame = Frame(top_frame)
        entry_frame.pack(side='left', fill='x', expand=True, pady=4)
        self.tag_entry = ttk.Entry(entry_frame)
        self.tag_entry.pack(side='left', fill='x', expand=True)
        self.tag_entry.bind('<Return>', lambda event: (self.add_tag(self.tag_entry.get()), self.tag_entry.delete(0, 'end')))
        add_btn = ttk.Button(entry_frame, text="Add", command=lambda: (self.add_tag(self.tag_entry.get()), self.tag_entry.delete(0, 'end')))
        add_btn.pack(side='left')
        save_btn = ttk.Button(top_frame, text="Save Tags", takefocus=False, command=self.save_my_tags_file)
        save_btn.pack(side='right')
        # Middle Row
        self.text_frame = ttk.PanedWindow(tab_frame, orient='horizontal')
        self.text_frame.grid(row=1, column=0, sticky='nsew')
        # My Tags section
        my_tags_frame = Frame(self.text_frame)
        self.text_frame.add(my_tags_frame, weight=1)
        my_tags_frame.grid_rowconfigure(1, weight=1)
        my_tags_frame.grid_columnconfigure(0, weight=1)
        top_frame = Frame(my_tags_frame)
        top_frame.grid(row=0, column=0, sticky='ew', padx=2, pady=(2,0))
        ttk.Label(top_frame, text="My Tags:").pack(side='left', padx=(0,5))
        self.custom_dictionary_listbox = Listbox(my_tags_frame, selectmode='extended')
        self.custom_dictionary_listbox.grid(row=1, column=0, sticky='nsew')
        self.custom_dictionary_listbox.bind("<Button-3>", show_context_menu)
        self.custom_dictionary_listbox.bind("<Double-Button-1>", lambda event: self.insert_selected_tags(self.custom_dictionary_listbox, 'end'))
        # Middle-mouse drag & drop reordering (keeps left-click behavior intact)
        self.custom_dictionary_listbox.bind('<Button-2>', dnd_start)
        self.custom_dictionary_listbox.bind('<B2-Motion>', dnd_motion)
        self.custom_dictionary_listbox.bind('<ButtonRelease-2>', dnd_drop)
        # Buttons
        self.list_btn_frame = Frame(my_tags_frame)
        self.list_btn_frame.grid(row=2, column=0, sticky='ew', pady=(2,0))
        self.list_btn_frame.grid_columnconfigure(0, weight=1)
        self.list_btn_frame.grid_columnconfigure(1, weight=1)
        prefix_btn = ttk.Button(self.list_btn_frame, text="Prefix", command=lambda: self.insert_selected_tags(self.custom_dictionary_listbox, 'start'))
        prefix_btn.grid(row=0, column=0, sticky='ew', padx=2)
        append_btn = ttk.Button(self.list_btn_frame, text="Append", command=lambda: self.insert_selected_tags(self.custom_dictionary_listbox, 'end'))
        append_btn.grid(row=0, column=1, sticky='ew', padx=2)
        edit_btn = ttk.Button(self.list_btn_frame, text="Edit", command=self.edit_selected_tag_to_entry)
        edit_btn.grid(row=2, column=0, sticky='ew', padx=2)
        remove_btn = ttk.Button(self.list_btn_frame, text="Remove", command=self.remove_selected_tags)
        remove_btn.grid(row=2, column=1, sticky='ew', padx=2)
        up_btn = ttk.Button(self.list_btn_frame, text="Move Up", command=lambda: self.move_selection(self.custom_dictionary_listbox, 'up'))
        up_btn.grid(row=4, column=0, sticky='ew', padx=2)
        down_btn = ttk.Button(self.list_btn_frame, text="Move Down", command=lambda: self.move_selection(self.custom_dictionary_listbox, 'down'))
        down_btn.grid(row=4, column=1, sticky='ew', padx=2)
        # All Tags section
        self.alltags_frame = Frame(self.text_frame)
        self.text_frame.add(self.alltags_frame, weight=1)
        self.alltags_frame.grid_rowconfigure(1, weight=1)
        self.alltags_frame.grid_columnconfigure(0, weight=1)
        alltags_lbl = ttk.Label(self.alltags_frame, text="All Tags")
        alltags_lbl.grid(row=0, column=0, sticky='w', padx=2, pady=(2,0))
        self.alltags_listbox = Listbox(self.alltags_frame, selectmode='extended')
        self.alltags_listbox.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.alltags_listbox.bind("<Button-3>", show_context_menu)
        self.alltags_listbox.bind("<Double-Button-1>", lambda event: self.insert_selected_tags(self.alltags_listbox, 'end'))
        # Buttons
        self.alltags_btn_frame = Frame(self.alltags_frame)
        self.alltags_btn_frame.grid(row=2, column=0, sticky='ew', pady=(2,0))
        self.alltags_btn_frame.grid_columnconfigure(0, weight=1)
        self.alltags_btn_frame.grid_columnconfigure(1, weight=0)
        self.alltags_btn_frame.grid_columnconfigure(2, weight=1)
        prefix_btn = ttk.Button(self.alltags_btn_frame, text="Prefix", command=lambda: self.insert_selected_tags(self.alltags_listbox, 'start'))
        prefix_btn.grid(row=0, column=0, sticky='ew', padx=2)
        add_btn = ttk.Button(self.alltags_btn_frame, text="<", command=self.add_selected_alltags_to_mytags, width=2)
        add_btn.grid(row=0, column=1)
        ToolTip.create(add_btn, "Add selected tags to 'My Tags'", 200, 6, 12)
        append_btn = ttk.Button(self.alltags_btn_frame, text="Append", command=lambda: self.insert_selected_tags(self.alltags_listbox, 'end'))
        append_btn.grid(row=0, column=2, sticky='ew', padx=2)
        self.load_my_tags_file()
        self.app.refresh_custom_dictionary()


    def refresh_all_tags_listbox(self, tags=None):
        listbox = self.alltags_listbox
        if not tags:
            self.app.stat_calculator.calculate_file_stats()
            tags = self.app.stat_calculator.sorted_captions
        listbox.delete(0, 'end')
        for tag, count in tags:
            listbox.insert('end', tag)


    # --------------------
    # UI toggles
    # --------------------


    def toggle_all_tags_listbox(self):
        if self.show_all_tags_var.get():
            self.alltags_frame.grid(row=0, column=2, sticky='nsew')
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


    def show_my_tags_help(self):
        messagebox.showinfo("Help",
            "MyTags:\n"
            "A list of custom tags/keywords that will be used for autocomplete suggestions or for quick insertion into the text box.\n\n"
            "Basic Operations:\n"
            "• Add tags: Type + Enter, right-click text, or use All Tags list\n"
            "• Insert tags: Select and use Prefix/Append buttons or right-click menu\n"
            "• Double-click any tag to instantly insert it (append)\n\n"
            "Tag Management:\n"
            "• Edit/Remove selected tags\n"
            "• Reorder: drag with middle mouse, or use Move Up/Down (affects autocomplete priority)\n"
            "• Save changes to file (required to apply changes)\n\n"
            "Features:\n"
            "• Use MyTags: Toggle autocomplete suggestions\n"
            "• Show All Tags: View tags from all text files\n"
            "• Refresh: Update My Tags or All Tags lists\n"
            "• Hide Controls: Toggle visibility of control buttons\n"
            "• Open my_tags.csv: Edit tags directly in text editor\n\n"
            "Note: Tags are stored in 'my_tags.csv'\n"
            "Use 'Batch Tag Edit' tool to modify All Tags"
        )


    # --------------------
    # DnD helpers
    # --------------------


    def _compute_insert_index(self, listbox: 'Listbox', y: int) -> int:
        size = listbox.size()
        if size <= 0:
            return 0
        over_idx = listbox.nearest(y)
        if over_idx < 0:
            over_idx = 0
        if over_idx >= size:
            over_idx = size - 1
        bbox = listbox.bbox(over_idx)
        insert_idx = over_idx
        if bbox is not None:
            _, yrow, _, h = bbox
            if y > (yrow + h / 2):
                insert_idx = over_idx + 1
        if insert_idx < 0:
            insert_idx = 0
        if insert_idx > size:
            insert_idx = size
        return insert_idx


    def _remove_placeholder(self, listbox: 'Listbox'):
        ph_idx = self._drag_state.get('placeholder_index')
        if ph_idx is not None and 0 <= ph_idx < listbox.size():
            try:
                listbox.delete(ph_idx)
            except Exception:
                pass
        self._drag_state['placeholder_index'] = None


    def _insert_placeholder(self, listbox: 'Listbox', insert_idx: int):
        self._remove_placeholder(listbox)
        size = listbox.size()
        if insert_idx >= size:
            listbox.insert('end', '')
            self._drag_state['placeholder_index'] = listbox.size() - 1
        else:
            listbox.insert(insert_idx, '')
            self._drag_state['placeholder_index'] = insert_idx
        try:
            listbox.itemconfig(self._drag_state['placeholder_index'], bg=self._placeholder_bg)
        except Exception:
            pass


    def _move_placeholder(self, listbox: 'Listbox', insert_idx: int):
        size = listbox.size()
        target_idx = insert_idx if insert_idx < size else size
        ph_idx = self._drag_state.get('placeholder_index')
        if ph_idx is not None:
            if (target_idx == size and ph_idx == size - 1) or ph_idx == target_idx:
                return
        self._insert_placeholder(listbox, target_idx)


    def _dnd_start(self, event):
        listbox: 'Listbox' = event.widget
        if listbox is not self.custom_dictionary_listbox:
            return
        idx = listbox.nearest(event.y)
        if idx < 0 or idx >= listbox.size():
            return 'break'
        if idx not in listbox.curselection():
            listbox.selection_clear(0, 'end')
            listbox.selection_set(idx)
        self._drag_state['active'] = True
        self._drag_state['indices'] = tuple(sorted(listbox.curselection()))
        self._drag_state['start_index'] = idx
        listbox.activate(idx)
        self._drag_state['prev_cursor'] = listbox.cget('cursor')
        try:
            listbox.config(cursor='hand2')
        except Exception:
            pass
        insert_idx = self._compute_insert_index(listbox, event.y)
        self._move_placeholder(listbox, insert_idx)
        return 'break'


    def _dnd_motion(self, event):
        if not self._drag_state['active']:
            return 'break'
        listbox: 'Listbox' = event.widget
        height = listbox.winfo_height()
        margin = 12
        if event.y < margin:
            listbox.yview_scroll(-1, 'units')
        elif event.y > height - margin:
            listbox.yview_scroll(1, 'units')
        insert_idx = self._compute_insert_index(listbox, event.y)
        self._move_placeholder(listbox, insert_idx)
        return 'break'


    def _dnd_drop(self, event):
        if not self._drag_state['active']:
            return 'break'
        listbox: 'Listbox' = event.widget
        self._drag_state['active'] = False
        if not self._drag_state['indices']:
            return 'break'
        drop_idx_original = self._drag_state.get('placeholder_index')
        if drop_idx_original is None:
            drop_idx_original = self._compute_insert_index(listbox, event.y)
        self._remove_placeholder(listbox)
        sel_indices = list(listbox.curselection())
        sel_items = [listbox.get(i) for i in sel_indices]
        for i in reversed(sel_indices):
            listbox.delete(i)
        offset = sum(1 for i in sel_indices if i < drop_idx_original)
        drop_idx = max(0, drop_idx_original - offset)
        drop_idx = min(drop_idx, listbox.size())
        for n, item in enumerate(sel_items):
            listbox.insert(drop_idx + n, item)
        listbox.selection_clear(0, 'end')
        for n in range(len(sel_items)):
            listbox.selection_set(drop_idx + n)
        listbox.activate(drop_idx)
        try:
            listbox.config(cursor=self._drag_state.get('prev_cursor') or '')
        except Exception:
            pass
        return 'break'
