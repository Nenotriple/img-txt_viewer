#region Imports


# Standard Library
import os
import re


# Standard Library - GUI
from tkinter import (
    ttk, Tk, messagebox,
    Frame, scrolledtext,
    Label,
    font
)


# Third-Party Libraries
from tkmarktext import TextWindow
from TkToolTip.TkToolTip import TkToolTip as Tip


# Custom Libraries
import main.scripts.HelpText as HelpText
import main.scripts.entry_helper as entry_helper
from main.scripts.buttonmenu import ButtonMenu
from main.scripts.text_controller_my_tags import MyTags
from main.scripts.text_controller_auto_tag import AutoTag

# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region TextController


class TextController:
    def __init__(self, app: 'Main', root: 'Tk'):
        self.app = app
        self.root = root
        self.entry_helper = entry_helper

        self.filter_is_active = False
        self.auto_tag = AutoTag(self.app, self.root)
        self.my_tags = MyTags(self.app, self.root)


    def show_help_dialog(self, text):
        window = TextWindow(master=self.root)
        window.open_window(text=text, title="Help", geometry="600x300", icon=self.app.blank_image)


#endregion
#region (1) S&R


    def create_search_and_replace_widgets_tab1(self):
        btn_frame = Frame(self.app.tab1)
        btn_frame.pack(fill='x', pady=4)
        search_lbl = Label(btn_frame, width=8, text="Search:")
        search_lbl.pack(side='left', anchor="n")
        Tip.create(widget=search_lbl, text="Enter the EXACT text you want to search for")
        self.search_entry = ttk.Entry(btn_frame, textvariable=self.app.search_string_var, width=4)
        self.search_entry.pack(side='left', anchor="n", fill='both', expand=True)
        self.entry_helper.bind_helpers(self.search_entry)
        replace_lbl = Label(btn_frame, width=8, text="Replace:")
        replace_lbl.pack(side='left', anchor="n")
        Tip.create(widget=replace_lbl, text="Enter the text you want to replace the searched text with\n\nLeave empty to replace with nothing (delete)")
        self.replace_entry = ttk.Entry(btn_frame, textvariable=self.app.replace_string_var, width=4)
        self.replace_entry.pack(side='left', anchor="n", fill='both', expand=True)
        self.entry_helper.bind_helpers(self.replace_entry)
        self.replace_entry.bind('<Return>', lambda event: self.search_and_replace())
        replace_btn = ttk.Button(btn_frame, text="Go!", width=5, command=self.search_and_replace)
        replace_btn.pack(side='left', anchor="n")
        Tip.create(widget=replace_btn, text="Text files will be backup up")
        menu_btn = ButtonMenu(btn_frame, text="☰", width=2)
        menu_btn.pack(side='left', anchor="n")
        menu_btn.menu.add_command(label="Clear Fields", command=self.clear_search_and_replace_tab)
        menu_btn.menu.add_command(label="Undo Last Action", command=self.app.restore_backup)
        menu_btn.menu.add_separator()
        menu_btn.menu.add_checkbutton(label="Use Regular Expressions", variable=self.app.search_and_replace_regex_var)
        menu_btn.menu.add_separator()
        menu_btn.menu.add_command(label="Help", command=lambda: self.show_help_dialog(HelpText.SEARCH_AND_REPLACE_HELP))


    def clear_search_and_replace_tab(self):
        self.search_entry.delete(0, 'end')
        self.replace_entry.delete(0, 'end')
        self.app.search_and_replace_regex_var.set(False)


    def search_and_replace(self):
        if not self.app.check_if_directory():
            return
        search_string = self.app.search_string_var.get()
        replace_string = self.app.replace_string_var.get()
        if not search_string:
            return
        confirm = messagebox.askokcancel("Search and Replace", f"This will replace all occurrences of the text\n\n{search_string}\n\nWith\n\n{replace_string}\n\nA backup will be created before making changes.\n\nDo you want to proceed?")
        if not confirm:
            return
        self.app.backup_text_files()
        if not self.app.filter_string_var.get():
            self.app.update_image_file_count()
        files_altered = 0
        words_replaced = 0
        for text_file in self.app.text_files:
            try:
                if not os.path.exists(text_file):
                    continue
                with open(text_file, 'r', encoding="utf-8") as file:
                    filedata = file.read()
                original_data = filedata
                if self.app.search_and_replace_regex_var.get():
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
                messagebox.showerror("Error: text_controller.search_and_replace()", f"An error occurred while trying to replace text in {text_file}.\n\n{e}")
        self.app.cleanup_all_text_files(show_confirmation=False)
        self.app.show_pair()
        messagebox.showinfo("Search and Replace", f"Search and Replace completed successfully.\n\nFiles altered: {files_altered}\nWords replaced: {words_replaced}")


#endregion
#region (2) Prefix


    def create_prefix_text_widgets_tab2(self):
        btn_frame = Frame(self.app.tab2)
        btn_frame.pack(fill='x', pady=4)
        prefix_lbl = Label(btn_frame, width=8, text="Prefix:")
        prefix_lbl.pack(side='left', anchor="n")
        Tip.create(widget=prefix_lbl, text="Enter the text you want to insert at the START of all text files\n\nCommas will be inserted as needed")
        self.prefix_entry = ttk.Entry(btn_frame, textvariable=self.app.prefix_string_var)
        self.prefix_entry.pack(side='left', anchor="n", fill='both', expand=True)
        self.entry_helper.bind_helpers(self.prefix_entry)
        self.prefix_entry.bind('<Return>', lambda event: self.prefix_text_files())
        prefix_btn = ttk.Button(btn_frame, text="Go!", width=5, command=self.prefix_text_files)
        prefix_btn.pack(side='left', anchor="n")
        Tip.create(widget=prefix_btn, text="Text files will be backup up")
        menu_btn = ButtonMenu(btn_frame, text="☰", width=2)
        menu_btn.pack(side='left', anchor="n")
        menu_btn.menu.add_command(label="Clear Field", command=lambda: self.prefix_entry.delete(0, 'end'))
        menu_btn.menu.add_command(label="Undo Last Action", command=self.app.restore_backup)
        menu_btn.menu.add_separator()
        menu_btn.menu.add_command(label="Help", command=lambda: self.show_help_dialog(HelpText.PREFIX_HELP))


    def prefix_text_files(self):
        if not self.app.check_if_directory():
            return
        prefix_text = self.app.prefix_string_var.get()
        if not prefix_text:
            return
        if not prefix_text.endswith(', '):
            prefix_text += ', '
        confirm = messagebox.askokcancel("Prefix", "This will prefix all text files with:\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(prefix_text))
        if not confirm:
            return
        self.app.backup_text_files()
        if not self.app.filter_string_var.get():
            self.app.update_image_file_count()
        for text_file in self.app.text_files:
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
                messagebox.showerror("Error: text_controller.prefix_text_files()", f"An error occurred while trying to prefix text in {text_file}.\n\n{e}")
        self.app.cleanup_all_text_files(show_confirmation=False)
        self.app.show_pair()
        messagebox.showinfo("Prefix", "Prefix completed successfully.")


#endregion
#region (3) Append


    def create_append_text_widgets_tab3(self):
        btn_frame = Frame(self.app.tab3)
        btn_frame.pack(fill='x', pady=4)
        append_lbl = Label(btn_frame, width=8, text="Append:")
        append_lbl.pack(side='left', anchor="n")
        Tip.create(widget=append_lbl, text="Enter the text you want to insert at the END of all text files\n\nCommas will be inserted as needed")
        self.append_entry = ttk.Entry(btn_frame, textvariable=self.app.append_string_var)
        self.append_entry.pack(side='left', anchor="n", fill='both', expand=True)
        self.entry_helper.bind_helpers(self.append_entry)
        self.append_entry.bind('<Return>', lambda event: self.append_text_files())
        append_btn = ttk.Button(btn_frame, text="Go!", width=5, command=self.append_text_files)
        append_btn.pack(side='left', anchor="n")
        Tip.create(widget=append_btn, text="Text files will be backup up")
        menu_btn = ButtonMenu(btn_frame, text="☰", width=2)
        menu_btn.pack(side='left', anchor="n")
        menu_btn.menu.add_command(label="Clear Field", command=lambda: self.append_entry.delete(0, 'end'))
        menu_btn.menu.add_command(label="Undo Last Action", command=self.app.restore_backup)
        menu_btn.menu.add_separator()
        menu_btn.menu.add_command(label="Help", command=lambda: self.show_help_dialog(HelpText.APPEND_HELP))


    def append_text_files(self):
        if not self.app.check_if_directory():
            return
        append_text = self.app.append_string_var.get()
        if not append_text:
            return
        if not append_text.startswith(', '):
            append_text = ', ' + append_text
        confirm = messagebox.askokcancel("Append", "This will append all text files with:\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(append_text))
        if not confirm:
            return
        self.app.backup_text_files()
        if not self.app.filter_string_var.get():
            self.app.update_image_file_count()
        for text_file in self.app.text_files:
            try:
                if not os.path.exists(text_file):
                    with open(text_file, 'w', encoding="utf-8") as file:
                        file.write(append_text)
                else:
                    with open(text_file, 'a', encoding="utf-8") as file:
                        file.write(append_text)
            except Exception as e:
                messagebox.showerror("Error: text_controller.append_text_files()", f"An error occurred while trying to append text in {text_file}.\n\n{e}")
        self.app.cleanup_all_text_files(show_confirmation=False)
        self.app.show_pair()
        messagebox.showinfo("Append", "Append completed successfully.")


#endregion
#region (4) Auto-Tag


    def create_auto_tag_widgets_tab4(self):
        self.auto_tag.create_auto_tag_widgets_tab4()


#endregion
#region (5) Filter


    def create_filter_text_image_pairs_widgets_tab5(self):
        btn_frame = Frame(self.app.tab5)
        btn_frame.pack(fill='x', pady=4)
        self.filter_lbl = Label(btn_frame, width=8, text="Filter:")
        self.filter_lbl.pack(side='left', anchor="n")
        Tip.create(widget=self.filter_lbl, text="Enter the EXACT text you want to filter by\nThis will filter all img-txt pairs based on the provided text, see below for more info")
        self.filter_entry = ttk.Entry(btn_frame, width=11, textvariable=self.app.filter_string_var)
        self.filter_entry.pack(side='left', anchor="n", fill='both', expand=True)
        self.entry_helper.bind_helpers(self.filter_entry)
        self.filter_entry.bind('<Return>', lambda event: self.filter_text_image_pairs())
        self.filter_btn = ttk.Button(btn_frame, text="Go!", width=5, command=self.filter_text_image_pairs)
        self.filter_btn.pack(side='left', anchor="n")
        Tip.create(widget=self.filter_btn, text="Text files will be filtered based on the entered text")
        menu_btn = ButtonMenu(btn_frame, text="☰", width=2)
        menu_btn.pack(side='left', anchor="n")
        menu_btn.menu.add_command(label="Clear And Reset Filter", command=lambda: self.filter_entry.delete(0, 'end'))
        menu_btn.menu.add_separator()
        menu_btn.menu.add_checkbutton(label="Use Regular Expressions", variable=self.app.filter_use_regex_var)
        menu_btn.menu.add_checkbutton(label="Show Empty Text Files Only", variable=self.app.filter_empty_files_var, command=self.toggle_empty_files_filter)
        menu_btn.menu.add_separator()
        menu_btn.menu.add_command(label="Help", command=lambda: self.show_help_dialog(HelpText.FILTER_HELP))


    def filter_text_image_pairs(self):  # Filter
        if not self.app.check_if_directory():
            return
        if not self.app.filter_empty_files_var.get():
            self.revert_text_image_filter(silent=True)
        filter_string = self.app.filter_string_var.get()
        if not filter_string and not self.app.filter_empty_files_var.get():
            self.app.image_index_entry.delete(0, "end")
            self.app.image_index_entry.insert(0, "1")
            return
        self.filtered_image_files = []
        self.filtered_text_files = []
        for image_file in self.app.image_files:
            text_file = os.path.splitext(image_file)[0] + ".txt"
            filedata = ""
            try:
                with open(text_file, 'r', encoding="utf-8") as file:
                    filedata = file.read()
            except FileNotFoundError:
                text_file = text_file
            if self.app.filter_empty_files_var.get():
                if not filedata.strip():
                    self.filtered_image_files.append(image_file)
                    self.filtered_text_files.append(text_file)
            else:
                if self.app.filter_use_regex_var.get():
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
        self.app.image_files = self.filtered_image_files
        self.app.text_files = self.filtered_text_files
        if hasattr(self, 'total_images_label'):
            self.app.total_images_label.config(text=f"of {len(self.app.image_files)}")
        self.app.current_index = 0
        self.app.show_pair()
        messagebox.showinfo("Filter", f"Filter applied successfully.\n\n{len(self.app.image_files)} images found.")
        self.app.update_total_image_label()
        if self.app.is_image_grid_visible_var.get():
            self.app.image_grid.reload_grid()



    def revert_text_image_filter(self, clear=None, silent=False): # Filter
        if not self.filter_is_active and not self.app.filter_empty_files_var.get():
            return
        last_index = self.app.current_index
        if clear:
            self.app.filter_string_var.set("")
            self.app.filter_use_regex_var.set(False)
            self.app.image_index_entry.delete(0, "end")
            self.app.image_index_entry.insert(0, last_index + 1)
        self.app.update_image_file_count()
        self.app.current_index = last_index if last_index < len(self.app.image_files) else 0
        self.app.show_pair()
        if not silent:
            messagebox.showinfo("Filter", "Filter has been cleared.")
        self.filter_is_active = False
        self.app.filter_empty_files_var.set(False)
        self.app.update_total_image_label()
        if self.app.is_image_grid_visible_var.get():
            self.app.image_grid.reload_grid()
        if self.app.filter_empty_files_var.get():
            self.toggle_filter_widgets(state=True)
        else:
            self.toggle_filter_widgets(state=False)


    def toggle_empty_files_filter(self): # Filter
        if self.app.filter_empty_files_var.get():
            self.app.image_index_entry.delete(0, "end")
            self.app.image_index_entry.insert(0, 1)
            self.app.filter_string_var.set("")
            self.filter_text_image_pairs()
            self.app.filter_use_regex_var.set(False)
            self.toggle_filter_widgets(state=True)
        else:
            self.revert_text_image_filter(silent=True)
            self.toggle_filter_widgets(state=False)


    def toggle_filter_widgets(self, state): # Filter
            if state:
                for widget in [self.filter_lbl, self.filter_entry, self.filter_btn]:
                    widget.config(state="disabled")
            else:
                for widget in [self.filter_lbl, self.filter_entry, self.filter_btn]:
                    widget.config(state="normal")


#endregion
#region (6) Highlight


    def create_custom_active_highlight_widgets_tab6(self):
        btn_frame = Frame(self.app.tab6)
        btn_frame.pack(fill='x', pady=4)
        highlight_lbl = Label(btn_frame, width=8, text="Highlight:")
        highlight_lbl.pack(side='left', anchor="n")
        Tip.create(widget=highlight_lbl, text="Enter the text you want to highlight\nUse ' + ' to highlight multiple strings of text\n\nExample: dog + cat")
        self.highlight_entry = ttk.Entry(btn_frame, textvariable=self.app.custom_highlight_string_var)
        self.highlight_entry.pack(side='left', anchor="n", fill='both', expand=True)
        self.entry_helper.bind_helpers(self.highlight_entry)
        self.highlight_entry.bind('<KeyRelease>', lambda event: self.app.highlight_custom_string())
        highlight_btn = ttk.Button(btn_frame, text="Go!", width=5, command=self.app.highlight_custom_string)
        highlight_btn.pack(side='left', anchor="n")
        Tip.create(widget=highlight_btn, text="Highlight the entered text in the current text file")
        menu_btn = ButtonMenu(btn_frame, text="☰", width=2)
        menu_btn.pack(side='left', anchor="n")
        menu_btn.menu.add_command(label="Clear Field", command=lambda: self.clear_highlight_tab())
        menu_btn.menu.add_checkbutton(label="Use Regular Expressions", variable=self.app.highlight_use_regex_var)
        menu_btn.menu.add_separator()
        menu_btn.menu.add_command(label="Help", command=lambda: self.show_help_dialog(HelpText.HIGHLIGHT_HELP))


    def clear_highlight_tab(self):
        self.highlight_entry.delete(0, 'end')
        self.app.highlight_use_regex_var.set(False)


#endregion
#region (7) Font


    def create_font_widgets_tab7(self, event=None):
        def set_font_and_size(font, size):
            if font and size:
                size = int(size)
                self.app.text_box.config(font=(font, size))
                self.font_size_lbl.config(text=f"Size: {size}")
                font_combo_tooltip.config(text=f"{font}")
        def reset_to_defaults():
            self.app.font_var.set(self.app.default_font)
            self.size_scale.set(self.app.default_font_size)
            set_font_and_size(self.app.default_font, self.app.default_font_size)

        self.app.tab7.config(pady=4)

        font_lbl = Label(self.app.tab7, width=8, text="Font:")
        font_lbl.pack(side="left", anchor="n")
        Tip.create(widget=font_lbl, text="Recommended Fonts: Courier New, Ariel, Consolas, Segoe UI")
        font_combo = ttk.Combobox(self.app.tab7, textvariable=self.app.font_var, width=4, takefocus=False, state="readonly", values=list(font.families()))
        font_combo.set(self.app.current_font_name)
        font_combo.bind("<<ComboboxSelected>>", lambda event: set_font_and_size(self.app.font_var.get(), self.size_scale.get()))
        font_combo.pack(side="left", anchor="n", fill="x", expand=True)
        font_combo_tooltip = Tip.create(widget=font_combo, text=f"{self.app.current_font_name}")
        self.font_size_lbl = Label(self.app.tab7, text=f"Size: {self.app.font_size_var.get()}", width=14)
        self.font_size_lbl.pack(side="left", anchor="n")
        Tip.create(widget=self.font_size_lbl, text="Default size: 10")
        self.size_scale = ttk.Scale(self.app.tab7, from_=6, to=24, variable=self.app.font_size_var, takefocus=False)
        self.size_scale.set(self.app.current_font_size)
        self.size_scale.bind("<B1-Motion>", lambda event: set_font_and_size(self.app.font_var.get(), self.size_scale.get()))
        self.size_scale.pack(side="left", anchor="n", fill="x", expand=True)
        reset_btn = ttk.Button(self.app.tab7, text="Reset", width=5, takefocus=False, command=reset_to_defaults)
        reset_btn.pack(side="left", anchor="n")


#endregion
#region (8) MyTags


    def create_custom_dictionary_widgets_tab8(self):
        self.my_tags.create_tab8()



#endregion
#region (9) File Stats


    def create_stats_widgets_tab9(self):
        tab = Frame(self.app.tab9)
        tab.pack(fill='x', pady=4)
        self.stats_info_lbl = Label(tab, text="Characters: 0  |  Words: 0")
        self.stats_info_lbl.pack(side='left')
        refresh_btn = ttk.Button(tab, width=10, text="Refresh", takefocus=False, command=lambda: self.app.stat_calculator.calculate_file_stats(manual_refresh=True))
        refresh_btn.pack(side='right')
        Tip.create(widget=refresh_btn, text="Refresh the file stats")
        truncate_chk = ttk.Checkbutton(tab, text="Truncate Captions", takefocus=False, variable=self.app.truncate_stat_captions_var)
        truncate_chk.pack(side='right')
        Tip.create(widget=truncate_chk, text="Limit the displayed captions if they exceed either 8 words or 50 characters")
        image_video_chk = ttk.Checkbutton(tab, text="Image/Video Stats", takefocus=False, variable=self.app.process_image_stats_var)
        image_video_chk.pack(side='right')
        Tip.create(widget=image_video_chk, text="Enable/Disable image and video stat processing (Can be slow with many HD images or videos)")
        self.filestats_textbox = scrolledtext.ScrolledText(self.app.tab9, wrap="word", state="disabled")
        self.filestats_textbox.pack(fill='both', expand=True)


#endregion
