#region Imports


# Standard Library
import os
import re
import time


# Standard Library - GUI
from tkinter import (
    ttk, Tk, Toplevel, messagebox,
    StringVar, BooleanVar,
    Frame, Menu, Scrollbar, scrolledtext, PanedWindow,
    Label, Listbox,
    font, TclError
)


# Third-Party Libraries
from TkToolTip.TkToolTip import TkToolTip as ToolTip


# Custom Libraries
from main.scripts.OnnxTagger import OnnxTagger as OnnxTagger
import main.scripts.video_thumbnail_generator as vtg
import main.scripts.entry_helper as entry_helper
from main.scripts.text_controller_my_tags import MyTags


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region TextController


class TextController:
    def __init__(self, parent: 'Main', root: 'Tk'):
        self.parent = parent
        self.root = root
        self.entry_helper = entry_helper

        # AutoTag
        self.onnx_model_dict = {}
        self.auto_insert_mode_var = StringVar(value="disable")
        self.batch_interrogate_images_var = BooleanVar(value=False)
        self.auto_exclude_tags_var = BooleanVar(value=False)
        self.filter_is_active = False

        # MyTags
        self.my_tags = MyTags(self.parent, self.root)


#endregion
#region (1) S&R


    def create_search_and_replace_widgets_tab1(self):
        tab_frame = Frame(self.parent.tab1)
        tab_frame.pack(side='top', fill='both')
        btn_frame = Frame(tab_frame)
        btn_frame.pack(side='top', fill='x')
        search_lbl = Label(btn_frame, width=8, text="Search:")
        search_lbl.pack(side='left', anchor="n", pady=4)
        ToolTip.create(search_lbl, "Enter the EXACT text you want to search for", 200, 6, 12)
        self.search_entry = ttk.Entry(btn_frame, textvariable=self.parent.search_string_var, width=4)
        self.search_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.entry_helper.setup_entry_binds(self.search_entry)
        replace_lbl = Label(btn_frame, width=8, text="Replace:")
        replace_lbl.pack(side='left', anchor="n", pady=4)
        ToolTip.create(replace_lbl, "Enter the text you want to replace the searched text with\n\nLeave empty to replace with nothing (delete)", 200, 6, 12)
        self.replace_entry = ttk.Entry(btn_frame, textvariable=self.parent.replace_string_var, width=4)
        self.replace_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.entry_helper.setup_entry_binds(self.replace_entry)
        self.replace_entry.bind('<Return>', lambda event: self.search_and_replace())
        replace_btn = ttk.Button(btn_frame, text="Go!", width=5, command=self.search_and_replace)
        replace_btn.pack(side='left', anchor="n", pady=4)
        ToolTip.create(replace_btn, "Text files will be backup up", 200, 6, 12)
        clear_btn = ttk.Button(btn_frame, text="Clear", width=5, command=self.clear_search_and_replace_tab)
        clear_btn.pack(side='left', anchor="n", pady=4)
        undo_btn = ttk.Button(btn_frame, text="Undo", width=5, command=self.parent.restore_backup)
        undo_btn.pack(side='left', anchor="n", pady=4)
        ToolTip.create(undo_btn, "Revert last action", 200, 6, 12)
        regex_chk = ttk.Checkbutton(btn_frame, text="Regex", variable=self.parent.search_and_replace_regex_var)
        regex_chk.pack(side='left', anchor="n", pady=4)
        ToolTip.create(regex_chk, "Use Regular Expressions in 'Search'", 200, 6, 12)
        text_frame = Frame(tab_frame, borderwidth=0)
        text_frame.pack(side='top', fill="both")
        info_text = scrolledtext.ScrolledText(text_frame, bg="#f0f0f0")
        info_text.pack(side='bottom', fill='both')
        info_text.insert("1.0",
            "Use this tool to search for a string of text across all text files in the selected directory.\n\n"
            "If a match is found, it will be replaced exactly with the given text.\n\n"
            "Example:\n"
            "Search for: the big brown dog\n"
            "Replace with: the big red dog\n\n"
            "This will replace all instances of 'the big brown dog' with 'the big red dog'.\n\n"
            "If a filter is applied, only text files that match the filter will be affected."
        )
        info_text.config(state="disabled", wrap="word")


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
        confirm = messagebox.askokcancel("Search and Replace", f"This will replace all occurrences of the text\n\n{search_string}\n\nWith\n\n{replace_string}\n\nA backup will be created before making changes.\n\nDo you want to proceed?")
        if not confirm:
            return
        self.parent.backup_text_files()
        if not self.parent.filter_string_var.get():
            self.parent.update_image_file_count()
        files_altered = 0
        words_replaced = 0
        for text_file in self.parent.text_files:
            try:
                if not os.path.exists(text_file):
                    continue
                with open(text_file, 'r', encoding="utf-8") as file:
                    filedata = file.read()
                original_data = filedata
                if self.parent.search_and_replace_regex_var.get():
                    new_data, count = re.subn(search_string, replace_string, filedata)
                else:
                    count = filedata.count(search_string)
                    new_data = filedata.replace(search_string, replace_string)
                if new_data != original_data:
                    files_altered += 1
                    words_replaced += count
                    with open(text_file, 'w', encoding="utf-8") as file:
                        file.write(new_data)
            except Exception as e:
                messagebox.showerror("Error: search_and_replace()", f"An error occurred while trying to replace text in {text_file}.\n\n{e}")
        self.parent.cleanup_all_text_files(show_confirmation=False)
        self.parent.show_pair()
        messagebox.showinfo("Search and Replace", f"Search and Replace completed successfully.\n\nFiles altered: {files_altered}\nWords replaced: {words_replaced}")


#endregion
#region (2) Prefix


    def create_prefix_text_widgets_tab2(self):
        tab_frame = Frame(self.parent.tab2)
        tab_frame.pack(side='top', fill='both')
        btn_frame = Frame(tab_frame)
        btn_frame.pack(side='top', fill='x')
        prefix_lbl = Label(btn_frame, width=8, text="Prefix:")
        prefix_lbl.pack(side='left', anchor="n", pady=4)
        ToolTip.create(prefix_lbl, "Enter the text you want to insert at the START of all text files\n\nCommas will be inserted as needed", 200, 6, 12)
        self.prefix_entry = ttk.Entry(btn_frame, textvariable=self.parent.prefix_string_var)
        self.prefix_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.entry_helper.setup_entry_binds(self.prefix_entry)
        self.prefix_entry.bind('<Return>', lambda event: self.prefix_text_files())
        prefix_btn = ttk.Button(btn_frame, text="Go!", width=5, command=self.prefix_text_files)
        prefix_btn.pack(side='left', anchor="n", pady=4)
        ToolTip.create(prefix_btn, "Text files will be backup up", 200, 6, 12)
        clear_btn = ttk.Button(btn_frame, text="Clear", width=5, command=lambda: self.prefix_entry.delete(0, 'end'))
        clear_btn.pack(side='left', anchor="n", pady=4)
        undo_btn = ttk.Button(btn_frame, text="Undo", width=5, command=self.parent.restore_backup)
        undo_btn.pack(side='left', anchor="n", pady=4)
        ToolTip.create(undo_btn, "Revert last action", 200, 6, 12)
        text_frame = Frame(tab_frame, borderwidth=0)
        text_frame.pack(side='top', fill="both")
        info_text = scrolledtext.ScrolledText(text_frame, bg="#f0f0f0")
        info_text.pack(side='bottom', fill='both')
        info_text.insert("1.0",
            "Use this tool to prefix all text files in the selected directory with the entered text.\n\n"
            "This means that the entered text will appear at the start of each text file.\n\n"
            "If a filter is applied, only text files that match the filter will be affected."
        )
        info_text.config(state="disabled", wrap="word")


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
#region (3) Append


    def create_append_text_widgets_tab3(self):
        tab_frame = Frame(self.parent.tab3)
        tab_frame.pack(side='top', fill='both')
        btn_frame = Frame(tab_frame)
        btn_frame.pack(side='top', fill='x')
        append_lbl = Label(btn_frame, width=8, text="Append:")
        append_lbl.pack(side='left', anchor="n", pady=4)
        ToolTip.create(append_lbl, "Enter the text you want to insert at the END of all text files\n\nCommas will be inserted as needed", 200, 6, 12)
        self.append_entry = ttk.Entry(btn_frame, textvariable=self.parent.append_string_var)
        self.append_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.entry_helper.setup_entry_binds(self.append_entry)
        self.append_entry.bind('<Return>', lambda event: self.append_text_files())
        append_btn = ttk.Button(btn_frame, text="Go!", width=5, command=self.append_text_files)
        append_btn.pack(side='left', anchor="n", pady=4)
        ToolTip.create(append_btn, "Text files will be backup up", 200, 6, 12)
        clear_btn = ttk.Button(btn_frame, text="Clear", width=5, command=lambda: self.append_entry.delete(0, 'end'))
        clear_btn.pack(side='left', anchor="n", pady=4)
        undo_btn = ttk.Button(btn_frame, text="Undo", width=5, command=self.parent.restore_backup)
        undo_btn.pack(side='left', anchor="n", pady=4)
        ToolTip.create(undo_btn, "Revert last action", 200, 6, 12)
        text_frame = Frame(tab_frame, borderwidth=0)
        text_frame.pack(side='top', fill="both")
        info_text = scrolledtext.ScrolledText(text_frame, bg="#f0f0f0")
        info_text.pack(side='bottom', fill='both')
        info_text.insert("1.0",
            "Use this tool to append all text files in the selected directory with the entered text.\n\n"
            "This means that the entered text will appear at the end of each text file.\n\n"
            "If a filter is applied, only text files that match the filter will be affected."
        )
        info_text.config(state="disabled", wrap="word")


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
#region (4) Auto-Tag


    def create_auto_tag_widgets_tab4(self):
        def invert_selection():
            for i in range(self.autotag_listbox.size()):
                if self.autotag_listbox.selection_includes(i):
                    self.autotag_listbox.selection_clear(i)
                else:
                    self.autotag_listbox.select_set(i)
            self.update_auto_tag_stats_label()

        def clear_selection():
            self.autotag_listbox.selection_clear(0, 'end')
            self.update_auto_tag_stats_label()

        def all_selection():
            self.autotag_listbox.select_set(0, 'end')
            self.update_auto_tag_stats_label()

        def copy_selection():
            _, extracted_tags = self.get_auto_tag_selection()
            if extracted_tags:
                self.autotag_listbox.clipboard_clear()
                self.autotag_listbox.clipboard_append(', '.join(extracted_tags))

        # Top Frame for Buttons
        top_frame = Frame(self.parent.tab4)
        top_frame.pack(fill='x')
        help_btn = ttk.Button(top_frame, text="?", takefocus=False, width=2, command=self.show_auto_tag_help)
        help_btn.pack(side='left')
        self.tag_list_stats_lbl = Label(top_frame, text="Total: 0  |  Selected: 0")
        self.tag_list_stats_lbl.pack(side='left')
        interrogate_btn = ttk.Button(top_frame, text="Interrogate", takefocus=False, command=self.interrogate_image_tags)
        interrogate_btn.pack(side='right')
        ToolTip.create(interrogate_btn, "Interrogate the current image using the selected ONNX vision model.", 500, 6, 12)
        ins_menubutton = ttk.Menubutton(top_frame, text="Auto-Insert", takefocus=False)
        ins_menubutton.pack(side='right')
        ins_menu = Menu(ins_menubutton, tearoff=0)
        ins_menu.add_radiobutton(label="Disable", variable=self.auto_insert_mode_var, value="disable")
        ins_menu.add_separator()
        ins_menu.add_radiobutton(label="Prefix", variable=self.auto_insert_mode_var, value="prefix")
        ins_menu.add_radiobutton(label="Append", variable=self.auto_insert_mode_var, value="append")
        ins_menu.add_radiobutton(label="Replace", variable=self.auto_insert_mode_var, value="replace")
        ins_menubutton.config(menu=ins_menu)
        batch_chk = ttk.Checkbutton(top_frame, text="Batch", takefocus=False, variable=self.batch_interrogate_images_var)
        batch_chk.pack(side='right')
        ToolTip.create(batch_chk, "Interrogate all images\nAn Auto-Insert mode must be selected", 200, 6, 12)

        # Main Paned Window
        pane = PanedWindow(self.parent.tab4, orient='horizontal', sashwidth=6, bg="#d0d0d0")
        pane.pack(fill='both', expand=True)

        # Listbox Frame
        listbox_frame = Frame(pane)
        pane.add(listbox_frame, stretch="never")
        pane.paneconfig(listbox_frame, width=200, minsize=40)
        scrollbar = Scrollbar(listbox_frame, orient="vertical")
        self.autotag_listbox = Listbox(listbox_frame, width=20, selectmode="extended", exportselection=False, yscrollcommand=scrollbar.set)
        self.autotag_listbox.bind('<<ListboxSelect>>', lambda event: self.update_auto_tag_stats_label())
        self.autotag_listbox.bind("<Button-3>", lambda event: contextmenu.tk_popup(event.x_root, event.y_root))
        scrollbar.config(command=self.autotag_listbox.yview)
        self.autotag_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        # Listbox - Context Menu
        contextmenu = Menu(self.autotag_listbox, tearoff=0)
        contextmenu.add_command(label="Insert: Prefix", command=lambda: self.insert_listbox_selection(prefix=True))
        contextmenu.add_command(label="Insert: Append", command=lambda: self.insert_listbox_selection(append=True))
        contextmenu.add_command(label="Insert: Replace", command=lambda: self.insert_listbox_selection(replace=True))
        contextmenu.add_separator()
        contextmenu.add_command(label="Copy Selected Tags", command=copy_selection)
        contextmenu.add_command(label="Select All", command=all_selection)
        contextmenu.add_command(label="Invert Selection", command=invert_selection)
        contextmenu.add_command(label="Clear Selection", command=clear_selection)
        contextmenu.add_separator()
        contextmenu.add_command(label="Add to MyTags", command=lambda: self.my_tags.add_to_custom_dictionary(origin="auto_tag"))
        contextmenu.add_separator()
        contextmenu.add_command(label="Add to Exclude", command=lambda: self.add_selected_tags_to_excluded_tags())
        contextmenu.add_command(label="Add to Keep", command=lambda: self.add_selected_tags_to_keep_tags())
        # Control Frame
        control_frame = Frame(pane)
        pane.add(control_frame, stretch="always")
        pane.paneconfig(control_frame, minsize=200)
        # Model Selection
        model_frame = Frame(control_frame)
        model_frame.pack(side='top', fill='x', padx=2, pady=2)
        model_label = Label(model_frame, text="Model:", width=16, anchor="w")
        model_label.pack(side='left')
        ToolTip.create(model_label, "Select the ONNX vision model to use for interrogation", 200, 6, 12)
        self.get_onnx_model_list()
        self.autotag_model_combo = ttk.Combobox(model_frame, width=25, takefocus=False, state="readonly", values=list(self.onnx_model_dict.keys()))
        self.autotag_model_combo.pack(side='right')
        self.set_auto_tag_combo_box()
        # General Threshold
        gen_thr_frame = Frame(control_frame)
        gen_thr_frame.pack(side='top', fill='x', padx=2, pady=2)
        gen_thr_lbl = Label(gen_thr_frame, text="General Threshold:", width=16, anchor="w")
        gen_thr_lbl.pack(side='left')
        ToolTip.create(gen_thr_lbl, "The minimum confidence threshold for general tags", 200, 6, 12)
        self.autotag_gen_threshold_spinbox = ttk.Spinbox(gen_thr_frame, takefocus=False, from_=0, to=1, increment=0.01, width=8)
        self.autotag_gen_threshold_spinbox.pack(side='right')
        self.autotag_gen_threshold_spinbox.set(self.parent.onnx_tagger.general_threshold)
        # Character Threshold
        char_thr_frame = Frame(control_frame)
        char_thr_frame.pack(side='top', fill='x', padx=2, pady=2)
        char_thr_lbl = Label(char_thr_frame, text="Character Threshold:", width=16, anchor="w")
        char_thr_lbl.pack(side='left')
        ToolTip.create(char_thr_lbl, "The minimum confidence threshold for character tags", 200, 6, 12)
        self.autotag_char_threshold_spinbox = ttk.Spinbox(char_thr_frame, takefocus=False, from_=0, to=1, increment=0.01, width=8)
        self.autotag_char_threshold_spinbox.pack(side='right')
        self.autotag_char_threshold_spinbox.set(self.parent.onnx_tagger.character_threshold)
        # Max Tags
        max_tags_frame = Frame(control_frame)
        max_tags_frame.pack(side='top', fill='x', padx=2, pady=2)
        max_tags_lbl = Label(max_tags_frame, text="Max Tags:", width=16, anchor="w")
        max_tags_lbl.pack(side='left')
        ToolTip.create(max_tags_lbl, "The maximum number of tags that will be generated\nAdditional tags will be ignored", 200, 6, 12)
        self.autotag_max_tags_spinbox = ttk.Spinbox(max_tags_frame, takefocus=False, from_=1, to=999, increment=1, width=8)
        self.autotag_max_tags_spinbox.pack(side='right')
        self.autotag_max_tags_spinbox.set(40)
        # Checkbutton Frame
        chk_frame = Frame(control_frame)
        chk_frame.pack(side='top', fill='x', padx=2, pady=2)
        # Keep (_)
        self.autotag_keep_underscore_chk = ttk.Checkbutton(chk_frame, text="Keep: _", takefocus=False, variable=self.parent.onnx_tagger.keep_underscore)
        self.autotag_keep_underscore_chk.pack(side='left', anchor='w', padx=2, pady=2)
        ToolTip.create(self.autotag_keep_underscore_chk, "If enabled, Underscores will be kept in tags, otherwise they will be replaced with a space\n\nExample: Keep = simple_background, Replace = simple background", 200, 6, 12)
        # Keep (\)
        self.autotag_keep_escape_chk = ttk.Checkbutton(chk_frame, text="Keep: \\", takefocus=False, variable=self.parent.onnx_tagger.keep_escape_character)
        self.autotag_keep_escape_chk.pack(side='left', anchor='w', padx=2, pady=2)
        ToolTip.create(self.autotag_keep_escape_chk, "If enabled, the escape character will be kept in tags\n\nExample: Keep = \(cat\), Replace = (cat)", 200, 6, 12)
        # Entry Frame
        entry_frame = Frame(control_frame)
        entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        excluded_entry_frame = Frame(entry_frame)
        excluded_entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        exclude_tags_lbl = Label(excluded_entry_frame, text="Exclude:", width=9, anchor="w")
        exclude_tags_lbl.pack(side='left')
        ToolTip.create(exclude_tags_lbl, "Enter tags that will be excluded from interrogation\nSeparate tags with commas", 200, 6, 12)
        self.excluded_tags_entry = ttk.Entry(excluded_entry_frame, width=5)
        self.excluded_tags_entry.pack(side='left', fill='both', expand=True)
        self.entry_helper.setup_entry_binds(self.excluded_tags_entry)
        auto_exclude_tags_chk = ttk.Checkbutton(excluded_entry_frame, text="Auto", takefocus=False, variable=self.auto_exclude_tags_var)
        auto_exclude_tags_chk.pack(side='left', anchor='w', padx=2, pady=2)
        ToolTip.create(auto_exclude_tags_chk, "Automatically exclude tags that are already in the text box", 200, 6, 12)
        keep_entry_frame = Frame(entry_frame)
        keep_entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        keep_tags_lbl = Label(keep_entry_frame, text="Keep:", width=9, anchor="w")
        keep_tags_lbl.pack(side='left')
        ToolTip.create(keep_tags_lbl, "Enter tags that will always be included in interrogation\nSeparate tags with commas", 200, 6, 12)
        self.keep_tags_entry = ttk.Entry(keep_entry_frame, width=25)
        self.keep_tags_entry.pack(side='left', fill='both', expand=True)
        self.entry_helper.setup_entry_binds(self.keep_tags_entry)
        replace_entry_frame = Frame(entry_frame)
        replace_entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        replace_tags_lbl = Label(replace_entry_frame, text="Replace:", width=9, anchor="w")
        replace_tags_lbl.pack(side='left')
        ToolTip.create(replace_tags_lbl, "Enter tags that will be replaced during interrogation\nSeparate tags with commas, the index of the tag in the 'Replace' entry will be used to replace the tag in the 'With' entry", 200, 6, 12)
        self.replace_tags_entry = ttk.Entry(replace_entry_frame, width=1)
        self.replace_tags_entry.pack(side='left', fill='both', expand=True)
        self.entry_helper.setup_entry_binds(self.replace_tags_entry)
        replace_with_tags_lbl = Label(replace_entry_frame, text="With:", anchor="w")
        replace_with_tags_lbl.pack(side='left')
        ToolTip.create(replace_with_tags_lbl, "Enter tags that will replace the tags entered in the 'Replace' entry\nSeparate tags with commas, ensure tags match the index of the tags in the 'Replace' entry", 200, 6, 12)
        self.replace_with_tags_entry = ttk.Entry(replace_entry_frame, width=1)
        self.replace_with_tags_entry.pack(side='left', fill='both', expand=True)
        self.entry_helper.setup_entry_binds(self.replace_with_tags_entry)
        # Selection Button Frame
        btn_frame = ttk.LabelFrame(control_frame, text="Selection")
        btn_frame.pack(side="bottom", fill='both', padx=2)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        # Selection Buttons
        ins_sel_prefix_btn = ttk.Button(btn_frame, text="Prefix", command=lambda: self.insert_listbox_selection(prefix=True))
        ins_sel_prefix_btn.grid(row=0, column=0, sticky='ew', pady=2)
        ins_sel_prefix_btn.bind("<Button-3>", lambda event: self.insert_listbox_selection(replace=True))
        ToolTip.create(ins_sel_prefix_btn, "Insert the selected tags at the START of the text box\nRight-click to replace the current tags", 500, 6, 12)
        ins_sel_append_btn = ttk.Button(btn_frame, text="Append", command=lambda: self.insert_listbox_selection(append=True))
        ins_sel_append_btn.grid(row=0, column=1, sticky='ew', pady=2)
        ins_sel_append_btn.bind("<Button-3>", lambda event: self.insert_listbox_selection(replace=True))
        ToolTip.create(ins_sel_append_btn, "Insert the selected tags at the END of the text box\nRight-click to replace the current tags", 500, 6, 12)
        copy_btn = ttk.Button(btn_frame, text="Copy", command=copy_selection)
        copy_btn.grid(row=0, column=2, sticky='ew', pady=2)
        ToolTip.create(copy_btn, "Copy the selected tags to the clipboard", 500, 6, 12)
        all_btn = ttk.Button(btn_frame, text="All", command=all_selection)
        all_btn.grid(row=1, column=0, sticky='ew', pady=2)
        ToolTip.create(all_btn, "Select all tags", 500, 6, 12)
        invert_btn = ttk.Button(btn_frame, text="Invert", command=invert_selection)
        invert_btn.grid(row=1, column=1, sticky='ew', pady=2)
        ToolTip.create(invert_btn, "Invert the current selection", 500, 6, 12)
        clear_btn = ttk.Button(btn_frame, text="Clear", command=clear_selection)
        clear_btn.grid(row=1, column=2, sticky='ew', pady=2)
        ToolTip.create(clear_btn, "Clear the current selection", 500, 6, 12)


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
        total_tags = self.autotag_listbox.size()
        selected_tags = len(self.autotag_listbox.curselection())
        selected_tags_padded = str(selected_tags).zfill(len(str(total_tags)))
        self.tag_list_stats_lbl.config(text=f"Total: {total_tags}  |  Selected: {selected_tags_padded}")


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
        selected_items = [self.autotag_listbox.get(i) for i in self.autotag_listbox.curselection()]
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

        validate_spinbox_value(self.autotag_max_tags_spinbox, 40, 1, 999)
        self.parent.onnx_tagger.general_threshold = validate_spinbox_value(self.autotag_gen_threshold_spinbox, 0.35, 0, 1)
        self.parent.onnx_tagger.character_threshold = validate_spinbox_value(self.autotag_char_threshold_spinbox, 0.85, 0, 1)


    def interrogate_image_tags(self):
        self.parent.text_notebook.select(self.parent.tab4)
        if self.batch_interrogate_images_var.get():
            self.batch_interrogate_images()
            return
        image_path = self.parent.image_files[self.parent.current_index]
        if image_path.lower().endswith('.mp4'):
            image_path = self.parent.video_player.get_current_frame()
        selected_model_path = self.onnx_model_dict.get(self.autotag_model_combo.get())
        if not selected_model_path or not os.path.exists(selected_model_path):
            confirm = messagebox.askyesno("Error", f"Model file not found: {selected_model_path}\n\nWould you like to view the Auto-Tag Help?")
            if confirm:
                self.show_auto_tag_help()
            return
        self.update_tag_thresholds()
        self.update_tag_options()
        tag_list, tag_dict = self.parent.onnx_tagger.tag_image(image_path, model_path=selected_model_path)
        max_tags = int(self.autotag_max_tags_spinbox.get())
        tag_list = tag_list[:max_tags]
        tag_dict = {k: v for k, v in list(tag_dict.items())[:max_tags]}
        self.populate_auto_tag_listbox(tag_dict)
        self.auto_insert_tags(tag_list)


    def populate_auto_tag_listbox(self, tag_dict):
        self.autotag_listbox.delete(0, "end")
        if not tag_dict:
            self.update_auto_tag_stats_label()
            return
        max_length = max(len(f"{float(confidence):.2f}") for confidence, _ in tag_dict.values())
        for tag, (confidence, category) in tag_dict.items():
            padded_score = f"{float(confidence):.2f}".ljust(max_length, '0')
            self.autotag_listbox.insert("end", f" {padded_score}: {tag}")
            if category == "character":
                self.autotag_listbox.itemconfig("end", {'fg': '#148632'})
            if category == "keep":
                self.autotag_listbox.itemconfig("end", {'fg': '#c00004'})
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
            self.autotag_model_combo.set(first_model_key)


    def batch_interrogate_images(self):
        def stop_batch_process():
            self.stop_batch = True
            popup.destroy()
            messagebox.showinfo("Batch Interrogate", f"Batch interrogation stopped\n\n{index} out of {total_images} images were interrogated")
        popup = None
        if self.auto_insert_mode_var.get() == "disable":
            messagebox.showinfo("Batch Interrogate", "Auto-Insert must be enabled to use Batch Interrogate")
            return
        try:
            confirm = messagebox.askyesno("Batch Interrogate", "Interrogate all images in the current directory?")
            if not confirm:
                return
            self.stop_batch = False
            popup = Toplevel(self.root)
            popup.iconbitmap(self.parent.icon_path)
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
            selected_model_path = self.onnx_model_dict.get(self.autotag_model_combo.get())
            if not selected_model_path or not os.path.exists(selected_model_path):
                confirm = messagebox.askyesno("Error", f"Model file not found: {selected_model_path}\n\nWould you like to view the Auto-Tag Help?")
                if confirm:
                    self.show_auto_tag_help()
                popup.destroy()
                return
            self.update_tag_thresholds()
            max_tags = int(self.autotag_max_tags_spinbox.get())
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
                if image_path.lower().endswith('.mp4'):
                    video_frame = vtg.get_video_frame(image_path, timestamp_seconds=2.0)
                    if video_frame:
                        tag_list, tag_dict = self.parent.onnx_tagger.tag_image(video_frame, model_path=selected_model_path)
                    else:
                        tag_list, tag_dict = [], {}  # Video frame could not be extracted
                        continue
                else:
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


    def add_selected_tags_to_excluded_tags(self):
        selected_items, extracted_tags = self.get_auto_tag_selection()
        if not extracted_tags:
            return
        # Strip escape characters from extracted tags
        extracted_tags = [tag.replace('\\', '') for tag in extracted_tags]
        current_excluded = self.excluded_tags_entry.get().strip()
        excluded_list = [tag.strip() for tag in current_excluded.split(',') if tag.strip()] if current_excluded else []
        # Strip escape characters from existing excluded tags
        excluded_list = [tag.replace('\\', '') for tag in excluded_list]
        for tag in extracted_tags:
            if tag not in excluded_list:
                excluded_list.append(tag)
        self.excluded_tags_entry.delete(0, 'end')
        self.excluded_tags_entry.insert(0, ', '.join(excluded_list))


    def add_selected_tags_to_keep_tags(self):
        selected_items, extracted_tags = self.get_auto_tag_selection()
        if not extracted_tags:
            return
        # Strip escape characters from extracted tags
        extracted_tags = [tag.replace('\\', '') for tag in extracted_tags]
        current_keep = self.keep_tags_entry.get().strip()
        keep_list = [tag.strip() for tag in current_keep.split(',') if tag.strip()] if current_keep else []
        # Strip escape characters from existing keep tags
        keep_list = [tag.replace('\\', '') for tag in keep_list]
        for tag in extracted_tags:
            if tag not in keep_list:
                keep_list.append(tag)
        self.keep_tags_entry.delete(0, 'end')
        self.keep_tags_entry.insert(0, ', '.join(keep_list))


#endregion
#region (5) Filter


    def create_filter_text_image_pairs_widgets_tab5(self):
        tab_frame = Frame(self.parent.tab5)
        tab_frame.pack(side='top', fill='both')
        btn_frame = Frame(tab_frame)
        btn_frame.pack(side='top', fill='x')
        self.filter_lbl = Label(btn_frame, width=8, text="Filter:")
        self.filter_lbl.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.filter_lbl, "Enter the EXACT text you want to filter by\nThis will filter all img-txt pairs based on the provided text, see below for more info", 200, 6, 12)
        self.filter_entry = ttk.Entry(btn_frame, width=11, textvariable=self.parent.filter_string_var)
        self.filter_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.entry_helper.setup_entry_binds(self.filter_entry)
        self.filter_entry.bind('<Return>', lambda event: self.filter_text_image_pairs())
        self.filter_btn = ttk.Button(btn_frame, text="Go!", width=5, command=self.filter_text_image_pairs)
        self.filter_btn.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.filter_btn, "Text files will be filtered based on the entered text", 200, 6, 12)
        self.revert_filter_btn = ttk.Button(btn_frame, text="Clear", width=5, command=lambda: (self.revert_text_image_filter(clear=True)))
        self.revert_filter_btn.pack(side='left', anchor="n", pady=4)
        self.revert_filter_button_tooltip = ToolTip.create(self.revert_filter_btn, "Clear any filtering applied", 200, 6, 12)
        self.regex_filter_chk = ttk.Checkbutton(btn_frame, text="Regex", variable=self.parent.filter_use_regex_var)
        self.regex_filter_chk.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.regex_filter_chk, "Use Regular Expressions for filtering", 200, 6, 12)
        self.empty_files_chk = ttk.Checkbutton(btn_frame, text="Empty", variable=self.parent.filter_empty_files_var, command=self.toggle_empty_files_filter)
        self.empty_files_chk.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.empty_files_chk, "Check this to show only empty text files\n\nImages without a text pair are also considered as empty", 200, 6, 12)
        text_frame = Frame(tab_frame, borderwidth=0)
        text_frame.pack(side='top', fill="both")
        info_text = scrolledtext.ScrolledText(text_frame, bg="#f0f0f0")
        info_text.pack(side='bottom', fill='both')
        info_text.insert("1.0",
            "This tool will filter all img-txt pairs based on the provided text.\n\n"
            "Enter any string of text to display only img-txt pairs containing that text.\n"
            "Use ' + ' to include multiple strings when filtering.\n"
            "Use '!' before the text to exclude any pairs containing that text.\n\n"
            "Examples:\n"
            "'dog' (shows only pairs containing the text dog)\n"
            "'!dog' (removes all pairs containing the text dog)\n"
            "'!dog + cat' (remove dog pairs, display cat pairs)"
        )
        info_text.config(state="disabled", wrap="word")


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
        self.revert_filter_btn.config(style="Red.TButton")
        self.revert_filter_button_tooltip.config(text="Filter is active\n\nClear any filtering applied")
        self.parent.update_total_image_label()
        if self.parent.is_image_grid_visible_var.get():
            self.parent.image_grid.reload_grid()



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
        self.revert_filter_btn.config(style="")
        self.revert_filter_button_tooltip.config(text="Filter is inactive\n\nClear any filtering applied")
        self.parent.filter_empty_files_var.set(False)
        self.parent.update_total_image_label()
        if self.parent.is_image_grid_visible_var.get():
            self.parent.image_grid.reload_grid()
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
                for widget in [self.filter_lbl, self.filter_entry, self.filter_btn, self.regex_filter_chk]:
                    widget.config(state="disabled")
            else:
                for widget in [self.filter_lbl, self.filter_entry, self.filter_btn, self.regex_filter_chk]:
                    widget.config(state="normal")


#endregion
#region (6) Highlight


    def create_custom_active_highlight_widgets_tab6(self):
        tab_frame = Frame(self.parent.tab6)
        tab_frame.pack(side='top', fill='both')
        btn_frame = Frame(tab_frame)
        btn_frame.pack(side='top', fill='x')
        highlight_lbl = Label(btn_frame, width=8, text="Highlight:")
        highlight_lbl.pack(side='left', anchor="n", pady=4)
        ToolTip.create(highlight_lbl, "Enter the text you want to highlight\nUse ' + ' to highlight multiple strings of text\n\nExample: dog + cat", 200, 6, 12)
        self.highlight_entry = ttk.Entry(btn_frame, textvariable=self.parent.custom_highlight_string_var)
        self.highlight_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.entry_helper.setup_entry_binds(self.highlight_entry)
        self.highlight_entry.bind('<KeyRelease>', lambda event: self.parent.highlight_custom_string())
        highlight_btn = ttk.Button(btn_frame, text="Go!", width=5, command=self.parent.highlight_custom_string)
        highlight_btn.pack(side='left', anchor="n", pady=4)
        clear_btn = ttk.Button(btn_frame, text="Clear", width=5, command=self.clear_highlight_tab)
        clear_btn.pack(side='left', anchor="n", pady=4)
        regex_highlight_chk = ttk.Checkbutton(btn_frame, text="Regex", variable=self.parent.highlight_use_regex_var)
        regex_highlight_chk.pack(side='left', anchor="n", pady=4)
        ToolTip.create(regex_highlight_chk, "Use Regular Expressions for highlighting text", 200, 6, 12)
        text_frame = Frame(tab_frame, borderwidth=0)
        text_frame.pack(side='top', fill="both")
        info_text = scrolledtext.ScrolledText(text_frame, bg="#f0f0f0")
        info_text.pack(side='bottom', fill='both')
        info_text.insert("1.0",
            "Enter the text you want to highlight each time you move to a new img-txt pair.\n\n"
            "Use ' + ' to highlight multiple strings of text\n\n"
            "Example: dog + cat"
        )
        info_text.config(state="disabled", wrap="word")


    def clear_highlight_tab(self):
        self.highlight_entry.delete(0, 'end')
        self.parent.highlight_use_regex_var.set(False)


#endregion
#region (7) Font


    def create_font_widgets_tab7(self, event=None):
        def set_font_and_size(font, size):
            if font and size:
                size = int(size)
                self.parent.text_box.config(font=(font, size))
                self.font_size_lbl.config(text=f"Size: {size}")
                font_combo_tooltip.config(text=f"{font}")
        def reset_to_defaults():
            self.parent.font_var.set(self.parent.default_font)
            self.size_scale.set(self.parent.default_font_size)
            set_font_and_size(self.parent.default_font, self.parent.default_font_size)
        font_lbl = Label(self.parent.tab7, width=8, text="Font:")
        font_lbl.pack(side="left", anchor="n", pady=4)
        ToolTip.create(font_lbl, "Recommended Fonts: Courier New, Ariel, Consolas, Segoe UI", 200, 6, 12)
        font_combo = ttk.Combobox(self.parent.tab7, textvariable=self.parent.font_var, width=4, takefocus=False, state="readonly", values=list(font.families()))
        font_combo.set(self.parent.current_font_name)
        font_combo.bind("<<ComboboxSelected>>", lambda event: set_font_and_size(self.parent.font_var.get(), self.size_scale.get()))
        font_combo.pack(side="left", anchor="n", pady=4, fill="x", expand=True)
        font_combo_tooltip = ToolTip.create(font_combo, f"{self.parent.current_font_name}", 200, 6, 12)
        self.font_size_lbl = Label(self.parent.tab7, text=f"Size: {self.parent.font_size_var.get()}", width=14)
        self.font_size_lbl.pack(side="left", anchor="n", pady=4)
        ToolTip.create(self.font_size_lbl, "Default size: 10", 200, 6, 12)
        self.size_scale = ttk.Scale(self.parent.tab7, from_=6, to=24, variable=self.parent.font_size_var, takefocus=False)
        self.size_scale.set(self.parent.current_font_size)
        self.size_scale.bind("<B1-Motion>", lambda event: set_font_and_size(self.parent.font_var.get(), self.size_scale.get()))
        self.size_scale.pack(side="left", anchor="n", pady=4, fill="x", expand=True)
        reset_btn = ttk.Button(self.parent.tab7, text="Reset", width=5, takefocus=False, command=reset_to_defaults)
        reset_btn.pack(side="left", anchor="n", pady=4)


#endregion
#region (8) MyTags


    def create_custom_dictionary_widgets_tab8(self):
        self.my_tags.create_tab8()



#endregion
#region (9) File Stats


    def create_stats_widgets_tab9(self):
        tab_frame = Frame(self.parent.tab9)
        tab_frame.pack(fill='both', expand=True)
        btn_frame = Frame(tab_frame)
        btn_frame.pack(side='top', fill='x', pady=4)
        self.stats_info_lbl = Label(btn_frame, text="Characters: 0  |  Words: 0")
        self.stats_info_lbl.pack(side='left')
        refresh_btn = ttk.Button(btn_frame, width=10, text="Refresh", takefocus=False, command=lambda: self.parent.stat_calculator.calculate_file_stats(manual_refresh=True))
        refresh_btn.pack(side='right')
        ToolTip.create(refresh_btn, "Refresh the file stats", 200, 6, 12)
        truncate_chk = ttk.Checkbutton(btn_frame, text="Truncate Captions", takefocus=False, variable=self.parent.truncate_stat_captions_var)
        truncate_chk.pack(side='right')
        ToolTip.create(truncate_chk, "Limit the displayed captions if they exceed either 8 words or 50 characters", 200, 6, 12)
        image_video_chk = ttk.Checkbutton(btn_frame, text="Image/Video Stats", takefocus=False, variable=self.parent.process_image_stats_var)
        image_video_chk.pack(side='right')
        ToolTip.create(image_video_chk, "Enable/Disable image and video stat processing (Can be slow with many HD images or videos)", 200, 6, 12)
        self.filestats_textbox = scrolledtext.ScrolledText(tab_frame, wrap="word", state="disabled")
        self.filestats_textbox.pack(fill='both', expand=True)


#endregion
