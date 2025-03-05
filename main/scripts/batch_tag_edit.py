#region - Imports


# Standard Library
from collections import Counter


# Standard Library - GUI
from tkinter import (
    ttk, Tk, messagebox, simpledialog,
    BooleanVar,
    Frame, Menu,
    Label, Listbox, Scrollbar,
    TclError
)


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip


# Custom Libraries
from main.scripts import TagEditor, help_window, HelpText
import main.scripts.entry_helper as entry_helper


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
################################################################################################################################################
#region - CLASS: BatchTagEdit


class BatchTagEdit:
    def __init__(self):
        # Inherited Variables
        self.parent: 'Main' = None
        self.root: 'Tk' = None
        self.text_files = None
        self.working_dir = None
        self.batch_tag_edit_frame = None
        self.help_window = None
        self.entry_helper = entry_helper
        # Local Variables
        self.tag_counts = 0
        self.total_unique_tags = 0
        self.visible_tags = 0
        self.selected_tags = 0
        self.pending_delete = 0
        self.pending_edit = 0


#endregion
################################################################################################################################################
#region - Setup - UI


    def setup_window(self, parent, root):
        self.parent = parent
        self.root = root
        self.text_files = self.parent.text_files
        self.working_dir = self.parent.image_dir.get()
        self.batch_tag_edit_frame = None
        self.help_window = help_window.HelpWindow(self.root)

        tag_dict = self.analyze_tags()
        self.tag_counts, self.total_unique_tags = self.count_file_tags(tag_dict)
        self.original_tags = []
        self.create_ui()
        self.sort_tags(self.tag_counts.items(), "Frequency", False)


    def create_ui(self):
        self.setup_primary_frame()
        self.setup_top_frame()
        self.setup_listbox_frame()
        self.setup_option_frame()
        self.count_listbox_tags()


    def setup_primary_frame(self):
        # Primary Frame
        self.batch_tag_edit_frame = self.parent.batch_tag_edit_tab
        self.batch_tag_edit_frame.grid_columnconfigure(1, weight=1)
        self.batch_tag_edit_frame.grid_rowconfigure(1, weight=1)


    def setup_top_frame(self):
        # Frame
        top_frame = Frame(self.batch_tag_edit_frame)
        top_frame.grid(row=0, column=0, columnspan=99, sticky="nsew", pady=2)
        top_frame.grid_columnconfigure(0, weight=1)
        # Label
        self.info_label = Label(top_frame, anchor="w", text=f"Total: {self.total_unique_tags}  | Visible: {self.visible_tags}  |  Selected: {self.selected_tags}  |  Pending Delete: {self.pending_delete}  |  Pending Edit: {self.pending_edit}")
        self.info_label.grid(row=0, column=0, padx=1, sticky="ew")
        # Button
        self.button_save = ttk.Button(top_frame, text="Save Changes", width=15, state="disabled", command=self.apply_tag_edits)
        self.button_save.grid(row=0, column=1, padx=2)
        # Button
        refresh_button = ttk.Button(top_frame, text="Refresh", width=8, command=self.clear_filter)
        refresh_button.grid(row=0, column=2, padx=2)
        # Button
        help_button = ttk.Button(top_frame, text="?", width=2, command=self.open_help_window)
        help_button.grid(row=0, column=3, padx=2)
        ToolTip.create(help_button, "Show/Hide Help", 50, 6, 12)


    def setup_listbox_frame(self):
        # Frame
        listbox_frame = ttk.Labelframe(self.batch_tag_edit_frame, text="Tags")
        listbox_frame.grid(row=1, column=0, padx=2, sticky="nsew")
        # Listbox
        self.listbox = Listbox(listbox_frame, width=50, selectmode="extended", relief="groove", exportselection=False)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.listbox.bind("<Control-c>", self.copy_listbox_selection)
        self.listbox.bind("<Button-3>", self.show_listbox_context_menu)
        self.listbox.bind("<<ListboxSelect>>", self.count_listbox_tags)
        listbox_frame.grid_rowconfigure(0, weight=1)
        # Scrollbars
        self.vertical_scrollbar = Scrollbar(listbox_frame, orient="vertical", command=self.listbox.yview)
        self.vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        self.horizontal_scrollbar = Scrollbar(listbox_frame, orient="horizontal", command=self.listbox.xview)
        self.horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        self.listbox.config(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)
        self.setup_listbox_sub_frame(listbox_frame)


    def setup_listbox_sub_frame(self, listbox_frame):
        # Frame
        self.listbox_sub_frame = Frame(listbox_frame)
        self.listbox_sub_frame.grid(row=2, column=0, sticky="ew")
        self.listbox_sub_frame.grid_columnconfigure(0, weight=1)
        self.listbox_sub_frame.grid_columnconfigure(1, weight=1)
        self.listbox_sub_frame.grid_columnconfigure(2, weight=1)
        # Select All
        self.button_all = ttk.Button(self.listbox_sub_frame, text="All", width=8, command=lambda: self.listbox_selection("all"))
        self.button_all.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_all, "Select all tags in the listbox", 150, 6, 12)
        # Invert Selection
        self.button_invert = ttk.Button(self.listbox_sub_frame, text="Invert", width=8, command=lambda: self.listbox_selection("invert"))
        self.button_invert.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_invert, "Invert the current selection of tags", 150, 6, 12)
        # Clear Selection
        self.button_clear = ttk.Button(self.listbox_sub_frame, text="Clear", width=8, command=lambda: self.listbox_selection("clear"))
        self.button_clear.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_clear, "Clear the current selection of tags", 150, 6, 12)
        # Revert Selection
        self.button_revert_sel = ttk.Button(self.listbox_sub_frame, text="Revert Sel", width=8, command=self.revert_listbox_changes)
        self.button_revert_sel.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_revert_sel, "Revert the selected tags to their original state", 150, 6, 12)
        # Revert All
        self.button_revert_all = ttk.Button(self.listbox_sub_frame, text="Revert All", width=8, command=self.clear_filter)
        self.button_revert_all.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_revert_all, "Revert all tags to their original state. (Reset)", 150, 6, 12)
        # Copy
        self.button_copy = ttk.Button(self.listbox_sub_frame, text="Copy", width=8, command=self.copy_listbox_selection)
        self.button_copy.grid(row=1, column=2, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_copy, "Copy the selected tags to the clipboard", 150, 6, 12)


    def setup_option_frame(self):
        # Frame
        self.option_frame = ttk.Labelframe(self.batch_tag_edit_frame, text="Options")
        self.option_frame.grid(row=1, column=1, padx=2, sticky="nsew")
        self.option_frame.grid_columnconfigure(0, weight=1)
        # Frame
        self.sort_filter_frame = ttk.Labelframe(self.option_frame, text="Sort & Filter")
        self.sort_filter_frame.grid(row=0, column=0, padx=2, pady=10, sticky="ew")
        self.setup_sort_frame()
        self.setup_filter_frame()
        self.setup_edit_frame()


    def setup_sort_frame(self):
        # Frame
        self.sort_frame = Frame(self.sort_filter_frame)
        self.sort_frame.grid(row=0, column=0, padx=2, pady=10, sticky="ew")
        # Label
        self.sort_label = Label(self.sort_frame, text="Sort by:", width=8)
        self.sort_label.grid(row=0, column=0, padx=2)
        ToolTip.create(self.sort_label, "Sort the visible tags", 250, 6, 12)
        # Combobox
        self.sort_options_combobox = ttk.Combobox(self.sort_frame, values=["Frequency", "Name", "Length"], state="readonly", width=12)
        self.sort_options_combobox.set("Frequency")
        self.sort_options_combobox.grid(row=0, column=1, padx=2, sticky="e")
        self.sort_options_combobox.bind("<<ComboboxSelected>>", lambda event: self.warn_before_action(action="sort"))
        # Checkbutton
        self.reverse_sort_var = BooleanVar()
        self.reverse_sort_checkbutton = ttk.Checkbutton(self.sort_frame, text="Reverse Order", variable=self.reverse_sort_var, command=lambda: self.warn_before_action(action="sort"))
        self.reverse_sort_checkbutton.grid(row=0, column=2, padx=2, sticky="e")


    def setup_filter_frame(self):
        # Frame
        filter_frame = Frame(self.sort_filter_frame)
        filter_frame.grid(row=1, column=0, padx=2, pady=10, sticky="ew")
        filter_frame.grid_columnconfigure(2, weight=1)
        self.sort_filter_frame.grid_columnconfigure(0, weight=1)
        # Label
        self.filter_label = Label(filter_frame, text="Filter :", width=8)
        self.filter_label.grid(row=0, column=0, padx=2)
        ToolTip.create(self.filter_label, "All options except <, and >, support multiple values separated by commas.\n\nTag : Filter tags by the input text\n!Tag : Filter tags that do not contain the input text\n== : Filter tags equal to the given value\n!= : Filter tags not equal to the given value\n< : Filter tags less than the given value\n> : Filter tags greater than the given value", 250, 6, 12)
        # Combobox
        self.filter_combobox = ttk.Combobox(filter_frame, values=["Tag", "!Tag", "==", "!=", "<", ">"], state="readonly", width=12)
        self.filter_combobox.set("Tag")
        self.filter_combobox.grid(row=0, column=1, padx=2, sticky="e")
        self.filter_combobox.bind("<<ComboboxSelected>>", lambda event: self.warn_before_action(action="filter"))
        # Entry
        self.filter_entry = ttk.Entry(filter_frame)
        self.filter_entry.grid(row=0, column=2, padx=2, sticky="ew")
        self.filter_entry.bind("<KeyRelease>", lambda event: self.warn_before_action(action="filter"))
        self.entry_helper.setup_entry_binds(self.filter_entry)
        # Button
        self.filter_apply_button = ttk.Button(filter_frame, text="Apply", command=lambda: self.warn_before_action(action="filter"))
        self.filter_apply_button.grid(row=0, column=3, padx=2, sticky="e")
        # Button
        filter_clear_button = ttk.Button(filter_frame, text="Reset", command=self.clear_filter)
        filter_clear_button.grid(row=0, column=4, padx=2, sticky="e")
        ToolTip.create(filter_clear_button, "Clear any filters or pending changes", 250, 6, 12)


    def setup_edit_frame(self):
        # Frame
        edit_frame = ttk.Labelframe(self.option_frame, text="Edit & Delete")
        edit_frame.grid(row=2, column=0, padx=2, pady=10, sticky="ew")
        edit_frame.columnconfigure(0, weight=1)

        # Edit frame
        edit_row_frame = ttk.Frame(edit_frame)
        edit_row_frame.grid(row=0, column=0, sticky="ew", padx=2, pady=5)
        edit_row_frame.columnconfigure(1, weight=1)
        # Label
        edit_label = ttk.Label(edit_row_frame, text="Edit:", width=10)
        edit_label.grid(row=0, column=0, sticky="w", padx=2, pady=5)
        ToolTip.create(edit_label, "Select an option and enter text to apply to the selected tags", 250, 6, 12, justify="left")
        # Entry
        self.edit_entry = ttk.Entry(edit_row_frame)
        self.edit_entry.grid(row=0, column=1, sticky="ew", padx=2, pady=5)
        self.edit_entry.bind("<Return>", self.apply_commands_to_listbox)
        self.entry_helper.setup_entry_binds(self.edit_entry)
        # Button
        edit_apply_button = ttk.Button(edit_row_frame, text="Apply", command=self.apply_commands_to_listbox)
        edit_apply_button.grid(row=0, column=2, sticky="e", padx=2, pady=5)
        ToolTip.create(edit_apply_button, "Apply the selected changes to the listbox. This does not apply the changes to the text files!", 250, 6, 12)
        # Button
        edit_reset_button = ttk.Button(edit_row_frame, text="Reset", command=self.clear_filter)
        edit_reset_button.grid(row=0, column=3, sticky="e", padx=2, pady=5)
        ToolTip.create(edit_reset_button, "Clear any filters or pending changes", 250, 6, 12)

        # Delete frame
        delete_row = ttk.Frame(edit_frame)
        delete_row.grid(row=2, column=0, sticky="ew", padx=2, pady=5)
        delete_row.columnconfigure(1, weight=1)
        # label
        delete_label = ttk.Label(delete_row, text="Delete Tags:")
        delete_label.grid(row=0, column=0, sticky="ew", padx=2, pady=5)
        # Label
        self.delete_center_label = ttk.Label(delete_row, text="Select tags and click delete", anchor="center")
        self.delete_center_label.grid(row=0, column=1, columnspan=2, sticky="ew", padx=2, pady=5)
        # Button
        delete_button = ttk.Button(delete_row, text="Delete", command=lambda: self.apply_commands_to_listbox(delete=True))
        delete_button.grid(row=0, column=3, sticky="e", padx=2, pady=5)
        ToolTip.create(delete_button, "Delete the selected tags", 250, 6, 12)


#endregion
################################################################################################################################################
#region - Primary Functions


    def analyze_tags(self):
        tag_dict = TagEditor.analyze_tags(self.parent.text_files)
        return tag_dict


    def count_file_tags(self, tags):
        tag_counts = Counter()
        for tag, positions in tags.items():
            tag_counts[tag] = len(positions)
        total_unique_tags = len(tag_counts)
        return tag_counts, total_unique_tags


    def refresh_counts(self):
        self.original_tags = []
        tag_dict = self.analyze_tags()
        self.tag_counts, self.total_unique_tags = self.count_file_tags(tag_dict)
        self.sort_tags(self.tag_counts.items(), self.sort_options_combobox.get(), self.reverse_sort_var.get())
        self.toggle_filter_and_sort_widgets()


    def sort_tags(self, tags, option, reverse):
        if option == "Frequency":
            sorted_tags = sorted(tags, key=lambda tag: tag[1], reverse=not reverse)
        elif option == "Name":
            sorted_tags = sorted(tags, reverse=reverse)
        elif option == "Length":
            sorted_tags = sorted(tags, key=lambda tag: len(tag[0]), reverse=not reverse)
        self.update_listbox(sorted_tags)


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
                filtered_tags = [(tag, count) for tag, count in self.tag_counts.items() if filter_functions[filter_option](tag, count)]
            self.sort_tags(filtered_tags, self.sort_options_combobox.get(), self.reverse_sort_var.get())
        except ValueError:
            messagebox.showinfo("Error", "Invalid filter value. Please enter a number.")
            self.filter_entry.delete(0, "end")
            return


    def apply_commands_to_listbox(self, event=None, delete=False, edit=None):
        tags = self.listbox.curselection()
        selected_items = [self.original_tags[i][0] for i in tags]
        if edit is None:  # If None, use the edit entry
            edit = self.edit_entry.get()
        if edit == "":  # If empty, delete the tags
            delete = True
        for i, item in zip(reversed(tags), reversed(selected_items)):
            current_text = self.listbox.get(i)
            # If the item is already altered, remove the previous alteration
            if current_text.startswith("DELETE :") or current_text.startswith("EDIT :"):
                # Strip away "DELETE :" or "EDIT :" to get the original item
                item = current_text.split(":", 1)[1].strip().split(">", 1)[0].strip()
            if delete:  # If delete, add delete command
                self.listbox.delete(i)
                self.listbox.insert(i, f"DELETE : {item}")
                self.listbox.itemconfig(i, {'fg': 'red'})
            else:  # If not delete, add edit command
                self.listbox.delete(i)
                self.listbox.insert(i, f"EDIT : {item} > {edit}")
                self.listbox.itemconfig(i, {'fg': 'green'})
        self.count_listbox_tags()


    def revert_listbox_changes(self):
        padding_width = len(str(self.total_unique_tags))
        tags = self.listbox.curselection()
        for i in tags:
            current_text = self.listbox.get(i)
            if current_text.startswith("DELETE :") or current_text.startswith("EDIT :"):
                original_item = current_text.split(":", 1)[1].strip().split(">", 1)[0].strip()
                for tag, count in self.tag_counts.items():
                    if tag == original_item:
                        padded_count = str(count).zfill(padding_width)
                        reverted_text = f" {padded_count}, {tag}"
                        self.listbox.delete(i)
                        self.listbox.insert(i, reverted_text)
                        self.listbox.itemconfig(i, {'fg': 'black'})
                        self.count_listbox_tags()
                        break


    def apply_tag_edits(self):
        if self.pending_delete or self.pending_edit:
            confirm = messagebox.askyesno("Save Changes", f"Commit pending changes to text files?\nThis action cannot be undone, you should make backups!\n\nPending Edits: {self.pending_edit}\nPending Deletes: {self.pending_delete}")
            if not confirm:
                return
        delete_tags = []
        edit_tags = {}
        for i in range(self.listbox.size()):
            current_text = self.listbox.get(i)
            if current_text.startswith("DELETE :"):
                tag = current_text.split(":", 1)[1].strip()
                delete_tags.append(tag)
            elif current_text.startswith("EDIT :"):
                original_tag, new_tag = current_text.split(":", 1)[1].strip().split(">", 1)
                original_tag = original_tag.strip()
                new_tag = new_tag.strip()
                edit_tags[original_tag] = new_tag
        if delete_tags:
            TagEditor.edit_tags(self.parent.text_files, delete_tags, delete=True)
        if edit_tags:
            for original_tag, new_tag in edit_tags.items():
                TagEditor.edit_tags(self.text_files, [original_tag], edit=new_tag)
        self.clear_filter(warn=False)
        self.parent.refresh_text_box()


# --------------------------------------
# Listbox
# --------------------------------------
    def update_listbox(self, tags):
        self.listbox.delete(0, "end")
        padding_width = len(str(self.total_unique_tags))
        self.original_tags = tags
        for tag, count in tags:
            padded_count = str(count).zfill(padding_width)
            self.listbox.insert("end", f" {padded_count}, {tag}")
        self.count_listbox_tags()
        return tags


    def count_listbox_tags(self, event=None):
        self.pending_delete = 0
        self.pending_edit = 0
        for i in range(self.listbox.size()):
            item = self.listbox.get(i)
            if item.startswith("DELETE :"):
                self.pending_delete += 1
            elif item.startswith("EDIT :"):
                self.pending_edit += 1
        self.visible_tags = self.listbox.size()
        self.selected_tags = len(self.listbox.curselection())
        padding_width = len(str(self.total_unique_tags))
        pending_delete_str = str(self.pending_delete).zfill(padding_width)
        pending_edit_str = str(self.pending_edit).zfill(padding_width)
        visible_tags_str = str(self.visible_tags).zfill(padding_width)
        selected_tags_str = str(self.selected_tags).zfill(padding_width)
        self.info_label.config(text=f"Total: {self.total_unique_tags}  | Visible: {visible_tags_str}  |  Selected: {selected_tags_str}  |  Pending Delete: {pending_delete_str}  |  Pending Edit: {pending_edit_str}")
        if self.pending_delete > 0 or self.pending_edit > 0:
            self.button_save.config(state="normal")
        else:
            self.button_save.config(state="disabled")
        self.toggle_filter_and_sort_widgets()


    def listbox_selection(self, action):
        if action == "all":
            self.listbox.selection_set(0, "end")
        elif action == "invert":
            selected_indices = self.listbox.curselection()
            all_indices = set(range(self.listbox.size()))
            new_selection = all_indices - set(selected_indices)
            self.listbox.selection_clear(0, "end")
            for index in new_selection:
                self.listbox.selection_set(index)
        elif action == "clear":
            self.listbox.selection_anchor(0)
            self.listbox.selection_clear(0, "end")
        self.count_listbox_tags()


    def copy_listbox_selection(self, event=None):
        selected_tags = [self.listbox.get(i).split(", ", 1)[1].strip() for i in self.listbox.curselection()]
        self.root.clipboard_clear()
        self.root.clipboard_append(", ".join(selected_tags))


    def context_menu_edit_tag(self):
        edit_string = simpledialog.askstring("Edit Tag", "Enter new tag:", parent=self.root)
        if edit_string is not None:
            self.apply_commands_to_listbox(edit=edit_string)


# --------------------------------------
# UI Helpers
# --------------------------------------
    def toggle_filter_and_sort_widgets(self, event=None):
        try:
            widgets = [
                self.sort_label,
                self.sort_options_combobox,
                self.reverse_sort_checkbutton,
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


    def clear_filter(self, warn=True):
        if warn and (self.pending_delete or self.pending_edit):
            if not messagebox.askyesno("Warning", "Clear all pending changes.\n\nContinue?"):
                return
        self.filter_entry.delete(0, "end")
        self.refresh_counts()


    def show_listbox_context_menu(self, event):
        listbox = event.widget
        if not listbox.curselection():
            return
        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="Delete", command=lambda: self.apply_commands_to_listbox(delete=True))
        context_menu.add_command(label="Edit...", command=self.context_menu_edit_tag)
        context_menu.add_command(label="Copy", command=self.copy_listbox_selection)
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=lambda: self.listbox_selection("all"))
        context_menu.add_command(label="Invert Selection", command=lambda: self.listbox_selection("invert"))
        context_menu.add_command(label="Clear Selection", command=lambda: self.listbox_selection("clear"))
        context_menu.add_separator()
        context_menu.add_command(label="Revert Selection", command=self.revert_listbox_changes)
        context_menu.add_command(label="Revert All", command=self.clear_filter)
        context_menu.post(event.x_root, event.y_root)


# --------------------------------------
# Misc
# --------------------------------------
    def warn_before_action(self, event=None, action=None):
        if self.pending_delete or self.pending_edit:
            if not messagebox.askyesno("Warning", "Adjusting this option will clear all pending changes. Continue?"):
                return
        if action == "sort":
            self.sort_tags(self.tag_counts.items(), self.sort_options_combobox.get(), self.reverse_sort_var.get())
            self.filter_tags(self.filter_combobox.get(), self.filter_entry.get())
        elif action == "filter":
            self.filter_tags(self.filter_combobox.get(), self.filter_entry.get())


    def set_working_directory(self, working_dir=None):
        """
        Updates the working directory and refreshes the UI with new tag data.
        Args:
            working_dir (str): Path to the new working directory
        """
        # Update working directory
        if working_dir:
            self.working_dir = working_dir
        else:
            self.working_dir = self.parent.image_dir.get()
        # Reset UI state variables
        self.tag_counts = 0
        self.total_unique_tags = 0
        self.visible_tags = 0
        self.selected_tags = 0
        self.pending_delete = 0
        self.pending_edit = 0
        self.original_tags = []
        # Clear UI elements
        self.listbox.delete(0, "end")
        self.filter_entry.delete(0, "end")
        self.edit_entry.delete(0, "end")
        # Reset sort options
        self.sort_options_combobox.set("Frequency")
        self.reverse_sort_var.set(False)
        # Analyze new tags and update UI
        tag_dict = self.analyze_tags()
        self.tag_counts, self.total_unique_tags = self.count_file_tags(tag_dict)
        self.sort_tags(self.tag_counts.items(), "Frequency", False)
        self.toggle_filter_and_sort_widgets()


    def open_help_window(self):
        help_text = HelpText.BATCH_TAG_EDIT_HELP
        self.help_window.open_window(geometry="700x700", help_text=help_text)
