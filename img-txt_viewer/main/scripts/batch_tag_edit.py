#region Imports


# Standard Library
from collections import Counter
import re


# Standard Library - GUI
from tkinter import (
    ttk, Tk, messagebox,
    Frame, Menu, Label,
    font, Scrollbar,
    BooleanVar,
)

# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as Tip


# Custom Libraries
from main.scripts import TagEditor, help_window, HelpText, custom_simpledialog
import main.scripts.entry_helper as entry_helper


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region BatchTagEdit


class BatchTagEdit:
    def __init__(self):
        # Inherited Variables
        self.parent: 'Main' = None
        self.root: 'Tk' = None
        self.text_files = None
        self.working_dir = None
        self.batch_tag_edit_frame = None
        self.help_window = None
        # Local Variables
        self.tag_counts = 0
        self.total_unique_tags = 0
        self.visible_tags = 0
        self.selected_tags = 0
        self.pending_delete = 0
        self.pending_edit = 0
        # Sorting state dictionary
        self.tree_sort_dict = {
            "option": "Frequency",  # "Frequency", "Name", or "Length"
            "reverse": False
        }
        self.tag_tooltip = None
        self._tree_tooltip_text = None
        self.long_tag_tooltip_threshold = 64


    def set_working_directory(self, working_dir=None):
        """Updates the working directory and refreshes the UI with new tag data.
        Args:
            working_dir (str): Path to the new working directory
        """
        # Update working directory
        if working_dir:
            self.working_dir = working_dir
        else:
            self.working_dir = self.parent.image_dir.get()
        self.text_files = self.parent.text_files
        # Reset UI state variables
        self.tag_counts = 0
        self.total_unique_tags = 0
        self.visible_tags = 0
        self.selected_tags = 0
        self.pending_delete = 0
        self.pending_edit = 0
        self.original_tags = []
        # Clear UI elements
        if hasattr(self, "tag_tree") and self.tag_tree is not None:
            self.tag_tree.delete(*self.tag_tree.get_children())
        if hasattr(self, "filter_entry") and self.filter_entry is not None:
            self.filter_entry.delete(0, "end")
        if hasattr(self, "edit_entry") and self.edit_entry is not None:
            self.edit_entry.delete(0, "end")
        # Get tags and update UI
        tag_dict = self.get_tags()
        self.tag_counts, self.total_unique_tags = self.count_file_tags(tag_dict)
        self.sort_tags(self.tag_counts.items())
        self.toggle_filter_widgets()


#endregion
#region GUI Setup


    def setup_window(self, parent, root):
        self.parent = parent
        self.root = root
        self.text_files = self.parent.text_files
        self.working_dir = self.parent.image_dir.get()
        self.batch_tag_edit_frame = None
        self.help_window = help_window.HelpWindow(self.root)
        tag_dict = self.get_tags()
        self.tag_counts, self.total_unique_tags = self.count_file_tags(tag_dict)
        self.original_tags = []
        self.create_ui()
        self.sort_tags(self.tag_counts.items())


    def create_ui(self):
        self.setup_primary_frame()
        self.setup_option_frame()
        self.setup_treeview_frame()
        self.setup_bottom_frame()
        self.count_treeview_tags()


    def setup_primary_frame(self):
        # Primary Frame
        self.batch_tag_edit_frame = self.parent.batch_tag_edit_tab
        self.batch_tag_edit_frame.grid_columnconfigure(0, weight=1)
        self.batch_tag_edit_frame.grid_columnconfigure(1, weight=1)
        self.batch_tag_edit_frame.grid_rowconfigure(2, weight=1)
        self.batch_tag_edit_frame.grid_rowconfigure(3, weight=0)


    def setup_option_frame(self):
        # Frame
        self.option_frame = Frame(self.batch_tag_edit_frame)
        self.option_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.option_frame.grid_columnconfigure(0, weight=1)
        self.option_frame.grid_rowconfigure(0, weight=0)
        # Frame
        self.sort_filter_frame = Frame(self.option_frame)
        self.sort_filter_frame.grid(row=0, column=0, sticky="ew")
        self.sort_filter_frame.grid_columnconfigure(0, weight=1)
        self.setup_filter_frame()
        self.setup_edit_frame()


    def setup_filter_frame(self):
        # Frame
        filter_frame = Frame(self.sort_filter_frame)
        filter_frame.grid(row=1, column=0, sticky="ew")
        filter_frame.grid_columnconfigure(2, weight=1)
        # Label
        self.filter_label = ttk.Label(filter_frame, text="Filter:", width=6)
        self.filter_label.grid(row=0, column=0, sticky="w")
        Tip.create(widget=self.filter_label, text="All options except <, and >, support multiple values separated by commas.\n\nTag : Filter tags by the input text\n!Tag : Filter tags that do not contain the input text\n== : Filter tags equal to the given value\n!= : Filter tags not equal to the given value\n< : Filter tags less than the given value\n> : Filter tags greater than the given value")
        filter_options = [
            ("Tag", "Contains Text"),
            ("!Tag", "Does Not Contain"),
            ("==", "Count Equals"),
            ("!=", "Count Not Equals"),
            ("<", "Count Less Than"),
            (">", "Count Greater Than")
        ]
        self.filter_option_map = {desc: key for key, desc in filter_options}
        filter_descriptions = [desc for _, desc in filter_options]
        self.filter_combobox = ttk.Combobox(filter_frame, values=filter_descriptions, state="readonly")
        self.filter_combobox.set("Contains Text")
        self.filter_combobox.grid(row=0, column=1, sticky="e")
        self.filter_combobox.bind("<<ComboboxSelected>>", lambda event: self.warn_before_action(action="filter"))
        # Entry
        self.filter_entry = ttk.Entry(filter_frame)
        self.filter_entry.grid(row=0, column=2, sticky="ew")
        self.filter_entry.bind("<KeyRelease>", lambda event: self.warn_before_action(action="filter"))
        entry_helper.bind_helpers(self.filter_entry)
        # Button
        self.filter_apply_button = ttk.Button(filter_frame, text="Apply", width=8, command=lambda: self.warn_before_action(action="filter"))
        self.filter_apply_button.grid(row=0, column=3, sticky="e")
        Tip.create(widget=self.filter_apply_button, text="Apply tag list filter", justify="left")


    def setup_edit_frame(self):
        # Frame
        edit_frame = Frame(self.option_frame)
        edit_frame.grid(row=2, column=0, sticky="ew")
        edit_frame.columnconfigure(0, weight=1)
        # Edit frame
        edit_row_frame = ttk.Frame(edit_frame)
        edit_row_frame.grid(row=0, column=0, sticky="ew")
        edit_row_frame.columnconfigure(1, weight=1)
        # Label
        edit_label = ttk.Label(edit_row_frame, text="Edit:", width=6)
        edit_label.grid(row=0, column=0, sticky="w")
        Tip.create(widget=edit_label, text="Select an option and enter text to add a pending change", justify="left")
        # Entry
        self.edit_entry = ttk.Entry(edit_row_frame)
        self.edit_entry.grid(row=0, column=1, sticky="ew")
        self.edit_entry.bind("<Return>", self.apply_commands_to_tree)
        entry_helper.bind_helpers(self.edit_entry)
        # Button
        edit_apply_button = ttk.Button(edit_row_frame, text="Apply", width=8, command=self.apply_commands_to_tree)
        edit_apply_button.grid(row=0, column=2, sticky="e")
        Tip.create(widget=edit_apply_button, text="Add to pending changes.")


    def setup_treeview_frame(self):
        # Frame
        tree_frame = Frame(self.batch_tag_edit_frame)
        tree_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        # Treeview
        self.tag_tree = ttk.Treeview(tree_frame, columns=("count", "action", "tag", "new_tag"), show="headings")
        self.tag_tree.heading("count", text="Count", command=lambda: self.on_treeview_heading_click("count"))
        self.tag_tree.heading("action", text="Action", anchor="w")
        self.tag_tree.heading("tag", text="Tag", anchor="w", command=lambda: self.on_treeview_heading_click("tag"))
        self.tag_tree.heading("new_tag", text="New Tag", anchor="w")
        self.tag_tree.column("count", width=60, anchor="center", stretch=False)
        self.tag_tree.column("action", width=60, anchor="w", stretch=False)
        self.tag_tree.column("tag", width=200, anchor="w", stretch=True)
        self.tag_tree.column("new_tag", width=200, anchor="w", stretch=True)
        self.tag_tree.grid(row=0, column=0, sticky="nsew")
        self.tag_tree.bind("<Control-c>", self.copy_tree_selection)
        self.tag_tree.bind("<Button-3>", self.show_tree_context_menu)
        self.tag_tree.bind("<<TreeviewSelect>>", self.count_treeview_tags)
        self.tag_tree.bind("<Double-Button-1>", self._on_tree_double_left_click)
        self.tag_tree.bind("<Motion>", self.on_tree_motion, add="+")
        self.tag_tree.bind("<Leave>", self._disable_tag_tooltip, add="+")
        self.tag_tree.bind("<Control-a>", lambda event: self.tree_selection("all"))
        self.tag_tree.bind("<Control-i>", lambda event: self.tree_selection("invert"))
        self.tag_tree.bind("<Escape>", lambda event: self.tree_selection("clear"))
        # Scrollbar
        vert_scrollbar = Scrollbar(tree_frame, orient="vertical", command=self.tag_tree.yview)
        vert_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tag_tree.configure(yscrollcommand=vert_scrollbar.set)
        self.tag_tooltip = Tip.create(widget=self.tag_tree, text="", state="disabled", wraplength=400, origin="mouse", follow_mouse=True, show_delay=200)


    def setup_bottom_frame(self):
        # Frame
        bottom_frame = Frame(self.batch_tag_edit_frame)
        bottom_frame.grid(row=3, column=0, columnspan=99, sticky="nsew", pady=(3,0))
        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=0)
        # Labels
        labels_frame = Frame(bottom_frame)
        labels_frame.grid(row=0, column=0, sticky="ew")
        self.total_label = Label(labels_frame, anchor="w", text=f"Total: {self.total_unique_tags}", relief="groove", width=15)
        self.total_label.pack(side="left", padx=1)
        self.visible_label = Label(labels_frame, anchor="w", text=f"Filtered: {self.visible_tags}", relief="groove", width=15)
        self.visible_label.pack(side="left", padx=1)
        self.selected_label = Label(labels_frame, anchor="w", text=f"Selected: {self.selected_tags}", relief="groove", width=15)
        self.selected_label.pack(side="left", padx=1)
        self.pending_delete_label = Label(labels_frame, anchor="w", text=f"Delete: {self.pending_delete}", relief="groove", width=15)
        self.pending_delete_label.pack(side="left", padx=1)
        self.pending_edit_label = Label(labels_frame, anchor="w", text=f"Edit: {self.pending_edit}", relief="groove", width=15)
        self.pending_edit_label.pack(side="left", padx=1)
        # Buttons
        buttons_frame = Frame(bottom_frame)
        buttons_frame.grid(row=0, column=1, sticky="e")
        # Commit button
        self.button_save = ttk.Button(buttons_frame, text="Commit Changes", state="disabled", command=self.apply_tag_edits)
        self.button_save.pack(side="right")
        self.button_save_tip = Tip.create(widget=self.button_save, text="Commit pending changes to text files", show_delay=50, state="disabled")
        # Refresh button
        refresh_button = ttk.Button(buttons_frame, text="Refresh", width=8, command=self.clear_filter)
        refresh_button.pack(side="right")
        Tip.create(widget=refresh_button, text="Refresh the tag list and clear any pending changes or filters", show_delay=50)
        # Help button
        help_button = ttk.Button(buttons_frame, text="?", width=2, command=self.open_help_window)
        help_button.pack(side="right")
        Tip.create(widget=help_button, text="Show/Hide Help", show_delay=50)
        # Actions Menubutton
        self.actions_menu = Menu(buttons_frame, tearoff=0)
        self.actions_menu.add_command(label="Convert to Lowercase", command=lambda: self.transform_selected_tags("lower"))
        self.actions_menu.add_command(label="Convert to Uppercase", command=lambda: self.transform_selected_tags("upper"))
        self.actions_menu.add_command(label="Convert to Title Case", command=lambda: self.transform_selected_tags("title"))
        self.actions_menu.add_separator()
        self.actions_menu.add_command(label="Convert Spaces to Underscores", command=lambda: self.transform_selected_tags("spaces_to_underscores"))
        self.actions_menu.add_command(label="Convert Underscores to Spaces", command=lambda: self.transform_selected_tags("underscores_to_spaces"))
        self.actions_menu.add_separator()
        self.actions_menu.add_command(label="Remove Escape Characters Around Parentheses/Brackets", command=lambda: self.transform_selected_tags("remove_escape"))
        self.actions_menu.add_command(label="Remove Non-Alphanumeric Characters", command=lambda: self.transform_selected_tags("remove_non_alphanumeric"))
        self.actions_menu.add_command(label="Remove Punctuation", command=lambda: self.transform_selected_tags("remove_punctuation"))
        self.actions_menu.add_command(label="Remove Digits", command=lambda: self.transform_selected_tags("remove_digits"))
        self.actions_menu.add_separator()
        self.actions_menu.add_command(label="Add Escape Characters Around Parentheses/Brackets", command=lambda: self.transform_selected_tags("add_escape"))
        actions_menubutton = ttk.Menubutton(buttons_frame, text="Actions", menu=self.actions_menu, width=8)
        actions_menubutton.pack(side="right")
        actions_menubutton["menu"] = self.actions_menu
        Tip.create(widget=actions_menubutton, text="Common tag editing actions.\nApplies to selected tags", justify="left")
        # Options Menubutton
        self.double_click_to_edit_var = BooleanVar(value=True)
        options_menu = Menu(buttons_frame, tearoff=0)
        options_menu.add_radiobutton(label="Double-Click to Edit", variable=self.double_click_to_edit_var, value=True)
        options_menu.add_radiobutton(label="Double-Click to Delete", variable=self.double_click_to_edit_var, value=False)
        options_menubutton = ttk.Menubutton(buttons_frame, text="Options", menu=options_menu, width=8)
        options_menubutton.pack(side="right")
        options_menubutton["menu"] = options_menu
        Tip.create(widget=options_menubutton, text="Additional options and settings", justify="left")



#endregion
#region Treeview interaction


    def show_tree_context_menu(self, event):
        tree = event.widget
        if not tree.selection():
            return
        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="Copy", command=self.copy_tree_selection)
        context_menu.add_command(label="Delete", command=lambda: self.apply_commands_to_tree(delete=True))
        context_menu.add_command(label="Edit...", command=self.context_menu_edit_tag)
        context_menu.add_separator()
        context_menu.add_cascade(label="Quick Actions", menu=self.actions_menu)
        context_menu.add_separator()
        selection_menu = Menu(context_menu, tearoff=0)
        selection_menu.add_command(label="Select All", command=lambda: self.tree_selection("all"))
        selection_menu.add_command(label="Invert Selection", command=lambda: self.tree_selection("invert"))
        selection_menu.add_command(label="Clear Selection", command=lambda: self.tree_selection("clear"))
        context_menu.add_cascade(label="Selection", menu=selection_menu)
        context_menu.add_separator()
        context_menu.add_command(label="Revert Selection", command=self.revert_tree_changes)
        context_menu.add_command(label="Revert All", command=self.clear_filter)
        context_menu.post(event.x_root, event.y_root)


    def apply_commands_to_tree(self, event=None, delete=False, edit=None):
        selected_iids = self.tag_tree.selection()
        selected_indices = [self.tag_tree.index(iid) for iid in selected_iids]
        selected_items = [self.original_tags[i][0] for i in selected_indices if i < len(self.original_tags)]
        if edit is None:
            edit = self.edit_entry.get()
        if edit == "":
            delete = True
        for iid, original_tag in zip(reversed(selected_iids), reversed(selected_items)):
            values = list(self.tag_tree.item(iid, "values"))
            if not values:
                continue
            count_value = values[0]
            if delete:
                self.tag_tree.item(iid, values=(count_value, "Delete", original_tag, ""))
                self.tag_tree.tag_configure("deleted", foreground="red", background="#ffe5e5")
                self.tag_tree.item(iid, tags=("deleted",))
            else:
                new_value = edit
                if new_value == original_tag:
                    self.tag_tree.item(iid, values=(count_value, "", original_tag, original_tag))
                    self.tag_tree.item(iid, tags=())
                else:
                    self.tag_tree.item(iid, values=(count_value, "Edit", original_tag, new_value))
                    self.tag_tree.tag_configure("edited", foreground="green", background="#e5ffe5")
                    self.tag_tree.item(iid, tags=("edited",))
        self.count_treeview_tags()


    def context_menu_edit_tag(self):
        initialvalue = None
        selection = self.tag_tree.selection()
        if len(selection) == 1:
            idx = self.tag_tree.index(selection[0])
            if idx < len(self.original_tags):
                initialvalue = self.original_tags[idx][0]
        edit_string = custom_simpledialog.askstring("Edit Tag", "Enter new tag:", parent=self.root, initialvalue=initialvalue)
        if edit_string is not None:
            self.apply_commands_to_tree(edit=edit_string)


    def copy_tree_selection(self, event=None):
        selected_tags = []
        for iid in self.tag_tree.selection():
            idx = self.tag_tree.index(iid)
            values = self.tag_tree.item(iid, "values")
            if not values or idx >= len(self.original_tags):
                continue
            original_tag = self.original_tags[idx][0]
            new_tag = values[3] if len(values) > 3 else original_tag
            if new_tag == "":
                selected_tags.append(original_tag)
            elif new_tag != original_tag:
                selected_tags.append(new_tag)
            else:
                selected_tags.append(original_tag)
        self.root.clipboard_clear()
        self.root.clipboard_append(", ".join(selected_tags))


    def tree_selection(self, action):
        all_iids = self.tag_tree.get_children()
        if action == "all":
            self.tag_tree.selection_set(all_iids)
        elif action == "invert":
            selected = set(self.tag_tree.selection())
            new_selection = [iid for iid in all_iids if iid not in selected]
            self.tag_tree.selection_set(new_selection)
        elif action == "clear":
            self.tag_tree.selection_remove(all_iids)
        self.count_treeview_tags()


    def revert_tree_changes(self):
        padding_width = len(str(self.total_unique_tags))
        selected_iids = self.tag_tree.selection()
        for iid in selected_iids:
            idx = self.tag_tree.index(iid)
            if idx >= len(self.original_tags):
                continue
            original_tag, original_count = self.original_tags[idx]
            padded_count = str(original_count).zfill(padding_width)
            self.tag_tree.item(iid, values=(padded_count, "", original_tag, original_tag), tags=())
        self.count_treeview_tags()


    def on_treeview_heading_click(self, column):
        if column == "count":
            if self.tree_sort_dict["option"] == "Frequency":
                self.tree_sort_dict["reverse"] = not self.tree_sort_dict["reverse"]
            else:
                self.tree_sort_dict["option"] = "Frequency"
                self.tree_sort_dict["reverse"] = False
        elif column == "action":
            if self.tree_sort_dict["option"] == "Action":
                self.tree_sort_dict["reverse"] = not self.tree_sort_dict["reverse"]
            else:
                self.tree_sort_dict["option"] = "Action"
                self.tree_sort_dict["reverse"] = False
        elif column == "tag":
            # Cycle through: Name → Name (reverse) → Length → Length (reverse) → Name...
            tag_sort_modes = [("Name", False), ("Name", True), ("Length", False), ("Length", True)]
            current = (self.tree_sort_dict["option"], self.tree_sort_dict["reverse"])
            try:
                idx = tag_sort_modes.index(current)
                next_idx = (idx + 1) % len(tag_sort_modes)
            except ValueError:
                next_idx = 0
            self.tree_sort_dict["option"], self.tree_sort_dict["reverse"] = tag_sort_modes[next_idx]
        elif column == "new_tag":
            if self.tree_sort_dict["option"] == "NewTag":
                self.tree_sort_dict["reverse"] = not self.tree_sort_dict["reverse"]
            else:
                self.tree_sort_dict["option"] = "NewTag"
                self.tree_sort_dict["reverse"] = False
        self.sort_tags(self.original_tags)


    def on_tree_motion(self, event):
        if not hasattr(self, "tag_tree") or self.tag_tree is None or not self.tag_tooltip:
            return
        iid = self.tag_tree.identify_row(event.y)
        column = self.tag_tree.identify_column(event.x)
        if not iid or not column:
            self._disable_tag_tooltip()
            return
        try:
            column_index = int(column[1:]) - 1
        except (ValueError, TypeError):
            self._disable_tag_tooltip()
            return
        if column_index < 0:
            self._disable_tag_tooltip()
            return
        values = self.tag_tree.item(iid, "values")
        columns = self.tag_tree["columns"]
        if not values or column_index >= len(values) or column_index >= len(columns):
            self._disable_tag_tooltip()
            return
        column_name = columns[column_index]
        if column_name not in ("tag", "new_tag"):
            self._disable_tag_tooltip()
            return
        tag_text = values[column_index]
        if not tag_text or len(tag_text) < self.long_tag_tooltip_threshold:
            self._disable_tag_tooltip()
            return
        if self.tag_tooltip.state == "disabled" or tag_text != self._tree_tooltip_text:
            self.tag_tooltip.config(text=tag_text, state="normal")
            self._tree_tooltip_text = tag_text


    def _on_tree_double_left_click(self, event):
        self.auto_size_tree_column(event)
        if not self.tag_tree.selection():
            return
        if self.double_click_to_edit_var.get():
            self.context_menu_edit_tag()
        else:
            self.apply_commands_to_tree(None, True)


    def auto_size_tree_column(self, event=None):
        if event is None:
            col_id = "tag"
        else:
            region = self.tag_tree.identify_region(event.x, event.y)
            if region != "separator":
                return
            col = self.tag_tree.identify_column(event.x)
            if not col:
                return
            col_id = self.tag_tree["columns"][int(col[1:]) - 1]
        style = ttk.Style(self.tag_tree)
        treeview_font_name = style.lookup("Treeview", "font")
        if not treeview_font_name:
            treeview_font_name = "TkDefaultFont"
        tree_font = font.nametofont(treeview_font_name)
        max_width = 0
        heading_text = self.tag_tree.heading(col_id)["text"]
        max_width = tree_font.measure(heading_text)
        for iid in self.tag_tree.get_children():
            value = self.tag_tree.set(iid, col_id)
            width = tree_font.measure(str(value))
            if width > max_width:
                max_width = width
        max_width += 40
        self.tag_tree.column(col_id, width=max_width)



#endregion
#region Tag Editing


    def get_tags(self):
        tag_dict = TagEditor.extract_tags_from_files(self.parent.text_files)
        return tag_dict


    def count_file_tags(self, tags):
        tag_counts = Counter()
        for tag, positions in tags.items():
            tag_counts[tag] = len(positions)
        total_unique_tags = len(tag_counts)
        return tag_counts, total_unique_tags


    def refresh_counts(self):
        self.original_tags = []
        tag_dict = self.get_tags()
        self.tag_counts, self.total_unique_tags = self.count_file_tags(tag_dict)
        self.sort_tags(self.tag_counts.items())
        self.toggle_filter_widgets()


    def apply_tag_edits(self):
        if self.pending_delete or self.pending_edit:
            confirm = messagebox.askyesno("Save Changes", f"Commit pending changes to text files?\nThis action cannot be undone, you should make backups!\n\nPending Edits: {self.pending_edit}\nPending Deletes: {self.pending_delete}")
            if not confirm:
                return
        delete_tags = []
        edit_tags = {}
        target_files = self.parent.text_files
        for idx, iid in enumerate(self.tag_tree.get_children()):
            values = self.tag_tree.item(iid, "values")
            if not values or len(values) < 4 or idx >= len(self.original_tags):
                continue
            original_tag = self.original_tags[idx][0]
            new_tag = values[3]
            if new_tag == "":
                delete_tags.append(original_tag)
            elif new_tag != original_tag:
                edit_tags[original_tag] = new_tag
        if delete_tags:
            TagEditor.edit_tags(target_files, delete_tags, delete=True)
        if edit_tags:
            for original_tag, new_tag in edit_tags.items():
                TagEditor.edit_tags(target_files, [original_tag], edit=new_tag)
        self.clear_filter(warn=False)
        self.parent.refresh_text_box()


#endregion
#region Filter & Sort


    def warn_before_action(self, event=None, action=None):
        if self.pending_delete or self.pending_edit:
            if not messagebox.askyesno("Warning", "Adjusting this option will clear all pending changes. Continue?"):
                return
            self._reset_tag_changes()
        if action == "sort":
            self.sort_tags(self.tag_counts.items())
            # Correct usage: pass filter key and value
            filter_key = self.filter_option_map[self.filter_combobox.get()]
            filter_value = self.filter_entry.get()
            self.filter_tags(filter_key, filter_value)
        elif action == "filter":
            # Correct usage: pass filter key and value
            filter_key = self.filter_option_map[self.filter_combobox.get()]
            filter_value = self.filter_entry.get()
            self.filter_tags(filter_key, filter_value)


    def clear_filter(self, warn=True):
        if warn and (self.pending_delete or self.pending_edit):
            if not messagebox.askyesno("Warning", "Clear all pending changes.\n\nContinue?"):
                return
        if hasattr(self, "filter_entry") and self.filter_entry is not None:
            self.filter_entry.delete(0, "end")
        self.refresh_counts()


    def _reset_tag_changes(self):
        if not hasattr(self, "tag_tree") or self.tag_tree is None:
            return
        if not self.original_tags:
            return
        self.update_tree(list(self.original_tags), state={})


    def filter_tags(self, filter_option, filter_value):
        try:
            if not filter_value:
                filtered_tags = self.tag_counts.items()
            else:
                filter_values = [val.strip().lower() for val in filter_value.split(',') if val.strip()]
                filter_functions = {
                    "Tag": lambda tag, count: any(val in tag.lower() for val in filter_values),
                    "!Tag": lambda tag, count: all(val not in tag.lower() for val in filter_values),
                    "<": lambda tag, count: count < int(filter_values[0]),
                    ">": lambda tag, count: count > int(filter_values[0]),
                    "!=": lambda tag, count: all(count != int(val) for val in filter_values),
                    "==": lambda tag, count: any(count == int(val) for val in filter_values)
                }
                selected_key = filter_option
                filtered_tags = [(tag, count) for tag, count in self.tag_counts.items() if filter_functions[selected_key](tag, count)]
            self.sort_tags(filtered_tags)
        except ValueError:
            messagebox.showinfo("Error", "Invalid filter value. Please enter a number.")
            self.filter_entry.delete(0, "end")
            return


    def sort_tags(self, tags):
        pending_state = self._capture_tree_state()
        option = self.tree_sort_dict.get("option", "Frequency")
        reverse = self.tree_sort_dict.get("reverse", False)
        self._update_treeview_headings(option, reverse)
        tags = list(tags)
        if option == "Frequency":
            sorted_tags = sorted(tags, key=lambda tag: tag[1], reverse=not reverse)
        elif option == "Name":
            sorted_tags = sorted(tags, reverse=reverse)
        elif option == "Length":
            sorted_tags = sorted(tags, key=lambda tag: len(tag[0]), reverse=not reverse)
        elif option == "Action":
            def action_key(item):
                tag, _ = item
                new_value = pending_state.get(tag, tag)
                if new_value == "":
                    action_label = "Delete"
                elif new_value != tag:
                    action_label = "Edit"
                else:
                    action_label = ""
                priority = {"Delete": 0, "Edit": 1, "": 2}[action_label]
                return (priority, tag.lower(), str(new_value).lower())
            sorted_tags = sorted(tags, key=action_key, reverse=reverse)
        elif option == "NewTag":
            def new_tag_key(item):
                tag, _ = item
                new_value = pending_state.get(tag, tag)
                return (str(new_value).lower(), tag.lower())
            sorted_tags = sorted(tags, key=new_tag_key, reverse=reverse)
        else:
            sorted_tags = tags
        self.update_tree(sorted_tags, pending_state)


    def _update_treeview_headings(self, option, reverse):
        arrow_up = " ↑"
        arrow_down = " ↓"
        count_title = "Count"
        action_title = "Action"
        tag_title = "Tag"
        new_tag_title = "New Tag"
        # Determine which column is sorted and direction
        if option == "Frequency":
            count_title += arrow_up if not reverse else arrow_down
        elif option == "Name":
            tag_title += arrow_up if not reverse else arrow_down
        elif option == "Length":
            tag_title += f" (Len){arrow_up if not reverse else arrow_down}"
        elif option == "Action":
            action_title += arrow_up if not reverse else arrow_down
        elif option == "NewTag":
            new_tag_title += arrow_up if not reverse else arrow_down
        # Set headings
        self.tag_tree.heading("count", text=count_title, anchor="center", command=lambda: self.on_treeview_heading_click("count"))
        self.tag_tree.heading("action", text=action_title, anchor="w", command=lambda: self.on_treeview_heading_click("action"))
        self.tag_tree.heading("tag", text=tag_title, anchor="w", command=lambda: self.on_treeview_heading_click("tag"))
        self.tag_tree.heading("new_tag", text=new_tag_title, anchor="w", command=lambda: self.on_treeview_heading_click("new_tag"))


    def toggle_filter_widgets(self, event=None):
        try:
            widgets = [
                self.filter_label,
                self.filter_combobox,
                self.filter_entry,
                self.filter_apply_button
            ]
            state = "disabled" if self.pending_delete or self.pending_edit else "normal"
            for widget in widgets:
                if isinstance(widget, ttk.Combobox):
                    widget.configure(state="readonly" if state == "normal" else state)
                else:
                    widget.configure(state=state)
        except AttributeError:
            pass


#endregion
#region Treeview Helpers


    def update_tree(self, tags, state=None):
        if state is None:
            state = {}
        self.tag_tree.delete(*self.tag_tree.get_children())
        tags = list(tags)
        padding_width = len(str(self.total_unique_tags))
        self.original_tags = tags
        self.tag_tree.tag_configure("deleted", foreground="red", background="#ffe5e5")
        self.tag_tree.tag_configure("edited", foreground="green", background="#e5ffe5")
        for tag, count in tags:
            padded_count = str(count).zfill(padding_width)
            new_tag_value = state.get(tag, tag)
            if new_tag_value == "":
                item_tags = ("deleted",)
                action_label = "Delete"
            elif new_tag_value != tag:
                item_tags = ("edited",)
                action_label = "Edit"
            else:
                item_tags = ()
                action_label = ""
            self.tag_tree.insert("", "end", values=(padded_count, action_label, tag, new_tag_value), tags=item_tags)
        self.count_treeview_tags()
        if self.tag_tooltip:
            self._disable_tag_tooltip()
        return tags


    def count_treeview_tags(self, event=None):
        tag_tree = self.tag_tree
        original_tags = self.original_tags
        get_children = tag_tree.get_children
        get_item = tag_tree.item
        get_index = tag_tree.index
        pending_delete = 0
        pending_edit = 0
        children = list(get_children())
        num_children = len(children)
        for idx, iid in enumerate(children):
            values = get_item(iid, "values")
            if not values or len(values) < 4 or idx >= len(original_tags):
                continue
            original_tag = original_tags[idx][0]
            new_tag = values[3] if len(values) > 3 else original_tag
            if new_tag == "":
                pending_delete += 1
            elif new_tag != original_tag:
                pending_edit += 1
        visible_tags = num_children
        selected_iids = tag_tree.selection()
        selected_tags = len(selected_iids)
        # Only update UI if values have changed
        if getattr(self, "pending_delete", None) != pending_delete:
            self.pending_delete = pending_delete
        if getattr(self, "pending_edit", None) != pending_edit:
            self.pending_edit = pending_edit
        if getattr(self, "visible_tags", None) != visible_tags:
            self.visible_tags = visible_tags
        if getattr(self, "selected_tags", None) != selected_tags:
            self.selected_tags = selected_tags
        # Update labels
        self.total_label.config(text=f"Total: {self.total_unique_tags} ")
        self.visible_label.config(text=f"Filtered: {visible_tags} ")
        self.selected_label.config(text=f"Selected: {selected_tags} ")
        bg_normal = self.batch_tag_edit_frame.cget("background")
        if pending_delete > 0:
            self.pending_delete_label.config(text=f"Delete: {pending_delete} ", foreground="red", background="#ffe5e5")
        else:
            self.pending_delete_label.config(text=f"Delete: {pending_delete} ", foreground="black", background=bg_normal)
        if pending_edit > 0:
            self.pending_edit_label.config(text=f"Edit: {pending_edit} ", foreground="green", background="#e5ffe5")
        else:
            self.pending_edit_label.config(text=f"Edit: {pending_edit} ", foreground="black", background=bg_normal)
        # Enable/disable buttons only if state changes
        if pending_delete > 0 or pending_edit > 0:
            self.button_save.config(state="normal")
            self.button_save_tip.config(state="normal")
        else:
            self.button_save.config(state="disabled")
            self.button_save_tip.config(state="disabled")
        self.toggle_filter_widgets()
        # Only update edit_entry if needed
        if hasattr(self, "edit_entry") and self.edit_entry is not None:
            edit_entry = self.edit_entry
            if len(selected_iids) == 1:
                iid = selected_iids[0]
                idx = get_index(iid)
                values = get_item(iid, "values")
                if values and idx < len(original_tags):
                    original_tag = original_tags[idx][0]
                    new_tag = values[3] if len(values) > 3 else original_tag
                    tag_to_insert = new_tag if new_tag != "" else original_tag
                    current = edit_entry.get()
                    if current != tag_to_insert:
                        edit_entry.delete(0, "end")
                        edit_entry.insert(0, tag_to_insert)
            else:
                if self.edit_entry.get() != "":
                    self.edit_entry.delete(0, "end")


    def _disable_tag_tooltip(self, event=None):
        if not self.tag_tooltip:
            return
        self.tag_tooltip.hide()
        if self.tag_tooltip.state != "disabled" or self._tree_tooltip_text:
            self.tag_tooltip.config(state="disabled", text="")
        self._tree_tooltip_text = None


    def _capture_tree_state(self):
        state = {}
        if not hasattr(self, "tag_tree") or self.tag_tree is None:
            return state
        for idx, iid in enumerate(self.tag_tree.get_children()):
            if idx >= len(self.original_tags):
                continue
            values = self.tag_tree.item(iid, "values")
            if not values or len(values) < 4:
                continue
            original_tag = self.original_tags[idx][0]
            new_tag = values[3]
            if new_tag == "" or new_tag != original_tag:
                state[original_tag] = new_tag
        return state


    def transform_selected_tags(self, transform_type: str):
        if not hasattr(self, "tag_tree") or self.tag_tree is None:
            return
        selected_iids = list(self.tag_tree.selection())
        if not selected_iids:
            return
        original_selection = list(selected_iids)
        for iid in original_selection:
            idx = self.tag_tree.index(iid)
            if idx >= len(self.original_tags):
                continue
            original_tag = self.original_tags[idx][0]
            new_tag = self._apply_transformation(original_tag, transform_type)
            try:
                self.tag_tree.selection_set(iid)
            except Exception:
                pass
            if hasattr(self, "edit_entry") and self.edit_entry is not None:
                self.edit_entry.delete(0, "end")
                if new_tag is not None:
                    self.edit_entry.insert(0, new_tag)
            self.apply_commands_to_tree(edit=new_tag)
        try:
            self.tag_tree.selection_set(original_selection)
        except Exception:
            pass
        self.count_treeview_tags()


    def _apply_transformation(self, text: str, transform_type: str) -> str:
        if text is None:
            return text
        if transform_type == "lower":
            return text.lower()
        if transform_type == "upper":
            return text.upper()
        if transform_type == "title":
            return text.title()
        if transform_type == "spaces_to_underscores":
            return text.replace(" ", "_")
        if transform_type == "underscores_to_spaces":
            return text.replace("_", " ")
        if transform_type == "remove_non_alphanumeric":
            return re.sub(r'[^a-zA-Z0-9_\-\s]', '', text)
        if transform_type == "remove_escape":
            return re.sub(r'\\([\(\)\[\]\{\}])', r'\1', text)
        if transform_type == "remove_punctuation":
            return re.sub(r'[^\w\s]', '', text)
        if transform_type == "remove_digits":
            return re.sub(r'\d', '', text)
        if transform_type == "add_escape":
            return re.sub(r'([\(\)\[\]\{\}])', r'\\\1', text)
        # default: no change
        return text


#endregion
#region Misc


    def open_help_window(self):
        help_text = HelpText.BATCH_TAG_EDIT_HELP
        self.help_window.open_window(geometry="700x700", help_text=help_text)


#endregion

