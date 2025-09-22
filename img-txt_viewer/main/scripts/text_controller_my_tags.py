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


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip


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
        self.hide_mytags_controls_var = BooleanVar(value=False)
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


    #region UI Build


    def create_tab8(self):
        # Context menu (handles both tree and listbox)
        def show_context_menu(event):
            widget: 'ttk.Treeview' | 'Listbox' = event.widget
            if widget == self.custom_dictionary_treeview:
                iid = widget.identify_row(event.y)
                if not widget.selection():
                    if iid:
                        widget.selection_set(iid)
                elif iid and iid not in widget.selection():
                    widget.selection_set(iid)

                def select_all():
                    widget.selection_set(widget.get_children())

                def invert_selection():
                    current = set(widget.selection())
                    all_iids = set(widget.get_children())
                    inverted = all_iids - current
                    widget.selection_remove(*current)
                    widget.selection_set(*inverted)

                menu = Menu(widget, tearoff=0)
                menu.add_command(label="Prefix", command=lambda: self.insert_selected_tags(widget, 'start'))
                menu.add_command(label="Append", command=lambda: self.insert_selected_tags(widget, 'end'))
                menu.add_separator()
                menu.add_command(label="Edit", command=self.edit_selected_tag_to_entry)
                menu.add_command(label="Remove", command=self.remove_selected_tags)
                menu.add_separator()
                menu.add_command(label="Move Up", command=lambda: self.move_selection(widget, 'up'))
                menu.add_command(label="Move Down", command=lambda: self.move_selection(widget, 'down'))
                menu.add_separator()
                menu.add_command(label="Selection: All", command=select_all)
                menu.add_command(label="Selection: Invert", command=invert_selection)
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

                if widget.curselection():
                    menu = Menu(widget, tearoff=0)
                    menu.add_command(label="Prefix", command=lambda: self.insert_selected_tags(widget, 'start'))
                    menu.add_command(label="Append", command=lambda: self.insert_selected_tags(widget, 'end'))
                    menu.add_separator()
                    menu.add_command(label="Add to MyTags", command=self.add_selected_alltags_to_mytags)
                    menu.add_separator()
                    menu.add_command(label="Refresh", command=self.refresh_all_tags_listbox)
                    menu.add_separator()
                    menu.add_command(label="Selection: All", command=select_all)
                    menu.add_command(label="Selection: Invert", command=invert_selection)
                    menu.tk_popup(event.x_root, event.y_root)

        # Interface
        self.create_custom_dictionary(refresh=False)

        tab_frame = Frame(self.app.tab8)
        tab_frame.pack(side='top', fill='both', expand=True)
        tab_frame.grid_rowconfigure(1, weight=1)
        tab_frame.grid_columnconfigure(0, weight=1)

        # Top Row
        top_frame = Frame(tab_frame)
        top_frame.grid(row=0, column=0, sticky='ew')

        help_btn = ttk.Button(top_frame, text="?", takefocus=False, width=2, command=self.show_my_tags_help)
        help_btn.pack(side='left')

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
        menu.add_command(label="Cleanup MyTags", command=self.cleanup_custom_dictionary)
        menu.add_command(label="Open MyTags File...", command=lambda: self.app.open_textfile(self.app.my_tags_csv))

        entry_frame = Frame(top_frame)
        entry_frame.pack(side='left', fill='x', expand=True, pady=4)

        self.tag_entry = ttk.Entry(entry_frame)
        self.tag_entry.pack(side='left', fill='x', expand=True)
        self.tag_entry.bind('<Return>', lambda event: (self.add_tag(self.tag_entry.get()), self.tag_entry.delete(0, 'end')))

        add_btn = ttk.Button(entry_frame, text="Add", command=lambda: (self.add_tag(self.tag_entry.get()), self.tag_entry.delete(0, 'end')))
        add_btn.pack(side='left')
        ToolTip.create(add_btn, "Add tag to 'My Tags'", 200, 6, 12)

        save_btn = ttk.Button(top_frame, text="Save Tags", takefocus=False, command=self.save_my_tags_file)
        save_btn.pack(side='right')
        ToolTip.create(save_btn, "Save changes to 'My Tags' file", 200, 6, 12)

        # Middle Row
        self.text_frame = ttk.PanedWindow(tab_frame, orient='horizontal')
        self.text_frame.grid(row=1, column=0, sticky='nsew')

        # My Tags section
        my_tags_frame = Frame(self.text_frame)
        self.text_frame.add(my_tags_frame, weight=1)
        my_tags_frame.grid_rowconfigure(1, weight=1)
        my_tags_frame.grid_columnconfigure(0, weight=1)

        top_frame = Frame(my_tags_frame)
        top_frame.grid(row=0, column=0, sticky='ew', padx=2, pady=(2, 0))
        ttk.Label(top_frame, text="My Tags:").pack(side='left', padx=(0, 5))

        self.custom_dictionary_treeview = ttk.Treeview(my_tags_frame, columns=('Tag',), show='headings', selectmode='extended', height=12)
        self.custom_dictionary_treeview.heading('Tag', text='Tag')
        self.custom_dictionary_treeview.grid(row=1, column=0, sticky='nsew')
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
        ToolTip.create(add_btn, "Add selected tags to 'My Tags'", 200, 6, 12)
        append_btn = ttk.Button(self.alltags_btn_frame, text="Append", command=lambda: self.insert_selected_tags(self.alltags_listbox, 'end'))
        append_btn.grid(row=0, column=2, sticky='ew', padx=2)

        self.load_my_tags_file()
        self.refresh_custom_dictionary()


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
        try:
            with open(self.app.my_tags_csv, 'r', encoding='utf-8') as file:
                content = self.remove_extra_newlines(file.read())
        except Exception:
            content = ''
        for line in content.split('\n'):
            tag = line.strip()
            if tag:
                self.custom_dictionary_treeview.insert('', 'end', values=(tag,))


    def save_my_tags_file(self):
        if not self.custom_dictionary_treeview:
            return
        tags = [self.custom_dictionary_treeview.item(iid)['values'][0] for iid in self.custom_dictionary_treeview.get_children()]
        content = '\n'.join(tags) + ('\n' if tags else '')
        try:
            with open(self.app.my_tags_csv, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tags file:\n{e}")
            return
        self.root.after(100, self.refresh_custom_dictionary)


    def add_tag(self, tag_text: str):
        if not self.custom_dictionary_treeview:
            return
        tag = (tag_text or '').strip()
        if tag:
            existing = set(self.custom_dictionary_treeview.item(iid)['values'][0] for iid in self.custom_dictionary_treeview.get_children())
            if tag not in existing:
                self.custom_dictionary_treeview.insert('', 'end', values=(tag,))


    def remove_selected_tags(self):
        if not self.custom_dictionary_treeview:
            return
        selected = self.custom_dictionary_treeview.selection()
        for iid in selected:
            self.custom_dictionary_treeview.delete(iid)


    def edit_selected_tag_to_entry(self):
        if not self.custom_dictionary_treeview or not self.tag_entry:
            return
        selected = self.custom_dictionary_treeview.selection()
        if not selected:
            return
        iid = selected[0]
        tag = self.custom_dictionary_treeview.item(iid)['values'][0]
        self.tag_entry.delete(0, 'end')
        self.tag_entry.insert(0, tag)
        self.custom_dictionary_treeview.delete(iid)


    def move_selection(self, treeview: 'ttk.Treeview', direction: str):
        selected = treeview.selection()
        if not selected:
            return
        items = list(treeview.get_children())
        delta = -1 if direction == 'up' else 1
        for iid in (selected if direction == 'up' else reversed(selected)):
            idx = items.index(iid)
            new_idx = idx + delta
            if 0 <= new_idx < len(items):
                treeview.move(iid, '', new_idx)
                treeview.selection_set(iid)


    def add_selected_alltags_to_mytags(self):
        if not self.alltags_listbox or not self.custom_dictionary_treeview:
            return
        selected_indices = self.alltags_listbox.curselection()
        if not selected_indices:
            return
        existing = set(self.custom_dictionary_treeview.item(iid)['values'][0] for iid in self.custom_dictionary_treeview.get_children())
        for idx in selected_indices:
            tag = self.alltags_listbox.get(idx)
            if tag not in existing:
                self.custom_dictionary_treeview.insert('', 'end', values=(tag,))


    def refresh_all_tags_listbox(self, tags=None):
        listbox = self.alltags_listbox
        if tags is None:
            self.app.stat_calculator.calculate_file_stats()
            tags = self.app.stat_calculator.sorted_captions
        listbox.delete(0, 'end')
        for tag, count in tags:
            listbox.insert('end', tag)


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
        with open(self.app.my_tags_csv, 'r', encoding='utf-8') as file:
            content = self.remove_extra_newlines(file.read())
            tags = [tag.strip() for tag in content.split('\n') if tag.strip()]
            treeview = self.custom_dictionary_treeview
            # Clear existing items
            for item in treeview.get_children():
                treeview.delete(item)
            # Insert tags into Treeview
            for tag in tags:
                treeview.insert('', 'end', values=(tag,))
            self.app.autocomplete.update_autocomplete_dictionary()


    def create_custom_dictionary(self, reset=False, refresh=True):
        try:
            csv_filename = self.app.my_tags_csv
            if reset or not os.path.isfile(csv_filename):
                with open(csv_filename, 'w', newline='', encoding="utf-8") as file:
                    file.write("")
                if refresh:
                    self.refresh_custom_dictionary()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: create_custom_dictionary()", f"An error occurred while creating the custom dictionary file:\n\n{csv_filename}\n\n{e}")


    def remove_extra_newlines(self, text: "str"):
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if line.strip() != '']
        result = '\n'.join(cleaned_lines)
        if not result.endswith('\n'):
            result += '\n'
        return result


    def cleanup_custom_dictionary(self):
        try:
            if not os.path.isfile(self.app.my_tags_csv):
                return
            with open(self.app.my_tags_csv, 'r', encoding='utf-8') as file:
                content = file.read()
            lines = content.split('\n')
            cleaned_lines = []
            seen = set()
            for line in lines:
                cleaned_line = line.replace('"', '').replace("'", "").strip()
                if cleaned_line and cleaned_line not in seen:
                    seen.add(cleaned_line)
                    cleaned_lines.append(cleaned_line)
            cleaned_content = '\n'.join(cleaned_lines) + '\n'
            with open(self.app.my_tags_csv, 'w', encoding='utf-8') as file:
                file.write(cleaned_content)
            self.refresh_custom_dictionary()
            messagebox.showinfo("Success", "Custom dictionary has been cleaned.")
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: cleanup_custom_dictionary()", f"An error occurred while cleaning the custom dictionary:\n\n{e}")


    def add_to_custom_dictionary(self, origin):
        try:
            if origin == "text_box":
                selected_text = self.app.text_box.get("sel.first", "sel.last")
            elif origin == "auto_tag":
                selected_text = self.app.text_controller.autotag_listbox.get("active")
                selected_text = selected_text.split(':', 1)[-1].strip()
            with open(self.app.my_tags_csv, 'a', encoding="utf-8") as f:
                f.write(selected_text.strip() + "\n")
            self.refresh_custom_dictionary()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: add_to_custom_dictionary()", f"An error occurred while saving the selected to 'my_tags.csv'.\n\n{e}")


    #endregion
    #region Helpers


    def _split_csv(self, text: str):
        return [t.strip() for t in text.split(',') if t.strip()]


    def _join_csv(self, parts):
        return ', '.join([p for p in parts if p])


    def _get_selected_tags(self, widget):
        # Treeview
        if hasattr(widget, 'selection') and callable(getattr(widget, 'selection')):
            selected = widget.selection()
            return [widget.item(iid)['values'][0] for iid in selected] if selected else []
        # Listbox
        if hasattr(widget, 'curselection') and callable(getattr(widget, 'curselection')):
            indices = widget.curselection()
            return [widget.get(i) for i in indices] if indices else []
        return []


    #endregion
    #region DnD


    def _compute_insert_index(self, tree: 'ttk.Treeview', y: int) -> int:
        items = list(tree.get_children(''))
        # Exclude placeholder if present
        ph_iid = self._drag_state.get('placeholder_iid')
        items_wo = [iid for iid in items if iid != ph_iid]
        size = len(items_wo)
        if size <= 0:
            return 0
        over_iid = tree.identify_row(y)
        # If outside any row, decide top/bottom by position
        if not over_iid:
            first_bbox = tree.bbox(items_wo[0])
            last_bbox = tree.bbox(items_wo[-1])
            if last_bbox and y >= (last_bbox[1] + last_bbox[3]):
                return size
            if first_bbox and y <= first_bbox[1]:
                return 0
            return size
        # If hovering placeholder, use its own midpoint
        if ph_iid and over_iid == ph_iid:
            bbox = tree.bbox(over_iid)
            idx = tree.index(over_iid)
            if bbox and y > (bbox[1] + bbox[3] / 2):
                return min(idx + 1, len(items)) - (1 if ph_iid in items and tree.index(ph_iid) < idx + 1 else 0)
            else:
                # Adjust to ignore placeholder itself
                return idx - (1 if ph_iid in items and tree.index(ph_iid) <= idx else 0)
        # Normal row hovered
        # Base index relative to list without placeholder
        try:
            base_idx = items_wo.index(over_iid)
        except ValueError:
            base_idx = 0
        bbox = tree.bbox(over_iid)
        insert_idx = base_idx
        if bbox is not None:
            if y > (bbox[1] + bbox[3] / 2):
                insert_idx = base_idx + 1
        if insert_idx < 0:
            insert_idx = 0
        if insert_idx > size:
            insert_idx = size
        return insert_idx


    def _remove_placeholder(self, tree: 'ttk.Treeview'):
        ph_iid = self._drag_state.get('placeholder_iid')
        if ph_iid:
            try:
                tree.delete(ph_iid)
            except Exception:
                pass
        self._drag_state['placeholder_iid'] = None


    def _insert_placeholder(self, tree: 'ttk.Treeview', insert_idx: int):
        self._remove_placeholder(tree)
        items = list(tree.get_children(''))
        size = len([iid for iid in items if iid != self._drag_state.get('placeholder_iid')])
        try:
            tree.tag_configure('placeholder', background=self._placeholder_bg)
        except Exception:
            pass
        if insert_idx >= size:
            ph_iid = tree.insert('', 'end', values=('',), tags=('placeholder',))
        else:
            ph_iid = tree.insert('', insert_idx, values=('',), tags=('placeholder',))
        self._drag_state['placeholder_iid'] = ph_iid


    def _move_placeholder(self, tree: 'ttk.Treeview', insert_idx: int):
        items = list(tree.get_children(''))
        # Exclude placeholder in size calculation
        ph_iid = self._drag_state.get('placeholder_iid')
        items_wo = [iid for iid in items if iid != ph_iid]
        size = len(items_wo)
        target_idx = insert_idx if insert_idx < size else size
        if ph_iid and ph_iid in items:
            current_idx = tree.index(ph_iid)
            # Adjust target against current placeholder position
            if (target_idx == size and current_idx == len(items) - 1) or current_idx == target_idx:
                return
            try:
                tree.move(ph_iid, '', target_idx)
                return
            except Exception:
                pass
        self._insert_placeholder(tree, target_idx)


    def _dnd_start(self, event):
        tree: 'ttk.Treeview' = event.widget
        if tree is not self.custom_dictionary_treeview:
            return
        over_iid = tree.identify_row(event.y)
        if not over_iid:
            return 'break'
        if over_iid not in tree.selection():
            tree.selection_set(over_iid)
        # Order selected items as they appear in the tree
        ordered = [iid for iid in tree.get_children('') if iid in set(tree.selection())]
        if not ordered:
            return 'break'
        self._drag_state['active'] = True
        self._drag_state['selected_iids'] = tuple(ordered)
        self._drag_state['start_iid'] = over_iid
        tree.focus(over_iid)
        self._drag_state['prev_cursor'] = tree.cget('cursor')
        try:
            tree.config(cursor='hand2')
        except Exception:
            pass
        insert_idx = self._compute_insert_index(tree, event.y)
        self._move_placeholder(tree, insert_idx)
        return 'break'


    def _dnd_motion(self, event):
        if not self._drag_state['active']:
            return 'break'
        tree: 'ttk.Treeview' = event.widget
        height = tree.winfo_height()
        margin = 12
        if event.y < margin:
            tree.yview_scroll(-1, 'units')
        elif event.y > height - margin:
            tree.yview_scroll(1, 'units')
        insert_idx = self._compute_insert_index(tree, event.y)
        self._move_placeholder(tree, insert_idx)
        return 'break'


    def _dnd_drop(self, event):
        if not self._drag_state['active']:
            return 'break'
        tree: 'ttk.Treeview' = event.widget
        self._drag_state['active'] = False
        selected = list(self._drag_state.get('selected_iids') or ())
        if not selected:
            return 'break'
        all_items = list(tree.get_children(''))
        ph_iid = self._drag_state.get('placeholder_iid')
        # Determine raw drop index among all items (including selected, excluding none or including placeholder)
        if ph_iid and ph_iid in all_items:
            drop_idx_original = tree.index(ph_iid)
        else:
            drop_idx_original = self._compute_insert_index(tree, event.y)
        # Prepare lists and maps
        sel_set = set(selected)
        ordered_selected = [iid for iid in all_items if iid in sel_set]
        # Others excludes selected and placeholder
        others = [iid for iid in all_items if iid not in sel_set and iid != ph_iid]
        index_map = {iid: idx for idx, iid in enumerate(all_items)}
        # Convert drop index to index within 'others' by removing selected before it
        offset_before = sum(1 for iid in ordered_selected if index_map[iid] < drop_idx_original)
        drop_idx_others = max(0, min(len(others), drop_idx_original - offset_before))
        # Clean placeholder now that we have computed indices
        self._remove_placeholder(tree)
        # If dropping into the same spot (within the selected block), no-op
        if ordered_selected:
            sel_start = min(index_map[iid] for iid in ordered_selected)
            sel_end = max(index_map[iid] for iid in ordered_selected) + 1
            start_in_others = sum(1 for iid in others if index_map[iid] < sel_start)
            # end_in_others would be the same because others excludes selected
            if drop_idx_others == start_in_others:
                try:
                    tree.config(cursor=self._drag_state.get('prev_cursor') or '')
                except Exception:
                    pass
                self._drag_state['selected_iids'] = tuple()
                self._drag_state['start_iid'] = None
                return 'break'
        # Determine anchor to insert before; if at end, anchor is None
        anchor_iid = None
        if drop_idx_others < len(others):
            anchor_iid = others[drop_idx_others]
        # Move selected items as a group preserving order
        try:
            if anchor_iid is None:
                for iid in ordered_selected:
                    tree.move(iid, '', 'end')
            else:
                for iid in ordered_selected:
                    tree.move(iid, '', tree.index(anchor_iid))
        except Exception:
            pass
        # Restore selection and focus
        try:
            tree.selection_set(ordered_selected)
            tree.focus(ordered_selected[0])
        except Exception:
            pass
        try:
            tree.config(cursor=self._drag_state.get('prev_cursor') or '')
        except Exception:
            pass
        # Clear state
        self._drag_state['selected_iids'] = tuple()
        self._drag_state['start_iid'] = None
        return 'break'


    #endregion


#endregion
