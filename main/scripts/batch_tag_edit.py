"""
########################################
#             BatchTagEdit             #
#   Version : v1.01                    #
#   Author  : github.com/Nenotriple    #
########################################

Description:
-------------
Quickly edit/delete tags from all files in a folder

More info here: https://github.com/Nenotriple/img-txt_viewer

"""


################################################################################################################################################
#region - Imports


# Standard Library
from collections import Counter


# Standard Library - GUI
from tkinter import (
    ttk, messagebox, simpledialog,
    BooleanVar,
    Frame, Menu,
    Label, Listbox, Scrollbar,
    TclError
)


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip


# Custom Libraries
from main.scripts import TagEditor


#endregion
################################################################################################################################################
#region - CLASS: BatchTagEdit


class BatchTagEdit:
    def __init__(self):
        # Inherited Variables
        self.parent = None
        self.root = None
        self.text_files = None
        self.working_dir = None
        self.batch_tag_edit_frame = None
        self.version = None
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
        self.version = self.parent.app_version

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
        self.batch_tag_edit_frame = self.parent.batch_tag_edit_tab
        self.batch_tag_edit_frame.grid_columnconfigure(1, weight=1)
        self.batch_tag_edit_frame.grid_rowconfigure(1, weight=1)


    def setup_top_frame(self):
        self.top_frame = Frame(self.batch_tag_edit_frame)
        self.top_frame.grid(row=0, column=0, columnspan=99, sticky="nsew", pady=2)
        self.top_frame.grid_columnconfigure(3, weight=1)

        self.button_save_changes = ttk.Button(self.top_frame, text="Save Changes", width=15, state="disabled", command=self.apply_tag_edits)
        self.button_save_changes.grid(row=0, column=1, padx=2, sticky="w")

        self.info_label = Label(self.top_frame, anchor="w", text=f"Total: {self.total_unique_tags}  | Visible: {self.visible_tags}  |  Selected: {self.selected_tags}  |  Pending Delete: {self.pending_delete}  |  Pending Edit: {self.pending_edit}")
        self.info_label.grid(row=0, column=2, padx=2, sticky="ew")

        self.help_button = ttk.Button(self.top_frame, text="?", width=2, command=self.toggle_info_message)
        self.help_button.grid(row=0, column=3, padx=2, sticky="e")
        ToolTip.create(self.help_button, "Show/Hide Help", 50, 6, 12)


    def setup_listbox_frame(self):
        self.listbox_frame = Frame(self.batch_tag_edit_frame)
        self.listbox_frame.grid(row=1, column=0, padx=2, sticky="nsew")

        self.listbox = Listbox(self.listbox_frame, width=50, selectmode="extended", relief="groove", exportselection=False)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.listbox.bind("<Control-c>", self.copy_listbox_selection)
        self.listbox.bind("<Button-3>", self.show_listbox_context_menu)
        self.listbox.bind("<<ListboxSelect>>", self.count_listbox_tags)
        self.listbox_frame.grid_rowconfigure(0, weight=1)

        self.vertical_scrollbar = Scrollbar(self.listbox_frame, orient="vertical", command=self.listbox.yview)
        self.vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        self.horizontal_scrollbar = Scrollbar(self.listbox_frame, orient="horizontal", command=self.listbox.xview)
        self.horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        self.listbox.config(yscrollcommand=self.vertical_scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)
        self.setup_listbox_sub_frame(self.listbox_frame)


    def setup_listbox_sub_frame(self, listbox_frame):
        self.listbox_sub_frame = Frame(listbox_frame)
        self.listbox_sub_frame.grid(row=2, column=0, sticky="ew")
        self.listbox_sub_frame.grid_columnconfigure(0, weight=1)
        self.listbox_sub_frame.grid_columnconfigure(1, weight=1)
        self.listbox_sub_frame.grid_columnconfigure(2, weight=1)

        self.button_all = ttk.Button(self.listbox_sub_frame, text="All", width=8, command=lambda: self.listbox_selection("all"))
        self.button_all.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_all, "Select all tags in the listbox", 150, 6, 12)
        self.button_invert = ttk.Button(self.listbox_sub_frame, text="Invert", width=8, command=lambda: self.listbox_selection("invert"))
        self.button_invert.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_invert, "Invert the current selection of tags", 150, 6, 12)
        self.button_clear = ttk.Button(self.listbox_sub_frame, text="Clear", width=8, command=lambda: self.listbox_selection("clear"))
        self.button_clear.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_clear, "Clear the current selection of tags", 150, 6, 12)
        self.button_revert_sel = ttk.Button(self.listbox_sub_frame, text="Revert Sel", width=8, command=self.revert_listbox_changes)
        self.button_revert_sel.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_revert_sel, "Revert the selected tags to their original state", 150, 6, 12)
        self.button_revert_all = ttk.Button(self.listbox_sub_frame, text="Revert All", width=8, command=self.clear_filter)
        self.button_revert_all.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_revert_all, "Revert all tags to their original state. (Reset)", 150, 6, 12)
        self.button_copy = ttk.Button(self.listbox_sub_frame, text="Copy", width=8, command=self.copy_listbox_selection)
        self.button_copy.grid(row=1, column=2, padx=2, pady=2, sticky="ew")
        ToolTip.create(self.button_copy, "Copy the selected tags to the clipboard", 150, 6, 12)


    def setup_option_frame(self):
        self.option_frame = Frame(self.batch_tag_edit_frame, borderwidth=1, relief="groove")
        self.option_frame.grid(row=1, column=1, padx=2, sticky="nsew")
        self.option_frame.grid_columnconfigure(0, weight=1)
        self.setup_sort_frame()
        self.setup_filter_frame()
        self.setup_edit_frame()
        self.setup_help_frame()


    def setup_sort_frame(self):
        self.sort_frame = Frame(self.option_frame)
        self.sort_frame.grid(row=0, column=0, padx=2, pady=10, sticky="ew")

        self.sort_label = Label(self.sort_frame, text="Sort by:", width=6)
        self.sort_label.grid(row=0, column=0, padx=2)
        ToolTip.create(self.sort_label, "Sort the visible tags", 250, 6, 12)

        self.sort_options_combobox = ttk.Combobox(self.sort_frame, values=["Frequency", "Name", "Length"], state="readonly", width=12)
        self.sort_options_combobox.set("Frequency")
        self.sort_options_combobox.grid(row=0, column=1, padx=2, sticky="e")
        self.sort_options_combobox.bind("<<ComboboxSelected>>", lambda event: self.warn_before_action(action="sort"))

        self.reverse_sort_var = BooleanVar()
        self.reverse_sort_checkbutton = ttk.Checkbutton(self.sort_frame, text="Reverse Order", variable=self.reverse_sort_var, command=lambda: self.warn_before_action(action="sort"))
        self.reverse_sort_checkbutton.grid(row=0, column=2, padx=2, sticky="e")


    def setup_filter_frame(self):
        self.filter_frame = Frame(self.option_frame)
        self.filter_frame.grid(row=1, column=0, padx=2, pady=10, sticky="ew")
        self.filter_frame.grid_columnconfigure(2, weight=1)

        self.filter_label = Label(self.filter_frame, text="Filter :", width=6)
        self.filter_label.grid(row=0, column=0, padx=2)
        ToolTip.create(self.filter_label, "All options except <, and >, support multiple values separated by commas.\n\nTag : Filter tags by the input text\n!Tag : Filter tags that do not contain the input text\n== : Filter tags equal to the given value\n!= : Filter tags not equal to the given value\n< : Filter tags less than the given value\n> : Filter tags greater than the given value", 250, 6, 12)

        self.filter_combobox = ttk.Combobox(self.filter_frame, values=["Tag", "!Tag", "==", "!=", "<", ">"], state="readonly", width=12)
        self.filter_combobox.set("Tag")
        self.filter_combobox.grid(row=0, column=1, padx=2, sticky="e")
        self.filter_combobox.bind("<<ComboboxSelected>>", lambda event: self.warn_before_action(action="filter"))

        self.filter_entry = ttk.Entry(self.filter_frame, width=20)
        self.filter_entry.grid(row=0, column=2, padx=2, sticky="ew")
        self.filter_entry.bind("<KeyRelease>", lambda event: self.warn_before_action(action="filter"))
        self.filter_entry.bind("<Button-3>", self.show_entry_context_menu)

        self.filter_apply_button = ttk.Button(self.filter_frame, text="Apply", width=6, command=lambda: self.warn_before_action(action="filter"))
        self.filter_apply_button.grid(row=0, column=3, padx=2, sticky="e")

        self.filter_clear_button = ttk.Button(self.filter_frame, text="Reset", width=6, command=self.clear_filter)
        self.filter_clear_button.grid(row=0, column=4, padx=2, sticky="e")
        ToolTip.create(self.filter_clear_button, "Clear any filters or pending changes", 250, 6, 12)

        ttk.Separator(self.filter_frame, orient="horizontal").grid(row=1, column=0, columnspan=5, sticky="ew", pady=(20,0))


    def setup_edit_frame(self):
        self.edit_frame = Frame(self.option_frame)
        self.edit_frame.grid(row=2, column=0, padx=2, pady=10, sticky="ew")
        self.edit_frame.grid_columnconfigure(2, weight=1)

        self.edit_label = Label(self.edit_frame, text="Edit :", width=6)
        self.edit_label.grid(row=0, column=0, padx=2)
        ToolTip.create(self.edit_label, "Select an option and enter text to apply to the selected tags", 250, 6, 12, justify="left")

        self.edit_entry = ttk.Entry(self.edit_frame, width=20)
        self.edit_entry.grid(row=0, column=2, padx=2, sticky="ew")
        self.edit_entry.bind("<Return>", self.apply_commands_to_listbox)
        self.edit_entry.bind("<Button-3>", self.show_entry_context_menu)

        self.edit_apply_button = ttk.Button(self.edit_frame, text="Apply", width=6, command=self.apply_commands_to_listbox)
        self.edit_apply_button.grid(row=0, column=3, padx=2, sticky="e")
        ToolTip.create(self.edit_apply_button, "Apply the selected changes to the listbox. This does not apply the changes to the text files!", 250, 6, 12)

        self.edit_reset_button = ttk.Button(self.edit_frame, text="Reset", width=6, command=self.clear_filter)
        self.edit_reset_button.grid(row=0, column=4, padx=2, sticky="e")
        ToolTip.create(self.edit_reset_button, "Clear any filters or pending changes", 250, 6, 12)

        self.delete_button = ttk.Button(self.edit_frame, text="Delete", width=6, command=lambda: self.apply_commands_to_listbox(delete=True))
        self.delete_button.grid(row=1, column=0, padx=2, sticky="e")
        ToolTip.create(self.delete_button, "Delete the selected tags", 250, 6, 12)


    def setup_help_frame(self):
        self.help_frame = Frame(self.option_frame)
        self.help_frame.grid(row=3, column=0, padx=(20,10), pady=10, sticky="nw")
        self.help_message = Label(self.help_frame, justify="left", text=
            "Help:\n"
            "Press F5 to open and close Batch Tag Edit.\n"
            "The number next to the tag indicates its frequency in the dataset.\n"
            "This tool is not perfect; it may not work as expected with certain combinations of characters, text or their formatting.\n"
            "   - It works best with CSV-like text files. Both commas and periods are treated as caption delimiters.\n"
            "   - You should always make backups of your text files before saving any changes.\n\n"
            "Instructions:\n"
            "1) Use the filter or sort options to refine the tag list.\n"
            "   - You can input multiple filter values separated by commas.\n"
            "2) Select the tags you want to modify from the listbox.\n"
            "3) Choose an edit option:\n"
            "   - Replace: Enter the new text to replace the selected tags.\n"
            "   - Delete: If the entry is empty, or the Delete option is selected, the selected tags will be deleted.\n"
            "4) Click *Edit > Apply* to see the changes in the listbox. This does not apply the changes to the text files.\n"
            "5) Click *Save Changes* to apply the modifications to the text files. This action cannot be undone, so make sure to backup your files.\n"
            "6) Use the *Reset* buttons to clear any pending changes or filters.\n"
            "7) Use the buttons below the listbox to:\n"
            "   - Select All: Select all tags in the listbox.\n"
            "   - Invert Selection: Invert the current selection of tags.\n"
            "   - Clear Selection: Clear the current selection of tags.\n"
            "   - Revert Sel: Revert the selected tags to their original state.\n"
            "   - Revert All: Revert all tags to their original state. (Reset)\n"
            "8) Click the *Close* button to exit the Batch Tag Edit without saving and pending changes.\n"
        )
        self.help_message.grid(row=1, column=0, padx=2, pady=2, sticky="nw")
        self.help_frame.grid_remove()


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
            self.button_save_changes.config(state="normal")
        else:
            self.button_save_changes.config(state="disabled")
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


    def toggle_info_message(self):
        if self.help_frame.winfo_viewable():
            self.help_frame.grid_remove()
        else:
            self.help_frame.grid()


    def show_listbox_context_menu(self, event):
        listbox = event.widget
        if not listbox.curselection():
            return
        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="Delete", command=lambda: self.apply_commands_to_listbox(delete=True))
        context_menu.add_command(label="Replace...", command=self.context_menu_edit_tag)
        context_menu.add_command(label="Copy", command=self.copy_listbox_selection)
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=lambda: self.listbox_selection("all"))
        context_menu.add_command(label="Invert Selection", command=lambda: self.listbox_selection("invert"))
        context_menu.add_command(label="Clear Selection", command=lambda: self.listbox_selection("clear"))
        context_menu.add_separator()
        context_menu.add_command(label="Revert Selection", command=self.revert_listbox_changes)
        context_menu.add_command(label="Revert All", command=self.clear_filter)
        context_menu.post(event.x_root, event.y_root)


    def show_entry_context_menu(self, event):
        widget = event.widget
        if isinstance(widget, ttk.Entry):
            context_menu = Menu(self.root, tearoff=0)
            try:
                widget.selection_get()
                has_selection = True
            except TclError:
                has_selection = False
            has_text = bool(widget.get())
            context_menu.add_command(label="Cut", command=lambda: widget.event_generate("<Control-x>"), state="normal" if has_selection else "disabled")
            context_menu.add_command(label="Copy", command=lambda: widget.event_generate("<Control-c>"), state="normal" if has_selection else "disabled")
            context_menu.add_command(label="Paste", command=lambda: widget.event_generate("<Control-v>"))
            context_menu.add_separator()
            context_menu.add_command(label="Delete", command=lambda: widget.delete("sel.first", "sel.last"), state="normal" if has_selection else "disabled")
            context_menu.add_command(label="Clear", command=lambda: widget.delete(0, "end"), state="normal" if has_text else "disabled")
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


#endregion
