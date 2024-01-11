"""
########################################
#                                      #
#            IMG-TXT VIEWER            #
#                                      #
#   Version : v1.84                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
Display an image and text file side-by-side for easy manual caption editing.

More info here: https://github.com/Nenotriple/img-txt_viewer

"""


VERSION = "v1.84"


################################################################################################################################################
################################################################################################################################################
#                  #
#region -  Imports #
#                  #


import os
import re
import csv
import sys
import glob
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
        from PIL import Image, ImageTk
    else:
        sys.exit()


#endregion
##########################################################################################################################################################################
##########################################################################################################################################################################
#                   #
#region AboutWindow #
#                   #


class AboutWindow(Toplevel):
    info_headers = ["Shortcuts:", "Tips:", "Text Tools:", "Auto-Save:"]
    info_content = [
        " ⦁ALT+Left/Right: Quickly move between img-txt pairs.\n"
        " ⦁Del: Send the current pair to a local trash folder.\n"
        " ⦁ALT: Cycle through auto-suggestions.\n"
        " ⦁TAB: Insert the highlighted suggestion.\n"
        " ⦁CTRL+F: Highlight all duplicate words.\n"
        " ⦁CTRL+S: Save the current text file.\n"
        " ⦁CTRL+Z / CTRL+Y: Undo/Redo.\n"
        " ⦁Middle-click a tag to delete it.\n",

        " ⦁Highlight duplicates by selecting text.\n"
        " ⦁List Mode: Display tags in a list format while saving in standard format.\n"
        " ⦁Blank text files can be created for images without any matching pair when loading a directory.\n"
        " ⦁When selecting a suggestion dictionary, you can use either Anime tags, English dictionary, or Both.\n"
        " ⦁Use an asterisk * while typing to return suggestions using 'fuzzy search'.\n",

        " ⦁Search and Replace: Edit all text files at once.\n"
        " ⦁Prefix Text Files: Insert text at the START of all text files.\n"
        " ⦁Append Text Files: Insert text at the END of all text files.\n"
        " ⦁Batch Tag Delete: View all tags in a directory as a list, and quickly delete them.\n"
        " ⦁Cleanup Text: Fix typos in all text files of the selected folder, such as duplicate tags, multiple spaces or commas, missing spaces, and more.\n",

        " ⦁Check the auto-save box to save text when navigating between img/txt pairs or closing the window.\n"
        " ⦁Text is cleaned up when saved, so you can ignore things like duplicate tags, trailing comma/spaces, double comma/spaces, etc.\n"
        " ⦁Text cleanup can be disabled from the options menu.",]


    def __init__(self, master=None):
        super().__init__(master=master)
        self.title("About")
        self.geometry("850x560")
        self.maxsize(900, 900)
        self.minsize(300, 300)
        self.github_url = "https://github.com/Nenotriple/img-txt_viewer"
        self.create_url_button()
        self.create_info_text()
        self.create_made_by_label()


    def create_url_button(self):
        self.url_button = Button(self, text=f"Open: {self.github_url}", fg="blue", overrelief="groove", command=self.open_url)
        self.url_button.pack(fill="x")
        ToolTip.create(self.url_button, "Click this button to open the repo in your default browser", 10, 6, 4)


    def create_info_text(self):
        self.info_text = ScrolledText(self)
        self.info_text.pack(expand=True, fill='both')
        for header, section in zip(AboutWindow.info_headers, AboutWindow.info_content):
            self.info_text.insert("end", header + "\n", "header")
            self.info_text.insert("end", section + "\n", "section")
        self.info_text.tag_config("header", font=("Segoe UI", 10, "bold"))
        self.info_text.tag_config("section", font=("Segoe UI", 10))
        self.info_text.config(state='disabled', wrap="word")


    def create_made_by_label(self):
        self.made_by_label = Label(self, text=f"{VERSION} img-txt_viewer - Created by: Nenotriple (2023)", font=("Arial", 10))
        self.made_by_label.pack(pady=5)
        ToolTip.create(self.made_by_label, "🤍Thank you for using my app!🤍 (^‿^)", 10, 6, 4)


    def open_url(self):
        import webbrowser
        webbrowser.open(f"{self.github_url}")


#endregion
################################################################################################################################################
################################################################################################################################################
#                   #
#region -  ToolTips #
#                   #

''' Example ToolTip: ToolTip.create(WIDGET, "TOOLTIP TEXT", delay=0, x_offset=0, y_offset=0) '''


class ToolTip:
    def __init__(self, widget, x_offset=0, y_offset=0):
        self.widget = widget
        self.tip_window = None
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.id = None
        self.hide_id = None
        self.hide_time = 0

    def show_tip(self, tip_text, x, y):
        if self.tip_window or not tip_text:
            return
        x += self.x_offset
        y += self.y_offset
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.wm_attributes("-topmost", True)
        tw.wm_attributes("-disabled", True)
        label = Label(tw, text=tip_text, background="#ffffee", relief="ridge", borderwidth=1, justify="left", padx=4, pady=4)
        label.pack()
        self.hide_id = self.widget.after(5000, self.hide_tip)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
        self.hide_time = time.time()

    @staticmethod
    def create(widget, text, delay=0, x_offset=0, y_offset=0):
        tool_tip = ToolTip(widget, x_offset, y_offset)
        def enter(event):
            if tool_tip.id:
                widget.after_cancel(tool_tip.id)
            if time.time() - tool_tip.hide_time > 0.1:
                tool_tip.id = widget.after(delay, lambda: tool_tip.show_tip(text, widget.winfo_pointerx(), widget.winfo_pointery()))
        def leave(event):
            if tool_tip.id:
                widget.after_cancel(tool_tip.id)
            tool_tip.hide_tip()
        def motion(event):
            if tool_tip.id:
                widget.after_cancel(tool_tip.id)
            tool_tip.id = widget.after(delay, lambda: tool_tip.show_tip(text, widget.winfo_pointerx(), widget.winfo_pointery()))
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        widget.bind('<Motion>', motion)


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
        files = {'danbooru.csv': "https://raw.githubusercontent.com/Nenotriple/img-txt_viewer/main/danbooru.csv",
                 'dictionary.csv': "https://raw.githubusercontent.com/Nenotriple/img-txt_viewer/main/dictionary.csv",
                 'e621.csv': "https://raw.githubusercontent.com/Nenotriple/img-txt_viewer/main/e621.csv"}
        missing_files = [file for file in files if not os.path.exists(file)]
        if missing_files:
            download = messagebox.askyesno("Files not found.", f"The following dictionaries required for autocomplete suggestions were not found: \n\n{', '.join(missing_files)}.\n\nDo you want to download them from the repo? ~2MB each\n\nYes = Download All\nNo = Ignore")
            if download:
                for data_file in missing_files:
                    url = files[data_file]
                    threading.Thread(target=self.download_file, args=(url, data_file)).start()


    def download_file(self, url, data_file):
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
        text_with_asterisks = re.escape(text_with_underscores).replace("\\*", ".*")
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
        self.stop_thread = False
        self.about_window = None
        self.panes_swapped = False
        self.text_modified = False
        self.watching_files = False
        self.is_alt_arrow_pressed = False


        # Navigation variables
        self.selected_suggestion_index = 0
        self.prev_num_files = 0
        self.current_index = 0


        # Text tool strings
        self.search_string_var = StringVar()
        self.replace_string_var = StringVar()
        self.prefix_string_var = StringVar()
        self.append_string_var = StringVar()


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
        self.image_dir = StringVar(value="Choose Directory...")
        self.list_mode = BooleanVar(value=False)
        self.bold_commas = BooleanVar(value=False)
        self.cleaning_text = BooleanVar(value=True)
        self.auto_save_var = BooleanVar(value=False)
        self.use_colored_suggestions = BooleanVar(value=True)
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
        self.optionsMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", underline=0, menu=self.optionsMenu)


        # Suggestion Dictionary Menu
        dictionaryMenu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Suggestion Dictionary", underline=11, state="disable", menu=dictionaryMenu)
        dictionaryMenu.add_checkbutton(label="English Dictionary", underline=0, variable=self.csv_var, onvalue='dictionary.csv', offvalue='danbooru.csv', command=self.change_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Danbooru", underline=0, variable=self.csv_var, onvalue='danbooru.csv', offvalue='dictionary.csv', command=self.change_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="e621", underline=0, variable=self.csv_var, onvalue='e621.csv', offvalue='danbooru.csv', command=self.change_autocomplete_dictionary)
        dictionaryMenu.add_separator()
        dictionaryMenu.add_checkbutton(label="All (slow)", underline=0, variable=self.csv_var, onvalue='all', command=self.change_autocomplete_dictionary)


        # Suggestion Quantity Menu
        suggestion_quantity_menu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Suggestion Quantity", underline=11, state="disable", menu=suggestion_quantity_menu)
        for i in range(1, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(i), variable=self.suggestion_quantity, value=i, command=lambda suggestion_quantity=i: self.set_suggestion_quantity(suggestion_quantity))
        self.optionsMenu.add_separator()


        # Max Image Size Menu
        sizeMenu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Max Image Size", underline=0, state="disable", menu=sizeMenu)
        self.sizes = [("Small", 512),
                      ("Normal",  2500),
                      ("Larger",  4000)]
        for size in self.sizes:
            sizeMenu.add_radiobutton(label=size[0], variable=self.max_img_width, value=size[1], underline=0, command=lambda s=size: self.save_text_file())

# Please alter "Use Colored Suggestion" so it also runs  "change_autocomplete_dictionary"
        # Options
        self.optionsMenu.add_checkbutton(label="Highlighting Duplicates", underline=0, state="disable", variable=self.highlighting_duplicates)
        self.optionsMenu.add_checkbutton(label="Cleaning Text on Save", underline=0, state="disable", variable=self.cleaning_text)
        self.optionsMenu.add_checkbutton(label="Colored Suggestions", underline=0, state="disable", variable=self.use_colored_suggestions, command=self.change_autocomplete_dictionary)
        self.optionsMenu.add_checkbutton(label="Big Comma Mode", underline=0, state="disable", variable=self.bold_commas, command=self.toggle_big_comma_mode)
        self.optionsMenu.add_checkbutton(label="List View", underline=0, state="disable", variable=self.list_mode, command=self.toggle_list_mode)
        self.optionsMenu.add_separator()
        self.optionsMenu.add_checkbutton(label="Always On Top", underline=0, command=self.toggle_always_on_top)
        self.optionsMenu.add_checkbutton(label="Vertical View", underline=0, state="disable", command=self.swap_pane_orientation)
        self.optionsMenu.add_command(label="Swap img-txt Sides", underline=0, state="disable", command=self.swap_pane_sides)


####### Tools Menu ##################################################
        self.toolsMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", underline=0, menu=self.toolsMenu)


        # Tools
        self.toolsMenu.add_command(label="Batch Tag Delete...", underline=0, command=self.batch_tag_delete)
        self.toolsMenu.add_command(label="Resize Images...", underline=0, command=self.resize_images)
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Cleanup Text", underline=0, state="disable", command=self.cleanup_all_text_files)
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Open Current Directory...", underline=13, state="disable", command=self.open_current_directory)
        self.toolsMenu.add_command(label="Open Current Image...", underline=13, state="disable", command=self.open_current_image)
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Delete img-txt Pair", accelerator="Del", state="disable", command=self.delete_pair)
        self.toolsMenu.add_command(label="Undo Delete", underline=0, command=self.undo_delete_pair, state="disabled")


####### About Menu ##################################################
        menubar.add_command(label="About", underline=0, command=self.toggle_about_window)


#endregion
################################################################################################################################################
################################################################################################################################################
#                                    #
#region -  Buttons, Labels, and more #
#                                    #


        # This PanedWindow holds both master frames.
        self.primary_paned_window = PanedWindow(master, orient="horizontal", sashwidth=5, bg="#d0d0d0", bd=0)
        self.primary_paned_window.pack(fill="both", expand=1)
        self.primary_paned_window.bind('<ButtonRelease-1>', self.snap_sash_to_half)


        # This frame is exclusively used for the displayed image.
        self.master_image_frame = Frame(master)
        self.primary_paned_window.add(self.master_image_frame, stretch="always")


        # This frame serves as a container for all primary UI frames, with the exception of the master_image_frame.
        self.master_control_frame = Frame(master)
        self.primary_paned_window.add(self.master_control_frame, stretch="always", )
        self.primary_paned_window.paneconfigure(self.master_control_frame, minsize=300)
        self.primary_paned_window.update(); self.primary_paned_window.sash_place(0, 0, 0)


        # Image Label
        self.image_preview = Button(self.master_image_frame, relief="flat")
        self.image_preview.pack(side="left")
        self.image_preview.bind("<Double-1>", self.open_current_image)
        self.image_preview.bind('<Button-2>', self.open_current_directory)
        self.image_preview.bind("<MouseWheel>", self.mouse_scroll)
        self.image_preview.bind("<Button-3>", self.show_imageContext_menu)
        ToolTip.create(self.image_preview, "Double-Click to open in system image viewer \n\nRight-click / Middle-click to open in file explorer\n\nALT+Left/Right, Mouse-Wheel to move between img-txt pairs", 1000, 6, 4)


        # Directory Button
        top_button_frame = Frame(self.master_control_frame)
        top_button_frame.pack(side="top", fill="x")
        self.directory_button = Button(top_button_frame, overrelief="groove", textvariable=self.image_dir, command=self.choose_working_directory)
        self.directory_button.pack(side="top", fill="x")
        self.directory_button.bind('<Button-2>', self.open_current_directory)
        self.directory_button.bind('<Button-3>', self.copy_to_clipboard)
        ToolTip.create(self.directory_button, "Right click to copy path\n\nMiddle click to open in file explorer", 1000, 6, 4)


        # Save Button
        self.save_button = Button(top_button_frame, overrelief="groove", text="Save", fg="blue", state="disabled", command=self.save_text_file)
        self.save_button.pack(side="top", fill="x", pady=2)
        ToolTip.create(self.save_button, "CTRL+S ", 1000, 6, 4)


        # Navigation Buttons
        nav_button_frame = Frame(self.master_control_frame)
        nav_button_frame.pack()
        self.next_button = Button(nav_button_frame, overrelief="groove", text="Next--->", state="disabled", command=lambda event=None: self.next_pair(event), width=16)
        self.prev_button = Button(nav_button_frame, overrelief="groove", text="<---Previous", state="disabled", command=lambda event=None: self.prev_pair(event), width=16)
        self.next_button.pack(side="right", padx=2, pady=2)
        self.prev_button.pack(side="right", padx=2, pady=2)
        ToolTip.create(self.next_button, "ALT+R ", 1000, 6, 4)
        ToolTip.create(self.prev_button, "ALT+L ", 1000, 6, 4)


        # Saved Label / Autosave
        saved_label_frame = Frame(self.master_control_frame)
        saved_label_frame.pack(pady=2)
        self.auto_save_checkbutton = Checkbutton(saved_label_frame, overrelief="groove", text="Auto-save", state="disabled", variable=self.auto_save_var, command=self.change_label)
        self.auto_save_checkbutton.pack(side="right")
        self.saved_label = Label(saved_label_frame, text="No Changes", state="disabled", width=23)
        self.saved_label.pack()


        # Image Index
        self.index_frame = Frame(self.master_control_frame)
        self.index_frame.pack(side="top", expand="no")
        self.current_images_label = Label(self.index_frame, text="Pair", state="disabled")
        self.current_images_label.pack(side="left", expand="yes")
        self.image_index_entry = Entry(self.index_frame, width=5, state="disabled")
        self.image_index_entry.bind("<Return>", self.jump_to_image)
        self.image_index_entry.pack(side="left", expand="no")
        self.total_images_label = Label(self.index_frame, text=f"of {len(self.image_files)}", state="disabled")
        self.total_images_label.pack(side="left", expand="yes")


        # Suggestion text
        self.suggestion_textbox = Text(self.master_control_frame, height=1, borderwidth=0, highlightthickness=0, bg='#f0f0f0')
        self.suggestion_textbox.pack(side="top", fill="x")


        # Startup info text
        self.info_text = ScrolledText(self.master_control_frame)
        self.info_text.pack(expand=True, fill="both")
        for header, section in zip(AboutWindow.info_headers, AboutWindow.info_content):
            self.info_text.insert("end", header + "\n", "header")
            self.info_text.insert("end", section + "\n", "section")
        self.info_text.tag_config("header", font=("Segoe UI", 10, "bold"))
        self.info_text.tag_config("section", font=("Segoe UI", 10))
        self.info_text.bind("<Button-3>", self.show_textContext_menu)
        self.info_text.config(state='disabled', wrap="word")


#                 #
# End of __init__ #
#                 #
#endregion        #
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
#                         #
#region -  Text Box setup #
#                         #


    def create_text_pane(self):
        if not hasattr(self, 'text_pane'):
            self.text_pane = PanedWindow(self.master_control_frame, orient="vertical", sashwidth=5, bg="#d0d0d0", bd=0)
            self.text_pane.pack(side="bottom", fill="both", expand=1)


    def create_text_box(self):
        self.create_text_pane()
        if not hasattr(self, 'text_frame'):
            self.text_frame = Frame(self.master_control_frame)
            self.text_pane.add(self.text_frame, stretch="always")
            self.text_pane.paneconfigure(self.text_frame, minsize=80)
            self.text_box = ScrolledText(self.text_frame, wrap="word", undo=True, maxundo=200, inactiveselectbackground="#0078d7")
            self.text_box.pack(side="top", expand="yes", fill="both")
            self.text_box.tag_configure("highlight", background="#5da9be", foreground="white")
            self.set_text_box_binds()
        if not hasattr(self, 'text_widget_frame'):
            self.create_text_control_frame()
        ToolTip.create(self.suggestion_textbox,
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
                               1000, 6, 4)


    def create_text_control_frame(self):
        self.text_widget_frame = Frame(self.master_control_frame)
        self.text_pane.add(self.text_widget_frame, stretch="never")
        self.text_pane.paneconfigure(self.text_widget_frame)
        # Create the notebook and tabs
        self.text_notebook = ttk.Notebook(self.text_widget_frame)
        self.tab1 = Frame(self.text_notebook)
        self.tab2 = Frame(self.text_notebook)
        self.tab3 = Frame(self.text_notebook)
        self.tab4 = Frame(self.text_notebook)
        self.tab5 = Frame(self.text_notebook)
        self.text_notebook.add(self.tab1, text='Search & Replace')
        self.text_notebook.add(self.tab2, text='Prefix Text')
        self.text_notebook.add(self.tab3, text='Append Text')
        self.text_notebook.add(self.tab4, text='Font Settings')
        self.text_notebook.add(self.tab5, text='Custom Dictionary')
        self.text_notebook.pack(fill='both')
        self.create_search_and_replace_widgets()
        self.create_prefix_text_widgets()
        self.create_append_text_widgets()
        self.create_font_widgets()
        self.create_custom_dictionary_widgets()


    def create_search_and_replace_widgets(self):
        def clear_all():
            self.search_entry.delete(0, 'end')
            self.replace_entry.delete(0, 'end')
        self.search_label = Label(self.tab1, text="Search for:")
        self.search_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.search_label, "Enter the EXACT text you want to search for", 200, 6, 4)
        self.search_entry = Entry(self.tab1, textvariable=self.search_string_var, width=4)
        self.search_entry.pack(side='left', anchor="n", pady=4, fill='x', expand=True)
        self.replace_label = Label(self.tab1, text="Replace with:")
        self.replace_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.replace_label, "Enter the text you want to replace the searched text with\n\nLeave empty to replace with nothing (delete)", 200, 6, 4)
        self.replace_entry = Entry(self.tab1, textvariable=self.replace_string_var, width=4)
        self.replace_entry.pack(side='left', anchor="n", pady=4, fill='x', expand=True)
        self.replace_entry.bind('<Return>', lambda event: self.search_and_replace())
        self.replace_button = Button(self.tab1, text="Go!", overrelief="groove", width=4, command=self.search_and_replace)
        self.replace_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.replace_button, "Text files will be backup up", 200, 6, 4)
        self.clear_button = Button(self.tab1, text="Clear", overrelief="groove", width=4, command=clear_all)
        self.clear_button.pack(side='left', anchor="n", pady=4, padx=1)
        self.undo_button = Button(self.tab1, text="Undo", overrelief="groove", width=4, command=self.restore_backup)
        self.undo_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.undo_button, "Revert last action", 200, 6, 4)


    def create_prefix_text_widgets(self):
        def clear():
            self.prefix_entry.delete(0, 'end')
        self.prefix_label = Label(self.tab2, text="Prefix text:")
        self.prefix_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.prefix_label, "Enter the text you want to insert at the START of all text files\n\nCommas will be inserted as needed", 200, 6, 4)
        self.prefix_entry = Entry(self.tab2, textvariable=self.prefix_string_var, width=4)
        self.prefix_entry.pack(side='left', anchor="n", pady=4, fill='x', expand=True)
        self.prefix_entry.bind('<Return>', lambda event: self.prefix_text_files())
        self.prefix_button = Button(self.tab2, text="Go!", overrelief="groove", width=4, command=self.prefix_text_files)
        self.prefix_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.prefix_button, "Text files will be backup up", 200, 6, 4)
        self.clear_button = Button(self.tab2, text="Clear", overrelief="groove", width=4, command=clear)
        self.clear_button.pack(side='left', anchor="n", pady=4, padx=1)
        self.undo_button = Button(self.tab2, text="Undo", overrelief="groove", width=4, command=self.restore_backup)
        self.undo_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.undo_button, "Revert last action", 200, 6, 4)


    def create_append_text_widgets(self):
        def clear():
            self.append_entry.delete(0, 'end')
        self.append_label = Label(self.tab3, text="Append text:")
        self.append_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.append_label, "Enter the text you want to insert at the END of all text files\n\nCommas will be inserted as needed", 200, 6, 4)
        self.append_entry = Entry(self.tab3, textvariable=self.append_string_var, width=4)
        self.append_entry.pack(side='left', anchor="n", pady=4, fill='x', expand=True)
        self.append_entry.bind('<Return>', lambda event: self.append_text_files())
        self.append_button = Button(self.tab3, text="Go!", overrelief="groove", width=4, command=self.append_text_files)
        self.append_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.append_button, "Text files will be backup up", 200, 6, 4)
        self.clear_button = Button(self.tab3, text="Clear", overrelief="groove", width=4, command=clear)
        self.clear_button.pack(side='left', anchor="n", pady=4, padx=1)
        self.undo_button = Button(self.tab3, text="Undo", overrelief="groove", width=4, command=self.restore_backup)
        self.undo_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.undo_button, "Revert last action", 200, 6, 4)


    def create_font_widgets(self, event=None):
        def open_dropdown(event):
            event.widget.after(100, lambda: event.widget.event_generate('<Down>'))
        def set_font_and_size(font, size):
            if font and size:
                self.text_box.config(font=(font, int(size)))
        def reset_to_defaults():
            self.font_var.set(default_font)
            size_scale.set(default_size)
            set_font_and_size(default_font, default_size)
        current_font = self.text_box.cget("font")
        current_font_name = self.text_box.tk.call("font", "actual", current_font, "-family")
        current_font_size = self.text_box.tk.call("font", "actual", current_font, "-size")
        default_font = current_font_name
        default_size = current_font_size
        font_label = Label(self.tab4, text="Font:")
        font_label.pack(side="left", anchor="n", pady=4)
        ToolTip.create(font_label, "Recommended Fonts: Courier New, Ariel, Consolas, Segoe UI", 200, 6, 4)
        font_box = ttk.Combobox(self.tab4, textvariable=self.font_var, width=4, takefocus=False)
        font_box['values'] = list(tkinter.font.families())
        font_box.set(current_font_name)
        font_box.bind("<<ComboboxSelected>>", lambda event: set_font_and_size(self.font_var.get(), size_scale.get()))
        font_box.bind("<Button-1>", open_dropdown)
        font_box.pack(side="left", anchor="n", pady=4, fill="x", expand=True)
        font_size = Label(self.tab4, text="Font Size:")
        font_size.pack(side="left", anchor="n", pady=4)
        ToolTip.create(font_size, "Default size = 10", 200, 6, 4)
        size_scale = Scale(self.tab4, from_=8, to=19, showvalue=False, orient="horizontal", cursor="hand2", takefocus=False)
        size_scale.set(current_font_size)
        size_scale.bind("<ButtonRelease-1>", lambda event: set_font_and_size(self.font_var.get(), size_scale.get()))
        size_scale.pack(side="left", anchor="n", pady=4, fill="x", expand=True)
        reset_button = Button(self.tab4, text="Reset", overrelief="groove", width=4, command=reset_to_defaults)
        reset_button.pack(side="left", anchor="n", pady=4, padx=1)


    def create_custom_dictionary_widgets(self):
        def save_content():
            with open('my_tags.csv', 'w') as file:
                file.write(self.custom_dictionary_textbox.get("1.0", "end-1c"))
                self.change_autocomplete_dictionary()
        def refresh_content():
            with open('my_tags.csv', 'r') as file:
                content = file.read()
                self.custom_dictionary_textbox.delete("1.0", 'end')
                self.custom_dictionary_textbox.insert('end', content)
                self.change_autocomplete_dictionary()
        self.create_custom_dictionary()
        self.tab5_frame = Frame(self.tab5)
        self.tab5_frame.pack(side='top', fill='both')
        self.tab5_button_frame = Frame(self.tab5_frame)
        self.tab5_button_frame.pack(side='top', fill='x', pady=4)
        self.save_dictionary_button = Button(self.tab5_button_frame, text="Save", overrelief="groove", takefocus=False, command=save_content)
        ToolTip.create(self.save_dictionary_button, "Save the current changes to the 'my_tags.csv' file", 200, 6, 4)
        self.save_dictionary_button.pack(side='left', padx=1, fill='x', expand=True)
        self.tab5_label = Label(self.tab5_button_frame, text="^^^Expand this frame to view the text box^^^")
        self.tab5_label.pack(side='left')
        ToolTip.create(self.tab5_label, "Click and drag the gray bar up to reveal the text box", 200, 6, 4)
        self.refresh_button = Button(self.tab5_button_frame, text="Refresh", overrelief="groove", takefocus=False, command=refresh_content)
        ToolTip.create(self.refresh_button, "Refresh the suggestion dictionary after saving your changes", 200, 6, 4)
        self.refresh_button.pack(side='left', padx=1, fill='x', expand=True)
        self.custom_dictionary_textbox = ScrolledText(self.tab5_frame)
        self.custom_dictionary_textbox.pack(side='bottom', fill='both')
        with open('my_tags.csv', 'r') as file:
            content = file.read()
            self.custom_dictionary_textbox.insert('end', content)
        self.custom_dictionary_textbox.configure(undo=True)


    def set_text_box_binds(self):
        # Mouse binds
        self.text_box.bind("<Button-1>", lambda event: (self.remove_tag(), self.clear_suggestions()))
        self.text_box.bind("<Button-2>", lambda event: (self.delete_tag_under_mouse(event), self.change_label()))
        self.text_box.bind("<Button-3>", lambda event: (self.show_textContext_menu(event)))
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
        self.text_box.bind("<Key>", lambda event: self.text_modified())
        self.text_box.bind("<Key>", lambda event: self.change_label())
        # Disable normal button behavior
        self.text_box.bind("<Tab>", self.disable_button)
        self.text_box.bind("<Alt_L>", self.disable_button)
        self.text_box.bind("<Alt_R>", self.disable_button)


    # Text Box context menu
    def show_textContext_menu(self, e):
        textContext_menu = Menu(root, tearoff=0)
        widget_in_focus = root.focus_get()
        if widget_in_focus == self.info_text:
            textContext_menu.add_command(label="Copy", command=lambda: widget_in_focus.event_generate('<<Copy>>'))
        elif widget_in_focus == self.text_box:
            textContext_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: (widget_in_focus.event_generate('<<Cut>>'), self.change_label()))
            textContext_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: widget_in_focus.event_generate('<<Copy>>'))
            textContext_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: (widget_in_focus.event_generate('<<Paste>>'), self.change_label()))
            textContext_menu.add_command(label="Delete", accelerator="Del", command=lambda: (widget_in_focus.event_generate('<<Clear>>'), self.change_label()))
            textContext_menu.add_separator()
            textContext_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: (widget_in_focus.event_generate('<<Undo>>'), self.change_label()))
            textContext_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: (widget_in_focus.event_generate('<<Redo>>'), self.change_label()))
            textContext_menu.add_separator()
            textContext_menu.add_command(label="Open Text Directory...", command=self.open_current_directory)
            textContext_menu.add_separator()
            textContext_menu.add_command(label="Highlight all Duplicates", accelerator="Ctrl+F", command=self.highlight_all_duplicates)
            textContext_menu.add_separator()
            textContext_menu.add_checkbutton(label="Highlighting Duplicates", variable=self.highlighting_duplicates)
            textContext_menu.add_checkbutton(label="Clean Text on Save", variable=self.cleaning_text)
            textContext_menu.add_checkbutton(label="Big Comma Mode", variable=self.bold_commas, command=self.toggle_big_comma_mode)
            textContext_menu.add_checkbutton(label="List View", variable=self.list_mode, command=self.toggle_list_mode)
        textContext_menu.tk_popup(e.x_root, e.y_root)


    # Image context menu
    def show_imageContext_menu(self, event):
        imageContext_menu = Menu(self.master, tearoff=0)
        imageContext_menu.add_command(label="Open Current Directory...", command=self.open_current_directory)
        imageContext_menu.add_command(label="Open Current Image...", command=self.open_current_image)
        imageContext_menu.add_separator()
        imageContext_menu.add_command(label="Delete img-txt Pair", accelerator="Del", command=self.delete_pair)
        imageContext_menu.add_command(label="Undo Delete", command=self.undo_delete_pair, state=self.undo_state.get())
        imageContext_menu.add_separator()
        imageContext_menu.add_checkbutton(label="Vertical View", command=self.swap_pane_orientation)
        imageContext_menu.add_command(label="Swap img-txt - Sides", command=self.swap_pane_sides)
        imageContext_menu.add_separator()
        imageContext_menu.add_command(label="Max Image Size", state="disabled", activebackground="#f0f0f0", activeforeground="black")
        for size in self.sizes:
            imageContext_menu.add_radiobutton(label=size[0], variable=self.max_img_width, value=size[1], command=lambda s=size: self.save_text_file())
        imageContext_menu.tk_popup(event.x_root, event.y_root)


#endregion
################################################################################################################################################
################################################################################################################################################
#                                     #
#region -  Additional Interface Setup #
#                                     #


    def set_icon(self):
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(__file__)
        icon_path = os.path.join(application_path, "icon.ico")
        try:
            self.master.iconbitmap(icon_path)
        except TclError: pass


    def enable_menu_options(self):
        tool_commands =    [
                           "Open Current Directory...",
                           "Open Current Image...",
                           "Cleanup Text",
                           "Delete img-txt Pair"
                           ]
        options_commands = [
                            "Suggestion Dictionary",
                            "Suggestion Quantity",
                            "Max Image Size",
                            "Highlighting Duplicates",
                            "Cleaning Text on Save",
                            "Colored Suggestions",
                            "Big Comma Mode",
                            "List View",
                            "Vertical View",
                            "Swap img-txt Sides"
                            ]
        for t_command in tool_commands:
            self.toolsMenu.entryconfig(t_command, state="normal")
        for o_command in options_commands:
            self.optionsMenu.entryconfig(o_command, state="normal")
        self.current_images_label.configure(state="normal")
        self.image_index_entry.configure(state="normal")
        self.total_images_label.configure(state="normal")
        self.saved_label.configure(state="normal")
        self.save_button.configure(state="normal")
        self.next_button.configure(state="normal")
        self.prev_button.configure(state="normal")
        self.auto_save_checkbutton.configure(state="normal")


####### PanedWindow ##################################################
    def configure_pane_position(self):
        window_width = self.master.winfo_width()
        self.primary_paned_window.sash_place(0, window_width // 2, 0)
        self.configure_pane()


    def swap_pane_sides(self):
        self.primary_paned_window.remove(self.master_image_frame)
        self.primary_paned_window.remove(self.master_control_frame)
        if not self.panes_swapped:
            self.primary_paned_window.add(self.master_control_frame)
            self.primary_paned_window.add(self.master_image_frame)
        else:
            self.primary_paned_window.add(self.master_image_frame)
            self.primary_paned_window.add(self.master_control_frame)
        self.master.after_idle(self.configure_pane_position)
        self.configure_pane()
        self.panes_swapped = not self.panes_swapped


    def swap_pane_orientation(self):
        current_orient = self.primary_paned_window.cget('orient')
        new_orient = 'vertical' if current_orient == 'horizontal' else 'horizontal'
        self.primary_paned_window.configure(orient=new_orient)
        if new_orient == 'horizontal':
            self.master.minsize(600, 300)
        else:
            self.master.minsize(300, 600)
        self.master.after_idle(self.configure_pane_position)


    def snap_sash_to_half(self, event):
        total_width = self.primary_paned_window.winfo_width()
        half_point = int(total_width / 2)
        sash_pos = self.primary_paned_window.sash_coord(0)[0]
        if abs(sash_pos - half_point) < 75:
            self.primary_paned_window.sash_place(0, half_point, 0)
        self.configure_pane()


    def configure_pane(self):
        self.primary_paned_window.paneconfigure(self.master_image_frame, minsize=300, stretch="always")
        self.primary_paned_window.paneconfigure(self.master_control_frame, minsize=300, stretch="always")


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
        if self.use_colored_suggestions.get() == True:
            self.suggestion_colors = {0: "black", 1: "#c00004", 2: "black", 3: "#a800aa", 4: "#00ab2c", 5: "#fd9200"} #0=General tags, 1=Artists, 2=UNUSED, 3=Copyright, 4=Character, 5=Meta
        else:
            self.suggestion_colors = {0: "black", 1: "black", 2: "black", 3: "black", 4: "black", 5: "black"}
        if self.csv_var.get() == 'all':
            self.autocomplete = Autocomplete('danbooru.csv')
            self.autocomplete.data.update(Autocomplete('dictionary.csv').data)
            self.autocomplete.data.update(Autocomplete('e621.csv').data)
        elif self.csv_var.get() == 'e621.csv':
            self.autocomplete = Autocomplete(self.csv_var.get())
            if self.use_colored_suggestions.get() == True:
                self.suggestion_colors = {-1: "black", 0: "black", 1: "#f2ac08", 3: "#dd00dd", 4: "#00aa00", 5: "#ed5d1f", 6: "#ff3d3d", 7: "#ff3d3d", 8: "#228822"}
            else:
                self.suggestion_colors = {0: "black", 1: "black", 2: "black", 3: "black", 4: "black", 5: "black", 6: "black", 7: "black", 8: "black"}
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
        self.enable_menu_options()
        self.create_text_box()
        self.show_pair()
        self.saved_label.config(text="No Changes", bg="#f0f0f0", fg="black")
        self.configure_pane_position()
        self.directory_button.config(relief="groove", overrelief="ridge")
        if hasattr(self, 'total_images_label'):
            self.total_images_label.config(text=f"of {len(self.image_files)}")
        self.prev_num_files = len(files_in_dir)
        if not self.watching_files:
            self.start_watching_file()


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
            self.text_box.delete("1.0", "end")
            if text_file and os.path.isfile(text_file):
                with open(text_file, "r") as f:
                    self.text_box.insert("end", f.read())
            self.text_modified = False
            self.text_box.config(undo=True)
            self.image_index_entry.delete(0, "end")
            self.image_index_entry.insert(0, f"{self.current_index + 1}")
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
        new_width = min(max_img_width, w)
        new_height = int(new_width / aspect_ratio)
        if new_height > max_height:
            new_height = max_height
            new_width = int(new_height * aspect_ratio)
        image = image.resize((new_width, new_height))
        if event:
            window_height = event.height
            window_width = event.width
            new_height = min(window_height, new_height)
            new_width = int(new_height * aspect_ratio)
            if new_width > window_width:
                new_width = window_width
                new_height = int(new_width / aspect_ratio)
            image = image.resize((new_width, new_height))
            photo = ImageTk.PhotoImage(image)
            self.image_preview.config(image=photo)
            self.image_preview.image = photo
        return image, aspect_ratio


    def start_watching_file(self):
        if not self.text_files:
            return
        if self.current_index >= len(self.text_files):
            return
        thread = threading.Thread(target=self.watch_file)
        thread.start()


    def watch_file(self):
        text_file = self.text_files[self.current_index]
        if not os.path.exists(text_file):
            return
        try:
            last_modified = os.path.getmtime(text_file)
        except OSError:
            return
        while not self.stop_thread:
            time.sleep(2)
            if not os.path.exists(text_file):
                return
            try:
                current_modified = os.path.getmtime(text_file)
            except OSError:
                return
            if current_modified != last_modified:
                self.show_pair()
                last_modified = current_modified


#endregion
################################################################################################################################################
################################################################################################################################################
#                     #
#region -  Navigation #
#                     #


    def update_pair(self, direction):
        if self.image_dir.get() == "Choose Directory...":
            return
        self.is_alt_arrow_pressed = True
        num_files_in_dir = len(os.listdir(self.image_dir.get()))
        if num_files_in_dir != self.prev_num_files:
            self.update_image_file_count()
            self.prev_num_files = num_files_in_dir
        if not self.text_modified:
            self.saved_label.config(text="No Changes", bg="#f0f0f0", fg="black")
        self.text_box.config(undo=False)
        self.text_box.edit_reset()
        if self.auto_save_var.get():
            self.save_text_file()
        if direction == 'next':
            self.current_index = (self.current_index + 1) % len(self.image_files)
        elif direction == 'prev':
            self.current_index = (self.current_index - 1) % len(self.image_files)
        self.show_pair()


    def next_pair(self, event):
        self.update_pair('next')


    def prev_pair(self, event):
        self.update_pair('prev')


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
        except ValueError: pass


    def update_image_file_count(self):
        extensions = ['.jpg', '.jpeg', '.jpg_large', '.jfif', '.png', '.webp', '.bmp']
        self.image_files = [file for ext in extensions for file in glob.glob(f"{self.image_dir.get()}/*{ext}")]
        self.text_files = [os.path.splitext(file)[0] + '.txt' for file in self.image_files]
        self.total_images_label.config(text=f"of {len(self.image_files)}")


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


    def toggle_list_mode(self, event=None):
        self.text_box.config(undo=False)
        if self.list_mode.get():
            contents = self.text_box.get("1.0", "end").strip().split(',')
            formatted_contents = '\n'.join([item.strip() for item in contents if item.strip()])
            self.text_box.delete("1.0", "end")
            self.text_box.insert("1.0", self.cleanup_text(formatted_contents))
            self.text_box.insert("end", "\n")
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
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        main_window_x = root.winfo_x() + 250 + main_window_width // 2
        main_window_y = root.winfo_y() - 300 + main_window_height // 2
        directory = self.image_dir.get()
        python_script_path = "./batch_tag_delete.py"
        if os.path.isfile(python_script_path):
            command = ["python", python_script_path, str(directory), str(main_window_x), str(main_window_y)]
        else:
            executable_path = "./batch_tag_delete.exe"
            command = [executable_path, str(directory), str(main_window_x), str(main_window_y)]
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)


    def search_and_replace(self):
        if not self.check_current_directory():
            return
        search_string = self.search_string_var.get()
        replace_string = self.replace_string_var.get()
        if not search_string:
            return
        confirm = messagebox.askokcancel("Confirmation", "This will replace all occurrences of the text\n\n{}\n\nWith\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(search_string, replace_string))
        if not confirm:
            return
        self.backup_text_files()
        self.update_image_file_count()
        for text_file in self.text_files:
            try:
                with open(text_file, 'r') as file:
                    filedata = file.read()
                filedata = filedata.replace(search_string, replace_string)
                with open(text_file, 'w') as file:
                    file.write(filedata)
            except Exception: pass
        self.cleanup_all_text_files(show_confirmation=False)
        self.show_pair()
        self.saved_label.config(text="Search & Replace Complete!", bg="#6ca079", fg="white")


    def prefix_text_files(self):
        if not self.check_current_directory():
            return
        prefix_text = self.prefix_string_var.get()
        if not prefix_text:
            return
        if not prefix_text.endswith(', '):
            prefix_text += ', '
        confirm = messagebox.askokcancel("Confirmation", "This will prefix all text files with:\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(prefix_text))
        if not confirm:
            return
        self.backup_text_files()
        self.update_image_file_count()
        for text_file in self.text_files:
            try:
                if not os.path.exists(text_file):
                    with open(text_file, 'w') as file:
                        file.write(prefix_text)
                else:
                    with open(text_file, 'r+') as file:
                        content = file.read()
                        file.seek(0, 0)
                        file.write(prefix_text + content)
            except Exception: pass
        self.cleanup_all_text_files(show_confirmation=False)
        self.show_pair()
        self.saved_label.config(text="Prefix Text Complete!", bg="#6ca079", fg="white")


    def append_text_files(self):
        if not self.check_current_directory():
            return
        append_text = self.append_string_var.get()
        if not append_text:
            return
        if not append_text.startswith(', '):
            append_text = ', ' + append_text
        confirm = messagebox.askokcancel("Confirmation", "This will append all text files with:\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(append_text))
        if not confirm:
            return
        self.backup_text_files()
        self.update_image_file_count()
        for text_file in self.text_files:
            try:
                if not os.path.exists(text_file):
                    with open(text_file, 'w') as file:
                        file.write(append_text)
                else:
                    with open(text_file, 'a') as file:
                        file.write(append_text)
            except Exception: pass
        self.cleanup_all_text_files(show_confirmation=False)
        self.show_pair()
        self.saved_label.config(text="Append Text Complete!", bg="#6ca079", fg="white")


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


#endregion
################################################################################################################################################
################################################################################################################################################
#                     #
#region - Image Tools #
#                     #


    def resize_images(self):
        if os.path.isfile('resize_images.py'):
            command = f'python resize_images.py --folder_path "{self.image_dir.get()}"'
        else:
            command = f'resize_images.exe --folder_path "{self.image_dir.get()}"'
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)


#endregion
################################################################################################################################################
################################################################################################################################################
#                        #
#region - Misc Functions #
#                        #


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
        except Exception: pass


    def disable_button(self, event):
        return "break"


    def toggle_always_on_top(self):
        current_state = root.attributes('-topmost')
        new_state = 0 if current_state == 1 else 1
        root.attributes('-topmost', new_state)


#endregion
################################################################################################################################################
################################################################################################################################################
#                      #
#region - About Window #
#                      #


    def toggle_about_window(self):
        if self.about_window is not None:
            self.close_about_window()
        else:
            self.open_about_window()


    def open_about_window(self):
        self.about_window = AboutWindow(self.master)
        self.about_window.protocol("WM_DELETE_WINDOW", self.close_about_window)
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        main_window_x = root.winfo_x() - 425 + main_window_width // 2
        main_window_y = root.winfo_y() - 275 + main_window_height // 2
        self.about_window.geometry("+{}+{}".format(main_window_x, main_window_y))


    def close_about_window(self):
        self.about_window.destroy()
        self.about_window = None


#endregion
################################################################################################################################################
################################################################################################################################################
#                      #
#region - Text Cleanup #
#                      #


    def cleanup_all_text_files(self, show_confirmation=True):
        if not self.check_current_directory():
            return
        if show_confirmation:
            user_confirmation = messagebox.askokcancel("Confirmation", "This operation will clean all text files from typos like:\nDuplicate tags, Extra commas, Extra spaces, trailing commas/spaces, commas without spaces, and more.\n\nExample Cleanup:\n  From: dog,solo,  ,happy  ,,\n       To: dog, solo, happy")
            self.saved_label.config(text="Text Files Cleaned Up!", bg="#6ca079", fg="white")
            if not user_confirmation:
                return
        for text_file in self.text_files:
            if os.path.exists(text_file):
                with open(text_file, "r+", encoding="utf-8") as f:
                    text = f.read().strip()
                    cleaned_text = self.cleanup_text(text)
                    f.seek(0)
                    f.write(cleaned_text)
                    f.truncate()
            else:
                return
        self.show_pair()


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
        if self.image_dir.get() != "Choose Directory..." and self.check_current_directory() and self.text_files:
            self.save_file()
            self.saved_label.config(text="Saved", bg="#6ca079", fg="white")
            self.save_file()
            self.show_pair()


    def save_file(self):
        text_file = self.text_files[self.current_index]
        text = self.text_box.get("1.0", "end").strip()
        if text == "None" or text == "":
            if os.path.exists(text_file):
                os.remove(text_file)
            return
        with open(text_file, "w", encoding="utf-8") as f:
            if self.cleaning_text.get():
                text = self.cleanup_text(text)
            if self.list_mode.get():
                text = ', '.join(text.split('\n'))
            f.write(text)


    def on_closing(self):
        self.stop_thread = True
        if not os.path.isdir(self.image_dir.get()):
            root.destroy()
        elif self.saved_label.cget("text") in ["No Changes", "Saved", "Changes Saved!", "Text Files Cleaned up!"]:
            root.destroy()
        elif self.auto_save_var.get():
            self.cleanup_all_text_files(show_confirmation=False)
            self.save_text_file()
            root.destroy()
        else:
            try:
                if messagebox.askyesno("Quit", "Quit without saving?"):
                    root.destroy()
            except Exception: pass
        self.delete_text_backup()
        self.delete_trash_folder()


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
        try:
            directory = askdirectory()
            if directory and directory != self.image_dir.get():
                if any(fname.lower().endswith(('.jpg', '.jpeg', '.jpg_large', '.jfif', '.png', '.webp', '.bmp')) for fname in os.listdir(directory)):
                    self.delete_text_backup()
                    self.image_dir.set(directory)
                    self.current_index = 0
                    self.load_pairs()
                    self.directory_button.config(anchor='w')
                else:
                    messagebox.showwarning("No Images", "The selected directory does not contain any images.")
        except Exception: pass


    def open_current_directory(self, event=None):
        try:
            os.startfile(self.image_dir.get())
        except Exception: pass


    def open_current_image(self, event=None):
        try:
            os.startfile(self.image_file)
        except Exception: pass


    def check_current_directory(self):
        if not os.path.isdir(self.image_dir.get()):
            messagebox.showerror("Error!", "Invalid or No directory selected.\n\n Select a directory before using this tool.")
            return False
        return True


    def create_custom_dictionary(self):
        csv_filename = 'my_tags.csv'
        if not os.path.isfile(csv_filename):
            with open(csv_filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["### This is where you can create a custom dictionary of tags."])
                writer.writerow(["### These tags will be loaded alongside the chosen autocomplete dictionary."])
                writer.writerow(["### Tags near the top of the list have a higher priority than lower tags."])
                writer.writerow([])
                writer.writerow(["supercalifragilisticexpialidocious"])
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


    def restore_backup(self):
        backup_dir = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
        if not os.path.exists(backup_dir):
            return
        confirm = messagebox.askokcancel("Confirmation", "This will restore all text files in the selected directory from the latest backup.\n\nDo you want to proceed?")
        if not confirm:
            return
        for backup_file in os.listdir(backup_dir):
            if backup_file.endswith(".bak"):
                original_file = os.path.join(os.path.dirname(backup_dir), os.path.splitext(backup_file)[0] + ".txt")
                try:
                    if os.path.exists(original_file):
                        os.remove(original_file)
                    shutil.copy2(os.path.join(backup_dir, backup_file), original_file)
                    os.rename(original_file, original_file.replace('.bak', '.txt'))
                    os.utime(original_file, (time.time(), time.time()))
                    self.show_pair()
                    self.saved_label.config(text="Files Restored", bg="#6ca079", fg="white")
                except Exception: pass


    def backup_text_files(self):
        if not self.check_current_directory():
            return
        backup_dir = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        for text_file in self.text_files:
            try:
                base = os.path.splitext(text_file)[0]
                new_backup = os.path.join(backup_dir, os.path.basename(base) + ".bak")
                shutil.copy2(text_file, new_backup)
            except Exception: pass


    def delete_text_backup(self):
        if self.text_files:
            backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
            if os.path.exists(backup_folder):
                shutil.rmtree(backup_folder)


    def delete_trash_folder(self):
        trash_dir = os.path.join(self.image_dir.get(), "Trash")
        if os.path.exists(trash_dir) and not os.listdir(trash_dir):
            shutil.rmtree(trash_dir)


    def delete_pair(self):
        if not self.check_current_directory():
            return
        if messagebox.askokcancel("Warning", "This will move the img-txt pair to a local trash folder.\n\nThe trash folder will be created in the selected directory."):
            if self.current_index < len(self.image_files):
                trash_dir = os.path.join(os.path.dirname(self.image_files[self.current_index]), "Trash")
                os.makedirs(trash_dir, exist_ok=True)
                deleted_pair = []
                for file_list in [self.image_files, self.text_files]:
                    if os.path.exists(file_list[self.current_index]):
                        trash_file = os.path.join(trash_dir, os.path.basename(file_list[self.current_index]))
                        os.rename(file_list[self.current_index], trash_file)
                        deleted_pair.append((file_list, self.current_index, trash_file))
                        del file_list[self.current_index]
                self.deleted_pairs.append(deleted_pair)
                self.total_images_label.config(text=f"of {len(self.image_files)}")
                if self.current_index >= len(self.image_files):
                    self.current_index = len(self.image_files) - 1
                self.show_pair()
                self.undo_state.set("normal")
                self.toolsMenu.entryconfig("Undo Delete", state="normal")
            else: pass


    def undo_delete_pair(self):
        if not self.check_current_directory():
            return
        if not self.deleted_pairs:
            return
        deleted_pair = self.deleted_pairs.pop()
        for file_list, index, trash_file in deleted_pair:
            original_path = os.path.join(self.image_dir.get(), os.path.basename(trash_file))
            os.rename(trash_file, original_path)
            file_list.insert(index, original_path)
        self.total_images_label.config(text=f"of {len(self.image_files)}")
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
root.title(f"{VERSION} - img-txt_viewer  ---  github.com/Nenotriple/img-txt_viewer")
root.mainloop()


#endregion
################################################################################################################################################
################################################################################################################################################
#                   #
#region - Changelog #
#                   #


'''


[v1.84 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.84)

  - New:
    - New tool: `Resize Images`: You can find this in the Tools menu.
      - Resize operations: Resize to Resolution, Resize to Width, Resize to Height, Resize to Shorter Side, Resize to Longer Side
      - Just like "batch_tag_delete.py", "resize_images.py" is a stand-alone tool. You can run it 100% independently of img-txt_viewer.
      - Images will be overwritten when resized.
      - New option: `Colored Suggestions`, Use this to enable or disable the color coded autocomplete suggestions.

<br>

  - Fixed:
    - Fixed suggestions breaking when typing a parentheses.

<br>

  - Other changes:
    - Batch Tag Delete is no longer bundled within img-txt_viewer. This allows you to run them separately.


<!-- New -->
[]:

<!-- Fixed -->
[]:

<!-- Other changes -->
[]:


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
  -

  - **Minor** Undo should be less jarring when inserting a suggestion.
  - **Minor** After deleting or Undo Delete. PanedWindow sash moves position.


'''

#endregion
