"""
########################################
#                                      #
#            IMG-TXT VIEWER            #
#                                      #
#   Version : v1.80                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
Display an image and text file side-by-side for easy manual caption editing.

More info here: https://github.com/Nenotriple/img-txt_viewer

"""
################################################################################################################################################
################################################################################################################################################
#                  #
#region -  Imports #
#                  #

import os
import re
import csv
import sys
import time
import shutil
import ctypes
import random
import requests
import threading
import subprocess
import tkinter.font
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.filedialog import askdirectory
from tkinter.scrolledtext import ScrolledText

##################
#                #
# Install Pillow #
#                #
##################

try:
    from PIL import Image, ImageTk
except ImportError:
    import subprocess, sys
    import threading
    from tkinter import Tk, Label, messagebox

    def download_pillow():
        cmd = ["pythonw", '-m', 'pip', 'install', 'pillow']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        for line in iter(lambda: process.stdout.readline(), b''):
            pillow_label = Label(root, wraplength=450)
            pillow_label.pack(anchor="w")
            pillow_label.config(text=line.rstrip())
        process.stdout.close()
        process.wait()
        done_label = Label(root, text="\nAll done! This window will now close...", wraplength=450)
        done_label.pack(anchor="w")
        root.after(3000, root.destroy)

    root = Tk()
    root.title("Pillow Is Installing...")
    root.geometry('600x200')
    root.resizable(False, False)
    root.withdraw()
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    install_pillow = messagebox.askyesno("Pillow not installed!", "Pillow not found!\npypi.org/project/Pillow\n\nWould you like to install it? ~2.5MB \n\n It's required to view images.")
    if install_pillow:
        root.deiconify()
        pillow_label = Label(root, wraplength=450)
        pillow_label.pack(anchor="w")
        pillow_label.config(text="Beginning Pillow install now...\n")
        threading.Thread(target=download_pillow).start()
        root.mainloop()
        from PIL import Image
    else:
        sys.exit()

#endregion
################################################################################################################################################
################################################################################################################################################
#                   #
#region -  ToolTips #
#                   #

class ToolTip:
    def __init__(self, widget, x_offset=0, y_offset=0):
        self.widget = widget
        self.tip_window = None
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.id = None
        self.hide_time = 0

    def show_tip(self, tip_text, x, y):
        if self.tip_window or not tip_text:
            return
        x, y = x + self.x_offset, y + self.y_offset
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.wm_attributes("-topmost", True)
        tw.wm_attributes("-disabled", True)
        label = Label(tw, text=tip_text, background="#ffffee", relief=RIDGE, borderwidth=1, justify=LEFT, padx=3, pady=3)
        label.pack()
        self.id = self.widget.after(3000, self.hide_tip)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
        self.hide_time = time.time()

    def create_tooltip(widget, text, delay=0, x_offset=0, y_offset=0):
        tool_tip = ToolTip(widget, x_offset, y_offset)
        def enter(event):
            if tool_tip.id is not None:
                widget.after_cancel(tool_tip.id)
            if time.time() - tool_tip.hide_time > 0.1:
                tool_tip.id = widget.after(delay, lambda: tool_tip.show_tip(text, widget.winfo_pointerx(), widget.winfo_pointery()))
        def leave(event):
            if tool_tip.id is not None:
                widget.after_cancel(tool_tip.id)
            tool_tip.hide_tip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

#endregion
################################################################################################################################################
################################################################################################################################################
#                       #
#region -  Autocomplete #
#                       #

class Autocomplete:
    def __init__(self, data_file, max_suggestions=4):
        self.data = self.load_data(data_file)
        self.max_suggestions = max_suggestions
        self.previous_text = None
        self.previous_suggestions = None

    def download_data(self):
        files = {
            'danbooru.csv': "https://raw.githubusercontent.com/Nenotriple/img-txt_viewer/main/danbooru.csv",
            'dictionary.csv': "https://raw.githubusercontent.com/Nenotriple/img-txt_viewer/main/dictionary.csv",
            'e621.csv': "https://raw.githubusercontent.com/Nenotriple/img-txt_viewer/main/e621.csv"
        }

        missing_files = [file for file in files if not os.path.exists(file)]
        if missing_files:
            download = messagebox.askyesno("Files not found.", f"The following dictionaries required for autocomplete suggestions were not found: \n\n{', '.join(missing_files)}.\n\nDo you want to download them from the repo? ~2MB each\n\nYes = Download All\nNo = Ignore")
            if download:
                for data_file in missing_files:
                    url = files[data_file]
                    response = requests.get(url)
                    with open(data_file, 'wb') as f:
                        f.write(response.content)

    def load_data(self, data_file, additional_file='my_tags.csv'):
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        data_file_path = os.path.join(application_path, data_file)
        additional_file_path = os.path.join(application_path, additional_file)
        data = {}
        if not os.path.isfile(data_file_path):
            self.download_data()
        if not os.path.isfile(data_file_path):
            return None
        with open(data_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and not row[0].startswith('###'):
                    true_name = row[0]
                    classifier_id = row[1]
                    similar_names = row[3].split(',') if len(row) > 3 else []
                    data[true_name] = (classifier_id, similar_names)
        if os.path.isfile(additional_file_path):
            with open(additional_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and not row[0].startswith('###'):
                        true_name = row[0]
                        similar_names = row[3].split(',') if len(row) > 3 else []
                        if true_name in data:
                            data[true_name][1].extend(similar_names)
                        else:
                            data[true_name] = ('', similar_names)
        return data

    def autocomplete(self, text):
        if not hasattr(self, 'data') or not self.data:
            return None
        text_with_underscores = text.replace(" ", "_")
        text_with_asterisks = text_with_underscores.replace("*", ".*")
        pattern = re.compile(text_with_asterisks)
        if self.previous_text is not None and text.startswith(self.previous_text):
            suggestions = [suggestion for suggestion in self.previous_suggestions if pattern.match(suggestion[0])]
        else:
            suggestions = []
            for true_name, (classifier_id, similar_names) in self.data.items():
                if len(suggestions) >= 100000:
                    break
                if pattern.match(true_name):
                    suggestions.append((true_name, classifier_id, similar_names))
                else:
                    for sim_name in similar_names:
                        if pattern.match(sim_name):
                            suggestions.append((true_name, classifier_id, similar_names))
                            break
        suggestions.sort(key=lambda x: self.get_score(x[0], text_with_underscores), reverse=True)
        self.previous_text = text
        self.previous_suggestions = suggestions
        return suggestions[:self.max_suggestions]

    def get_score(self, suggestion, text):
        score = 0
        if suggestion == text:
            score += len(text) * 2
        else:
            for i in range(len(text)):
                if i < len(suggestion) and suggestion[i] == text[i]:
                    score += 1
                else:
                    break
        if self.data[suggestion][0] == '' and suggestion[:3] == text[:3]:
            score += 1
        return score

#endregion
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
#                     #
#region -  Main Class #
#                     #

class ImgTxtViewer:
    def __init__(self, master):
        self.master = master

        # Window settings
        self.set_appid()
        self.set_window_size(master)
        self.set_icon()

        # Variables
        self.panes_swapped = False
        self.text_modified = False
        self.thread_running = False
        self.watcher_process = None
        self.user_selected_no = False
        self.is_alt_arrow_pressed = False
        self.current_index = 0
        self.prev_num_files = 0
        self.selected_suggestion_index = 0

        # File lists
        self.text_files = []
        self.image_files = []
        self.suggestions = []
        self.deleted_pairs = []
        self.new_text_files = []

        # Settings
        self.font_var = StringVar()
        self.max_img_width = IntVar(value=2500)
        self.undo_state = StringVar(value="disabled")
        self.image_dir = StringVar(value="Choose Directory")
        self.list_mode = BooleanVar(value=False)
        self.bold_commas = BooleanVar(value=False)
        self.cleaning_text = BooleanVar(value=True)
        self.auto_save_var = BooleanVar(value=False)
        self.highlighting_duplicates = BooleanVar(value=True)
        self.highlighting_all_duplicates = BooleanVar(value=False)

        # Autocomplete settings
        self.autocomplete = Autocomplete("danbooru.csv")
        self.csv_var = StringVar(value='danbooru.csv')
        self.suggestion_quantity = IntVar(value=4)

        # Bindings
        master.bind("<Control-f>", lambda event: self.toggle_highlight_all_duplicates())
        master.bind("<Control-s>", lambda event: self.save_text_file())
        master.bind("<Alt-Right>", lambda event: self.next_pair(event))
        master.bind("<Alt-Left>", lambda event: self.prev_pair(event))
        master.bind('<Delete>', lambda event: self.delete_pair())

#endregion
################################################################################################################################################
################################################################################################################################################
#                  #
#region -  Menubar #
#                  #

####### Initilize Menu Bar ############################################
        menubar = Menu(self.master)
        self.master.config(menu=menubar)

####### Options Menu ##################################################
        optionsMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=optionsMenu)

        # Edit Suggestions
        optionsMenu.add_command(label="Edit Custom Suggestions...", command=self.create_and_open_custom_dictionary)

        # Suggestion Dictionary Menu
        dictionaryMenu = Menu(optionsMenu, tearoff=0)
        optionsMenu.add_cascade(label="Suggestion Dictionary", menu=dictionaryMenu)
        dictionaryMenu.add_checkbutton(label="English Dictionary", variable=self.csv_var, onvalue='dictionary.csv', offvalue='danbooru.csv', command=self.change_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Danbooru", variable=self.csv_var, onvalue='danbooru.csv', offvalue='dictionary.csv', command=self.change_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="e621", variable=self.csv_var, onvalue='e621.csv', offvalue='danbooru.csv', command=self.change_autocomplete_dictionary)
        dictionaryMenu.add_separator()
        dictionaryMenu.add_checkbutton(label="All (slow)", variable=self.csv_var, onvalue='all', command=self.change_autocomplete_dictionary)

        # Suggestion Quantity Menu
        suggestion_quantity_menu = Menu(optionsMenu, tearoff=0)
        optionsMenu.add_cascade(label="Suggestion Quantity", menu=suggestion_quantity_menu)
        for i in range(1, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(i), variable=self.suggestion_quantity, value=i, command=lambda suggestion_quantity=i: self.set_suggestion_quantity(suggestion_quantity))

        # Text options and More
        optionsMenu.add_separator()
        optionsMenu.add_command(label="Font Options", command=self.set_font)
        optionsMenu.add_separator()

        # Max Image Size Menu
        sizeMenu = Menu(optionsMenu, tearoff=0)
        optionsMenu.add_cascade(label="Max Image Size", menu=sizeMenu)
        self.sizes = [("Smaller", 512),
                      ("Normal",  2500),
                      ("Larger",  4000)]
        for size in self.sizes:
            sizeMenu.add_radiobutton(label=size[0], variable=self.max_img_width, value=size[1], command=lambda s=size: self.save_text_file())

        optionsMenu.add_checkbutton(label="Highlighting Duplicates", variable=self.highlighting_duplicates)
        optionsMenu.add_checkbutton(label="Cleaning Text on Save", variable=self.cleaning_text)
        optionsMenu.add_checkbutton(label="Big Comma Mode", variable=self.bold_commas, command=self.toggle_big_comma_mode)
        optionsMenu.add_checkbutton(label="List View", variable=self.list_mode, command=self.toggle_list_mode)
        optionsMenu.add_separator()
        optionsMenu.add_command(label="Swap img-txt sides", command=self.swap_panes)
        optionsMenu.add_checkbutton(label="Always On Top", command=self.toggle_always_on_top)

####### Tools Menu ##################################################
        self.toolsMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=self.toolsMenu)

        # Tools
        self.toolsMenu.add_command(label="Open Directory...", command=self.open_current_directory)
        self.toolsMenu.add_command(label="Open Image...", command=self.open_current_image)
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Cleanup Text", command=self.cleanup_all_text_files)
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Batch Tag Delete...", command=self.batch_tag_delete)
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Search and Replace", command=self.search_and_replace)
        self.toolsMenu.add_command(label="Prefix Text Files", command=self.prefix_text_files)
        self.toolsMenu.add_command(label="Append Text Files", command=self.append_text_files)
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Delete img-txt Pair", command=self.delete_pair)
        self.toolsMenu.add_command(label="Undo Delete", command=self.undo_delete_pair, state="disabled")

#endregion
################################################################################################################################################
################################################################################################################################################
#                                    #
#region -  Buttons, Labels, and more #
#                                    #

        # This PanedWindow holds both master frames.
        self.paned_window = PanedWindow(master, orient=HORIZONTAL, sashwidth=10, bg="#d0d0d0", bd=0)
        self.paned_window.pack(fill=BOTH, expand=1)
        self.paned_window.bind('<ButtonRelease-1>', self.snap_sash_to_half)

        # This frame is exclusively used for the displayed image.
        self.master_image_frame = Frame(master)
        self.paned_window.add(self.master_image_frame, stretch="always")

        # This frame serves as a container for all primary UI frames, with the exception of the master_image_frame.
        self.master_control_frame = Frame(master)
        self.paned_window.add(self.master_control_frame, stretch="always", )
        self.paned_window.paneconfigure(self.master_control_frame, minsize=300)
        self.paned_window.sash_place(0, 5, 0)

        # Suggestion Label
        self.suggestion_textbox = Text(self.master_control_frame, height=1, borderwidth=0, highlightthickness=0, bg='#f0f0f0')
        self.suggestion_colors = {0: "black", 1: "#c00004", 2: "black", 3: "#a800aa", 4: "#00ab2c", 5: "#fd9200"} #0=General tags, 1=Artists, 2=UNUSED, 3=Copyright, 4=Character, 5=Meta

        # Text Box
        self.text_box = ScrolledText(self.master_control_frame, wrap=WORD, undo=True, maxundo=200, inactiveselectbackground="#c8c8c8")
        self.text_box.tag_configure("highlight", background="#5da9be", foreground="white")

        # Image Label
        self.image_preview = Label(self.master_image_frame)
        self.image_preview.pack(side=LEFT)
        self.image_preview.bind("<Double-1>", self.open_current_image)
        self.image_preview.bind('<Button-2>', self.open_current_directory)
        self.image_preview.bind("<MouseWheel>", self.mouse_scroll)
        self.image_preview.bind("<Button-3>", self.show_imageContext_menu)
        ToolTip.create_tooltip(self.image_preview, "Double-Click to open in system image viewer \n\nRight-click / Middle-click to open in file explorer\n\nALT+Left/Right, Mouse-Wheel to move between img-txt pairs", 1000, 6, 4)

        # Directory Button
        top_button_frame = Frame(self.master_control_frame)
        top_button_frame.pack(side=TOP, fill=X)
        self.directory_button = Button(top_button_frame, overrelief="groove", textvariable=self.image_dir, command=self.choose_working_directory)
        self.directory_button.pack(side=TOP, fill=X)
        self.directory_button.bind('<Button-2>', self.open_current_directory)
        self.directory_button.bind('<Button-3>', self.copy_to_clipboard)
        ToolTip.create_tooltip(self.directory_button, "Right click to copy path\n\nMiddle click to open in file explorer", 1000, 6, 4)

        # Save Button
        self.save_button = Button(top_button_frame, overrelief="groove", text="Save", fg="blue", command=self.save_text_file)
        self.save_button.pack(side=TOP, fill=X, pady=2)
        ToolTip.create_tooltip(self.save_button, "CTRL+S ", 1000, 6, 4)

        # Navigation Buttons
        nav_button_frame = Frame(self.master_control_frame)
        nav_button_frame.pack()
        self.next_button = Button(nav_button_frame, overrelief="groove", text="Next--->", command=lambda event=None: self.next_pair(event), width=16)
        self.prev_button = Button(nav_button_frame, overrelief="groove", text="<---Previous", command=lambda event=None: self.prev_pair(event), width=16)
        self.next_button.pack(side=RIGHT, padx=2, pady=2)
        self.prev_button.pack(side=RIGHT, padx=2, pady=2)
        ToolTip.create_tooltip(self.next_button, "ALT+R ", 1000, 6, 4)
        ToolTip.create_tooltip(self.prev_button, "ALT+L ", 1000, 6, 4)

        # Saved Label / Autosave
        saved_label_frame = Frame(self.master_control_frame)
        saved_label_frame.pack(pady=2)
        self.auto_save_checkbutton = Checkbutton(saved_label_frame, overrelief="groove", text="Auto-save", variable=self.auto_save_var, command=self.change_label)
        self.auto_save_checkbutton.pack(side=RIGHT)
        self.saved_label(saved_label_frame)


#endregion
################################################################################################################################################
################################################################################################################################################
#                            #
#region -  Text Box Bindings #
#                            #

        # Mouse binds
        self.text_box.bind("<Button-1>", lambda event: (self.remove_tag(), self.clear_suggestions()))
        self.text_box.bind("<Button-2>", lambda event: (self.delete_tag_under_mouse(event), self.change_label()))
        self.text_box.bind("<Button-3>", lambda event: (self.remove_highlight(), self.show_textContext_menu(event)))

        # Update the autocomplete suggestion label after every KeyRelease event.
        self.text_box.bind("<KeyRelease>", lambda event: (self.update_suggestions(event), self.toggle_big_comma_mode(event)))

        # Insert a newline after inserting an autocomplete suggestion when list_mode is active.
        self.text_box.bind('<comma>', self.insert_newline_listmode)

        # Highlight duplicates when selecting text with keyboard or mouse.
        self.text_box.bind("<Shift-Right>", lambda event: self.highlight_duplicates(event, mouse=False))
        self.text_box.bind("<Shift-Left>", lambda event: self.highlight_duplicates(event, mouse=False))
        self.text_box.bind("<ButtonRelease-1>", self.highlight_duplicates)

        # Removes highlights when these keys are pressed.
        self.text_box.bind("<Up>", lambda event: self.remove_highlight())
        self.text_box.bind("<Down>", lambda event: self.remove_highlight())
        self.text_box.bind("<Left>", lambda event: self.remove_highlight())
        self.text_box.bind("<Right>", lambda event: self.remove_highlight())
        self.text_box.bind("<BackSpace>", lambda event: (self.remove_highlight(), self.change_label()))

        # Sets the "saved_label" whenver a key is pressed.
        self.text_box.bind("<Key>", lambda event: self.change_label())

        # Disable normal button behavior
        self.text_box.bind("<Tab>", self.disable_button)
        self.text_box.bind("<Alt_L>", self.disable_button)
        self.text_box.bind("<Alt_R>", self.disable_button)

#endregion
################################################################################################################################################
################################################################################################################################################
#                    #
#region -  Info_Text #
#                    #


        self.info_text = ScrolledText(self.master_control_frame)
        self.info_text.pack(expand=True, fill='both')
        headers = [" Shortcuts:", " Tips:", " Text Tools:", " Auto-Save:"]
        content = [
            " ▪️ ALT+Left/Right: Quickly move between img-txt pairs.\n"
            " ▪️ Del: Send the current pair to a local trash folder.\n"
            " ▪️ ALT: Cycle through auto-suggestions.\n"
            " ▪️ TAB: Insert the highlighted suggestion.\n"
            " ▪️ CTRL+F: Highlight all duplicate words.\n"
            " ▪️ CTRL+S: Save the current text file.\n"
            " ▪️ CTRL+Z / CTRL+Y: Undo/Redo.\n"
            " ▪️ Middle-click a tag to delete it.\n",

            " ▪️ Highlight duplicates by selecting text.\n"
            " ▪️ List Mode: Display tags in a list format while saving in standard format.\n"
            " ▪️ Blank text files can be created for images without any matching pair when loading a directory.\n"
            " ▪️ When selecting a suggestion dictionary, you can use either Anime tags, English dictionary, or Both.\n"
            " ▪️ Running 'Edit Custom Suggestions' will create the file 'my_tags.csv' where you can add your own words to the suggestion dictionary.\n",

            " ▪️ Search and Replace: Edit all text files at once.\n"
            " ▪️ Prefix Text Files: Insert text at the START of all text files.\n"
            " ▪️ Append Text Files: Insert text at the END of all text files.\n"
            " ▪️ Batch Tag Delete: View all tags in a directory as a list, and quickly delete them.\n"
            " ▪️ Cleanup Text: Fix typos in all text files of the selected folder, such as duplicate tags, multiple spaces or commas, missing spaces, and more.\n",

            " ▪️ Check the auto-save box to save text when navigating between img/txt pairs or closing the window.\n"
            " ▪️ Text is cleaned up when saved, so you can ignore things like duplicate tags, trailing comma/spaces, double comma/spaces, etc.\n"
            " ▪️ Text cleanup can be disabled from the options menu.",
        ]
        for header, section in zip(headers, content):
            self.info_text.insert(END, header + "\n", "header")
            self.info_text.insert(END, section + "\n", "section")

        self.info_text.tag_config("header", font=("Segoe UI", 10, "bold"))
        self.info_text.tag_config("section", font=("Segoe UI", 10))
        self.info_text.bind("<Button-3>", self.show_textContext_menu)
        self.info_text.config(state='disabled', wrap=WORD)

#                 #
# End of __init__ #
#                 #
#endregion
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
#                                     #
#region -  Additional Interface Setup #
#                                     #

    def display_text_box(self):
        self.suggestion_textbox.pack(side=TOP, fill=X)
        self.text_box.pack(side=TOP, expand=YES, fill=BOTH)
        ToolTip.create_tooltip(self.suggestion_textbox,
                               "TAB: insert highlighted suggestion\n"
                               "ALT: Cycle suggestions\n\n"
                               "Danbooru Color Code:\n"
                               "  Black = Normal Tag\n"
                               "  Red = Artist\n"
                               "  Purple = Copyright\n"
                               "  Green = Character\n"
                               "  Orange = Other\n\n"
                               "e621 Color Code:\n"
                               "  Black = General\n"
                               "  Light Orange = Artist\n"
                               "  Purple = Copyright\n"
                               "  Green = Character\n"
                               "  Dark Orange = Species\n"
                               "  Red = Invalid, Meta\n"
                               "  Dark Green = Lore",
                               1000, 6, 4
                               )

    def display_index_frame(self):
        if not hasattr(self, 'index_frame'):
            self.index_frame = Frame(self.master_control_frame)
            self.index_frame.pack(side=TOP, expand=NO)
            self.image_index_entry = Entry(self.index_frame, width=5)
            self.image_index_entry.bind("<Return>", self.jump_to_image)
            self.image_index_entry.pack(side=LEFT, expand=NO)
            self.total_images_label = Label(self.index_frame, text=f"/{len(self.image_files)}")
            self.total_images_label.pack(side=LEFT, expand=YES)

    def saved_label(self, saved_label_frame):
        self.saved_label = Label(saved_label_frame, text="No Changes", width=23)
        self.saved_label.pack()
        self.text_box.bind("<Key>", lambda event: self.text_modified())

    # Text Box context menu
    def show_textContext_menu(self, e):
        textContext_menu = Menu(root, tearoff=0)
        widget_in_focus = root.focus_get()
        if widget_in_focus == self.info_text:
            textContext_menu.add_command(label="Copy", command=lambda: widget_in_focus.event_generate('<<Copy>>'))
        elif widget_in_focus == self.text_box:
            textContext_menu.add_command(label="Cut" + ' ' * 54 + "Ctrl-X", command=lambda: (widget_in_focus.event_generate('<<Cut>>'), self.change_label()))
            textContext_menu.add_command(label="Copy" + ' ' * 51 + "Ctrl-C", command=lambda: widget_in_focus.event_generate('<<Copy>>'))
            textContext_menu.add_command(label="Paste" + ' ' * 51 + "Ctrl-V", command=lambda: (widget_in_focus.event_generate('<<Paste>>'), self.change_label()))
            textContext_menu.add_command(label="Delete" + ' ' * 54 + "Del", command=lambda: (widget_in_focus.event_generate('<<Clear>>'), self.change_label()))
            textContext_menu.add_separator()
            textContext_menu.add_command(label="Undo" + ' ' * 51 + "Ctrl-Z", command=lambda: (widget_in_focus.event_generate('<<Undo>>'), self.change_label()))
            textContext_menu.add_command(label="Redo" + ' ' * 52 + "Ctrl-Y", command=lambda: (widget_in_focus.event_generate('<<Redo>>'), self.change_label()))
            textContext_menu.add_separator()
            textContext_menu.add_command(label="Open Directory...", command=self.open_current_directory)
            textContext_menu.add_separator()
            textContext_menu.add_command(label="Highlight all Duplicates" + ' ' * 20 + "Ctrl-F", command=self.highlight_all_duplicates)
            textContext_menu.add_separator()
            textContext_menu.add_checkbutton(label="Highlighting Duplicates", variable=self.highlighting_duplicates)
            textContext_menu.add_checkbutton(label="Clean Text on Save", variable=self.cleaning_text)
            textContext_menu.add_checkbutton(label="Big Comma Mode", variable=self.bold_commas, command=self.toggle_big_comma_mode)
            textContext_menu.add_checkbutton(label="List View", variable=self.list_mode, command=self.toggle_list_mode)
        textContext_menu.tk_popup(e.x_root, e.y_root)

    # Image context menu
    def show_imageContext_menu(self, event):
        imageContext_menu = Menu(self.master, tearoff=0)
        imageContext_menu.add_command(label="Open Directory...", command=self.open_current_directory)
        imageContext_menu.add_command(label="Open Image...", command=self.open_current_image)
        imageContext_menu.add_separator()
        imageContext_menu.add_command(label="Delete img-txt Pair" + ' ' * 8 + "Del", command=self.delete_pair)
        imageContext_menu.add_command(label="Undo Delete", command=self.undo_delete_pair, state=self.undo_state.get())
        imageContext_menu.add_separator()
        imageContext_menu.add_command(label="Swap img/txt sides", command=self.swap_panes)
        imageContext_menu.add_separator()
        for size in self.sizes:
            imageContext_menu.add_radiobutton(label=size[0], variable=self.max_img_width, value=size[1], command=lambda s=size: self.save_text_file())
        imageContext_menu.tk_popup(event.x_root, event.y_root)

    def configure_pane_position(self):
        window_width = self.master.winfo_width()
        self.paned_window.sash_place(0, window_width // 2, 0)
        self.paned_window.paneconfigure(self.master_image_frame, minsize=300)

    def swap_panes(self):
        self.paned_window.remove(self.master_image_frame)
        self.paned_window.remove(self.master_control_frame)
        if not self.panes_swapped:
            self.paned_window.add(self.master_control_frame)
            self.paned_window.add(self.master_image_frame)
        else:
            self.paned_window.add(self.master_image_frame)
            self.paned_window.add(self.master_control_frame)
        self.configure_pane_position()
        self.paned_window.paneconfigure(self.master_control_frame, minsize=300)
        self.panes_swapped = not self.panes_swapped

    def snap_sash_to_half(self, event):
        total_width = self.paned_window.winfo_width()
        half_point = int(total_width / 2)
        sash_pos = self.paned_window.sash_coord(0)[0]
        if abs(sash_pos - half_point) < 75:
            self.paned_window.sash_place(0, half_point, 0)

    def toggle_always_on_top(self):
        current_state = root.attributes('-topmost')
        new_state = 0 if current_state == 1 else 1
        root.attributes('-topmost', new_state)

    def set_icon(self):
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(__file__)
        icon_path = os.path.join(application_path, "icon.ico")
        try:
            self.master.iconbitmap(icon_path)
        except TclError:
            pass

#endregion
################################################################################################################################################
################################################################################################################################################
#                       #
#region -  Autocomplete #
#                       #

### Display Suggestions ##################################################
    def handle_suggestion_event(self, event):
        if event.keysym == "Tab":
            if self.selected_suggestion_index < len(self.suggestions):
                selected_suggestion = self.suggestions[self.selected_suggestion_index]
                if isinstance(selected_suggestion, tuple):
                    selected_suggestion = selected_suggestion[0]
                selected_suggestion = selected_suggestion.strip()
                self.insert_selected_suggestion(selected_suggestion)
            self.clear_suggestions()
        elif event.keysym in ("Alt_L", "Alt_R"):
            if self.suggestions and not self.is_alt_arrow_pressed:
                if event.keysym == "Alt_R":
                    self.selected_suggestion_index = (self.selected_suggestion_index - 1) % len(self.suggestions)
                else:
                    self.selected_suggestion_index = (self.selected_suggestion_index + 1) % len(self.suggestions)
                self.highlight_suggestions()
            self.is_alt_arrow_pressed = False
        elif event.keysym in ("Up", "Down", "Left", "Right"):
            self.clear_suggestions()
        elif event.char == ",":
            self.clear_suggestions()
        else:
            return False
        return True

    def update_suggestions(self, event=None):
        tags_with_underscore = self.get_tags_with_underscore()
        if event is None:
            event = type('', (), {})()
            event.keysym = ''
            event.char = ''
        cursor_position = self.text_box.index("insert")
        if self.cursor_inside_tag(cursor_position):
            self.clear_suggestions()
            return
        if self.handle_suggestion_event(event):
            return
        text = self.text_box.get("1.0", "insert")
        self.clear_suggestions()
        if self.list_mode.get():
            elements = [element.strip() for element in text.split('\n')]
        else:
            elements = [element.strip() for element in text.split(',')]
        current_word = elements[-1]
        current_word = current_word.strip()
        if current_word:
            suggestions = self.autocomplete.autocomplete(current_word)
            suggestions.sort(key=lambda x: self.autocomplete.get_score(x[0], current_word), reverse=True)
            self.suggestions = [(suggestion[0].replace("_", " ") if suggestion[0] not in tags_with_underscore else suggestion[0], suggestion[1]) for suggestion in suggestions]
            if self.suggestions:
                self.highlight_suggestions()
            else:
                self.clear_suggestions()
        else:
            self.clear_suggestions()

    def highlight_suggestions(self):
        self.suggestion_textbox.config(state='normal')
        self.suggestion_textbox.delete('1.0', 'end')
        for i, (s, classifier_id) in enumerate(self.suggestions):
            if classifier_id and classifier_id.isdigit():
                color_id = int(classifier_id) % len(self.suggestion_colors)
            else:
                color_id = 0
            color = self.suggestion_colors[color_id]
            if i == self.selected_suggestion_index:
                self.suggestion_textbox.insert('end', "⚫")
                self.suggestion_textbox.insert('end', s, color)
                self.suggestion_textbox.tag_config(color, foreground=color, font=('Segoe UI', '9'))
            else:
                self.suggestion_textbox.insert('end', "⚪")
                self.suggestion_textbox.insert('end', s, color)
                self.suggestion_textbox.tag_config(color, foreground=color, font=('Segoe UI', '9'))
            if i != len(self.suggestions) - 1:
                self.suggestion_textbox.insert('end', ', ')
        self.suggestion_textbox.config(state='disabled')

    def cursor_inside_tag(self, cursor_position):
        line, column = map(int, cursor_position.split('.'))
        line_text = self.text_box.get(f"{line}.0", f"{line}.end")
        if self.list_mode.get():
            inside_tag = column not in (0, len(line_text))
        else:
            inside_tag = not (column == 0 or line_text[column-1:column] in (',', ' ') or line_text[column:column+1] in (',', ' ') or column == len(line_text))
        return inside_tag

    def clear_suggestions(self):
        self.suggestions = []
        self.selected_suggestion_index = 0
        self.suggestion_textbox.config(state='normal')
        self.suggestion_textbox.delete('1.0', 'end')
        self.suggestion_textbox.insert('1.0', "...")
        self.suggestion_textbox.config(state='disabled')

### Insert Suggestion ##################################################

    def insert_selected_suggestion(self, selected_suggestion):
        selected_suggestion = selected_suggestion.strip()
        text = self.text_box.get("1.0", "insert").rstrip()
        elements = [element.strip() for element in text.split('\n' if self.list_mode.get() else ',')]
        current_word = elements[-1]
        remaining_text = self.text_box.get("insert", "end").rstrip('\n')
        start_of_current_word = "1.0 + {} chars".format(len(text) - len(current_word))
        self.text_box.delete(start_of_current_word, "insert")
        if not remaining_text.startswith(('\n' if self.list_mode.get() else ',')):
            self.text_box.insert(start_of_current_word, selected_suggestion + ('\n' if self.list_mode.get() else ', '))
        else:
            self.text_box.insert(start_of_current_word, selected_suggestion)
        cleaned_text = self.cleanup_text(self.text_box.get("1.0", "end"))
        if not self.list_mode.get():
            cleaned_text = cleaned_text.rstrip() + ', '
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", cleaned_text)
        self.position_cursor(start_of_current_word, selected_suggestion)
        if self.list_mode.get():
            self.insert_newline_listmode(called_from_insert=True)

    def position_cursor(self, start_of_current_word, selected_suggestion):
        if self.text_box.get(start_of_current_word).startswith(' '):
            offset = len(selected_suggestion) + 2
        else:
            offset = len(selected_suggestion) + 1
        self.text_box.mark_set("insert", "{}+{}c".format(start_of_current_word, offset))
        self.text_box.insert("insert", " ")

    def insert_newline_listmode(self, event=None, called_from_insert=False):
        if self.list_mode.get():
            self.text_box.insert(INSERT, '\n')
            if called_from_insert and self.text_box.index(INSERT) != self.text_box.index("end-1c"):
                self.text_box.mark_set("insert", "insert-1l")
            return 'break'

### Suggestion Settings ##################################################

    def change_autocomplete_dictionary(self):
        if self.csv_var.get() == 'all':
            self.autocomplete = Autocomplete('danbooru.csv')
            self.autocomplete.data.update(Autocomplete('dictionary.csv').data)
            self.autocomplete.data.update(Autocomplete('e621.csv').data)
        elif self.csv_var.get() == 'e621.csv':
            self.autocomplete = Autocomplete(self.csv_var.get())
            self.suggestion_colors = {-1: "black", 0: "black", 1: "#f2ac08", 3: "#dd00dd", 4: "#00aa00", 5: "#ed5d1f", 6: "#ff3d3d", 7: "#ff3d3d", 8: "#228822"}
        else:
            self.autocomplete = Autocomplete(self.csv_var.get())

    def set_suggestion_quantity(self, suggestion_quantity):
        self.autocomplete.max_suggestions = suggestion_quantity
        self.update_suggestions(event=None)

    def get_tags_with_underscore(self):
        return {"0_0", "o_o", ">_o", "x_x", "|_|", "._.", "^_^", ">_<", "@_@", ">_@", "+_+", "+_-", "=_=", "<o>_<o>", "<|>_<|>", "ಠ_ಠ"}

#endregion
################################################################################################################################################
################################################################################################################################################
#                             #
#region -  TextBox Highlights #
#                             #

    def highlight_duplicates(self, event, mouse=True):
        if not self.highlighting_duplicates.get():
            return
        self.text_box.after_idle(self._highlight_duplicates, mouse)

    def _highlight_duplicates(self, mouse):
        self.text_box.tag_remove("highlight", "1.0", "end")
        if not self.text_box.tag_ranges("sel"):
            return
        selected_text = self.text_box.selection_get().strip()
        selected_text = selected_text.replace(',', '')
        if len(selected_text) < 3:
            return
        selected_words = selected_text.split()
        for word in selected_words:
            if len(word) < 3:
                continue
            pattern = re.escape(word)
            matches = [match for match in re.finditer(pattern, self.text_box.get("1.0", "end"))]
            if len(matches) > 1:
                for match in matches:
                    start = match.start()
                    end = match.end()
                    self.text_box.tag_add("highlight", f"1.0 + {start} chars", f"1.0 + {end} chars")

    def toggle_highlight_all_duplicates(self):
        self.highlighting_all_duplicates.set(not self.highlighting_all_duplicates.get())
        if self.highlighting_all_duplicates.get():
            self.highlight_all_duplicates()
        else:
            self.remove_highlight()

    def highlight_all_duplicates(self):
        self.text_box.tag_remove("highlight", "1.0", "end")
        text = self.text_box.get("1.0", "end").strip().replace(',', '')
        words = text.split()
                        # Blue      Pink      Green     Brown     Purple
        pastel_colors = ["A2D2FF", "FFAFCF", "AEC3AE", "EBE3D5", "BEADFA",
                         "CDF5FD", "FDCEDF", "C3EDC0", "D6C7AE", "DFCCFB",
                         "C0DBEA", "F2D8D8", "CBFFA9", "F9F3CC", "ACB1D6",
                         "A1CCD1", "DBA39A", "C4D7B2", "FFD9B7", "D9ACF5",
                         "7895B2", "FF8787", "90A17D", "F8C4B4", "AF7AB3"]
        random.shuffle(pastel_colors)
        color_dict = {}
        for word in set(words):
            if len(word) < 3 or words.count(word) == 1:
                continue
            if word not in color_dict and pastel_colors:
                color = pastel_colors.pop(0)
                color_dict[word] = '#' + color
                self.text_box.tag_config(word, background=color_dict[word])
            start = "1.0"
            while True:
                pos = self.text_box.search(word, start, stopindex="end")
                if not pos:
                    break
                end = f"{pos} + {len(word)}c"
                self.text_box.tag_add(word, pos, end)
                start = end

    def remove_highlight(self):
        self.text_box.tag_remove("highlight", "1.0", "end")
        self.master.after(100, lambda: self.remove_tag())

    def remove_tag(self):
        self.highlighting_all_duplicates.set(False)
        for tag in self.text_box.tag_names():
            self.text_box.tag_remove(tag, "1.0", "end")
        if self.bold_commas.get():
            self.toggle_big_comma_mode()

#endregion
################################################################################################################################################
################################################################################################################################################
#                            #
#region -  Primary Functions #
#                            #

    def load_pairs(self):
        self.info_text.pack_forget()
        self.image_files = []
        self.text_files = []
        self.new_text_files = []
        files_in_dir = sorted(os.listdir(self.image_dir.get()), key=self.natural_sort)
        for filename in files_in_dir:
            filename = self.rename_odd_files(filename)
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp")):
                image_file_path = os.path.join(self.image_dir.get(), filename)
                self.image_files.append(image_file_path)
                text_filename = os.path.splitext(filename)[0] + ".txt"
                text_file_path = os.path.join(self.image_dir.get(), text_filename)
                if not os.path.exists(text_file_path):
                    self.new_text_files.append(filename)
                self.text_files.append(text_file_path)
        if self.new_text_files:
            self.create_blank_textfiles(self.new_text_files)
        self.show_pair()
        self.saved_label.config(text="No Changes", bg="#f0f0f0", fg="black")
        self.configure_pane_position()
        self.directory_button.config(relief=GROOVE, overrelief=RIDGE)
        if hasattr(self, 'total_images_label'):
            self.total_images_label.config(text=f"/{len(self.image_files)}")
        self.prev_num_files = len(files_in_dir)

    def show_pair(self):
        if self.image_files:
            self.image_file = self.image_files[self.current_index]
            try:
                text_file = self.text_files[self.current_index]
            except IndexError:
                text_file = None
            image = Image.open(self.image_file)
            max_img_width = self.max_img_width.get()
            max_height = 2000
            image, _ = self.resize_and_scale_image(image, max_img_width, max_height)
            self.image_preview.config(width=max_img_width, height=max_height)
            self.image_preview.bind("<Configure>", lambda event: self.resize_and_scale_image(image, max_img_width, max_height, event))
            self.text_box.config(undo=False)
            self.text_box.delete("1.0", END)
            if text_file and os.path.isfile(text_file):
                with open(text_file, "r") as f:
                    self.text_box.insert(END, f.read())
            self.text_modified = False
            self.text_box.config(undo=True)
            self.update_image_index()
            self.display_text_box()
            window_height = self.image_preview.winfo_height()
            window_width = self.image_preview.winfo_width()
            event = Event()
            event.height = window_height
            event.width = window_width
            self.resize_and_scale_image(image, max_img_width, max_height, event)
        self.toggle_big_comma_mode()
        self.toggle_list_mode()
        self.clear_suggestions()
        self.highlighting_all_duplicates.set(False)

    def resize_and_scale_image(self, image, max_img_width, max_height, event=None):
        w, h = image.size
        aspect_ratio = w / h
        if w > max_img_width or h > max_height:
            if w > h:
                new_width = min(max_img_width, w)
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = min(max_height, h)
                new_width = int(new_height * aspect_ratio)
            image = image.resize((new_width, new_height))
        if event:
            window_height = event.height
            window_width = event.width
            new_height = window_height
            new_width = int(new_height * aspect_ratio)
            if new_width > window_width:
                new_width = window_width
                new_height = int(new_width / aspect_ratio)
            image = image.resize((new_width, new_height))
            photo = ImageTk.PhotoImage(image)
            self.image_preview.config(image=photo)
            self.image_preview.image = photo
        return image, aspect_ratio

#endregion
################################################################################################################################################
################################################################################################################################################
#                     #
#region -  Navigation #
#                     #

    def next_pair(self, event):
        if self.image_dir.get() == "Choose Directory":
            return
        self.is_alt_arrow_pressed = True
        num_files_in_dir = len(os.listdir(self.image_dir.get()))
        if num_files_in_dir != self.prev_num_files:
            self.load_pairs()
        if not self.text_modified:
            self.saved_label.config(text="No Changes", bg="#f0f0f0", fg="black")
        self.text_box.config(undo=False)
        self.text_box.edit_reset()
        if self.current_index < len(self.image_files) - 1:
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index += 1
        else:
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index = 0
        self.show_pair()

    def prev_pair(self, event):
        if self.image_dir.get() == "Choose Directory":
            return
        self.is_alt_arrow_pressed = True
        num_files_in_dir = len(os.listdir(self.image_dir.get()))
        if num_files_in_dir != self.prev_num_files:
            self.load_pairs()
        if not self.text_modified:
            self.saved_label.config(text="No Changes", bg="#f0f0f0", fg="black")
        self.text_box.config(undo=False)
        self.text_box.edit_reset()
        if self.current_index > 0:
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index -= 1
        else:
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index = len(self.image_files) - 1
        self.show_pair()

    def jump_to_image(self, event):
        try:
            index = int(self.image_index_entry.get()) - 1
            if index < 0:
                index = 0
            elif index >= len(self.image_files):
                index = len(self.image_files) - 1
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index = index
            self.show_pair()
            if not self.text_modified:
                self.saved_label.config(text="No Changes", bg="#f0f0f0", fg="black")
        except ValueError:
            pass

    def update_image_index(self):
        self.display_index_frame()
        self.image_index_entry.delete(0, END)
        self.image_index_entry.insert(0, f"{self.current_index + 1}")

    def mouse_scroll(self, event):
        if event.delta > 0:
            self.next_pair(event)
        else:
            self.prev_pair(event)

#endregion
################################################################################################################################################
################################################################################################################################################
#                       #
#region -  Text Options #
#                       #

    def set_font(self, event=None):
        def open_dropdown(event):
            event.widget.after(100, lambda: event.widget.event_generate('<Down>'))
        current_font = self.text_box.cget("font")
        current_font_name = self.text_box.tk.call("font", "actual", current_font, "-family")
        current_font_size = self.text_box.tk.call("font", "actual", current_font, "-size")
        dialog = Toplevel(self.master)
        dialog.focus_force()
        self.position_dialog(dialog, 220, 100)
        dialog.geometry("220x100")
        dialog.title("Font Options")
        dialog.attributes('-toolwindow', True)
        dialog.resizable(False, False)
        Label(dialog, text="Font:").pack()
        font_box = ttk.Combobox(dialog, textvariable=self.font_var, width=50)
        font_box['values'] = list(tkinter.font.families())
        font_box.set(current_font_name)
        font_box.bind("<<ComboboxSelected>>", lambda event: self.set_font_and_size(self.font_var.get(), size_var.get(), dialog))
        font_box.bind("<Button-1>", open_dropdown)
        ToolTip.create_tooltip(font_box, "Recommended Fonts: Courier New, Ariel, Consolas, Segoe UI", 200, 6, 4)
        font_box.pack()
        Label(dialog, text="Font Size:").pack()
        size_var = StringVar()
        size_box = ttk.Combobox(dialog, textvariable=size_var, width=50)
        size_box['values'] = list(range(9, 19))
        size_box.set(current_font_size)
        size_box.bind("<<ComboboxSelected>>", lambda event: self.set_font_and_size(self.font_var.get(), size_var.get(), dialog))
        size_box.bind("<Button-1>", open_dropdown)
        ToolTip.create_tooltip(size_box, "Default size = 10", 200, 6, 4)
        size_box.pack()

    def set_font_and_size(self, font, size, dialog):
        if font and size:
            self.text_box.config(font=(font, int(size)))

    def toggle_list_mode(self, event=None):
        self.text_box.config(undo=False)
        if self.list_mode.get():
            contents = self.text_box.get("1.0", "end").strip().split(',')
            formatted_contents = '\n'.join([item.strip() for item in contents if item.strip()])
            self.text_box.delete("1.0", "end")
            self.text_box.insert("1.0", self.cleanup_text(formatted_contents))
            self.text_box.insert(END, "\n")
        else:
            contents = self.text_box.get("1.0", "end").strip().split('\n')
            formatted_contents = ', '.join([item for item in contents if item])
            self.text_box.delete("1.0", "end")
            self.text_box.insert("1.0", self.cleanup_text(formatted_contents))
        self.text_box.config(undo=True)

    def toggle_big_comma_mode(self, event=None):
        if self.bold_commas.get():
            self.text_box.tag_remove("bold", "1.0", "end")
            index = "1.0"
            while True:
                index = self.text_box.search(",", index, stopindex="end")
                if not index:
                    break
                self.text_box.tag_add("bold", index, "{}+1c".format(index))
                index = "{}+1c".format(index)
            self.text_box.tag_configure("bold", font=(self.font_var.get(), 18, "bold"))
        else:
            self.text_box.tag_remove("bold", "1.0", "end")

#endregion
################################################################################################################################################
################################################################################################################################################
#                     #
#region -  Text Tools #
#                     #

    def batch_tag_delete(self):
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(application_path, 'batch_tag_delete.py')
        self.watcher_process = subprocess.Popen(["pythonw", script_path, self.image_dir.get()])
        threading.Thread(target=self.watch_files).start()
        self.thread_running = True

    def search_and_replace(self):
        if not self.check_directory():
            return
        self.delete_text_backup()
        dialog = Toplevel(self.master)
        dialog.focus_force()
        self.position_dialog(dialog, 345, 145)
        dialog.geometry("345x145")
        dialog.title("Search and Replace")
        dialog.attributes('-toolwindow', True)
        dialog.resizable(False, False)
        Label(dialog, text="Search For:").pack()
        search_string_var = StringVar()
        search_string_entry = Entry(dialog, textvariable=search_string_var, width=55)
        default_text = "Enter EXACT search string here"
        search_string_entry.insert(0, default_text)
        search_string_entry.bind('<FocusIn>', lambda event: self.clear_entry_field(event, search_string_entry, default_text))
        search_string_entry.pack()
        Label(dialog, text="\nReplace With:\n(Leave empty to replace with nothing)").pack()
        replace_string_var = StringVar()
        replace_string_entry = Entry(dialog, textvariable=replace_string_var, width=55)
        default_replace_text = ""
        replace_string_entry.insert(0, default_replace_text)
        replace_string_entry.bind('<FocusIn>', lambda event: self.clear_entry_field(event, replace_string_entry, default_replace_text))
        replace_string_entry.pack()
        def perform_search_and_replace():
            search_string = search_string_var.get()
            replace_string = replace_string_var.get()
            total_count = 0
            backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
            os.makedirs(backup_folder, exist_ok=True)
            for text_file in self.text_files:
                try:
                    with open(text_file, 'r') as file:
                        filedata = file.read()
                    count = filedata.count(search_string)
                    total_count += count
                except Exception as e:
                    print(f"Error while processing file {text_file}: {e}")
            msg = f"The string: '{search_string}'\n\nWas found {total_count} times across all files.\n\nDo you want to replace it with:\n\n{replace_string}"
            if messagebox.askyesno("Confirmation", msg):
                for text_file in self.text_files:
                    try:
                        backup_file = os.path.join(backup_folder, os.path.basename(text_file) + '.bak')
                        shutil.copy2(text_file, backup_file)
                        with open(text_file, 'r') as file:
                            filedata = file.read()
                        filedata = filedata.replace(search_string, replace_string)
                        with open(text_file, 'w') as file:
                            file.write(filedata)
                    except Exception as e:
                        print(f"Error while processing file {text_file}: {e}")
            self.show_pair()
        def undo_search_and_replace():
            backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
            for text_file in self.text_files:
                try:
                    backup_file = os.path.join(backup_folder, os.path.basename(text_file) + '.bak')
                    if os.path.exists(backup_file):
                        shutil.move(backup_file, text_file)
                except Exception as e:
                    print(f"Error while undoing changes for file {text_file}: {e}")
            self.show_pair()
        def close_dialog():
            self.delete_text_backup()
            dialog.destroy()
            self.show_pair()
        search_and_replace_button_frame = Frame(dialog)
        search_and_replace_button_frame.pack()
        Button(search_and_replace_button_frame, overrelief="groove", text="OK", command=perform_search_and_replace, width=15, relief=RAISED, borderwidth=3).pack(side=LEFT, pady=2, padx=2)
        Button(search_and_replace_button_frame, overrelief="groove", text="Undo", command=undo_search_and_replace, width=15).pack(side=LEFT, pady=2, padx=2)
        Button(search_and_replace_button_frame, overrelief="groove", text="Cancel", command=close_dialog, width=15).pack(side=LEFT, pady=2, padx=2)

    def prefix_text_files(self):
        if not self.check_directory():
            return
        self.delete_text_backup()
        dialog = Toplevel(self.master)
        dialog.focus_force()
        self.position_dialog(dialog, 405, 75)
        dialog.geometry("405x75")
        dialog.title("Prefix Text Files")
        dialog.attributes('-toolwindow', True)
        dialog.resizable(False, False)
        Label(dialog, text="Text to Prefix:").pack()
        prefix_text_var = StringVar()
        prefix_text_entry = Entry(dialog, textvariable=prefix_text_var, width=65)
        default_text = "Enter the text you want to prefix here"
        prefix_text_entry.insert(0, default_text)
        prefix_text_entry.bind('<FocusIn>', lambda event: self.clear_entry_field(event, prefix_text_entry, default_text))
        prefix_text_entry.pack()
        def perform_prefix_text():
            prefix_text = prefix_text_var.get()
            if not prefix_text.endswith(', '):
                prefix_text += ', '
            backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
            os.makedirs(backup_folder, exist_ok=True)
            for text_file in self.text_files:
                try:
                    backup_file = os.path.join(backup_folder, os.path.basename(text_file) + '.bak')
                    shutil.copy2(text_file, backup_file)
                    with open(text_file, 'r+') as file:
                        content = file.read()
                        file.seek(0, 0)
                        file.write(prefix_text + content)
                except Exception as e:
                    print(f"Error while processing file {text_file}: {e}")
            self.show_pair()
        def undo_prefix_text():
            backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
            for text_file in self.text_files:
                try:
                    backup_file = os.path.join(backup_folder, os.path.basename(text_file) + '.bak')
                    if os.path.exists(backup_file):
                        shutil.move(backup_file, text_file)
                except Exception as e:
                    print(f"Error while undoing changes for file {text_file}: {e}")
            self.show_pair()
        def close_dialog():
            self.delete_text_backup()
            dialog.destroy()
            self.show_pair()
        prefix_text_button_frame = Frame(dialog)
        prefix_text_button_frame.pack()
        Button(prefix_text_button_frame, overrelief="groove", text="OK", command=lambda: messagebox.askokcancel("Confirmation", f"Are you sure you want to prefix all files with:\n\n'{prefix_text_var.get()}, '", parent=dialog) and perform_prefix_text(), width=15, relief=RAISED, borderwidth=3).pack(side=LEFT, pady=2, padx=2)
        Button(prefix_text_button_frame, overrelief="groove", text="Undo", command=undo_prefix_text, width=15).pack(side=LEFT, pady=2, padx=2)
        Button(prefix_text_button_frame, overrelief="groove", text="Cancel", command=close_dialog, width=15).pack(side=LEFT, pady=2, padx=2)

    def append_text_files(self):
        if not self.check_directory():
            return
        self.delete_text_backup()
        dialog = Toplevel(self.master)
        dialog.focus_force()
        self.position_dialog(dialog, 405, 75)
        dialog.geometry("405x75")
        dialog.title("Append Text Files")
        dialog.attributes('-toolwindow', True)
        dialog.resizable(False, False)
        Label(dialog, text="Text to Append:").pack()
        append_text_var = StringVar()
        append_text_entry = Entry(dialog, textvariable=append_text_var, width=65)
        default_text = "Enter the text you want to append here"
        append_text_entry.insert(0, default_text)
        append_text_entry.bind('<FocusIn>', lambda event: self.clear_entry_field(event, append_text_entry, default_text))
        append_text_entry.pack()
        def perform_append_text():
            append_text = append_text_var.get()
            if not append_text.startswith(', '):
                append_text = ', ' + append_text
            backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
            os.makedirs(backup_folder, exist_ok=True)
            for text_file in self.text_files:
                try:
                    backup_file = os.path.join(backup_folder, os.path.basename(text_file) + '.bak')
                    shutil.copy2(text_file, backup_file)
                    with open(text_file, 'a') as file:
                        file.write(append_text)
                except Exception as e:
                    print(f"Error while processing file {text_file}: {e}")
            self.show_pair()
        def undo_append_text():
            backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
            for text_file in self.text_files:
                try:
                    backup_file = os.path.join(backup_folder, os.path.basename(text_file) + '.bak')
                    if os.path.exists(backup_file):
                        shutil.move(backup_file, text_file)
                except Exception as e:
                    print(f"Error while undoing changes for file {text_file}: {e}")
            self.show_pair()
        def close_dialog():
            self.delete_text_backup()
            dialog.destroy()
            self.show_pair()
        append_text_button_frame = Frame(dialog)
        append_text_button_frame.pack()
        Button(append_text_button_frame, overrelief="groove", text="OK", command=lambda: messagebox.askokcancel("Confirmation", f"Are you sure you want to append all files with:\n\n', {append_text_var.get()}'", parent=dialog) and perform_append_text(), width=15, relief=RAISED, borderwidth=3).pack(side=LEFT, pady=2, padx=2)
        Button(append_text_button_frame, overrelief="groove", text="Undo", command=undo_append_text, width=15).pack(side=LEFT, pady=2, padx=2)
        Button(append_text_button_frame, overrelief="groove", text="Cancel", command=close_dialog, width=15).pack(side=LEFT, pady=2, padx=2)

    def clear_entry_field(self, event, entry, default_text):
        if entry.get() == default_text:
            entry.delete(0, END)

    def delete_tag_under_mouse(self, event):
        cursor_pos = self.text_box.index(f"@{event.x},{event.y}")
        line_start = self.text_box.index(f"{cursor_pos} linestart")
        line_end = self.text_box.index(f"{cursor_pos} lineend")
        line_text = self.text_box.get(line_start, line_end)
        tags = line_text.split(',')
        for tag in tags:
            start_of_tag = line_text.find(tag)
            end_of_tag = start_of_tag + len(tag)
            if start_of_tag <= int(cursor_pos.split('.')[1]) <= end_of_tag:
                clicked_tag = tag
                break
        start_of_clicked_tag = line_text.find(clicked_tag)
        end_of_clicked_tag = start_of_clicked_tag + len(clicked_tag)
        self.text_box.tag_add("highlight", f"{line_start}+{start_of_clicked_tag}c", f"{line_start}+{end_of_clicked_tag}c")
        self.text_box.tag_config("highlight", background="#FD8A8A")
        self.text_box.update_idletasks()
        time.sleep(0.2)
        self.text_box.delete(f"{line_start}+{start_of_clicked_tag}c", f"{line_start}+{end_of_clicked_tag}c")
        cleaned_text = self.cleanup_text(self.text_box.get("1.0", "end"))
        cleaned_text = '\n'.join([line for line in cleaned_text.split('\n') if line.strip() != ''])
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", cleaned_text)
        self.text_box.tag_configure("highlight", background="#5da9be")

    def cleanup_all_text_files(self, show_confirmation=True):
        if not self.check_directory():
            return
        if show_confirmation:
            user_confirmation = messagebox.askokcancel("Confirmation", "This operation will clean all text files from typos like:\nDuplicate tags, Extra commas, Extra spaces, trailing commas/spaces, commas without spaces, and more.\n\nExample Cleanup:\n  From: dog,solo,  ,happy  ,,\n       To: dog, solo, happy")
            self.saved_label.config(text="Text Files Cleaned Up!", bg="#6ca079", fg="white")
            if not user_confirmation:
                return
        for text_file in self.text_files:
            with open(text_file, "r+", encoding="utf-8") as f:
                text = f.read().strip()
                cleaned_text = self.cleanup_text(text)
                f.seek(0)
                f.write(cleaned_text)
                f.truncate()
        self.show_pair()

#endregion
################################################################################################################################################
################################################################################################################################################
#                        #
#region - Misc Functions #
#                        #

    # Used to watch the current text file for changes while batch_tag_delete is running.
    def watch_files(self):
        self.saved_label.config(text="Batch Tag Delete!", bg="#f0f0f0", fg="black")
        last_modified_times = {}
        while self.watcher_process.poll() is None and self.thread_running:
            file_modified = False
            if self.current_index < len(self.text_files):
                current_text_file = self.text_files[self.current_index]
                if os.path.isfile(current_text_file):
                    last_modified = os.path.getmtime(current_text_file)
                    if current_text_file in last_modified_times:
                        if last_modified != last_modified_times[current_text_file]:
                            last_modified_times[current_text_file] = last_modified
                            file_modified = True
                    else:
                        last_modified_times[current_text_file] = last_modified
                if file_modified:
                    self.show_pair()
                    self.saved_label.config(text="File Modified!", bg="#5da9be", fg="white")
            time.sleep(1)
            self.saved_label.config(text="Watching for changes...", bg="#f0f0f0", fg="black")
        if self.watcher_process.poll() is not None:
            self.saved_label.config(text="Changes Saved!", bg="#5da9be", fg="white")

    # Used to position new windows beside the main window.
    def position_dialog(self, dialog, window_width, window_height):
        root_x = self.master.winfo_rootx()
        root_y = self.master.winfo_rooty()
        root_width = self.master.winfo_width()
        position_right = root_x + root_width
        position_top = root_y + -50
        dialog.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    def change_label(self):
        if self.auto_save_var.get():
            self.saved_label.config(text="Changes are autosaved", bg="#5da9be", fg="white")
        else:
            self.saved_label.config(text="Changes not saved", bg="#FD8A8A", fg="white")

    def copy_to_clipboard(self, event):
        try:
            self.master.clipboard_clear()
            image_dir = self.image_dir.get()
            if image_dir != "Copied!":
                self.master.clipboard_append(image_dir)
                self.image_dir.set("Copied!")
                self.master.after(400, lambda: self.image_dir.set(image_dir))
        except:
            pass

    def disable_button(self, event):
        return "break"

#endregion
################################################################################################################################################
################################################################################################################################################
#                      #
#region - Text Cleanup #
#                      #

    def cleanup_text(self, text):
        if self.cleaning_text.get():
            text = self.remove_duplicates(text)
            if self.list_mode.get():
                text = re.sub(r'\.\s', '\n', text)  # replace period and space with newline
                text = re.sub(' *\n *', '\n', text)  # replace one or more spaces surrounded by optional newlines with a single newline
            else:
                text = re.sub(r'\.\s', ', ', text)  # replace period and space with comma and space
                text = re.sub(' *, *', ',', text)  # replace one or more spaces surrounded by optional commas with a single comma
            text = re.sub(' +', ' ', text)  # replace multiple spaces with a single space
            text = re.sub(",+", ",", text)  # replace multiple commas with a single comma
            text = re.sub(",(?=[^\s])", ", ", text)  # add a space after a comma if it's not already there
            text = re.sub(r'\\\\+', r'\\', text)  # replace multiple backslashes with a single backslash
            text = re.sub(",+$", "", text)  # remove trailing commas
            text = re.sub(" +$", "", text)  # remove trailing spaces
            text = text.strip(",")  # remove leading and trailing commas
            text = text.strip()  # remove leading and trailing spaces
        return text

    def remove_duplicates(self, text):
        if self.list_mode.get():
            text = text.lower().split('\n')
        else:
            text = text.lower().split(',')
        text = [item.strip() for item in text]
        text = list(dict.fromkeys(text))
        if self.list_mode.get():
            text = '\n'.join(text)
        else:
            text = ','.join(text)
        return text

#endregion
################################################################################################################################################
################################################################################################################################################
#                         #
#region -  Save and close #
#                         #

    def save_text_file(self):
        if not self.check_directory():
            return
        if self.text_files:
            self.save_file()
            self.saved_label.config(text="Saved", bg="#6ca079", fg="white")
            self.save_file()
            self.show_pair()

    def save_file(self):
        text_file = self.text_files[self.current_index]
        with open(text_file, "w", encoding="utf-8") as f:
            text = self.text_box.get("1.0", END).strip()
            if self.cleaning_text.get():
                text = self.cleanup_text(text)
            if self.list_mode.get():
                text = ', '.join(text.split('\n'))
            f.write(text)

    def on_closing(self):
        self.thread_running = False
        if self.watcher_process is not None:
            self.watcher_process.terminate()
        if not os.path.isdir(self.image_dir.get()):
            root.destroy()
        elif self.saved_label.cget("text") in ["No Changes", "Saved", "Text Files Cleaned up!"]:
            root.destroy()
        elif self.auto_save_var.get():
            self.cleanup_all_text_files(show_confirmation=False)
            self.save_text_file()
            root.destroy()
        else:
            try:
                if messagebox.askyesno("Quit", "Are you sure you want to quit without saving?"):
                    root.destroy()
            except:
                pass
        self.delete_text_backup()

#endregion
################################################################################################################################################
################################################################################################################################################
#                          #
#region -  File Management #
#                          #

    def natural_sort(self, s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', s)]

    def choose_working_directory(self):
        self.user_selected_no = False
        try:
            directory = askdirectory()
            if directory:
                self.image_dir.set(directory)
                self.current_index = 0
                self.load_pairs()
                self.directory_button.config(anchor='w')
        except Exception as e:
            pass

    def open_current_directory(self, event=None):
        try:
            os.startfile(self.image_dir.get())
        except:
            pass

    def open_current_image(self, event=None):
        try:
            os.startfile(self.image_file)
        except:
            pass

    def check_directory(self):
        if not os.path.isdir(self.image_dir.get()):
            messagebox.showerror("Error!", "Invalid or No directory selected.\n\n Select a directory before using this tool.")
            return False
        return True

    def create_blank_textfiles(self, new_text_files):
        if not self.user_selected_no:
            msg = f"Do you want to create {len(new_text_files)} new text file(s)?\n\nImages will still have a text box, even without a text pair."
            result = messagebox.askquestion("Create Blank Text File?", msg)
            if result == "yes":
                for filename in new_text_files:
                    text_filename = os.path.splitext(filename)[0] + ".txt"
                    text_file_path = os.path.join(self.image_dir.get(), text_filename)
                    with open(text_file_path, "w") as f:
                        f.write("")
            elif result == "no":
                self.user_selected_no = True

    def create_and_open_custom_dictionary(self):
        csv_filename = 'my_tags.csv'
        if not os.path.isfile(csv_filename):
            with open(csv_filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["### This is where you can create a custom dictionary of tags."])
                writer.writerow(["### These tags will be loaded alongside the chosen autocomplete dictionary."])
                writer.writerow(["### Lines starting with 3 hash symbols '###' will be ignored so you can create comments."])
                writer.writerow(["### Tags near the top of the list have a higher priority than lower tags."])
                writer.writerow([])
                writer.writerow(["supercalifragilisticexpialidocious"])
        subprocess.Popen(f'start {csv_filename}', shell=True)
        self.change_autocomplete_dictionary()

    def rename_odd_files(self, filename):
        file_extension = os.path.splitext(filename)[1].lower()
        file_rename_dict = {".jpg_large": "jpg", ".jfif": "jpg"}
        if file_extension in file_rename_dict:
            new_file_extension = file_rename_dict[file_extension]
            base_filename = os.path.splitext(filename)[0]
            new_filename = base_filename + "." + new_file_extension
            counter = 1
            duplicate_files = []
            while os.path.exists(os.path.join(self.image_dir.get(), new_filename)):
                duplicate_files.append(new_filename)
                new_filename = base_filename + "_" + str(counter).zfill(3) + "." + new_file_extension
                counter += 1
            if duplicate_files:
                root = Tk()
                root.withdraw()
                MsgBox = messagebox.askquestion ('Rename Files','The following files are duplicates and will be renamed:\n' + '\n'.join(duplicate_files) + '\nDo you want to continue?',icon = 'warning')
                if MsgBox == 'no':
                    root.destroy()
                    return filename
            os.rename(os.path.join(self.image_dir.get(), filename), os.path.join(self.image_dir.get(), new_filename))
            filename = new_filename
        return filename

    def delete_text_backup(self):
        if self.text_files:
            backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
            if os.path.exists(backup_folder):
                shutil.rmtree(backup_folder)
        else:
            pass

    def delete_pair(self):
        if not self.check_directory():
            return
        if messagebox.askokcancel("Warning", "This will move the img-txt pair to a local trash folder.\n\nThe trash folder will be created in the selected directory."):
            if self.current_index < len(self.image_files):
                trash_dir = os.path.join(os.path.dirname(self.image_files[self.current_index]), "Trash")
                os.makedirs(trash_dir, exist_ok=True)
                deleted_pair = []
                for file_list in [self.image_files, self.text_files]:
                    trash_file = os.path.join(trash_dir, os.path.basename(file_list[self.current_index]))
                    os.rename(file_list[self.current_index], trash_file)
                    deleted_pair.append((file_list, self.current_index, trash_file))
                    del file_list[self.current_index]
                self.deleted_pairs.append(deleted_pair)
                self.total_images_label.config(text=f"/{len(self.image_files)}")
                if self.current_index >= len(self.image_files):
                    self.current_index = len(self.image_files) - 1
                self.show_pair()
                self.undo_state.set("normal")
                self.toolsMenu.entryconfig("Undo Delete", state="normal")
            else:
                print("Index out of range. No more files to delete.")

    def undo_delete_pair(self):
        if not self.check_directory():
            return
        if not self.deleted_pairs:
            print("No files to restore.")
            return
        deleted_pair = self.deleted_pairs.pop()
        for file_list, index, trash_file in deleted_pair:
            original_path = os.path.join(self.image_dir.get(), os.path.basename(trash_file))
            os.rename(trash_file, original_path)
            file_list.insert(index, original_path)
        self.total_images_label.config(text=f"/{len(self.image_files)}")
        self.show_pair()
        if not self.deleted_pairs:
            self.undo_state.set("disabled")
            self.toolsMenu.entryconfig("Undo Delete", state="disabled")

#endregion
################################################################################################################################################
################################################################################################################################################
#                    #
#region -  Framework #
#                    #

    def set_appid(self):
        myappid = 'ImgTxtViewer.Nenotriple'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    def set_window_size(self, master):
        master.minsize(600, 300) # Width x Height
        window_width = 1280
        window_height = 660
        position_right = root.winfo_screenwidth()//2 - window_width//2
        position_top = root.winfo_screenheight()//2 - window_height//2
        root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

root = Tk()
app = ImgTxtViewer(root)
app.toggle_always_on_top()
root.attributes('-topmost', 0)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.title("v1.80 - img-txt_viewer  ---  github.com/Nenotriple/img-txt_viewer")
root.mainloop()

#endregion
################################################################################################################################################
################################################################################################################################################
#           #
# Changelog #
#           #

'''

[v1.80 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.80)
  - New:
    - Small ui tweaks. [#22b2764][22b2764]
    - `Fuzzy Search` You can now use an asterisk while typing to "search" for tags. [#05ca179][05ca179]
      - For example: Typing `*lo*b` returns "**lo**oking **b**ack", and even "yel**lo**w **b**ackground"
    - You can now undo the last operation for search_and_replace, prefix_text, and append_text. [#c5be6a2][c5be6a2]
    - Batch Tag Delete no longer locks the main img-txt_viewer window. [#f2f8414][f2f8414]
      - While Batch Tag Delete is open, text files are scanned for changes and automatically updated. [#143140e][143140e], [#b38a786][b38a786]

<br>

  - Fixed:
    - Fixed autosave bug causing warning on window close without directory selection. [#b3f00a2][b3f00a2]

<br>

  - Other changes:
    - PanedWindow adjustments. [#2bfdb3a][2bfdb3a]
    - Other changes: [#f2f8414][f2f8414]

<!-- New -->
[22b2764]: https://github.com/Nenotriple/img-txt_viewer/commit/22b2764edbf16e4477dce16bebdf08cf2d3459df
[05ca179]: https://github.com/Nenotriple/img-txt_viewer/commit/05ca179914d3288108206465d78ab199874b6cc2
[c5be6a2]: https://github.com/Nenotriple/img-txt_viewer/commit/c5be6a2861192d634777d5c0d5c6d9a8804bbc72
[143140e]: https://github.com/Nenotriple/img-txt_viewer/commit/143140efc4bca1515579d3ce0d73c68837ac5c30
[b38a786]: https://github.com/Nenotriple/img-txt_viewer/commit/b38a786c4f75edf0ad03d2966076f32c7d870d3e

<!-- Fixed -->
[b3f00a2]: https://github.com/Nenotriple/img-txt_viewer/commit/b3f00a28c82beb2300e78693df5d771802b2cfe4

<!-- Other changes -->
[2bfdb3a]: https://github.com/Nenotriple/img-txt_viewer/commit/2bfdb3a6e4d075f26b6c89ef160e990190d27dc3
[f2f8414]: https://github.com/Nenotriple/img-txt_viewer/commit/f2f84141f2481fc555fc3a74393f1816f9a199ec

'''

################################################################################################################################################
################################################################################################################################################
#      #
# todo #
#      #

'''

- Todo
  -

- Tofix
  - **Minor** Undo should be less jarring when inserting a suggestion.

'''
