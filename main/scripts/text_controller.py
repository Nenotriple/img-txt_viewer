"""Module to handle text manipulation functions and widget creation for the ImgTxtViewer UI."""


################################################################################################################################################
#region - Imports


# Standard Library
import os
import re
import time


# Standard Library - GUI
from tkinter import (
    ttk, Toplevel, messagebox,
    StringVar, BooleanVar,
    Frame, Menu, Scrollbar, scrolledtext, PanedWindow,
    Label, Listbox,
    font, TclError
)


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip


# Custom Libraries
from main.scripts.OnnxTagger import OnnxTagger as OnnxTagger


#endregion
################################################################################################################################################
#region CLS TextController


class TextController:
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root

        # AutoTag
        self.onnx_model_dict = {}
        self.auto_insert_mode_var = StringVar(value="disable")
        self.batch_interrogate_images_var = BooleanVar(value=False)
        self.auto_exclude_tags_var = BooleanVar(value=False)
        self.filter_is_active = False

        # MyTags
        self.show_all_tags_var = BooleanVar(value=True)
        self.hide_mytags_controls_var = BooleanVar(value=False)
        self.hide_alltags_controls_var = BooleanVar(value=False)


#endregion
################################################################################################################################################
#region (1) S&R


    def create_search_and_replace_widgets_tab1(self):
        tab_frame = Frame(self.parent.tab1)
        tab_frame.pack(side='top', fill='both')
        button_frame = Frame(tab_frame)
        button_frame.pack(side='top', fill='x')
        search_label = Label(button_frame, width=8, text="Search:")
        search_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(search_label, "Enter the EXACT text you want to search for", 200, 6, 12)
        self.search_entry = ttk.Entry(button_frame, textvariable=self.parent.search_string_var, width=4)
        self.search_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.bind_entry_functions(self.search_entry)
        replace_label = Label(button_frame, width=8, text="Replace:")
        replace_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(replace_label, "Enter the text you want to replace the searched text with\n\nLeave empty to replace with nothing (delete)", 200, 6, 12)
        self.replace_entry = ttk.Entry(button_frame, textvariable=self.parent.replace_string_var, width=4)
        self.replace_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.bind_entry_functions(self.replace_entry)
        self.replace_entry.bind('<Return>', lambda event: self.search_and_replace())
        replace_button = ttk.Button(button_frame, text="Go!", width=5, command=self.search_and_replace)
        replace_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(replace_button, "Text files will be backup up", 200, 6, 12)
        clear_button = ttk.Button(button_frame, text="Clear", width=5, command=self.clear_search_and_replace_tab)
        clear_button.pack(side='left', anchor="n", pady=4)
        undo_button = ttk.Button(button_frame, text="Undo", width=5, command=self.parent.restore_backup)
        undo_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(undo_button, "Revert last action", 200, 6, 12)
        regex_search_replace_checkbutton = ttk.Checkbutton(button_frame, text="Regex", variable=self.parent.search_and_replace_regex_var)
        regex_search_replace_checkbutton.pack(side='left', anchor="n", pady=4)
        ToolTip.create(regex_search_replace_checkbutton, "Use Regular Expressions in 'Search'", 200, 6, 12)
        text_frame = Frame(tab_frame, borderwidth=0)
        text_frame.pack(side='top', fill="both")
        description_textbox = scrolledtext.ScrolledText(text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0",
            "Use this tool to search for a string of text across all text files in the selected directory.\n\n"
            "If a match is found, it will be replaced exactly with the given text.\n\n"
            "Example:\n"
            "Search for: the big brown dog\n"
            "Replace with: the big red dog\n\n"
            "This will replace all instances of 'the big brown dog' with 'the big red dog'.\n\n"
            "If a filter is applied, only text files that match the filter will be affected."
        )
        description_textbox.config(state="disabled", wrap="word")


    def clear_search_and_replace_tab(self):
        self.search_entry.delete(0, 'end')
        self.replace_entry.delete(0, 'end')
        self.parent.search_and_replace_regex_var.set(False)


    def search_and_replace(self):
        if not self.parent.check_if_directory():
            return
        search_string = self.parent.search_string_var.get()
        replace_string = self.parent.replace_string_var.get()
        if not search_string:
            return
        confirm = messagebox.askokcancel("Search and Replace", "This will replace all occurrences of the text\n\n{}\n\nWith\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(search_string, replace_string))
        if not confirm:
            return
        self.parent.backup_text_files()
        if not self.parent.filter_string_var.get():
            self.parent.update_image_file_count()
        for text_file in self.parent.text_files:
            try:
                with open(text_file, 'r', encoding="utf-8") as file:
                    filedata = file.read()
                if self.parent.search_and_replace_regex_var.get():
                    filedata = re.sub(search_string, replace_string, filedata)
                else:
                    filedata = filedata.replace(search_string, replace_string)
                with open(text_file, 'w', encoding="utf-8") as file:
                    file.write(filedata)
            except Exception as e:
                messagebox.showerror("Error: search_and_replace()", f"An error occurred while trying to replace text in {text_file}.\n\n{e}")
        self.parent.cleanup_all_text_files(show_confirmation=False)
        self.parent.show_pair()
        messagebox.showinfo("Search and Replace", "Search and Replace completed successfully.")


#endregion
################################################################################################################################################
#region (2) Prefix


    def create_prefix_text_widgets_tab2(self):
        tab_frame = Frame(self.parent.tab2)
        tab_frame.pack(side='top', fill='both')
        button_frame = Frame(tab_frame)
        button_frame.pack(side='top', fill='x')
        prefix_label = Label(button_frame, width=8, text="Prefix:")
        prefix_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(prefix_label, "Enter the text you want to insert at the START of all text files\n\nCommas will be inserted as needed", 200, 6, 12)
        self.prefix_entry = ttk.Entry(button_frame, textvariable=self.parent.prefix_string_var)
        self.prefix_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.bind_entry_functions(self.prefix_entry)
        self.prefix_entry.bind('<Return>', lambda event: self.prefix_text_files())
        prefix_button = ttk.Button(button_frame, text="Go!", width=5, command=self.prefix_text_files)
        prefix_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(prefix_button, "Text files will be backup up", 200, 6, 12)
        clear_button = ttk.Button(button_frame, text="Clear", width=5, command=lambda: self.prefix_entry.delete(0, 'end'))
        clear_button.pack(side='left', anchor="n", pady=4)
        undo_button = ttk.Button(button_frame, text="Undo", width=5, command=self.parent.restore_backup)
        undo_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(undo_button, "Revert last action", 200, 6, 12)
        text_frame = Frame(tab_frame, borderwidth=0)
        text_frame.pack(side='top', fill="both")
        description_textbox = scrolledtext.ScrolledText(text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0",
            "Use this tool to prefix all text files in the selected directory with the entered text.\n\n"
            "This means that the entered text will appear at the start of each text file.\n\n"
            "If a filter is applied, only text files that match the filter will be affected."
        )
        description_textbox.config(state="disabled", wrap="word")


    def prefix_text_files(self):
        if not self.parent.check_if_directory():
            return
        prefix_text = self.parent.prefix_string_var.get()
        if not prefix_text:
            return
        if not prefix_text.endswith(', '):
            prefix_text += ', '
        confirm = messagebox.askokcancel("Prefix", "This will prefix all text files with:\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(prefix_text))
        if not confirm:
            return
        self.parent.backup_text_files()
        if not self.parent.filter_string_var.get():
            self.parent.update_image_file_count()
        for text_file in self.parent.text_files:
            try:
                if not os.path.exists(text_file):
                    with open(text_file, 'w', encoding="utf-8") as file:
                        file.write(prefix_text)
                else:
                    with open(text_file, 'r+', encoding="utf-8") as file:
                        content = file.read()
                        file.seek(0, 0)
                        file.write(prefix_text + content)
            except Exception as e:
                messagebox.showerror("Error: prefix_text_files()", f"An error occurred while trying to prefix text in {text_file}.\n\n{e}")
        self.parent.cleanup_all_text_files(show_confirmation=False)
        self.parent.show_pair()
        messagebox.showinfo("Prefix", "Prefix completed successfully.")


#endregion
################################################################################################################################################
#region (3) Append


    def create_append_text_widgets_tab3(self):
        tab_frame = Frame(self.parent.tab3)
        tab_frame.pack(side='top', fill='both')
        button_frame = Frame(tab_frame)
        button_frame.pack(side='top', fill='x')
        append_label = Label(button_frame, width=8, text="Append:")
        append_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(append_label, "Enter the text you want to insert at the END of all text files\n\nCommas will be inserted as needed", 200, 6, 12)
        self.append_entry = ttk.Entry(button_frame, textvariable=self.parent.append_string_var)
        self.append_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.bind_entry_functions(self.append_entry)
        self.append_entry.bind('<Return>', lambda event: self.append_text_files())
        append_button = ttk.Button(button_frame, text="Go!", width=5, command=self.append_text_files)
        append_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(append_button, "Text files will be backup up", 200, 6, 12)
        clear_button = ttk.Button(button_frame, text="Clear", width=5, command=lambda: self.append_entry.delete(0, 'end'))
        clear_button.pack(side='left', anchor="n", pady=4)
        undo_button = ttk.Button(button_frame, text="Undo", width=5, command=self.parent.restore_backup)
        undo_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(undo_button, "Revert last action", 200, 6, 12)
        text_frame = Frame(tab_frame, borderwidth=0)
        text_frame.pack(side='top', fill="both")
        description_textbox = scrolledtext.ScrolledText(text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0",
            "Use this tool to append all text files in the selected directory with the entered text.\n\n"
            "This means that the entered text will appear at the end of each text file.\n\n"
            "If a filter is applied, only text files that match the filter will be affected."
        )
        description_textbox.config(state="disabled", wrap="word")


    def append_text_files(self):
        if not self.parent.check_if_directory():
            return
        append_text = self.parent.append_string_var.get()
        if not append_text:
            return
        if not append_text.startswith(', '):
            append_text = ', ' + append_text
        confirm = messagebox.askokcancel("Append", "This will append all text files with:\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(append_text))
        if not confirm:
            return
        self.parent.backup_text_files()
        if not self.parent.filter_string_var.get():
            self.parent.update_image_file_count()
        for text_file in self.parent.text_files:
            try:
                if not os.path.exists(text_file):
                    with open(text_file, 'w', encoding="utf-8") as file:
                        file.write(append_text)
                else:
                    with open(text_file, 'a', encoding="utf-8") as file:
                        file.write(append_text)
            except Exception as e:
                messagebox.showerror("Error: append_text_files()", f"An error occurred while trying to append text in {text_file}.\n\n{e}")
        self.parent.cleanup_all_text_files(show_confirmation=False)
        self.parent.show_pair()
        messagebox.showinfo("Append", "Append completed successfully.")


#endregion
################################################################################################################################################
#region (4) Auto-Tag


    def create_auto_tag_widgets_tab4(self):
        def invert_selection():
            for i in range(self.auto_tag_listbox.size()):
                if self.auto_tag_listbox.selection_includes(i):
                    self.auto_tag_listbox.selection_clear(i)
                else:
                    self.auto_tag_listbox.select_set(i)
            self.update_auto_tag_stats_label()

        def clear_selection():
            self.auto_tag_listbox.selection_clear(0, 'end')
            self.update_auto_tag_stats_label()

        def all_selection():
            self.auto_tag_listbox.select_set(0, 'end')
            self.update_auto_tag_stats_label()

        def copy_selection():
            _, extracted_tags = self.get_auto_tag_selection()
            if extracted_tags:
                self.auto_tag_listbox.clipboard_clear()
                self.auto_tag_listbox.clipboard_append(', '.join(extracted_tags))

        # Top Frame for Buttons
        top_frame = Frame(self.parent.tab4)
        top_frame.pack(fill='x')
        help_button = ttk.Button(top_frame, text="?", takefocus=False, width=2, command=self.show_auto_tag_help)
        help_button.pack(side='left')
        self.interrogation_stats_label = Label(top_frame, text="Total: 0  |  Selected: 0")
        self.interrogation_stats_label.pack(side='left')
        interrogate_button = ttk.Button(top_frame, text="Interrogate", takefocus=False, command=self.interrogate_image_tags)
        interrogate_button.pack(side='right')
        ToolTip.create(interrogate_button, "Interrogate the current image using the selected ONNX vision model.", 500, 6, 12)
        auto_insert_menubutton = ttk.Menubutton(top_frame, text="Auto-Insert", takefocus=False)
        auto_insert_menubutton.pack(side='right')
        auto_insert_menu = Menu(auto_insert_menubutton, tearoff=0)
        auto_insert_menu.add_radiobutton(label="Disable", variable=self.auto_insert_mode_var, value="disable")
        auto_insert_menu.add_separator()
        auto_insert_menu.add_radiobutton(label="Prefix", variable=self.auto_insert_mode_var, value="prefix")
        auto_insert_menu.add_radiobutton(label="Append", variable=self.auto_insert_mode_var, value="append")
        auto_insert_menu.add_radiobutton(label="Replace", variable=self.auto_insert_mode_var, value="replace")
        auto_insert_menubutton.config(menu=auto_insert_menu)
        batch_interrogate_checkbutton = ttk.Checkbutton(top_frame, text="Batch", takefocus=False, variable=self.batch_interrogate_images_var)
        batch_interrogate_checkbutton.pack(side='right')
        ToolTip.create(batch_interrogate_checkbutton, "Interrogate all images\nAn Auto-Insert mode must be selected", 200, 6, 12)
        # Main Frame
        widget_frame = Frame(self.parent.tab4)
        widget_frame.pack(fill='both', expand=True)

        # Main Paned Window
        paned_window = PanedWindow(self.parent.tab4, orient='horizontal', sashwidth=6, bg="#d0d0d0")
        paned_window.pack(fill='both', expand=True)

        # Listbox Frame
        listbox_frame = Frame(paned_window)
        paned_window.add(listbox_frame)

        listbox_y_scrollbar = Scrollbar(listbox_frame, orient="vertical")
        listbox_x_scrollbar = Scrollbar(listbox_frame, orient="horizontal")
        self.auto_tag_listbox = Listbox(listbox_frame, width=20, selectmode="extended", exportselection=False, yscrollcommand=listbox_y_scrollbar.set, xscrollcommand=listbox_x_scrollbar.set)
        self.auto_tag_listbox.bind('<<ListboxSelect>>', lambda event: self.update_auto_tag_stats_label())
        self.auto_tag_listbox.bind("<Button-3>", lambda event: listbox_context_menu.tk_popup(event.x_root, event.y_root))
        listbox_y_scrollbar.config(command=self.auto_tag_listbox.yview)
        listbox_x_scrollbar.config(command=self.auto_tag_listbox.xview)
        listbox_x_scrollbar.pack(side='bottom', fill='x')
        self.auto_tag_listbox.pack(side='left', fill='both', expand=True)
        listbox_y_scrollbar.pack(side='left', fill='y')
        # Listbox - Context Menu
        listbox_context_menu = Menu(self.auto_tag_listbox, tearoff=0)
        listbox_context_menu.add_command(label="Insert: Prefix", command=lambda: self.insert_listbox_selection(prefix=True))
        listbox_context_menu.add_command(label="Insert: Append", command=lambda: self.insert_listbox_selection(append=True))
        listbox_context_menu.add_command(label="Insert: Replace", command=lambda: self.insert_listbox_selection(replace=True))
        listbox_context_menu.add_separator()
        listbox_context_menu.add_command(label="Selection: Copy", command=copy_selection)
        listbox_context_menu.add_command(label="Selection: All", command=all_selection)
        listbox_context_menu.add_command(label="Selection: Invert", command=invert_selection)
        listbox_context_menu.add_command(label="Selection: Clear", command=clear_selection)
        listbox_context_menu.add_command(label="Selection: Add to MyTags", command=lambda: self.parent.add_to_custom_dictionary(origin="auto_tag"))
        # Control Frame
        control_frame = Frame(paned_window)
        paned_window.add(control_frame)
        # Model Selection
        model_selection_frame = Frame(control_frame)
        model_selection_frame.pack(side='top', fill='x', padx=2, pady=2)
        model_selection_label = Label(model_selection_frame, text="Model:", width=16, anchor="w")
        model_selection_label.pack(side='left')
        ToolTip.create(model_selection_label, "Select the ONNX vision model to use for interrogation", 200, 6, 12)
        self.get_onnx_model_list()
        self.auto_tag_model_combobox = ttk.Combobox(model_selection_frame, width=25, takefocus=False, state="readonly", values=list(self.onnx_model_dict.keys()))
        self.auto_tag_model_combobox.pack(side='right')
        self.set_auto_tag_combo_box()
        # General Threshold
        general_threshold_frame = Frame(control_frame)
        general_threshold_frame.pack(side='top', fill='x', padx=2, pady=2)
        general_threshold_label = Label(general_threshold_frame, text="General Threshold:", width=16, anchor="w")
        general_threshold_label.pack(side='left')
        ToolTip.create(general_threshold_label, "The minimum confidence threshold for general tags", 200, 6, 12)
        self.auto_tag_general_threshold_spinbox = ttk.Spinbox(general_threshold_frame, takefocus=False, from_=0, to=1, increment=0.01, width=8)
        self.auto_tag_general_threshold_spinbox.pack(side='right')
        self.auto_tag_general_threshold_spinbox.set(self.parent.onnx_tagger.general_threshold)
        # Character Threshold
        character_threshold_frame = Frame(control_frame)
        character_threshold_frame.pack(side='top', fill='x', padx=2, pady=2)
        character_threshold_label = Label(character_threshold_frame, text="Character Threshold:", width=16, anchor="w")
        character_threshold_label.pack(side='left')
        ToolTip.create(character_threshold_label, "The minimum confidence threshold for character tags", 200, 6, 12)
        self.auto_tag_character_threshold_spinbox = ttk.Spinbox(character_threshold_frame, takefocus=False, from_=0, to=1, increment=0.01, width=8)
        self.auto_tag_character_threshold_spinbox.pack(side='right')
        self.auto_tag_character_threshold_spinbox.set(self.parent.onnx_tagger.character_threshold)
        # Max Tags
        max_tags_frame = Frame(control_frame)
        max_tags_frame.pack(side='top', fill='x', padx=2, pady=2)
        max_tags_label = Label(max_tags_frame, text="Max Tags:", width=16, anchor="w")
        max_tags_label.pack(side='left')
        ToolTip.create(max_tags_label, "The maximum number of tags that will be generated\nAdditional tags will be ignored", 200, 6, 12)
        self.auto_tag_max_tags_spinbox = ttk.Spinbox(max_tags_frame, takefocus=False, from_=1, to=999, increment=1, width=8)
        self.auto_tag_max_tags_spinbox.pack(side='right')
        self.auto_tag_max_tags_spinbox.set(40)
        # Checkbutton Frame
        checkbutton_frame = Frame(control_frame)
        checkbutton_frame.pack(side='top', fill='x', padx=2, pady=2)
        # Keep (_)
        self.auto_tag_keep_underscore_checkbutton = ttk.Checkbutton(checkbutton_frame, text="Keep: _", takefocus=False, variable=self.parent.onnx_tagger.keep_underscore)
        self.auto_tag_keep_underscore_checkbutton.pack(side='left', anchor='w', padx=2, pady=2)
        ToolTip.create(self.auto_tag_keep_underscore_checkbutton, "If enabled, Underscores will be kept in tags, otherwise they will be replaced with a space\n\nExample: Keep = simple_background, Replace = simple background", 200, 6, 12)
        # Keep (\)
        self.auto_tag_keep_escape_checkbutton = ttk.Checkbutton(checkbutton_frame, text="Keep: \\", takefocus=False, variable=self.parent.onnx_tagger.keep_escape_character)
        self.auto_tag_keep_escape_checkbutton.pack(side='left', anchor='w', padx=2, pady=2)
        ToolTip.create(self.auto_tag_keep_escape_checkbutton, "If enabled, the escape character will be kept in tags\n\nExample: Keep = \(cat\), Replace = (cat)", 200, 6, 12)
        # Entry Frame
        entry_frame = Frame(control_frame)
        entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        excluded_entry_frame = Frame(entry_frame)
        excluded_entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        excluded_tags_label = Label(excluded_entry_frame, text="Exclude:", width=9, anchor="w")
        excluded_tags_label.pack(side='left')
        ToolTip.create(excluded_tags_label, "Enter tags that will be excluded from interrogation\nSeparate tags with commas", 200, 6, 12)
        self.excluded_tags_entry = ttk.Entry(excluded_entry_frame, width=5)
        self.excluded_tags_entry.pack(side='left', fill='both', expand=True)
        self.bind_entry_functions(self.excluded_tags_entry)
        auto_exclude_tags_checkbutton = ttk.Checkbutton(excluded_entry_frame, text="Auto", takefocus=False, variable=self.auto_exclude_tags_var)
        auto_exclude_tags_checkbutton.pack(side='left', anchor='w', padx=2, pady=2)
        self.auto_exclude_tags_tooltip = ToolTip.create(auto_exclude_tags_checkbutton, "Automatically exclude tags that are already in the text box", 200, 6, 12)
        keep_entry_frame = Frame(entry_frame)
        keep_entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        keep_tags_label = Label(keep_entry_frame, text="Keep:", width=9, anchor="w")
        keep_tags_label.pack(side='left')
        ToolTip.create(keep_tags_label, "Enter tags that will always be included in interrogation\nSeparate tags with commas", 200, 6, 12)
        self.keep_tags_entry = ttk.Entry(keep_entry_frame, width=25)
        self.keep_tags_entry.pack(side='left', fill='both', expand=True)
        self.bind_entry_functions(self.keep_tags_entry)
        replace_entry_frame = Frame(entry_frame)
        replace_entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        replace_tags_label = Label(replace_entry_frame, text="Replace:", width=9, anchor="w")
        replace_tags_label.pack(side='left')
        ToolTip.create(replace_tags_label, "Enter tags that will be replaced during interrogation\nSeparate tags with commas, the index of the tag in the 'Replace' entry will be used to replace the tag in the 'With' entry", 200, 6, 12)
        self.replace_tags_entry = ttk.Entry(replace_entry_frame, width=1)
        self.replace_tags_entry.pack(side='left', fill='both', expand=True)
        self.bind_entry_functions(self.replace_tags_entry)
        replace_with_tags_label = Label(replace_entry_frame, text="With:", anchor="w")
        replace_with_tags_label.pack(side='left')
        ToolTip.create(replace_with_tags_label, "Enter tags that will replace the tags entered in the 'Replace' entry\nSeparate tags with commas, ensure tags match the index of the tags in the 'Replace' entry", 200, 6, 12)
        self.replace_with_tags_entry = ttk.Entry(replace_entry_frame, width=1)
        self.replace_with_tags_entry.pack(side='left', fill='both', expand=True)
        self.bind_entry_functions(self.replace_with_tags_entry)
        # Selection Button Frame
        button_frame = ttk.LabelFrame(control_frame, text="Selection")
        button_frame.pack(side="bottom", fill='both', padx=2)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        # Selection Buttons
        insert_selection_prefix_button = ttk.Button(button_frame, text="Prefix", command=lambda: self.insert_listbox_selection(prefix=True))
        insert_selection_prefix_button.grid(row=0, column=0, sticky='ew', pady=2)
        insert_selection_prefix_button.bind("<Button-3>", lambda event: self.insert_listbox_selection(replace=True))
        ToolTip.create(insert_selection_prefix_button, "Insert the selected tags at the START of the text box\nRight-click to replace the current tags", 500, 6, 12)
        insert_selection_append_button = ttk.Button(button_frame, text="Append", command=lambda: self.insert_listbox_selection(append=True))
        insert_selection_append_button.grid(row=0, column=1, sticky='ew', pady=2)
        insert_selection_append_button.bind("<Button-3>", lambda event: self.insert_listbox_selection(replace=True))
        ToolTip.create(insert_selection_append_button, "Insert the selected tags at the END of the text box\nRight-click to replace the current tags", 500, 6, 12)
        copy_button = ttk.Button(button_frame, text="Copy", command=copy_selection)
        copy_button.grid(row=0, column=2, sticky='ew', pady=2)
        ToolTip.create(copy_button, "Copy the selected tags to the clipboard", 500, 6, 12)
        all_button = ttk.Button(button_frame, text="All", command=all_selection)
        all_button.grid(row=1, column=0, sticky='ew', pady=2)
        ToolTip.create(all_button, "Select all tags", 500, 6, 12)
        invert_button = ttk.Button(button_frame, text="Invert", command=invert_selection)
        invert_button.grid(row=1, column=1, sticky='ew', pady=2)
        ToolTip.create(invert_button, "Invert the current selection", 500, 6, 12)
        clear_button = ttk.Button(button_frame, text="Clear", command=clear_selection)
        clear_button.grid(row=1, column=2, sticky='ew', pady=2)
        ToolTip.create(clear_button, "Clear the current selection", 500, 6, 12)


    def show_auto_tag_help(self):
        confirm = messagebox.askokcancel("Auto-Tag Help",
            "Auto-Tagging uses an ONNX vision model to analyze images and generate tags displayed in the listbox.\n\n"
            "Download additional models from:\n\nhttps://huggingface.co/SmilingWolf\n\n"
            "Place models in subfolders within the 'onnx_models' directory, located in the same folder as this program. The subfolder name will be used as the model name.\n\n"
            "Each model subfolder should contain a 'model.onnx' file and a 'selected_tags.csv' file.\n\n"
            "Restart the program to load new models.\n\n"
            "Example:\n"
            "img-txt_viewer/\n"
            "  └── onnx_models/\n"
            "      └── wd-v1-4-moat-tagger-v2/\n"
            "          ├── model.onnx\n"
            "          └── selected_tags.csv\n\n"
            "Auto-Tagging was primarily tested with the 'wd-v1-4-moat-tagger-v2' model.\n\nCopy URL to clipboard?"
        )
        if confirm:
            self.parent.text_box.clipboard_clear()
            self.parent.text_box.clipboard_append("https://huggingface.co/SmilingWolf")


    def update_auto_tag_stats_label(self):
        total_tags = self.auto_tag_listbox.size()
        selected_tags = len(self.auto_tag_listbox.curselection())
        selected_tags_padded = str(selected_tags).zfill(len(str(total_tags)))
        self.interrogation_stats_label.config(text=f"Total: {total_tags}  |  Selected: {selected_tags_padded}")


    def insert_listbox_selection(self, prefix=False, append=False, replace=False):
        selected_items, extracted_tags = self.get_auto_tag_selection()
        if not selected_items:
            return
        current_text = self.parent.text_box.get("1.0", "end-1c").strip(', ')
        if replace:
            new_text = ', '.join(extracted_tags)
        elif prefix:
            new_text = ', '.join(extracted_tags) + ', ' + current_text
        elif append:
            new_text = current_text + ', ' + ', '.join(extracted_tags)
        else:
            new_text = ', '.join(extracted_tags)
        new_text = new_text.strip(', ')
        self.parent.text_box.delete("1.0", "end")
        self.parent.text_box.insert("1.0", new_text)


    def get_auto_tag_selection(self):
        selected_items = [self.auto_tag_listbox.get(i) for i in self.auto_tag_listbox.curselection()]
        extracted_tags = [item.split(': ', 1)[-1] for item in selected_items]
        return selected_items, extracted_tags


    def update_tag_options(self, current_tags=None):
        self.parent.onnx_tagger.exclude_tags.clear()
        self.parent.onnx_tagger.keep_tags.clear()
        self.parent.onnx_tagger.replace_tag_dict.clear()
        excluded_tags = [tag.strip().replace(' ', '_') for tag in self.excluded_tags_entry.get().strip().split(',')]
        if self.auto_exclude_tags_var.get():
            if current_tags is not None:
                source_tags = current_tags.strip()
            else:
                source_tags = self.parent.text_box.get("1.0", "end-1c").strip()
            excluded_tags.extend(tag.strip().replace(' ', '_') for tag in source_tags.split(','))
        self.parent.onnx_tagger.exclude_tags = [tag.strip() for tag in excluded_tags if tag.strip()]
        keep_tags = self.keep_tags_entry.get().strip().split(',')
        self.parent.onnx_tagger.keep_tags = [tag.strip() for tag in keep_tags if tag.strip()]
        replace_tags = self.replace_tags_entry.get().strip().split(',')
        replace_with_tags = self.replace_with_tags_entry.get().strip().split(',')
        self.parent.onnx_tagger.replace_tag_dict = {tag.strip(): replace_with_tags[i].strip() for i, tag in enumerate(replace_tags) if tag.strip() and i < len(replace_with_tags) and replace_with_tags[i].strip()}


    def update_tag_thresholds(self):
        def validate_spinbox_value(spinbox, default_value, from_, to):
            try:
                value = float(spinbox.get())
                if from_ <= value <= to:
                    return value
            except ValueError:
                pass
            spinbox.set(default_value)
            return default_value

        validate_spinbox_value(self.auto_tag_max_tags_spinbox, 40, 1, 999)
        self.parent.onnx_tagger.general_threshold = validate_spinbox_value(self.auto_tag_general_threshold_spinbox, 0.35, 0, 1)
        self.parent.onnx_tagger.character_threshold = validate_spinbox_value(self.auto_tag_character_threshold_spinbox, 0.85, 0, 1)


    def interrogate_image_tags(self):
        self.parent.text_notebook.select(self.parent.tab4)
        if self.batch_interrogate_images_var.get():
            self.batch_interrogate_images()
            return
        image_path = self.parent.image_files[self.parent.current_index]
        selected_model_path = self.onnx_model_dict.get(self.auto_tag_model_combobox.get())
        if not selected_model_path or not os.path.exists(selected_model_path):
            confirm = messagebox.askyesno("Error", f"Model file not found: {selected_model_path}\n\nWould you like to view the Auto-Tag Help?")
            if confirm:
                self.show_auto_tag_help()
            return
        self.update_tag_thresholds()
        self.update_tag_options()
        tag_list, tag_dict = self.parent.onnx_tagger.tag_image(image_path, model_path=selected_model_path)
        max_tags = int(self.auto_tag_max_tags_spinbox.get())
        tag_list = tag_list[:max_tags]
        tag_dict = {k: v for k, v in list(tag_dict.items())[:max_tags]}
        self.populate_auto_tag_listbox(tag_dict)
        self.auto_insert_tags(tag_list)


    def populate_auto_tag_listbox(self, tag_dict):
        self.auto_tag_listbox.delete(0, "end")
        if not tag_dict:
            self.update_auto_tag_stats_label()
            return
        max_length = max(len(f"{confidence:.2f}") for confidence, _ in tag_dict.values())
        for tag, (confidence, category) in tag_dict.items():
            padded_score = f"{confidence:.2f}".ljust(max_length, '0')
            self.auto_tag_listbox.insert("end", f" {padded_score}: {tag}")
            if category == "character":
                self.auto_tag_listbox.itemconfig("end", {'fg': '#148632'})
            if category == "keep":
                self.auto_tag_listbox.itemconfig("end", {'fg': '#c00004'})
        self.update_auto_tag_stats_label()


    def auto_insert_tags(self, tags):
        mode = self.auto_insert_mode_var.get()
        if mode == "disable":
            return
        tags_str = ', '.join(tags)
        current_text = self.parent.text_box.get("1.0", "end-1c")
        if mode == "prefix":
            new_text = tags_str + ', ' + current_text if current_text else tags_str
        elif mode == "append":
            new_text = current_text + ', ' + tags_str if current_text else tags_str
        elif mode == "replace":
            new_text = tags_str
        else:
            return
        self.parent.text_box.delete("1.0", "end")
        self.parent.text_box.insert("1.0", new_text)


    def get_onnx_model_list(self):
        model_dict = {}
        for onnx_model_path, dirs, files in os.walk(self.parent.onnx_models_dir):
            if "model.onnx" in files and "selected_tags.csv" in files:
                folder_name = os.path.basename(onnx_model_path)
                model_file_path = os.path.join(onnx_model_path, "model.onnx")
                model_dict[folder_name] = model_file_path
        self.onnx_model_dict = model_dict


    def set_auto_tag_combo_box(self):
        try:
            first_model_key = next(iter(self.onnx_model_dict.keys()), None)
        except Exception:
            first_model_key = None
        if first_model_key:
            self.auto_tag_model_combobox.set(first_model_key)


    def batch_interrogate_images(self):
        def stop_batch_process():
            self.stop_batch = True
            popup.destroy()
            messagebox.showinfo("Batch Interrogate", f"Batch interrogation stopped\n\n{index} out of {total_images} images were interrogated")

        if self.auto_insert_mode_var.get() == "disable":
            messagebox.showinfo("Batch Interrogate", "Auto-Insert must be enabled to use Batch Interrogate")
            return
        try:
            confirm = messagebox.askyesno("Batch Interrogate", "Interrogate all images in the current directory?")
            if not confirm:
                return
            self.stop_batch = False
            popup = Toplevel(self.root)
            popup.title("Batch Interrogate")
            popup.geometry("300x150")
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() - popup.winfo_reqwidth()) // 2
            y = (self.root.winfo_screenheight() - popup.winfo_reqheight()) // 2
            popup.geometry(f"+{x}+{y}")
            label = Label(popup, text="Starting...")
            label.pack(expand=True)
            progress = ttk.Progressbar(popup, orient="horizontal", length=200, mode="determinate")
            progress.pack(pady=10)
            stop_button = ttk.Button(popup, text="Stop", command=stop_batch_process)
            stop_button.pack(pady=10)
            popup.transient(self.root)
            popup.grab_set()
            self.root.update()
            popup.protocol("WM_DELETE_WINDOW", stop_batch_process)
            selected_model_path = self.onnx_model_dict.get(self.auto_tag_model_combobox.get())
            if not selected_model_path or not os.path.exists(selected_model_path):
                confirm = messagebox.askyesno("Error", f"Model file not found: {selected_model_path}\n\nWould you like to view the Auto-Tag Help?")
                if confirm:
                    self.show_auto_tag_help()
                popup.destroy()
                return
            self.update_tag_thresholds()
            max_tags = int(self.auto_tag_max_tags_spinbox.get())
            total_images = len(self.parent.image_files)
            progress["maximum"] = total_images
            start_time = time.time()
            for index, (image_path, text_file_path) in enumerate(zip(self.parent.image_files, self.parent.text_files), start=1):
                if self.stop_batch:
                    break
                current_text = ""
                if os.path.exists(text_file_path):
                    with open(text_file_path, "r", encoding="utf-8") as f:
                        current_text = f.read().strip()
                if self.auto_exclude_tags_var.get() and self.batch_interrogate_images_var.get():
                    self.update_tag_options(current_tags=current_text)
                else:
                    self.update_tag_options()
                tag_list, tag_dict = self.parent.onnx_tagger.tag_image(image_path, model_path=selected_model_path)
                tag_list = tag_list[:max_tags]
                tag_dict = {k: v for k, v in list(tag_dict.items())[:max_tags]}
                self.auto_insert_batch_tags(tag_list, text_file_path)
                elapsed_time = time.time() - start_time
                avg_time_per_image = elapsed_time / index if index > 0 else 0
                remaining_images = total_images - index
                eta_seconds = avg_time_per_image * remaining_images
                eta_formatted = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
                label.config(text=f"Working... {index} out of {total_images}\nETA: {eta_formatted}")
                progress["value"] = index
                self.root.update()
            popup.destroy()
            if not self.stop_batch:
                messagebox.showinfo("Batch Interrogate", f"Batch interrogation complete\n\n{total_images} images were interrogated")
        except TclError:
            pass
        finally:
            self.parent.refresh_text_box()
            if popup:
                popup.destroy()


    def auto_insert_batch_tags(self, tags, text_file_path):
        mode = self.auto_insert_mode_var.get()
        if mode == "disable":
            return
        tags_str = ', '.join(tags)
        current_text = ''
        if os.path.exists(text_file_path):
            with open(text_file_path, 'r', encoding='utf-8') as f:
                current_text = f.read().strip()
        else:
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write('')
        if mode == "prefix":
            new_text = tags_str + ', ' + current_text if current_text else tags_str
        elif mode == "append":
            new_text = current_text + ', ' + tags_str if current_text else tags_str
        elif mode == "replace":
            new_text = tags_str
        else:
            return
        new_text = new_text.strip(', ')
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write(new_text)


#endregion
################################################################################################################################################
#region (5) Filter


    def create_filter_text_image_pairs_widgets_tab5(self):
        tab_frame = Frame(self.parent.tab5)
        tab_frame.pack(side='top', fill='both')
        button_frame = Frame(tab_frame)
        button_frame.pack(side='top', fill='x')
        self.filter_label = Label(button_frame, width=8, text="Filter:")
        self.filter_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.filter_label, "Enter the EXACT text you want to filter by\nThis will filter all img-txt pairs based on the provided text, see below for more info", 200, 6, 12)
        self.filter_entry = ttk.Entry(button_frame, width=11, textvariable=self.parent.filter_string_var)
        self.filter_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.bind_entry_functions(self.filter_entry)
        self.filter_entry.bind('<Return>', lambda event: self.filter_text_image_pairs())
        self.filter_button = ttk.Button(button_frame, text="Go!", width=5, command=self.filter_text_image_pairs)
        self.filter_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.filter_button, "Text files will be filtered based on the entered text", 200, 6, 12)
        self.revert_filter_button = ttk.Button(button_frame, text="Clear", width=5, command=lambda: (self.revert_text_image_filter(clear=True)))
        self.revert_filter_button.pack(side='left', anchor="n", pady=4)
        self.revert_filter_button_tooltip = ToolTip.create(self.revert_filter_button, "Clear any filtering applied", 200, 6, 12)
        self.regex_filter_checkbutton = ttk.Checkbutton(button_frame, text="Regex", variable=self.parent.filter_use_regex_var)
        self.regex_filter_checkbutton.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.regex_filter_checkbutton, "Use Regular Expressions for filtering", 200, 6, 12)
        self.empty_files_checkbutton = ttk.Checkbutton(button_frame, text="Empty", variable=self.parent.filter_empty_files_var, command=self.toggle_empty_files_filter)
        self.empty_files_checkbutton.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.empty_files_checkbutton, "Check this to show only empty text files\n\nImages without a text pair are also considered as empty", 200, 6, 12)
        text_frame = Frame(tab_frame, borderwidth=0)
        text_frame.pack(side='top', fill="both")
        description_textbox = scrolledtext.ScrolledText(text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0",
            "This tool will filter all img-txt pairs based on the provided text.\n\n"
            "Enter any string of text to display only img-txt pairs containing that text.\n"
            "Use ' + ' to include multiple strings when filtering.\n"
            "Use '!' before the text to exclude any pairs containing that text.\n\n"
            "Examples:\n"
            "'dog' (shows only pairs containing the text dog)\n"
            "'!dog' (removes all pairs containing the text dog)\n"
            "'!dog + cat' (remove dog pairs, display cat pairs)"
        )
        description_textbox.config(state="disabled", wrap="word")


    def filter_text_image_pairs(self):  # Filter
        if not self.parent.check_if_directory():
            return
        if not self.parent.filter_empty_files_var.get():
            self.revert_text_image_filter(silent=True)
        filter_string = self.parent.filter_string_var.get()
        if not filter_string and not self.parent.filter_empty_files_var.get():
            self.parent.image_index_entry.delete(0, "end")
            self.parent.image_index_entry.insert(0, "1")
            return
        self.filtered_image_files = []
        self.filtered_text_files = []
        for image_file in self.parent.image_files:
            text_file = os.path.splitext(image_file)[0] + ".txt"
            filedata = ""
            try:
                with open(text_file, 'r', encoding="utf-8") as file:
                    filedata = file.read()
            except FileNotFoundError:
                text_file = text_file
            if self.parent.filter_empty_files_var.get():
                if not filedata.strip():
                    self.filtered_image_files.append(image_file)
                    self.filtered_text_files.append(text_file)
            else:
                if self.parent.filter_use_regex_var.get():
                    if re.search(filter_string, filedata):
                        self.filtered_image_files.append(image_file)
                        self.filtered_text_files.append(text_file)
                else:
                    filters = filter_string.split(' + ')
                    match = True
                    for filter in filters:
                        if filter.startswith('!'):
                            if filter[1:] in filedata:
                                match = False
                                break
                        elif filter not in filedata:
                            match = False
                            break
                    if match:
                        self.filtered_image_files.append(image_file)
                        self.filtered_text_files.append(text_file)
        if not self.filtered_image_files:
            messagebox.showinfo("Filter", f"0 images found matching the filter:\n\n{filter_string}")
            return
        self.filter_is_active = True
        self.parent.image_files = self.filtered_image_files
        self.parent.text_files = self.filtered_text_files
        if hasattr(self, 'total_images_label'):
            self.parent.total_images_label.config(text=f"of {len(self.parent.image_files)}")
        self.parent.current_index = 0
        self.parent.show_pair()
        messagebox.showinfo("Filter", f"Filter applied successfully.\n\n{len(self.parent.image_files)} images found.")
        self.revert_filter_button.config(style="Red.TButton")
        self.revert_filter_button_tooltip.config(text="Filter is active\n\nClear any filtering applied")
        self.parent.update_total_image_label()



    def revert_text_image_filter(self, clear=None, silent=False): # Filter
        last_index = self.parent.current_index
        if clear:
            self.parent.filter_string_var.set("")
            self.parent.filter_use_regex_var.set(False)
            self.parent.image_index_entry.delete(0, "end")
            self.parent.image_index_entry.insert(0, last_index + 1)
        self.parent.update_image_file_count()
        self.parent.current_index = last_index if last_index < len(self.parent.image_files) else 0
        self.parent.show_pair()
        if not silent:
            messagebox.showinfo("Filter", "Filter has been cleared.")
        self.filter_is_active = False
        self.revert_filter_button.config(style="")
        self.revert_filter_button_tooltip.config(text="Filter is inactive\n\nClear any filtering applied")
        self.parent.filter_empty_files_var.set(False)
        if self.parent.filter_empty_files_var.get():
            self.toggle_filter_widgets(state=True)
        else:
            self.toggle_filter_widgets(state=False)


    def toggle_empty_files_filter(self): # Filter
        if self.parent.filter_empty_files_var.get():
            self.parent.image_index_entry.delete(0, "end")
            self.parent.image_index_entry.insert(0, 1)
            self.parent.filter_string_var.set("")
            self.filter_text_image_pairs()
            self.parent.filter_use_regex_var.set(False)
            self.toggle_filter_widgets(state=True)
        else:
            self.revert_text_image_filter(silent=True)
            self.toggle_filter_widgets(state=False)


    def toggle_filter_widgets(self, state): # Filter
            if state:
                for widget in [self.filter_label, self.filter_entry, self.filter_button, self.regex_filter_checkbutton]:
                    widget.config(state="disabled")
            else:
                for widget in [self.filter_label, self.filter_entry, self.filter_button, self.regex_filter_checkbutton]:
                    widget.config(state="normal")


#endregion
################################################################################################################################################
#region (6) Highlight


    def create_custom_active_highlight_widgets_tab6(self):
        tab_frame = Frame(self.parent.tab6)
        tab_frame.pack(side='top', fill='both')
        button_frame = Frame(tab_frame)
        button_frame.pack(side='top', fill='x')
        highlight_label = Label(button_frame, width=8, text="Highlight:")
        highlight_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(highlight_label, "Enter the text you want to highlight\nUse ' + ' to highlight multiple strings of text\n\nExample: dog + cat", 200, 6, 12)
        self.highlight_entry = ttk.Entry(button_frame, textvariable=self.parent.custom_highlight_string_var)
        self.highlight_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.bind_entry_functions(self.highlight_entry)
        self.highlight_entry.bind('<KeyRelease>', lambda event: self.parent.highlight_custom_string())
        highlight_button = ttk.Button(button_frame, text="Go!", width=5, command=self.parent.highlight_custom_string)
        highlight_button.pack(side='left', anchor="n", pady=4)
        clear_button = ttk.Button(button_frame, text="Clear", width=5, command=self.clear_highlight_tab)
        clear_button.pack(side='left', anchor="n", pady=4)
        self.regex_highlight_checkbutton = ttk.Checkbutton(button_frame, text="Regex", variable=self.parent.highlight_use_regex_var)
        self.regex_highlight_checkbutton.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.regex_highlight_checkbutton, "Use Regular Expressions for highlighting text", 200, 6, 12)
        text_frame = Frame(tab_frame, borderwidth=0)
        text_frame.pack(side='top', fill="both")
        description_textbox = scrolledtext.ScrolledText(text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0",
            "Enter the text you want to highlight each time you move to a new img-txt pair.\n\n"
            "Use ' + ' to highlight multiple strings of text\n\n"
            "Example: dog + cat"
        )
        description_textbox.config(state="disabled", wrap="word")


    def clear_highlight_tab(self):
        self.highlight_entry.delete(0, 'end')
        self.parent.highlight_use_regex_var.set(False)


#endregion
################################################################################################################################################
#region (7) Font


    def create_font_widgets_tab7(self, event=None):
        def set_font_and_size(font, size):
            if font and size:
                size = int(size)
                self.parent.text_box.config(font=(font, size))
                self.font_size_label.config(text=f"Size: {size}")
                font_box_tooltip.config(text=f"{font}")
        def reset_to_defaults():
            self.parent.font_var.set(self.parent.default_font)
            self.size_scale.set(self.parent.default_font_size)
            set_font_and_size(self.parent.default_font, self.parent.default_font_size)
        font_label = Label(self.parent.tab7, width=8, text="Font:")
        font_label.pack(side="left", anchor="n", pady=4)
        ToolTip.create(font_label, "Recommended Fonts: Courier New, Ariel, Consolas, Segoe UI", 200, 6, 12)
        font_box = ttk.Combobox(self.parent.tab7, textvariable=self.parent.font_var, width=4, takefocus=False, state="readonly", values=list(font.families()))
        font_box.set(self.parent.current_font_name)
        font_box.bind("<<ComboboxSelected>>", lambda event: set_font_and_size(self.parent.font_var.get(), self.size_scale.get()))
        font_box_tooltip = ToolTip.create(font_box, f"{self.parent.current_font_name}", 200, 6, 12)
        font_box.pack(side="left", anchor="n", pady=4, fill="x", expand=True)
        self.font_size_label = Label(self.parent.tab7, text=f"Size: {self.parent.font_size_var.get()}", width=14)
        self.font_size_label.pack(side="left", anchor="n", pady=4)
        ToolTip.create(self.font_size_label, "Default size: 10", 200, 6, 12)
        self.size_scale = ttk.Scale(self.parent.tab7, from_=6, to=24, variable=self.parent.font_size_var, takefocus=False)
        self.size_scale.set(self.parent.current_font_size)
        self.size_scale.bind("<B1-Motion>", lambda event: set_font_and_size(self.parent.font_var.get(), self.size_scale.get()))
        self.size_scale.pack(side="left", anchor="n", pady=4, fill="x", expand=True)
        reset_button = ttk.Button(self.parent.tab7, text="Reset", width=5, takefocus=False, command=reset_to_defaults)
        reset_button.pack(side="left", anchor="n", pady=4)


#endregion
################################################################################################################################################
#region (8) MyTags


    def create_custom_dictionary_widgets_tab8(self):
        # LOAD
        def load_tag_file():
            with open(self.parent.my_tags_csv, 'r', encoding='utf-8') as file:
                content = self.parent.remove_extra_newlines(file.read())
                tags = content.split('\n')
                for tag in tags:
                    if tag.strip():
                        self.custom_dictionary_listbox.insert('end', tag.strip())
        # SAVE
        def save():
            tags = self.custom_dictionary_listbox.get(0, 'end')
            content = '\n'.join(tags) + '\n'
            with open(self.parent.my_tags_csv, 'w', encoding='utf-8') as file:
                file.write(content)
            self.root.after(100, self.parent.refresh_custom_dictionary)
        # ADD
        def add_tag():
            tag = tag_entry.get().strip()
            if tag:
                self.custom_dictionary_listbox.insert('end', tag)
                tag_entry.delete(0, 'end')
        # REMOVE
        def remove_tag():
            listbox = self.custom_dictionary_listbox
            selected_indices = listbox.curselection()
            if not selected_indices:
                return
            for index in reversed(selected_indices):
                listbox.delete(index)
        # EDIT
        def edit_tag():
            listbox = self.custom_dictionary_listbox
            selected_indices = listbox.curselection()
            if not selected_indices:
                return
            index = selected_indices[0]
            tag = listbox.get(index)
            tag_entry.delete(0, 'end')
            tag_entry.insert(0, tag)
            listbox.delete(index)
        # INSERT
        def insert_tag(listbox, position='start'):
            selected_indices = listbox.curselection()
            if not selected_indices:
                return
            for index in selected_indices:
                tag = listbox.get(index)
                current_text = self.parent.text_box.get('1.0', 'end-1c')
                separator = ', ' if current_text else ''
                if position == 'start':
                    self.parent.text_box.insert('1.0', f"{tag}{separator}")
                else:  # 'end'
                    self.parent.text_box.insert('end', f"{separator}{tag}")
        # MOVE
        def move(listbox, direction):
            selected_indices = listbox.curselection()
            if not selected_indices:
                return
            delta = -1 if direction == 'up' else 1
            for index in (selected_indices if direction == 'up' else reversed(selected_indices)):
                new_index = index + delta
                if 0 <= new_index < listbox.size():
                    tag = listbox.get(index)
                    listbox.delete(index)
                    listbox.insert(new_index, tag)
                    listbox.selection_set(new_index)
        # ADD TO MYTAGS
        def add_to_mytags():
            selected_indices = self.all_tags_listbox.curselection()
            if not selected_indices:
                return
            existing_tags = set(self.custom_dictionary_listbox.get(0, 'end'))
            for index in selected_indices:
                tag = self.all_tags_listbox.get(index)
                if tag not in existing_tags:
                    self.custom_dictionary_listbox.insert('end', tag)
        # CONTEXT MENU
        def show_context_menu(event):
            listbox = event.widget
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
                    menu.add_command(label="Prefix", command=lambda: insert_tag(listbox, 'start'))
                    menu.add_command(label="Append", command=lambda: insert_tag(listbox, 'end'))
                    menu.add_separator()
                    menu.add_command(label="Edit", command=edit_tag)
                    menu.add_command(label="Remove", command=remove_tag)
                    menu.add_separator()
                    menu.add_command(label="Move Up", command=lambda: move(listbox, 'up'))
                    menu.add_command(label="Move Down", command=lambda: move(listbox, 'down'))
                else:
                    menu.add_command(label="Prefix", command=lambda: insert_tag(listbox, 'start'))
                    menu.add_command(label="Append", command=lambda: insert_tag(listbox, 'end'))
                    menu.add_separator()
                    menu.add_command(label="Add to MyTags", command=add_to_mytags)
                    menu.add_separator()
                    menu.add_command(label="Refresh", command=self.refresh_all_tags_listbox)
                menu.add_separator()
                menu.add_command(label="Selection: All", command=select_all)
                menu.add_command(label="Selection: Invert", command=invert_selection)
                menu.tk_popup(event.x_root, event.y_root)
        # INTERFACE
        self.parent.create_custom_dictionary(refresh=False)
        tab_frame = Frame(self.parent.tab8)
        tab_frame.pack(side='top', fill='both', expand=True)
        tab_frame.grid_rowconfigure(1, weight=1)
        tab_frame.grid_columnconfigure(0, weight=1)
        # Top Row - Row 0
        top_frame = Frame(tab_frame)
        top_frame.grid(row=0, column=0, sticky='ew')
        help_button = ttk.Button(top_frame, text="?", takefocus=False, width=2, command=self.show_my_tags_help)
        help_button.pack(side='left')
        options_menu = ttk.Menubutton(top_frame, text="Options", takefocus=False)
        options_menu.pack(side='left')
        options_menu.menu = Menu(options_menu, tearoff=0)
        options_menu["menu"] = options_menu.menu
        options_menu.menu.add_checkbutton(label="Use: MyTags", variable=self.parent.use_mytags_var, command=self.parent.refresh_custom_dictionary)
        options_menu.menu.add_checkbutton(label="Show: All Tags", variable=self.show_all_tags_var, command=self.toggle_all_tags_listbox)
        options_menu.menu.add_separator()
        options_menu.menu.add_command(label="Refresh: My Tags", command=load_tag_file)
        options_menu.menu.add_command(label="Refresh: All Tags", command=self.refresh_all_tags_listbox)
        options_menu.menu.add_separator()
        options_menu.menu.add_checkbutton(label="Hide: My Tags - Controls", variable=self.hide_mytags_controls_var, command=self.toggle_mytags_controls)
        options_menu.menu.add_checkbutton(label="Hide: All Tags - Controls", variable=self.hide_alltags_controls_var, command=self.toggle_alltags_controls)
        options_menu.menu.add_separator()
        options_menu.menu.add_command(label="Open MyTags File...", command=lambda: self.parent.open_textfile(self.parent.my_tags_csv))
        # entry_frame
        entry_frame = Frame(top_frame)
        entry_frame.pack(side='left', fill='x', expand=True, pady=4)
        tag_entry = ttk.Entry(entry_frame)
        tag_entry.pack(side='left', fill='x', expand=True)
        tag_entry.bind('<Return>', lambda event: add_tag())
        add_button = ttk.Button(entry_frame, text="Add", command=add_tag)
        add_button.pack(side='left')
        save_button = ttk.Button(top_frame, text="Save Tags", takefocus=False, command=save)
        save_button.pack(side='right')
        # Middle Row
        self.text_frame = ttk.PanedWindow(tab_frame, orient='horizontal')
        self.text_frame.grid(row=1, column=0, sticky='nsew')
        # My Tags section
        my_tags_frame = Frame(self.text_frame)
        header_frame = Frame(my_tags_frame)
        header_frame.grid(row=0, column=0, sticky='ew', padx=2, pady=(2,0))
        my_tags_label = ttk.Label(header_frame, text="My Tags:")
        my_tags_label.pack(side='left', padx=(0,5))
        self.custom_dictionary_listbox = Listbox(my_tags_frame, selectmode='extended')
        self.custom_dictionary_listbox.grid(row=1, column=0, sticky='nsew')
        my_tags_frame.grid_rowconfigure(1, weight=1)
        my_tags_frame.grid_columnconfigure(0, weight=1)
        self.custom_dictionary_listbox.bind("<Button-3>", show_context_menu)
        self.custom_dictionary_listbox.bind("<Double-Button-1>", lambda event: insert_tag(self.custom_dictionary_listbox, 'end'))
        # Buttons
        self.my_tags_button_frame = Frame(my_tags_frame)
        self.my_tags_button_frame.grid(row=2, column=0, sticky='ew', pady=(2,0))
        self.my_tags_button_frame.grid_columnconfigure(0, weight=1)
        self.my_tags_button_frame.grid_columnconfigure(1, weight=1)
        prefix_button = ttk.Button(self.my_tags_button_frame, text="Prefix", command=lambda: insert_tag(self.custom_dictionary_listbox, 'start'))
        prefix_button.grid(row=0, column=0, sticky='ew', padx=2)
        append_button = ttk.Button(self.my_tags_button_frame, text="Append", command=lambda: insert_tag(self.custom_dictionary_listbox, 'end'))
        append_button.grid(row=0, column=1, sticky='ew', padx=2)
        edit_button = ttk.Button(self.my_tags_button_frame, text="Edit", command=edit_tag)
        edit_button.grid(row=2, column=0, sticky='ew', padx=2)
        remove_button = ttk.Button(self.my_tags_button_frame, text="Remove", command=remove_tag)
        remove_button.grid(row=2, column=1, sticky='ew', padx=2)
        move_up_button = ttk.Button(self.my_tags_button_frame, text="Move Up", command=lambda: move(self.custom_dictionary_listbox, 'up'))
        move_up_button.grid(row=4, column=0, sticky='ew', padx=2)
        move_down_button = ttk.Button(self.my_tags_button_frame, text="Move Down", command=lambda: move(self.custom_dictionary_listbox, 'down'))
        move_down_button.grid(row=4, column=1, sticky='ew', padx=2)
        # All Tags section
        self.all_tags_frame = Frame(self.text_frame)
        self.all_tags_frame.grid_rowconfigure(1, weight=1)
        self.all_tags_frame.grid_columnconfigure(0, weight=1)
        all_tags_label = ttk.Label(self.all_tags_frame, text="All Tags")
        all_tags_label.grid(row=0, column=0, sticky='w', padx=2, pady=(2,0))
        self.all_tags_listbox = Listbox(self.all_tags_frame, selectmode='extended')
        self.all_tags_listbox.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.all_tags_listbox.bind("<Button-3>", show_context_menu)
        self.all_tags_listbox.bind("<Double-Button-1>", lambda event: insert_tag(self.all_tags_listbox, 'end'))
        # Add frames to PanedWindow
        self.text_frame.add(my_tags_frame, weight=1)
        self.text_frame.add(self.all_tags_frame, weight=1)
        # Buttons
        self.all_tags_button_frame = Frame(self.all_tags_frame)
        self.all_tags_button_frame.grid(row=2, column=0, sticky='ew', pady=(2,0))
        self.all_tags_button_frame.grid_columnconfigure(0, weight=1)
        self.all_tags_button_frame.grid_columnconfigure(1, weight=0)
        self.all_tags_button_frame.grid_columnconfigure(2, weight=1)
        prefix_button = ttk.Button(self.all_tags_button_frame, text="Prefix", command=lambda: insert_tag(self.all_tags_listbox, 'start'))
        prefix_button.grid(row=0, column=0, sticky='ew', padx=2)
        add_button = ttk.Button(self.all_tags_button_frame, text="<", command=add_to_mytags, width=2)
        add_button.grid(row=0, column=1)
        ToolTip.create(add_button, "Add selected tags to 'My Tags'", 200, 6, 12)
        append_button = ttk.Button(self.all_tags_button_frame, text="Append", command=lambda: insert_tag(self.all_tags_listbox, 'end'))
        append_button.grid(row=0, column=2, sticky='ew', padx=2)
        load_tag_file()
        self.parent.refresh_custom_dictionary()


    def refresh_all_tags_listbox(self, tags=None):
        listbox = self.all_tags_listbox
        if not tags:
            self.parent.stat_calculator.calculate_file_stats()
            tags = self.parent.stat_calculator.sorted_captions
        listbox.delete(0, 'end')
        for tag, count in tags:
            listbox.insert('end', tag)


    def toggle_all_tags_listbox(self):
        if self.show_all_tags_var.get():
            self.all_tags_frame.grid(row=0, column=2, sticky='nsew')
            self.text_frame.add(self.all_tags_frame, weight=1)
        else:
            self.text_frame.remove(self.all_tags_frame)


    def toggle_mytags_controls(self):
        if self.hide_mytags_controls_var.get():
            self.my_tags_button_frame.grid_remove()
        else:
            self.my_tags_button_frame.grid(row=2, column=0, sticky='ew', pady=(2,0))


    def toggle_alltags_controls(self):
        if self.hide_alltags_controls_var.get():
            self.all_tags_button_frame.grid_remove()
        else:
            self.all_tags_button_frame.grid(row=2, column=0, sticky='ew', pady=(2,0))


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
            "• Reorder with Move Up/Down (affects autocomplete priority)\n"
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
################################################################################################################################################
#region (9) File Stats


    def create_stats_widgets_tab9(self):
        tab_frame = Frame(self.parent.tab9)
        tab_frame.pack(fill='both', expand=True)
        button_frame = Frame(tab_frame)
        button_frame.pack(side='top', fill='x', pady=4)
        self.info_label = Label(button_frame, text="Characters: 0  |  Words: 0")
        self.info_label.pack(side='left')
        refresh_button = ttk.Button(button_frame, width=10, text="Refresh", takefocus=False, command=lambda: self.parent.stat_calculator.calculate_file_stats(manual_refresh=True))
        refresh_button.pack(side='right')
        ToolTip.create(refresh_button, "Refresh the file stats", 200, 6, 12)
        truncate_checkbutton = ttk.Checkbutton(button_frame, text="Truncate Captions", takefocus=False, variable=self.parent.truncate_stat_captions_var)
        truncate_checkbutton.pack(side='right')
        ToolTip.create(truncate_checkbutton, "Limit the displayed captions if they exceed either 8 words or 50 characters", 200, 6, 12)
        process_images_checkbutton = ttk.Checkbutton(button_frame, text="Process Image Stats", takefocus=False, variable=self.parent.process_image_stats_var)
        process_images_checkbutton.pack(side='right')
        ToolTip.create(process_images_checkbutton, "Enable/Disable image stat processing (Can be slow with many HD images)", 200, 6, 12)
        self.tab8_stats_textbox = scrolledtext.ScrolledText(tab_frame, wrap="word", state="disabled")
        self.tab8_stats_textbox.pack(fill='both', expand=True)



#endregion
################################################################################################################################################
#region Misc


    def bind_entry_functions(self, widget):
        widget.bind("<Double-1>", self.custom_select_word_for_entry)
        widget.bind("<Triple-1>", self.select_all_in_entry)
        widget.bind("<Button-3>", self.show_entry_context_menu)


    def custom_select_word_for_entry(self, event):
        widget = event.widget
        separators = " ,.-|()[]<>\\/\"'{}:;!@#$%^&*+=~`?"
        click_index = widget.index(f"@{event.x}")
        entry_text = widget.get()
        if click_index < len(entry_text) and entry_text[click_index] in separators:
            widget.selection_clear()
            widget.selection_range(click_index, click_index + 1)
        else:
            word_start = click_index
            while word_start > 0 and entry_text[word_start - 1] not in separators:
                word_start -= 1
            word_end = click_index
            while word_end < len(entry_text) and entry_text[word_end] not in separators:
                word_end += 1
            widget.selection_clear()
            widget.selection_range(word_start, word_end)
        widget.icursor(click_index)
        return "break"


    def select_all_in_entry(self, event):
        widget = event.widget
        widget.selection_range(0, 'end')
        return "break"


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
