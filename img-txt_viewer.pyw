"""
########################################
#                                      #
#            IMG-TXT VIEWER            #
#                                      #
#   Version : v1.94                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
Display an image and text file side-by-side for easy manual caption editing.

More info here: https://github.com/Nenotriple/img-txt_viewer

"""


VERSION = "v1.94"


################################################################################################################################################
#region -  Imports


import os
import re
import csv
import sys
import glob
import time
import numpy
import shutil
import ctypes
import itertools
import webbrowser
import subprocess
import configparser
from collections import defaultdict

import tkinter.font
from tkinter import ttk, Tk, Toplevel, messagebox, StringVar, BooleanVar, IntVar, Menu, PanedWindow, Frame, Label, Button, Entry, Checkbutton, Text, Event, Canvas, TclError
from tkinter.filedialog import askdirectory
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageTk, ImageSequence, UnidentifiedImageError

from main.scripts import crop_image, batch_crop_images, resize_image, image_grid
from main.scripts.TkToolTip import TkToolTip as ToolTip
from main.bin import upscale_image


#endregion
################################################################################################################################################
#region - CLASS: AboutWindow


class AboutWindow(Toplevel):
    info_headers = ["Shortcuts", "Tips", "Text Tools", "Other Tools", "Auto-Save"]
    info_content = [
        # Shortcuts
        " ⦁ALT+LEFT/RIGHT: Quickly move between img-txt pairs.\n"
        " ⦁SHIFT+DEL: Send the current pair to a local trash folder.\n"
        " ⦁ALT: Cycle through auto-suggestions.\n"
        " ⦁TAB: Insert the highlighted suggestion.\n"
        " ⦁CTRL+S: Save the current text file.\n"
        " ⦁CTRL+E: Jump to the next empty text file.\n"
        " ⦁CTRL+R: Jump to a random img-txt pair.\n"
        " ⦁CTRL+F: Highlight all duplicate words.\n"
        " ⦁CTRL+Z / CTRL+Y: Undo/Redo.\n"
        " ⦁F5: Refresh the text box.\n"
        " ⦁Middle-click a tag to delete it.\n",

        # Tips
        " ⦁Highlight matching words by selecting text.\n"
        " ⦁Quickly create text pairs by loading the image and saving the text.\n"
        " ⦁List Mode: Display tags in a list format while saving in standard format.\n"
        " ⦁Use an asterisk * while typing to return suggestions using fuzzy search.\n",

        # Text Tools
        " ⦁Search and Replace: Edit all text files at once.\n"
        " ⦁Prefix: Insert text at the START of all text files.\n"
        " ⦁Append: Insert text at the END of all text files.\n"
        " ⦁Filter: Filter pairs based on matching text, blank or missing txt files, and more.\n"
        " ⦁Highlight: Always highlight certain text.\n"
        " ⦁My Tags: Quickly add you own tags to be used as autocomplete suggestions.\n"
        " ⦁Batch Tag Delete: View all tags in a directory as a list, and quickly delete them.\n"
        " ⦁Cleanup Text: Fix typos in all text files of the selected folder, such as duplicate tags, multiple spaces or commas, missing spaces, and more.\n",

        # Other Tools
        " ⦁Batch Resize Images: Resize images using several methods.\n"
        " ⦁Crop Image: Crop the current image to a square or freeform ratio.\n"
        " ⦁Resize Image: Resize the current image either by exact resolution or percentage.\n"
        " ⦁Find Duplicate Files: Find and separate any duplicate files in a folder.\n"
        " ⦁Expand: Expand an image to a square ratio instead of cropping.\n"
        " ⦁Rename and Convert Pairs: Automatically rename files using a neat and tidy formatting.\n",

        # Auto Save
        " ⦁Check the auto-save box to save text when navigating between img/txt pairs or closing the window, etc.\n"
        " ⦁Text is cleaned up when saved, so you can ignore things like duplicate tags, trailing comma/spaces, double comma/spaces, etc.\n"
        " ⦁Text cleanup can be disabled from the options menu.",
        ]


    def __init__(self, master=None):
        super().__init__(master=master)
        self.title("About")
        self.geometry("850x650")
        self.maxsize(900, 900)
        self.minsize(630, 300)
        self.github_url = "https://github.com/Nenotriple/img-txt_viewer"
        self.create_info_text()
        self.create_other_widgets()
        self.focus_force()


    def create_info_text(self):
        self.info_text = ScrolledText(self)
        self.info_text.pack(expand=True, fill='both')
        for header, section in zip(AboutWindow.info_headers, AboutWindow.info_content):
            self.info_text.insert("end", header + "\n", "header")
            self.info_text.insert("end", section + "\n", "section")
        self.info_text.tag_config("header", font=("Segoe UI", 9, "bold"))
        self.info_text.tag_config("section", font=("Segoe UI", 9))
        self.info_text.config(state='disabled', wrap="word", height=1)


    def create_other_widgets(self):
        frame = Frame(self)
        frame.pack(fill="x")

        self.url_button = Button(frame, text=f"{self.github_url}", fg="blue", relief="flat", overrelief="groove", command=self.open_url)
        self.url_button.pack(side="left", fill="x", padx=10)
        ToolTip.create(self.url_button, "Click this button to open the repo in your default browser", 10, 6, 12)

        self.made_by_label = Label(frame, text=f"{VERSION} - img-txt_viewer - Created by: Nenotriple (2023-2024)", font=("Arial", 10))
        self.made_by_label.pack(side="left", expand=True, pady=10)
        ToolTip.create(self.made_by_label, "🤍Thank you for using my app!🤍 (^‿^)", 10, 6, 12)


    def open_url(self):
        webbrowser.open(f"{self.github_url}")


#endregion
################################################################################################################################################
#region - CLASS: PopUpZoom


class PopUpZoom:
    def __init__(self, widget):
        # Initialize the PopUpZoom class
        self.widget = widget  # The widget to which this zoom functionality is bound.
        self.zoom_factor = 1.75  # The initial zoom level for the image.
        self.min_zoom_factor = 0.5  # The minimum zoom level allowed.
        self.max_zoom_factor = 10.0  # The maximum zoom level allowed.
        self.max_image_size = 4096  # The maximum size (in pixels) of the image that can be displayed. Larger images will be downsampled to this size.

        # Initialize image attributes
        self.image = None
        self.image_path = None
        self.original_image = None
        self.resized_image = None
        self.resized_width = 0
        self.resized_height = 0

        # Initialize zoom enabled variable
        self.zoom_enabled = BooleanVar(value=False)

        # Set up the zoom window
        self.popup_size = 400  # The size (in pixels) of the popup window that shows the zoomed image.
        self.min_popup_size = 100  # Minimum popup size
        self.max_popup_size = 600  # Maximum popup size

        self.zoom_window = Toplevel(widget)  # Create a new top-level window for the zoomed image.
        self.zoom_window.withdraw()  # Hide the zoom window until it's needed.
        self.zoom_window.overrideredirect(True)  # Remove the window decorations (like title bar, close button, etc.)
        self.zoom_canvas = Canvas(self.zoom_window, width=self.popup_size, height=self.popup_size, highlightthickness=0)  # Create a canvas in the zoom window. This is where the zoomed image will be drawn.
        self.zoom_canvas.pack()  # Make the canvas fill the zoom window.

        # Bind events to the widget
        self.widget.bind("<Motion>", self.update_zoom, add="+")
        self.widget.bind("<Leave>", self.hide_zoom, add="+")
        self.widget.bind("<Button-1>", self.hide_zoom, add="+")
        self.widget.bind("<MouseWheel>", self.zoom, add="+")


    def set_image(self, image, path):
        '''Set the image and its path'''
        if self.image == image and self.image_path == path:
            return
        self.image = image
        self.image_path = path
        self.original_image = Image.open(self.image_path)
        self.resize_original_image()


    def resize_original_image(self):
        '''Resize the original image if it's too large'''
        max_size = self.max_image_size
        if self.original_image.width > max_size or self.original_image.height > max_size:
            aspect_ratio = self.original_image.width / self.original_image.height
            if self.original_image.width > self.original_image.height:
                new_width = max_size
                new_height = int(max_size / aspect_ratio)
            else:
                new_height = max_size
                new_width = int(max_size * aspect_ratio)
            self.original_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)


    def set_resized_image(self, resized_image, resized_width, resized_height):
        '''Set the resized image and its dimensions'''
        self.resized_image = resized_image
        self.resized_width = resized_width
        self.resized_height = resized_height


    def create_zoomed_image(self, left, top, right, bottom):
        '''Create and display the zoomed image in the zoom window'''
        cropped_image = self.original_image.crop((left, top, right, bottom))
        aspect_ratio = cropped_image.width / cropped_image.height
        if aspect_ratio > 1:
            new_width = self.popup_size
            new_height = int(self.popup_size / aspect_ratio)
        else:
            new_height = self.popup_size
            new_width = int(self.popup_size * aspect_ratio)
        resize_method = Image.NEAREST if self.zoom_factor >= 4 else Image.LANCZOS
        zoomed_image = cropped_image.resize((new_width, new_height), resize_method)
        self.zoom_photo_image = ImageTk.PhotoImage(zoomed_image)
        self.zoom_canvas.delete("all")
        x = (self.popup_size - new_width) // 2
        y = (self.popup_size - new_height) // 2
        self.zoom_canvas.create_image(x, y, anchor="nw", image=self.zoom_photo_image)


    def calculate_coordinates(self, img_x, img_y):
        '''Calculate the coordinates for the zoomed image'''
        half_size = self.popup_size // (2 * self.zoom_factor)
        left = max(0, int(img_x - half_size))
        right = min(self.original_image.width, int(img_x + half_size))
        top = max(0, int(img_y - half_size))
        bottom = min(self.original_image.height, int(img_y + half_size))
        # Ensure the coordinates are within bounds
        if right - left < self.popup_size // self.zoom_factor:
            left = max(0, right - self.popup_size // self.zoom_factor)
            right = min(self.original_image.width, left + self.popup_size // self.zoom_factor)
        if bottom - top < self.popup_size // self.zoom_factor:
            top = max(0, bottom - self.popup_size // self.zoom_factor)
            bottom = min(self.original_image.height, top + self.popup_size // self.zoom_factor)
        return left, top, right, bottom


    def update_zoom(self, event):
        '''Update the zoom window with the zoomed image'''
        if event is None:
            return
        if not self.zoom_enabled.get() or not (self.image and self.resized_image):
            return
        x, y = event.x, event.y
        screen_width, screen_height = self.widget.winfo_screenwidth(), self.widget.winfo_screenheight()
        new_x, new_y = event.x_root + 20, event.y_root + 20
        if new_x + self.popup_size > screen_width:
            new_x = event.x_root - self.popup_size - 20
        if new_y + self.popup_size > screen_height:
            new_y = event.y_root - self.popup_size - 20
        self.zoom_window.geometry(f"+{new_x}+{new_y}")
        pad_x = (self.widget.winfo_width() - self.resized_width) / 2
        pad_y = (self.widget.winfo_height() - self.resized_height) / 2
        img_x = (x - pad_x) * self.original_image.width / self.resized_width
        img_y = (y - pad_y) * self.original_image.height / self.resized_height
        left, top, right, bottom = self.calculate_coordinates(img_x, img_y)
        if left < right and top < bottom:
            self.create_zoomed_image(left, top, right, bottom)
            self.zoom_window.deiconify()
        else:
            self.zoom_window.withdraw()


    def zoom(self, event):
        '''Adjust the zoom factor or popup size based on the mouse wheel event'''
        if event.state & 0x0001:  # Shift key is held
            self.popup_size += 20 if event.delta > 0 else -20
            self.popup_size = max(self.min_popup_size, min(self.popup_size, self.max_popup_size))
            self.zoom_canvas.config(width=self.popup_size, height=self.popup_size)
        else:
            min_zoom = self.min_zoom_factor
            max_zoom = self.max_zoom_factor
            self.zoom_factor += min_zoom if event.delta > 0 else -min_zoom
            self.zoom_factor = max(min_zoom, min(self.zoom_factor, max_zoom))
        self.update_zoom(event)


    def hide_zoom(self, event):
        '''Hide the zoom window'''
        self.zoom_window.withdraw()


#endregion
################################################################################################################################################
#region - CLASS: Autocomplete


class Autocomplete:
    def __init__(self, data_file, max_suggestions=4, suggestion_threshold=115000):
        self.max_suggestions = max_suggestions
        self.suggestion_threshold = suggestion_threshold
        self.previous_text = None
        self.previous_suggestions = None
        self.previous_pattern = None
        self.data, self.similar_names_dict = self.load_data(data_file)


    def load_data(self, data_file, additional_file='my_tags.csv'):
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        data_file_path = os.path.join(application_path, "main/dict", data_file)
        additional_file_path = os.path.join(application_path, additional_file)
        data = {}
        similar_names_dict = defaultdict(list)
        if os.path.isfile(data_file_path):
            with open(data_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and not row[0].startswith('###'):
                        true_name = row[0]
                        classifier_id = row[1]
                        similar_names = set(row[3].split(',')) if len(row) > 3 else set()
                        data[true_name] = (classifier_id, similar_names)
                        for sim_name in similar_names:
                            similar_names_dict[sim_name].append(true_name)
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
                        for sim_name in similar_names:
                            similar_names_dict[sim_name].append(true_name)
        return data, similar_names_dict


    def get_suggestion(self, text):
        if not self.data:
            return None
        text_with_underscores = text.replace(" ", "_")
        text_with_asterisks = re.escape(text_with_underscores).replace("\\*", ".*")
        pattern = re.compile(text_with_asterisks)
        suggestions = {}
        suggestion_threshold = 25000 if not self.previous_suggestions else self.suggestion_threshold
        for true_name, (classifier_id, similar_names) in itertools.islice(self.data.items(), suggestion_threshold):
            if pattern.match(true_name):
                suggestions[true_name] = (classifier_id, similar_names)
        for sim_name in self.similar_names_dict:
            if pattern.match(sim_name):
                for true_name in self.similar_names_dict[sim_name]:
                    classifier_id, similar_names = self.data[true_name]
                    suggestions[true_name] = (classifier_id, similar_names)
        suggestions = list(suggestions.items())
        suggestions.sort(key=lambda x: self.get_score(x[0], text_with_underscores), reverse=True)
        self.previous_text = text
        self.previous_suggestions = suggestions
        self.previous_pattern = pattern
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
#region - CLASS: ImgTxtViewer


class ImgTxtViewer:
    def __init__(self, master):


        # Window Setup
        self.master = master
        self.set_appid()
        self.set_window_size(master)
        self.set_icon()


        # Setup ConfigParser
        self.config = configparser.ConfigParser()


        # Window drag variables
        self.drag_x = None
        self.drag_y = None


        # Navigation variables
        self.last_scroll_time = 0
        self.prev_num_files = 0
        self.current_index = 0


        # Text tools
        self.search_string_var = StringVar()
        self.replace_string_var = StringVar()
        self.prefix_string_var = StringVar()
        self.append_string_var = StringVar()
        self.custom_highlight_string_var = StringVar()


        # Filter variables
        self.original_image_files = []
        self.original_text_files = []
        self.filter_string_var = StringVar()


        # File lists
        self.text_files = []
        self.image_files = []
        self.deleted_pairs = []
        self.new_text_files = []


        # Misc variables
        self.about_window_open = None
        self.panes_swapped_var = False
        self.text_modified_var = False
        self.is_alt_arrow_pressed = False
        self.filepath_contains_images_var = False
        self.is_resizing_id = None
        self.toggle_zoom_var = None


        # GIF animation variables
        self.gif_frames = []
        self.gif_frame_cache = {}
        self.frame_durations = []
        self.current_frame = 0
        self.current_gif_frame_image = None
        self.animation_job = None


        # Misc Settings
        self.image_dir = StringVar(value="Choose Directory...")
        self.new_text_path = ""
        self.font_var = StringVar()
        self.font_size_var = 10
        self.undo_state = StringVar(value="disabled")
        self.list_mode_var = BooleanVar(value=False)
        self.cleaning_text_var = BooleanVar(value=True)
        self.auto_save_var = BooleanVar(value=False)
        self.big_save_button_var = BooleanVar(value=False)
        self.highlight_selection_var = BooleanVar(value=True)
        self.highlight_all_duplicates_var = BooleanVar(value=False)


        # Image Quality
        self.image_qualtiy_var = StringVar(value="Normal")
        self.quality_filter_dict = {"LANCZOS": Image.LANCZOS, "BILINEAR": Image.BILINEAR}
        self.quality_max_size = 1280
        self.quality_filter = "BILINEAR"


        # Autocomplete
        self.csv_danbooru = BooleanVar(value=True)
        self.csv_derpibooru = BooleanVar(value=False)
        self.csv_e621 = BooleanVar(value=False)
        self.csv_english_dictionary = BooleanVar(value=False)
        self.colored_suggestion_var = BooleanVar(value=True)
        self.suggestion_quantity_var = IntVar(value=4)
        self.suggestion_threshold_var = StringVar(value="Normal")
        self.last_word_match_var = BooleanVar(value=False)
        self.selected_suggestion_index = 0
        self.suggestions = []


        # Bindings
        master.bind("<Control-f>", lambda event: self.toggle_highlight_all_duplicates())
        master.bind("<Control-s>", lambda event: self.save_text_file())
        master.bind("<Alt-Right>", lambda event: self.next_pair(event))
        master.bind("<Alt-Left>", lambda event: self.prev_pair(event))
        master.bind('<Shift-Delete>', lambda event: self.delete_pair())
        master.bind('<Configure>', lambda event: self.on_resize(event))
        master.bind('<F1>', lambda event: self.toggle_zoom_popup(event))
        master.bind('<F2>', lambda event: self.view_image_grid(event))


#endregion
################################################################################################################################################
#region -  Menubar


####### Initilize Menu Bar ############################################


        # Main
        menubar = Menu(self.master)
        self.master.config(menu=menubar)


        # Options
        self.optionsMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", underline=0, menu=self.optionsMenu)


        # Tools
        self.toolsMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", underline=0, menu=self.toolsMenu)


        # About
        menubar.add_command(label="About", underline=0, command=self.toggle_about_window)


####### Options Menu ##################################################


        # Suggestion Dictionary Menu
        dictionaryMenu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Suggestion Dictionary", underline=11, state="disable", menu=dictionaryMenu)
        dictionaryMenu.add_checkbutton(label="English Dictionary", underline=0, variable=self.csv_english_dictionary, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Danbooru", underline=0, variable=self.csv_danbooru, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Derpibooru", underline=0, variable=self.csv_derpibooru, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="e621", underline=0, variable=self.csv_e621, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_separator()
        dictionaryMenu.add_command(label="Clear Selection", underline=0, command=self.clear_dictionary_csv_selection)


        # Suggestion Threshold Menu
        suggestion_threshold_menu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Suggestion Threshold", underline=11, state="disable", menu=suggestion_threshold_menu)
        for level in ["Slow", "Normal", "Fast", "Faster"]:
            suggestion_threshold_menu.add_radiobutton(label=level, variable=self.suggestion_threshold_var, value=level, command=self.set_suggestion_threshold)


        # Suggestion Quantity Menu
        suggestion_quantity_menu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Suggestion Quantity", underline=11, state="disable", menu=suggestion_quantity_menu)
        for quantity in range(0, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(quantity), variable=self.suggestion_quantity_var, value=quantity, command=lambda suggestion_quantity=quantity: self.set_suggestion_quantity(suggestion_quantity))


        # Match Mode Menu
        match_mode_menu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Match Mode", menu=match_mode_menu)
        match_modes = {"Match Whole String": False, "Match Last Word": True}
        for mode, value in match_modes.items():
            match_mode_menu.add_radiobutton(label=mode, variable=self.last_word_match_var, value=value)
        self.optionsMenu.add_separator()


        # Options
        self.optionsMenu.add_checkbutton(label="Cleaning Text on Save", underline=0, state="disable", variable=self.cleaning_text_var, command=self.toggle_list_menu)
        self.optionsMenu.add_checkbutton(label="Colored Suggestions", underline=1, state="disable", variable=self.colored_suggestion_var, command=self.update_autocomplete_dictionary)
        self.optionsMenu.add_checkbutton(label="Highlight Selection", underline=0, state="disable", variable=self.highlight_selection_var)
        self.optionsMenu.add_checkbutton(label="Big Save Button", underline=4, state="disable", variable=self.big_save_button_var, command=self.toggle_save_button_height)
        self.optionsMenu.add_checkbutton(label="List View", underline=0, state="disable", variable=self.list_mode_var, command=self.toggle_list_mode)
        self.optionsMenu.add_separator()
        self.optionsMenu.add_checkbutton(label="Always On Top", underline=0, command=self.toggle_always_on_top)
        #self.optionsMenu.add_checkbutton(label="Toggle Zoom", accelerator="F1", command=self.toggle_zoom_popup, variable=self.toggle_zoom_var) # Disabled because this checkbutton state isn't staying in sync with the "imageContext_menu" checkbutton.
        self.optionsMenu.add_checkbutton(label="Vertical View", underline=0, state="disable", command=self.swap_pane_orientation)
        self.optionsMenu.add_checkbutton(label="Swap img-txt Sides", underline=0, state="disable", command=self.swap_pane_sides)


        # Image Display Quality Menu
        image_quality_menu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Image Display Quality", underline=1, state="disable", menu=image_quality_menu)
        for value in ["High", "Normal", "Low"]:
            image_quality_menu.add_radiobutton(label=value, variable=self.image_qualtiy_var, value=value, command=self.set_image_quality)


####### Tools Menu ##################################################


        # Tools
        self.toolsMenu.add_command(label="Batch Tag Delete...", underline=0, command=self.batch_tag_delete)
        self.toolsMenu.add_command(label="Batch Resize Images...", underline=10, command=self.batch_resize_images)
        self.toolsMenu.add_command(label="Batch Crop Images...", underline=8, state="disable", command=self.batch_crop_images)
        self.toolsMenu.add_command(label="Find Duplicate Files...", underline=0, command=self.find_duplicate_files)
        self.toolsMenu.add_command(label="Rename img-txt Pairs...", underline=2, state="disable", command=self.rename_pairs)
        self.toolsMenu.add_command(label="Rename and Convert img-txt Pairs...", underline=3, state="disable", command=self.rename_and_convert_pairs)
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Upscale...", underline=0, state="disable", command=self.upscale_image)
        self.toolsMenu.add_command(label="Crop...", underline=0, state="disable", command=self.open_crop_tool)
        self.toolsMenu.add_command(label="Resize...", underline=0, state="disable", command=self.resize_image)
        self.toolsMenu.add_command(label="Expand", underline=1, state="disable", command=self.expand_image)
        self.toolsMenu.add_command(label="Rotate", underline=1, state="disable", command=self.rotate_current_image)
        self.toolsMenu.add_command(label="Flip", underline=1, state="disable", command=self.flip_current_image)

        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Next Empty Text File", accelerator="Ctrl+E", state="disable", command=self.index_goto_next_empty)
        self.toolsMenu.add_command(label="Cleanup all Text Files", underline=1, state="disable", command=self.cleanup_all_text_files)
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Open Current Directory...", underline=13, state="disable", command=self.open_current_directory)
        self.toolsMenu.add_command(label="Open Current Image...", underline=13, state="disable", command=self.open_current_image)
        self.toolsMenu.add_command(label="Open Image Grid...", accelerator="F2", underline=11, state="disabled", command=self.view_image_grid)

        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Duplicate img-txt pair", underline=2, state="disable", command=self.duplicate_pair)
        self.toolsMenu.add_command(label="Delete img-txt Pair", accelerator="Shift+Del", state="disable", command=self.delete_pair)
        self.toolsMenu.add_command(label="Undo Delete", underline=0, command=self.undo_delete_pair, state="disabled")


#endregion
################################################################################################################################################
#region -  Buttons, Labels, and more


        # This PanedWindow holds both master frames.
        self.primary_paned_window = PanedWindow(master, orient="horizontal", sashwidth=6, bg="#d0d0d0", bd=0)
        self.primary_paned_window.pack(fill="both", expand=1)
        self.primary_paned_window.bind('<ButtonRelease-1>', self.snap_sash_to_half)


        # This frame is exclusively used for the displayed image and image info.
        self.master_image_frame = Frame(master)
        self.primary_paned_window.add(self.master_image_frame, stretch="always")


        # This frame serves as a container for all primary UI frames, with the exception of the master_image_frame.
        self.master_control_frame = Frame(master)
        self.primary_paned_window.add(self.master_control_frame, stretch="always", )
        self.primary_paned_window.paneconfigure(self.master_control_frame, minsize=300)
        self.primary_paned_window.update(); self.primary_paned_window.sash_place(0, 0, 0)


        # Image Label
        self.stats_frame = Frame(self.master_image_frame)
        self.stats_frame.pack(side="top", fill="x")
        self.image_label = Label(self.stats_frame, text="...")
        self.image_label.pack(side="top", fill="x")
        self.image_preview = Button(self.master_image_frame, relief="flat", cursor="hand2")
        self.image_preview.pack(side="left")
        self.image_preview.bind("<Double-1>", self.open_current_image)
        self.image_preview.bind('<Button-2>', self.open_current_directory)
        self.image_preview.bind("<MouseWheel>", self.mouse_scroll)
        self.image_preview.bind("<Button-3>", self.show_imageContext_menu)
        self.image_preview.bind("<ButtonPress-1>", self.start_drag)
        self.image_preview.bind("<ButtonRelease-1>", self.stop_drag)
        self.image_preview.bind("<B1-Motion>", self.dragging_window)
        self.popup_zoom = PopUpZoom(self.image_preview)
        self.toggle_zoom_var = BooleanVar(value=self.popup_zoom.zoom_enabled.get())
        self.image_preview_tooltip = ToolTip.create(self.image_preview, "Double-Click to open in system image viewer \n\nMiddle click to open in file explorer\n\nALT+Left/Right or Mouse-Wheel to move between img-txt pairs", 1000, 6, 12)


        # Directory Selection
        directory_frame = Frame(self.master_control_frame)
        directory_frame.pack(side="top", fill="x")
        self.text_path_indicator = Label(directory_frame)
        self.text_path_indicator.pack(side="left", fill="y", pady=2)
        self.text_path_tooltip = ToolTip.create(self.text_path_indicator, "Text Path: Same as image path", 10, 6, 12)
        self.directory_entry = Entry(directory_frame, textvariable=self.image_dir)
        self.directory_entry.pack(side="left", fill="both", expand=True, pady=2)
        self.directory_entry.bind('<Return>', self.set_working_directory)
        self.dir_context_menu = Menu(self.directory_entry, tearoff=0)
        self.dir_context_menu.add_command(label="Cut", command=self.directory_cut)
        self.dir_context_menu.add_command(label="Copy", command=self.directory_copy)
        self.dir_context_menu.add_command(label="Paste", command=self.directory_paste)
        self.dir_context_menu.add_command(label="Delete", command=self.directory_delete)
        self.dir_context_menu.add_command(label="Clear", command=self.directory_clear)
        self.directory_entry.bind("<Button-3>", self.open_directory_context_menu)
        self.directory_entry.bind("<Button-1>", self.clear_directory_entry_on_click)
        self.browse_button = Button(directory_frame, overrelief="groove", text="Browse...", command=self.choose_working_directory)
        self.browse_button.pack(side="left", fill="x", padx=2, pady=2)
        ToolTip.create(self.browse_button, "Right click to set an alternate path for text files", 250, 6, 12)
        self.browse_context_menu = Menu(self.browse_button, tearoff=0)
        self.browse_context_menu.add_command(label="Set Text File Path...", state="disabled", command=self.set_text_file_path)
        self.browse_context_menu.add_command(label="Clear Text File Path", state="disabled", command=lambda: self.set_text_file_path(self.image_dir.get()))
        self.browse_button.bind("<Button-3>", self.open_browse_context_menu)
        self.open_button = Button(directory_frame, overrelief="groove", text="Open", command=lambda: self.open_directory(self.directory_entry.get()))
        self.open_button.pack(side="left", fill="x", padx=2, pady=2)


        # Image Index
        self.index_frame = Frame(self.master_control_frame)
        self.index_frame.pack(side="top", fill="x")
        self.index_pair_label = Label(self.index_frame, text="Pair", state="disabled")
        self.index_pair_label.pack(side="left")
        self.image_index_entry = Entry(self.index_frame, width=5, state="disabled")
        self.image_index_entry.bind("<Return>", self.jump_to_image)
        self.image_index_entry.pack(side="left")
        self.image_index_entry.bind("<MouseWheel>", self.mouse_scroll)

        self.index_context_menu = Menu(self.directory_entry, tearoff=0)
        self.index_context_menu.add_command(label="First", command=self.index_goto_first)
        self.index_context_menu.add_command(label="Random", accelerator="Ctrl+R", command=self.index_goto_random)
        self.index_context_menu.add_command(label="Next Empty", accelerator="Ctrl+E", command=self.index_goto_next_empty)

        self.total_images_label = Label(self.index_frame, text=f"of {len(self.image_files)}", state="disabled")
        self.total_images_label.pack(side="left", padx=(0, 2))


        # Save Button
        self.save_button = Button(self.index_frame, height=1, overrelief="groove", text="Save", fg="blue", state="disabled", command=self.save_text_file)
        self.save_button.pack(fill="x", side="left", expand=True, padx=2, pady=2)
        ToolTip.create(self.save_button, "CTRL+S to save\n\nRight-Click to make the save button larger", 1000, 6, 12)
        self.auto_save_checkbutton = Checkbutton(self.index_frame, overrelief="groove", width=10, text="Auto-save", state="disabled", variable=self.auto_save_var, command=self.change_message_label)
        self.auto_save_checkbutton.pack(side="left")
        self.save_button.bind('<Button-3>', self.toggle_save_button_height)


        # Navigation Buttons
        nav_button_frame = Frame(self.master_control_frame)
        nav_button_frame.pack()
        self.next_button = Button(nav_button_frame, overrelief="groove", text="Next--->", width=22, state="disabled", command=lambda event=None: self.next_pair(event))
        self.prev_button = Button(nav_button_frame, overrelief="groove", text="<---Previous", width=22, state="disabled", command=lambda event=None: self.prev_pair(event))
        self.next_button.pack(side="right", pady=2)
        self.prev_button.pack(side="right", padx=2, pady=2)
        ToolTip.create(self.next_button, "ALT+R ", 1000, 6, 12)
        ToolTip.create(self.prev_button, "ALT+L ", 1000, 6, 12)


        # Saved Label
        message_label_frame = Frame(self.master_control_frame)
        message_label_frame.pack(pady=2)
        self.message_label = Label(message_label_frame, text="No Change", state="disabled", width=35)
        self.message_label.pack()


        # Suggestion text
        self.suggestion_textbox = Text(self.master_control_frame, height=1, borderwidth=0, highlightthickness=0, bg='#f0f0f0', state="disabled", cursor="arrow")
        self.suggestion_textbox.pack(side="top", fill="x")
        self.suggestion_textbox.bind("<Button-1>", self.disable_button)
        self.suggestion_textbox.bind("<B1-Motion>", self.disable_button)
        ToolTip.create(self.suggestion_textbox,
                               "TAB: Insert the highlighted suggestion\n"
                               "ALT: Cycle suggestion selection\n\n"
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
                               1000, 6, 12)


        # Startup info text
        self.info_text = ScrolledText(self.master_control_frame)
        self.info_text.pack(expand=True, fill="both")
        for header, section in zip(AboutWindow.info_headers, AboutWindow.info_content):
            self.info_text.insert("end", header + "\n", "header")
            self.info_text.insert("end", section + "\n", "section")
        self.info_text.tag_config("header", font=("Segoe UI", 9, "bold"))
        self.info_text.tag_config("section", font=("Segoe UI", 9))
        self.info_text.bind("<Button-3>", self.show_textContext_menu)
        self.info_text.config(state='disabled', wrap="word")


#endregion
################################################################################################################################################
#region -  Text Box setup


    def create_text_pane(self):
        self.word_wrap_var = BooleanVar(value=True)
        if not hasattr(self, 'text_pane'):
            self.text_pane = PanedWindow(self.master_control_frame, orient="vertical", sashwidth=6, bg="#d0d0d0", bd=0)
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


    def create_text_control_frame(self):
        self.text_widget_frame = Frame(self.master_control_frame)
        self.text_pane.add(self.text_widget_frame, stretch="never")
        self.text_pane.paneconfigure(self.text_widget_frame)
        self.text_notebook = ttk.Notebook(self.text_widget_frame)
        self.tab1 = Frame(self.text_notebook)
        self.tab2 = Frame(self.text_notebook)
        self.tab3 = Frame(self.text_notebook)
        self.tab4 = Frame(self.text_notebook)
        self.tab5 = Frame(self.text_notebook)
        self.tab6 = Frame(self.text_notebook)
        self.tab7 = Frame(self.text_notebook)
        self.text_notebook.add(self.tab1, text='Search & Replace')
        self.text_notebook.add(self.tab2, text='Prefix')
        self.text_notebook.add(self.tab3, text='Append')
        self.text_notebook.add(self.tab4, text='Filter')
        self.text_notebook.add(self.tab5, text='Highlight')
        self.text_notebook.add(self.tab6, text='Font')
        self.text_notebook.add(self.tab7, text='My Tags')
        self.text_notebook.pack(fill='both')
        self.create_search_and_replace_widgets_tab1()
        self.create_prefix_text_widgets_tab2()
        self.create_append_text_widgets_tab3()
        self.create_filter_text_image_pairs_widgets_tab4()
        self.create_custom_active_highlight_widgets_tab5()
        self.create_font_widgets_tab6()
        self.create_custom_dictionary_widgets_tab7()


    def create_search_and_replace_widgets_tab1(self):
        def clear_all():
            self.search_entry.delete(0, 'end')
            self.replace_entry.delete(0, 'end')
        self.tab1_frame = Frame(self.tab1)
        self.tab1_frame.pack(side='top', fill='both')
        self.tab1_button_frame = Frame(self.tab1_frame)
        self.tab1_button_frame.pack(side='top', fill='x')
        self.search_label = Label(self.tab1_button_frame, width=8, text="Search:")
        self.search_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.search_label, "Enter the EXACT text you want to search for", 200, 6, 12)
        self.search_entry = Entry(self.tab1_button_frame, textvariable=self.search_string_var, width=4)
        self.search_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.replace_label = Label(self.tab1_button_frame, width=8, text="Replace:")
        self.replace_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.replace_label, "Enter the text you want to replace the searched text with\n\nLeave empty to replace with nothing (delete)", 200, 6, 12)
        self.replace_entry = Entry(self.tab1_button_frame, textvariable=self.replace_string_var, width=4)
        self.replace_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.replace_entry.bind('<Return>', lambda event: self.search_and_replace())
        self.replace_button = Button(self.tab1_button_frame, text="Go!", overrelief="groove", width=4, command=self.search_and_replace)
        self.replace_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.replace_button, "Text files will be backup up", 200, 6, 12)
        self.clear_button = Button(self.tab1_button_frame, text="Clear", overrelief="groove", width=4, command=clear_all)
        self.clear_button.pack(side='left', anchor="n", pady=4, padx=1)
        self.undo_button = Button(self.tab1_button_frame, text="Undo", overrelief="groove", width=4, command=self.restore_backup)
        self.undo_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.undo_button, "Revert last action", 200, 6, 12)
        self.tab1_text_frame = Frame(self.tab1_frame, borderwidth=0)
        self.tab1_text_frame.pack(side='top', fill="both")
        description_textbox = ScrolledText(self.tab1_text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0", "Use this tool to search for a string of text across all text files in the selected directory.\n\n"
                                   "If a match is found, it will be replaced exactly with the given text.\n\n"
                                   "Example:\n"
                                   "Search for: the big brown dog\n"
                                   "Replace with: the big red dog\n\n"
                                   "This will replace all instances of 'the big brown dog' with 'the big red dog'.")
        description_textbox.config(state="disabled", wrap="word")


    def create_prefix_text_widgets_tab2(self):
        def clear():
            self.prefix_entry.delete(0, 'end')
        self.tab2_frame = Frame(self.tab2)
        self.tab2_frame.pack(side='top', fill='both')
        self.tab2_button_frame = Frame(self.tab2_frame)
        self.tab2_button_frame.pack(side='top', fill='x')
        self.prefix_label = Label(self.tab2_button_frame, width=8, text="Prefix:")
        self.prefix_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.prefix_label, "Enter the text you want to insert at the START of all text files\n\nCommas will be inserted as needed", 200, 6, 12)
        self.prefix_entry = Entry(self.tab2_button_frame, textvariable=self.prefix_string_var)
        self.prefix_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.prefix_entry.bind('<Return>', lambda event: self.prefix_text_files())
        self.prefix_button = Button(self.tab2_button_frame, text="Go!", overrelief="groove", width=4, command=self.prefix_text_files)
        self.prefix_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.prefix_button, "Text files will be backup up", 200, 6, 12)
        self.clear_button = Button(self.tab2_button_frame, text="Clear", overrelief="groove", width=4, command=clear)
        self.clear_button.pack(side='left', anchor="n", pady=4, padx=1)
        self.undo_button = Button(self.tab2_button_frame, text="Undo", overrelief="groove", width=4, command=self.restore_backup)
        self.undo_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.undo_button, "Revert last action", 200, 6, 12)
        self.tab2_text_frame = Frame(self.tab2_frame, borderwidth=0)
        self.tab2_text_frame.pack(side='top', fill="both")
        description_textbox = ScrolledText(self.tab2_text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0", "Use this tool to prefix all text files in the selected directory with the entered text.\n\n"
                                   "This means that the entered text will appear at the start of each text file.")
        description_textbox.config(state="disabled", wrap="word")


    def create_append_text_widgets_tab3(self):
        def clear():
            self.append_entry.delete(0, 'end')
        self.tab3_frame = Frame(self.tab3)
        self.tab3_frame.pack(side='top', fill='both')
        self.tab3_button_frame = Frame(self.tab3_frame)
        self.tab3_button_frame.pack(side='top', fill='x')
        self.append_label = Label(self.tab3_button_frame, width=8, text="Append:")
        self.append_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.append_label, "Enter the text you want to insert at the END of all text files\n\nCommas will be inserted as needed", 200, 6, 12)
        self.append_entry = Entry(self.tab3_button_frame, textvariable=self.append_string_var)
        self.append_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.append_entry.bind('<Return>', lambda event: self.append_text_files())
        self.append_button = Button(self.tab3_button_frame, text="Go!", overrelief="groove", width=4, command=self.append_text_files)
        self.append_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.append_button, "Text files will be backup up", 200, 6, 12)
        self.clear_button = Button(self.tab3_button_frame, text="Clear", overrelief="groove", width=4, command=clear)
        self.clear_button.pack(side='left', anchor="n", pady=4, padx=1)
        self.undo_button = Button(self.tab3_button_frame, text="Undo", overrelief="groove", width=4, command=self.restore_backup)
        self.undo_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.undo_button, "Revert last action", 200, 6, 12)
        self.tab3_text_frame = Frame(self.tab3_frame, borderwidth=0)
        self.tab3_text_frame.pack(side='top', fill="both")
        description_textbox = ScrolledText(self.tab3_text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0", "Use this tool to append all text files in the selected directory with the entered text.\n\n"
                                   "This means that the entered text will appear at the end of each text file.")
        description_textbox.config(state="disabled", wrap="word")


    def create_filter_text_image_pairs_widgets_tab4(self):
        self.tab4_frame = Frame(self.tab4)
        self.tab4_frame.pack(side='top', fill='both')
        self.tab4_button_frame = Frame(self.tab4_frame)
        self.tab4_button_frame.pack(side='top', fill='x')
        self.filter_label = Label(self.tab4_button_frame, width=8, text="Filter:")
        self.filter_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.filter_label, "Enter the EXACT text you want to filter by\nThis will filter all img-txt pairs based on the provided text, see below for more info", 200, 6, 12)
        self.filter_entry = Entry(self.tab4_button_frame, width=11, textvariable=self.filter_string_var)
        self.filter_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.filter_button = Button(self.tab4_button_frame, text="Go!", overrelief="groove", width=4, command=self.filter_text_image_pairs)
        self.filter_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.filter_button, "Text files will be filtered based on the entered text", 200, 6, 12)
        self.revert_button = Button(self.tab4_button_frame, text="Clear", overrelief="groove", width=4, command=lambda: (self.revert_text_image_filter(clear=True)))
        self.revert_button.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.revert_button, "Clear any filtering applied", 200, 6, 12)
        self.filter_use_regex = BooleanVar()
        self.regex_checkbutton = Checkbutton(self.tab4_button_frame, text="Regex", overrelief="groove", variable=self.filter_use_regex)
        self.regex_checkbutton.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.regex_checkbutton, "Check this to use regular expressions for filtering", 200, 6, 12)
        self.filter_empty_files = BooleanVar()
        self.empty_files_checkbutton = Checkbutton(self.tab4_button_frame, text="Empty", overrelief="groove", variable=self.filter_empty_files, command=self.toggle_empty_files_filter)
        self.empty_files_checkbutton.pack(side='left', anchor="n", pady=4, padx=1)
        ToolTip.create(self.empty_files_checkbutton, "Check this to show only empty text files\n\nImages without a text pair are also consided as empty", 200, 6, 12)
        self.tab4_text_frame = Frame(self.tab4_frame, borderwidth=0)
        self.tab4_text_frame.pack(side='top', fill="both")
        description_textbox = ScrolledText(self.tab4_text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0", "This tool will filter all img-txt pairs based on the provided text.\n\n"
                                   "Enter any string of text to display only img-txt pairs containing that text.\n"
                                   "Use ' + ' to include multiple strings when filtering.\n"
                                   "Use '!' before the text to exclude any pairs containing that text.\n\n"
                                   "Examples:\n"
                                   "'dog' (shows only pairs containing the text dog)\n"
                                   "'!dog' (removes all pairs containing the text dog)\n"
                                   "'!dog + cat' (remove dog pairs, display cat pairs)")
        description_textbox.config(state="disabled", wrap="word")


    def create_custom_active_highlight_widgets_tab5(self):
        def clear():
            self.custom_entry.delete(0, 'end')
        self.tab5_frame = Frame(self.tab5)
        self.tab5_frame.pack(side='top', fill='both')
        self.tab5_button_frame = Frame(self.tab5_frame)
        self.tab5_button_frame.pack(side='top', fill='x')
        self.custom_label = Label(self.tab5_button_frame, width=8, text="Highlight:")
        self.custom_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.custom_label, "Enter the text you want to highlight\nUse ' + ' to highlight multiple strings of text\n\nExample: dog + cat", 200, 6, 12)
        self.custom_entry = Entry(self.tab5_button_frame, textvariable=self.custom_highlight_string_var)
        self.custom_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.custom_entry.bind('<KeyRelease>', lambda event: self.highlight_custom_string())
        self.highlight_button = Button(self.tab5_button_frame, text="Go!", overrelief="groove", width=4, command=self.highlight_custom_string)
        self.highlight_button.pack(side='left', anchor="n", pady=4, padx=1)
        self.clear_button = Button(self.tab5_button_frame, text="Clear", overrelief="groove", width=4, command=clear)
        self.clear_button.pack(side='left', anchor="n", pady=4, padx=1)
        self.tab5_text_frame = Frame(self.tab5_frame, borderwidth=0)
        self.tab5_text_frame.pack(side='top', fill="both")
        description_textbox = ScrolledText(self.tab5_text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0", "Enter the text you want to highlight each time you move to a new img-txt pair.\n\n"
                                   "Use ' + ' to highlight multiple strings of text\n\n"
                                   "Example: dog + cat")
        description_textbox.config(state="disabled", wrap="word")


    def create_font_widgets_tab6(self, event=None):
        def set_font_and_size(font, size):
            if font and size:
                size = int(size)
                self.text_box.config(font=(font, size))
                font_size.config(text=f"Size: {size}")
        def reset_to_defaults():
            self.font_var.set(default_font)
            self.size_scale.set(default_size)
            set_font_and_size(default_font, default_size)
        current_font = self.text_box.cget("font")
        current_font_name = self.text_box.tk.call("font", "actual", current_font, "-family")
        current_font_size = self.text_box.tk.call("font", "actual", current_font, "-size")
        default_font = current_font_name
        default_size = current_font_size
        font_label = Label(self.tab6, width=8, text="Font:")
        font_label.pack(side="left", anchor="n", pady=4)
        ToolTip.create(font_label, "Recommended Fonts: Courier New, Ariel, Consolas, Segoe UI", 200, 6, 12)
        font_box = ttk.Combobox(self.tab6, textvariable=self.font_var, width=4, takefocus=False, state="readonly", values=list(tkinter.font.families()))
        font_box.set(current_font_name)
        font_box.bind("<<ComboboxSelected>>", lambda event: set_font_and_size(self.font_var.get(), self.size_scale.get()))
        font_box.pack(side="left", anchor="n", pady=4, fill="x", expand=True)
        font_size = Label(self.tab6, text=f"Size: {self.font_size_var}", width=14)
        font_size.pack(side="left", anchor="n", pady=4)
        ToolTip.create(font_size, "Default size: 10", 200, 6, 12)
        self.size_scale = ttk.Scale(self.tab6, from_=6, to=24, variable=self.font_size_var, takefocus=False)
        self.size_scale.set(current_font_size)
        self.size_scale.bind("<B1-Motion>", lambda event: set_font_and_size(self.font_var.get(), self.size_scale.get()))
        self.size_scale.pack(side="left", anchor="n", pady=4, fill="x", expand=True)
        reset_button = Button(self.tab6, text="Reset", overrelief="groove", width=4, command=reset_to_defaults)
        reset_button.pack(side="left", anchor="n", pady=4, padx=1)


    def create_custom_dictionary_widgets_tab7(self):
        def save_content():
            with open('my_tags.csv', 'w') as file:
                file.write(self.custom_dictionary_textbox.get("1.0", "end-1c"))
                self.update_autocomplete_dictionary()
        def refresh_content():
            with open('my_tags.csv', 'r') as file:
                content = file.read()
                self.custom_dictionary_textbox.delete("1.0", 'end')
                self.custom_dictionary_textbox.insert('end', content)
                self.update_autocomplete_dictionary()
        self.create_custom_dictionary()
        self.tab7_frame = Frame(self.tab7)
        self.tab7_frame.pack(side='top', fill='both')
        self.tab7_button_frame = Frame(self.tab7_frame)
        self.tab7_button_frame.pack(side='top', fill='x', pady=4)
        self.save_dictionary_button = Button(self.tab7_button_frame, text="Save", overrelief="groove", takefocus=False, command=save_content)
        ToolTip.create(self.save_dictionary_button, "Save the current changes to the 'my_tags.csv' file", 200, 6, 12)
        self.save_dictionary_button.pack(side='left', padx=1, fill='x', expand=True)
        self.tab7_label = Label(self.tab7_button_frame, text="^^^Expand this frame to view the text box^^^")
        self.tab7_label.pack(side='left')
        ToolTip.create(self.tab7_label, "Click and drag the gray bar up to reveal the text box", 200, 6, 12)
        self.refresh_button = Button(self.tab7_button_frame, text="Refresh", overrelief="groove", takefocus=False, command=refresh_content)
        ToolTip.create(self.refresh_button, "Refresh the suggestion dictionary after saving your changes", 200, 6, 12)
        self.refresh_button.pack(side='left', padx=1, fill='x', expand=True)
        self.custom_dictionary_textbox = ScrolledText(self.tab7_frame, wrap="word")
        self.custom_dictionary_textbox.pack(side='bottom', fill='both')
        with open('my_tags.csv', 'r') as file:
            content = file.read()
            self.custom_dictionary_textbox.insert('end', content)
        self.custom_dictionary_textbox.configure(undo=True)


    def set_text_box_binds(self):
        # Mouse binds
        self.text_box.bind("<Button-1>", lambda event: (self.remove_tag(), self.clear_suggestions()))
        self.text_box.bind("<Button-2>", lambda event: (self.delete_tag_under_mouse(event), self.change_message_label()))
        self.text_box.bind("<Button-3>", lambda event: (self.show_textContext_menu(event)))
        # Update the autocomplete suggestion label after every KeyRelease event.
        self.text_box.bind("<KeyRelease>", lambda event: (self.update_suggestions(event), self.change_message_label()))
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
        self.text_box.bind("<BackSpace>", lambda event: (self.remove_highlight(), self.change_message_label()))
        # Sets the "message_label" whenver a key is pressed.
        self.text_box.bind("<Key>", lambda event: self.change_message_label())
        # Disable normal button behavior
        self.text_box.bind("<Tab>", self.disable_button)
        self.text_box.bind("<Alt_L>", self.disable_button)
        self.text_box.bind("<Alt_R>", self.disable_button)
        # Show next empty text file
        self.text_box.bind("<Control-e>", self.index_goto_next_empty)
        # Show random img-txt pair
        self.text_box.bind("<Control-r>", self.index_goto_random)
        # Refresh text box
        self.text_box.bind("<F5>", lambda event: self.refresh_text_box())


    # Text context menu
    def show_textContext_menu(self, event):
        widget_in_focus = root.focus_get()
        textContext_menu = Menu(root, tearoff=0)
        if widget_in_focus in [self.info_text, getattr(self, 'text_box', None)]:
            widget_in_focus.focus_set()
            if widget_in_focus == getattr(self, 'text_box', None):
                select_state = "disabled"
                cleaning_state = "normal" if self.cleaning_text_var.get() else "disabled"
                try:
                    selected_text = self.text_box.get("sel.first", "sel.last")
                    if len(selected_text) >= 3:
                        select_state = "normal"
                except TclError:
                    pass
                textContext_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: (widget_in_focus.event_generate('<<Cut>>'), self.change_message_label()))
                textContext_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: (widget_in_focus.event_generate('<<Paste>>'), self.change_message_label()))
                textContext_menu.add_command(label="Delete", accelerator="Del", command=lambda: (widget_in_focus.event_generate('<<Clear>>'), self.change_message_label()))
                textContext_menu.add_command(label="Refresh", accelerator="F5", command=self.refresh_text_box)
                textContext_menu.add_separator()
                textContext_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: (widget_in_focus.event_generate('<<Undo>>'), self.change_message_label()))
                textContext_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: (widget_in_focus.event_generate('<<Redo>>'), self.change_message_label()))
                textContext_menu.add_separator()
                textContext_menu.add_command(label="Open Text Directory...", command=self.open_current_directory)
                textContext_menu.add_command(label="Add Selected Text to My Tags", state=select_state, command=self.add_to_custom_dictionary)
                textContext_menu.add_separator()
                textContext_menu.add_command(label="Highlight all Duplicates", accelerator="Ctrl+F", command=self.highlight_all_duplicates)
                textContext_menu.add_command(label="Next Empty Text File", accelerator="Ctrl+E", command=self.index_goto_next_empty)
                textContext_menu.add_separator()
                textContext_menu.add_checkbutton(label="Highlight Selection", variable=self.highlight_selection_var)
                textContext_menu.add_checkbutton(label="Clean Text on Save", variable=self.cleaning_text_var, command=self.toggle_list_menu)
                textContext_menu.add_checkbutton(label="List View", variable=self.list_mode_var, state=cleaning_state, command=self.toggle_list_mode)
            elif widget_in_focus == self.info_text:
                textContext_menu.add_command(label="Copy", command=lambda: widget_in_focus.event_generate('<<Copy>>'))
            textContext_menu.tk_popup(event.x_root, event.y_root)


    # Image context menu
    def show_imageContext_menu(self, event):
        imageContext_menu = Menu(self.master, tearoff=0)
        # Open
        imageContext_menu.add_command(label="Open Current Directory...", command=self.open_current_directory)
        imageContext_menu.add_command(label="Open Current Image...", command=self.open_current_image)
        imageContext_menu.add_command(label="Open Image Grid...", accelerator="F2", command=self.view_image_grid)
        imageContext_menu.add_separator()
        # File
        imageContext_menu.add_command(label="Duplicate img-txt pair", command=self.duplicate_pair)
        imageContext_menu.add_command(label="Delete img-txt Pair", accelerator="Shift+Del", command=self.delete_pair)
        imageContext_menu.add_command(label="Undo Delete", command=self.undo_delete_pair, state=self.undo_state.get())
        imageContext_menu.add_separator()
        # Edit
        imageContext_menu.add_command(label="Upscale...", command=self.upscale_image)
        imageContext_menu.add_command(label="Resize...", command=self.resize_image)
        if not self.image_file.lower().endswith('.gif'):
            imageContext_menu.add_command(label="Crop...", command=self.open_crop_tool)
            imageContext_menu.add_command(label="Expand", command=self.expand_image)
        else:
            imageContext_menu.add_command(label="Crop...", state="disabled", command=self.open_crop_tool)
            imageContext_menu.add_command(label="Expand", state="disabled", command=self.expand_image)
        imageContext_menu.add_command(label="Rotate", command=self.rotate_current_image)
        imageContext_menu.add_command(label="Flip", command=self.flip_current_image)
        imageContext_menu.add_separator()
        # Misc
        imageContext_menu.add_checkbutton(label="Toggle Zoom", accelerator="F1", command=self.toggle_zoom_popup, variable=self.toggle_zoom_var)
        imageContext_menu.add_checkbutton(label="Vertical View", command=self.swap_pane_orientation)
        imageContext_menu.add_checkbutton(label="Swap img-txt Sides", command=self.swap_pane_sides)
        # Image Display Quality
        image_quality_menu = Menu(self.optionsMenu, tearoff=0)
        imageContext_menu.add_cascade(label="Image Display Quality", menu=image_quality_menu)
        for value in ["High", "Normal", "Low"]:
            image_quality_menu.add_radiobutton(label=value, variable=self.image_qualtiy_var, value=value, command=self.set_image_quality)
        imageContext_menu.tk_popup(event.x_root, event.y_root)


    # Suggestion context menu
    def show_suggestionContext_menu(self, event):
        suggestionContext_menu = Menu(self.master, tearoff=0)
        # Selected Dictionary
        dictionaryMenu = Menu(suggestionContext_menu, tearoff=0)
        suggestionContext_menu.add_cascade(label="Suggestion Dictionary", menu=dictionaryMenu)
        dictionaryMenu.add_checkbutton(label="English Dictionary", underline=0, variable=self.csv_english_dictionary, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Danbooru", underline=0, variable=self.csv_danbooru, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Derpibooru", underline=0, variable=self.csv_derpibooru, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="e621", underline=0, variable=self.csv_e621, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_separator()
        dictionaryMenu.add_command(label="Clear Selection", underline=0, command=self.clear_dictionary_csv_selection)
        # Suggestion Threshold
        suggestion_threshold_menu = Menu(suggestionContext_menu, tearoff=0)
        suggestionContext_menu.add_cascade(label="Suggestion Threshold", menu=suggestion_threshold_menu)
        threshold_levels = ["Slow", "Normal", "Fast", "Faster"]
        for level in threshold_levels:
            suggestion_threshold_menu.add_radiobutton(label=level, variable=self.suggestion_threshold_var, value=level, command=self.set_suggestion_threshold)
        # Suggestion Quantity
        suggestion_quantity_menu = Menu(suggestionContext_menu, tearoff=0)
        suggestionContext_menu.add_cascade(label="Suggestion Quantity", menu=suggestion_quantity_menu)
        for quantity in range(0, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(quantity), variable=self.suggestion_quantity_var, value=quantity, command=lambda suggestion_quantity=quantity: self.set_suggestion_quantity(suggestion_quantity))
        # Match Mode
        match_mode_menu = Menu(suggestionContext_menu, tearoff=0)
        suggestionContext_menu.add_cascade(label="Match Mode", menu=match_mode_menu)
        match_modes = {"Match Whole String": False, "Match Last Word": True}
        for mode, value in match_modes.items():
            match_mode_menu.add_radiobutton(label=mode, variable=self.last_word_match_var, value=value)
        suggestionContext_menu.tk_popup(event.x_root, event.y_root)


#endregion
################################################################################################################################################
#region -  Additional Interface Setup


####### Browse button context menu ##################################################


    def open_browse_context_menu(self, event):
        try:
            self.browse_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.browse_context_menu.grab_release()


    def set_text_file_path(self, path=None):
        if path == None:
            self.new_text_path = askdirectory()
        else:
            self.new_text_path = path
        if not self.new_text_path:
            return
        self.text_files = []
        for image_file in self.image_files:
            text_filename = os.path.splitext(os.path.basename(image_file))[0] + ".txt"
            text_file_path = os.path.join(self.new_text_path, text_filename)
            if not os.path.exists(text_file_path):
                self.new_text_files.append(text_filename)
            self.text_files.append(text_file_path)
        self.show_pair()
        self.update_text_path_indicator()


    def update_text_path_indicator(self):
        if os.path.normpath(self.new_text_path) != os.path.normpath(self.image_dir.get()):
            self.text_path_indicator.config(bg="#5da9be")
            self.text_path_tooltip.config(f"Text Path: {os.path.normpath(self.new_text_path)}", 10, 6, 12)
        else:
            self.text_path_indicator.config(bg="#f0f0f0")
            self.text_path_tooltip.config("Text Path: Same as image path", 10, 6, 12)



####### Directory entry context menu ##################################################


    def open_directory_context_menu(self, event):
        try:
            self.dir_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.dir_context_menu.grab_release()


    def directory_copy(self):
        try:
            selected_text = self.directory_entry.selection_get()
            self.directory_entry.clipboard_clear()
            self.directory_entry.clipboard_append(selected_text)
        except TclError: pass


    def directory_cut(self):
        try:
            selected_text = self.directory_entry.selection_get()
            self.directory_entry.clipboard_clear()
            self.directory_entry.clipboard_append(selected_text)
            start = self.directory_entry.index("sel_first")
            end = self.directory_entry.index("sel_last")
            self.directory_entry.delete(start, end)
        except TclError: pass


    def directory_paste(self):
        try:
            self.directory_entry.insert("insert", self.directory_entry.clipboard_get())
        except TclError: pass


    def directory_delete(self):
        try:
            start = self.directory_entry.index("sel_first")
            end = self.directory_entry.index("sel_last")
            self.directory_entry.delete(start, end)
        except TclError: pass


    def directory_clear(self):
        self.directory_entry.delete(0, "end")


    def clear_directory_entry_on_click(self, event):
        if self.directory_entry.get() == "Choose Directory...":
            self.directory_entry.delete(0, "end")


####### Index entry context menu ##################################################


    def open_index_context_menu(self, event):
        try:
            self.index_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.index_context_menu.grab_release()


    def index_goto_first(self):
        self.image_index_entry.delete(0, "end")
        self.image_index_entry.insert(0, 1)
        self.jump_to_image(index=0)


    def index_goto_random(self, event=None):
        total_images = len(self.text_files)
        random_index = self.current_index
        while random_index == self.current_index:
            random_index = numpy.random.randint(total_images)
        self.image_index_entry.delete(0, "end")
        self.image_index_entry.insert(0, random_index + 1)
        self.jump_to_image(random_index)


    def index_goto_next_empty(self, event=None):
            next_empty = self.get_next_empty_file_index()
            if next_empty is not None:
                self.image_index_entry.delete(0, "end")
                self.image_index_entry.insert(0, next_empty + 1)
                self.jump_to_image(next_empty)


    def get_next_empty_file_index(self):
        start_index = (self.current_index + 1) % len(self.text_files)
        for i in range(len(self.text_files)):
            index = (start_index + i) % len(self.text_files)
            text_file = self.text_files[index]
            try:
                with open(text_file, 'r', encoding="utf-8") as file:
                    if file.read().strip() == "":
                        return index
            except FileNotFoundError:
                return index
        return None


####### Misc setup ##################################################


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
        tool_commands =       [
                             "Open Current Directory...",
                             "Open Current Image...",
                             "Open Image Grid...",
                             "Next Empty Text File",
                             "Cleanup all Text Files",
                             "Delete img-txt Pair",
                             "Batch Crop Images...",
                             "Rename img-txt Pairs...",
                             "Rename and Convert img-txt Pairs...",
                             "Upscale...",
                             "Crop...",
                             "Resize...",
                             "Expand",
                             "Rotate",
                             "Flip",
                             "Duplicate img-txt pair"
                             ]
        options_commands =   [
                              "Suggestion Dictionary",
                              "Suggestion Threshold",
                              "Suggestion Quantity",
                              "Image Display Quality",
                              "Highlight Selection",
                              "Cleaning Text on Save",
                              "Colored Suggestions",
                              "Big Save Button",
                              "List View",
                              "Vertical View",
                              "Swap img-txt Sides"
                              ]
        for t_command in tool_commands:
            self.toolsMenu.entryconfig(t_command, state="normal")
        for o_command in options_commands:
            self.optionsMenu.entryconfig(o_command, state="normal")
        self.browse_context_menu.entryconfig("Set Text File Path...", state="normal")
        self.browse_context_menu.entryconfig("Clear Text File Path", state="normal")
        self.index_pair_label.configure(state="normal")
        self.image_index_entry.configure(state="normal")
        self.total_images_label.configure(state="normal")
        self.message_label.configure(state="normal")
        self.save_button.configure(state="normal")
        self.next_button.configure(state="normal")
        self.prev_button.configure(state="normal")
        self.auto_save_checkbutton.configure(state="normal")
        # Bindings
        self.suggestion_textbox.bind("<Button-3>", self.show_suggestionContext_menu)
        self.image_index_entry.bind("<Button-3>", self.open_index_context_menu)


    def toggle_save_button_height(self, event=None):
        current_height = self.save_button.cget('height')
        if current_height == 2:
            self.big_save_button_var.set(False)
            new_height = 1
        else:
            self.big_save_button_var.set(True)
            new_height = 2
        self.save_button.config(height=new_height)


    def toggle_zoom_popup(self, event=None):
        new_state = not self.popup_zoom.zoom_enabled.get()
        self.popup_zoom.zoom_enabled.set(new_state)
        self.toggle_zoom_var.set(new_state)
        state, text = ("disabled", "") if new_state else ("normal", "Double-Click to open in system image viewer \n\nMiddle click to open in file explorer\n\nALT+Left/Right or Mouse-Wheel to move between img-txt pairs")
        self.image_preview_tooltip.config(state=state, text=text)
        if new_state:
            self.popup_zoom.update_zoom(event)
        else:
            self.popup_zoom.hide_zoom(event)



####### PanedWindow ##################################################


    def configure_pane_position(self):
        window_width = self.master.winfo_width()
        self.primary_paned_window.sash_place(0, window_width // 2, 0)
        self.configure_pane()


    def swap_pane_sides(self):
        self.primary_paned_window.remove(self.master_image_frame)
        self.primary_paned_window.remove(self.master_control_frame)
        if not self.panes_swapped_var:
            self.primary_paned_window.add(self.master_control_frame)
            self.primary_paned_window.add(self.master_image_frame)
        else:
            self.primary_paned_window.add(self.master_image_frame)
            self.primary_paned_window.add(self.master_control_frame)
        self.master.after_idle(self.configure_pane_position)
        self.configure_pane()
        self.panes_swapped_var = not self.panes_swapped_var


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
#region -  Autocomplete


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
        if self.last_word_match_var.get():
            words = text.split()
            current_word = words[-1] if words else ''
        else:
            if self.list_mode_var.get():
                elements = [element.strip() for element in text.split('\n')]
            else:
                elements = [element.strip() for element in text.split(',')]
            current_word = elements[-1]
        current_word = current_word.strip()
        if current_word and len(self.selected_csv_files) >= 1:
            suggestions = self.autocomplete.get_suggestion(current_word)
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
            classifier_id = classifier_id[0]
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
        if self.list_mode_var.get():
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
        if self.last_word_match_var.get():
            words = text.split()
            current_word = words[-1] if words else ''
        else:
            elements = [element.strip() for element in text.split('\n' if self.list_mode_var.get() else ',')]
            current_word = elements[-1]
        remaining_text = self.text_box.get("insert", "end").rstrip('\n')
        start_of_current_word = "1.0 + {} chars".format(len(text) - len(current_word))
        self.text_box.delete(start_of_current_word, "insert")
        if not remaining_text.startswith(('\n' if self.list_mode_var.get() else ',')) and not self.last_word_match_var.get():
            self.text_box.insert(start_of_current_word, selected_suggestion + ('\n' if self.list_mode_var.get() else ','))
        else:
            self.text_box.insert(start_of_current_word, selected_suggestion)
        if self.list_mode_var.get() and remaining_text:
            self.insert_newline_listmode(called_from_insert=True)
            self.text_box.mark_set("insert", "insert + 1 lines")


    def position_cursor(self, start_of_current_word, selected_suggestion):
        if self.text_box.get(start_of_current_word).startswith(' '):
            offset = len(selected_suggestion) + 2
        else:
            offset = len(selected_suggestion) + 1
        self.text_box.mark_set("insert", "{}+{}c".format(start_of_current_word, offset))
        self.text_box.insert("insert", " ")


    def insert_newline_listmode(self, event=None, called_from_insert=False):
        if self.list_mode_var.get():
            self.text_box.insert("insert", '\n')
            if called_from_insert and self.text_box.index("insert") != self.text_box.index("end-1c"):
                self.text_box.mark_set("insert", "insert-1l")
            return 'break'


### Suggestion Settings ##################################################


    def update_autocomplete_dictionary(self):
        csv_vars = {
            'danbooru.csv': self.csv_danbooru,
            'e621.csv': self.csv_e621,
            'dictionary.csv': self.csv_english_dictionary,
            'derpibooru.csv': self.csv_derpibooru
        }
        self.selected_csv_files = [csv_file for csv_file, var in csv_vars.items() if var.get()]
        if not self.selected_csv_files:
            self.autocomplete = Autocomplete("None")
        else:
            self.autocomplete = Autocomplete(self.selected_csv_files[0])
            for csv_file in self.selected_csv_files[1:]:
                self.autocomplete.data.update(Autocomplete(csv_file).data)
        self.clear_suggestions()
        self.set_suggestion_color(self.selected_csv_files[0] if self.selected_csv_files else "None")
        self.set_suggestion_threshold()


    def set_suggestion_color(self, csv_file):
        color_mappings = {
            'None':             {0: "black"},
            'dictionary.csv':   {0: "black",    1: "black",     2: "black",     3: "black",     4: "black",     5: "black",     6: "black",     7: "black",     8: "black"},
            'danbooru.csv':     {0: "black",    1: "#c00004",   2: "black",     3: "#a800aa",   4: "#00ab2c",   5: "#fd9200"},
            'e621.csv':         {-1: "black",   0: "black",     1: "#f2ac08",   3: "#dd00dd",   4: "#00aa00",   5: "#ed5d1f",   6: "#ff3d3d",   7: "#ff3d3d",   8: "#228822"},
            'derpibooru.csv':   {0: "black",    1: "#e5b021",   3: "#fd9961",   4: "#cf5bbe",   5: "#3c8ad9",   6: "#a6a6a6",   7: "#47abc1",   8: "#7871d0",   9: "#df3647",   10: "#c98f2b",  11: "#e87ebe"}
            }
        black_mappings = {key: "black" for key in color_mappings[csv_file].keys()}
        self.suggestion_colors = color_mappings[csv_file] if self.colored_suggestion_var.get() else black_mappings


    def set_suggestion_quantity(self, suggestion_quantity):
        self.autocomplete.max_suggestions = suggestion_quantity
        self.update_suggestions(event=None)


    def set_suggestion_threshold(self):
        thresholds = {
            "Slow"  : 275000,
            "Normal": 130000,
            "Fast"  : 75000,
            "Faster": 40000
            }
        self.autocomplete.suggestion_threshold = thresholds.get(self.suggestion_threshold_var.get())


    def clear_dictionary_csv_selection(self):
        for attr in ['csv_danbooru', 'csv_derpibooru', 'csv_e621', 'csv_english_dictionary']:
            getattr(self, attr).set(False)
        self.update_autocomplete_dictionary()


    def get_tags_with_underscore(self):
        return {"0_0", "(o)_(o)", "o_o", ">_o", "u_u", "x_x", "|_|", "||_||", "._.", "^_^", ">_<", "@_@", ">_@", "+_+", "+_-", "=_=", "<o>_<o>", "<|>_<|>", "ಠ_ಠ", "3_3", "6_9"}


#endregion
################################################################################################################################################
#region -  TextBox Highlights


    def highlight_duplicates(self, event, mouse=True):
        if not self.highlight_selection_var.get():
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
        self.highlight_all_duplicates_var.set(not self.highlight_all_duplicates_var.get())
        if self.highlight_all_duplicates_var.get():
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
        numpy.random.shuffle(pastel_colors)
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


    def highlight_custom_string(self):
        self.text_box.tag_remove("highlight", "1.0", "end")
        if not self.custom_highlight_string_var.get():
            return
        words = self.custom_highlight_string_var.get().split('+')
        for word in words:
            pattern = re.escape(word.strip())
            matches = [match for match in re.finditer(pattern, self.text_box.get("1.0", "end"))]
            if matches:
                for match in matches:
                    start = match.start()
                    end = match.end()
                    self.text_box.tag_add("highlight", f"1.0 + {start} chars", f"1.0 + {end} chars")


    def remove_highlight(self):
        self.text_box.tag_remove("highlight", "1.0", "end")
        self.master.after(100, lambda: self.remove_tag())


    def remove_tag(self):
        self.highlight_all_duplicates_var.set(False)
        for tag in self.text_box.tag_names():
            self.text_box.tag_remove(tag, "1.0", "end")


#endregion
################################################################################################################################################
#region -  Primary Functions


    def load_pairs(self):
        self.info_text.pack_forget()
        self.image_files = []
        self.text_files = []
        self.new_text_files = []
        files_in_dir = sorted(os.listdir(self.image_dir.get()), key=self.natural_sort)
        self.validate_files(files_in_dir)
        self.original_image_files = list(self.image_files)
        self.original_text_files = list(self.text_files)
        self.message_label.config(text="No Change", bg="#f0f0f0", fg="black")
        self.enable_menu_options()
        self.create_text_box()
        self.update_pair(save=False)
        self.configure_pane_position()
        if hasattr(self, 'total_images_label'):
            self.total_images_label.config(text=f"of {len(self.image_files)}")
        self.prev_num_files = len(files_in_dir)


    def validate_files(self, files_in_dir):
        odd_files_exist = any(self.check_odd_files(filename) for filename in files_in_dir)
        if odd_files_exist and messagebox.askyesno("Confirmation", ".jfif, or .jpg_large files detected.\n\nIt's recommended to convert these files to .jpg for compatibility.\n\nDo you want to proceed?"):
            for filename in files_in_dir:
                if self.check_odd_files(filename):
                    self.rename_odd_files(filename)
        for filename in files_in_dir:
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")):
                image_file_path = os.path.join(self.image_dir.get(), filename)
                self.image_files.append(image_file_path)
                text_filename = os.path.splitext(filename)[0] + ".txt"
                text_file_path = os.path.join(self.image_dir.get(), text_filename)
                if not os.path.exists(text_file_path):
                    self.new_text_files.append(filename)
                self.text_files.append(text_file_path)


    def load_text_file(self, text_file):
        self.text_box.config(undo=False)
        self.text_box.delete("1.0", "end")
        if text_file and os.path.isfile(text_file):
            with open(text_file, "r", encoding="utf-8") as f:
                self.text_box.insert("end", f.read())
        self.text_modified_var = False
        self.text_box.config(undo=True)


    def load_image_file(self, image_file, text_file):
        try:
            with Image.open(self.image_file) as image_file:
                self.original_image_size = image_file.size
                max_size = (self.quality_max_size, self.quality_max_size)
                image_file.thumbnail(max_size, Image.NEAREST)
                if image_file.format == 'GIF':
                    self.gif_frames = [frame.copy() for frame in ImageSequence.Iterator(image_file)]
                    self.frame_durations = [frame.info['duration'] for frame in ImageSequence.Iterator(image_file)]
                else:
                    self.gif_frames = [image_file.copy()]
                    self.frame_durations = [None]
        except (FileNotFoundError, UnidentifiedImageError):
            self.update_image_file_count()
            self.image_files.remove(self.image_file)
            if text_file in self.text_files:
                self.text_files.remove(text_file)
            return
        return image_file


    def display_image(self):
        try:
            self.image_file = self.image_files[self.current_index]
            text_file = self.text_files[self.current_index] if self.current_index < len(self.text_files) else None
            image = self.load_image_file(self.image_file, text_file)
            max_img_width = 1280
            max_img_height = 1280
            resize_event = Event()
            resize_event.height = self.image_preview.winfo_height()
            resize_event.width = self.image_preview.winfo_width()
            resized_image, resized_width, resized_height = self.resize_and_scale_image(image, max_img_width, max_img_height, resize_event)
            if image.format == 'GIF':
                self.frame_iterator = iter(self.gif_frames)
                self.current_frame_index = 0
                self.display_animated_gif()
            else:
                self.frame_iterator = None
                self.current_frame_index = 0
            self.popup_zoom.set_image(image=image, path=self.image_file)
            self.popup_zoom.set_resized_image(resized_image, resized_width, resized_height)
            return text_file, image, max_img_height, max_img_width
        except ValueError:
            self.check_image_dir()


    def display_animated_gif(self):
        if self.animation_job is not None:
            root.after_cancel(self.animation_job)
            self.animation_job = None
        if self.frame_iterator is not None:
            try:
                self.current_frame = next(self.frame_iterator)
                start_width, start_height = self.current_frame.size
                scale_factor = min(self.image_preview.winfo_width() / start_width, self.image_preview.winfo_height() / start_height)
                new_width = int(start_width * scale_factor)
                new_height = int(start_height * scale_factor)
                cache_key = (id(self.current_frame), self.current_frame_index, new_width, new_height)
                if cache_key not in self.gif_frame_cache:
                    self.current_frame = self.current_frame.convert("RGBA")
                    self.current_frame = self.current_frame.resize((new_width, new_height), Image.LANCZOS)
                    self.gif_frame_cache[cache_key] = self.current_frame
                else:
                    self.current_frame = self.gif_frame_cache[cache_key]
                self.current_gif_frame_image = ImageTk.PhotoImage(self.current_frame)
                self.image_preview.config(image=self.current_gif_frame_image)
                self.image_preview.image = self.current_gif_frame_image
                delay = self.frame_durations[self.current_frame_index] if self.frame_durations[self.current_frame_index] else 100
                self.animation_job = root.after(delay, self.display_animated_gif)
                self.current_frame_index = (self.current_frame_index + 1) % len(self.gif_frames)
            except StopIteration:
                self.frame_iterator = iter(self.gif_frames)
                self.current_frame_index = 0
                self.display_animated_gif()


    def resize_and_scale_image(self, input_image, max_img_width, max_img_height, event, quality_filter=Image.LANCZOS):
        if input_image is None:
            return None, None, None
        start_width, start_height = self.original_image_size
        scale_factor = min(event.width / start_width, event.height / start_height)
        new_width = min(int(start_width * scale_factor), max_img_width)
        new_height = min(int(start_height * scale_factor), max_img_height)
        resized_image = input_image.resize((new_width, new_height), quality_filter)
        output_image = ImageTk.PhotoImage(resized_image)
        self.image_preview.config(image=output_image)
        self.image_preview.image = output_image
        percent_scale = int((new_width / start_width) * 100)
        self.update_imageinfo(percent_scale)
        return resized_image, new_width, new_height


    def show_pair(self):
        if self.image_files:
            text_file, image, max_img_height, max_img_width = self.display_image()
            self.load_text_file(text_file)
            self.image_preview.config(width=max_img_width, height=max_img_height)
            self.image_preview.bind("<Configure>", lambda event: self.resize_and_scale_image(image, max_img_width, max_img_height, event, Image.NEAREST))
            self.toggle_list_mode()
            self.clear_suggestions()
            self.highlight_custom_string()
            self.highlight_all_duplicates_var.set(False)


    def refresh_image(self):
        if self.image_files:
            self.display_image()


    def on_resize(self, event): # Window resize
        if hasattr(self, 'text_box'):
            if self.is_resizing_id:
                root.after_cancel(self.is_resizing_id)
            self.is_resizing_id = root.after(100, self.refresh_image)


    def update_imageinfo(self, percent_scale):
        if self.image_files:
            self.image_file = self.image_files[self.current_index]
            image_info = self.get_image_info(self.image_file)
            self.image_label.config(text=f"{image_info['filename']}  |  {image_info['resolution']}  |  {percent_scale}%  |  {image_info['size']}", anchor="w")


    def get_image_info(self, image_file):
        image = Image.open(image_file)
        width, height = image.size
        size = os.path.getsize(image_file)
        size_kb = size / 1024
        size_str = f"{round(size_kb)} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 2)} MB"
        filename = os.path.basename(image_file)
        filename = (filename[:61] + '(...)') if len(filename) > 64 else filename
        return {
            "filename": filename,
            "resolution": f"{width} x {height}",
            "size": size_str
        }


#endregion
################################################################################################################################################
#region -  Navigation


    def update_pair(self, direction=None, save=True):
        if self.image_dir.get() == "Choose Directory..." or len(self.image_files) == 0:
            return
        self.is_alt_arrow_pressed = True
        self.check_image_dir()
        if not self.text_modified_var:
            self.message_label.config(text="No Change", bg="#f0f0f0", fg="black")
        self.text_box.config(undo=False)
        self.text_box.edit_reset()
        if self.auto_save_var.get() and save:
            self.save_text_file()
        if direction == 'next':
            self.current_index = (self.current_index + 1) % len(self.image_files)
        elif direction == 'prev':
            self.current_index = (self.current_index - 1) % len(self.image_files)
        self.show_pair()
        self.image_index_entry.delete(0, "end")
        self.image_index_entry.insert(0, f"{self.current_index + 1}")


    def next_pair(self, event):
        self.check_working_directory()
        self.update_pair('next')


    def prev_pair(self, event):
        self.check_working_directory()
        self.update_pair('prev')


    def jump_to_image(self, index=None, event=None):
        try:
            self.check_working_directory()
            if isinstance(index, Event):
                index = None
            if index is None:
                index = int(self.image_index_entry.get()) - 1
            if index < 0:
                index = 0
            elif index >= len(self.image_files):
                index = len(self.image_files) - 1
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index = index
            self.show_pair()
            if not self.text_modified_var:
                self.message_label.config(text="No Change", bg="#f0f0f0", fg="black")
            self.image_index_entry.delete(0, "end")
            self.image_index_entry.insert(0, index + 1)
        except ValueError: pass


    def check_image_dir(self):
        try:
            num_files_in_dir = len(os.listdir(self.image_dir.get()))
        except Exception:
            return
        if num_files_in_dir != self.prev_num_files:
            self.update_image_file_count()
            self.prev_num_files = num_files_in_dir


    def update_image_file_count(self):
        extensions = ['.jpg', '.jpeg', '.jpg_large', '.jfif', '.png', '.webp', '.bmp', '.gif']
        self.image_files = [file for ext in extensions for file in glob.glob(f"{self.image_dir.get()}/*{ext}")]
        self.image_files.sort(key=self.natural_sort)
        self.text_files = [os.path.splitext(file)[0] + '.txt' for file in self.image_files]
        self.total_images_label.config(text=f"of {len(self.image_files)}")


    def mouse_scroll(self, event):
        if self.popup_zoom.zoom_enabled.get():
            return
        current_time = time.time()
        scroll_delay = 0.05
        if current_time - self.last_scroll_time < scroll_delay:
            return
        self.last_scroll_time = current_time
        if event.delta > 0:
            self.next_pair(event)
        else:
            self.prev_pair(event)


#endregion
################################################################################################################################################
#region -  Text Options


    def refresh_text_box(self):
        self.check_working_directory()
        if not self.check_if_contains_images(self.image_dir.get()):
            return
        text_file = self.text_files[self.current_index]
        self.text_box.delete("1.0", "end")
        if text_file and os.path.isfile(text_file):
            with open(text_file, "r", encoding="utf-8") as f:
                self.text_box.insert("end", f.read())
        self.text_modified_var = False
        self.message_label.config(text="No Change", bg="#f0f0f0", fg="black")
        self.toggle_list_mode()


    def toggle_list_mode(self, skip=False, event=None):
        self.text_box.config(undo=False)
        if self.cleaning_text_var.get() or skip:
            if self.list_mode_var.get():
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


#endregion
################################################################################################################################################
#region -  Text Tools


    def batch_tag_delete(self):
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        main_window_x = root.winfo_x() + 250 + main_window_width // 2
        main_window_y = root.winfo_y() - 300 + main_window_height // 2
        self.check_working_directory()
        directory = self.image_dir.get()
        python_script_path = "./main/bin/batch_tag_delete.py"
        if os.path.isfile(python_script_path):
            command = ["python", python_script_path, str(directory), str(main_window_x), str(main_window_y)]
        else:
            executable_path = "./batch_tag_delete.exe"
            command = [executable_path, str(directory), str(main_window_x), str(main_window_y)]
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)


    def search_and_replace(self):
        if not self.check_if_directory():
            return
        search_string = self.search_string_var.get()
        replace_string = self.replace_string_var.get()
        if not search_string:
            return
        confirm = messagebox.askokcancel("Confirmation", "This will replace all occurrences of the text\n\n{}\n\nWith\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(search_string, replace_string))
        if not confirm:
            return
        self.backup_text_files()
        if not self.filter_string_var.get():
            self.update_image_file_count()
        for text_file in self.text_files:
            try:
                with open(text_file, 'r', encoding="utf-8") as file:
                    filedata = file.read()
                filedata = filedata.replace(search_string, replace_string)
                with open(text_file, 'w', encoding="utf-8") as file:
                    file.write(filedata)
            except Exception: pass
        self.cleanup_all_text_files(show_confirmation=False)
        self.show_pair()
        self.message_label.config(text="Search & Replace Complete!", bg="#6ca079", fg="white")


    def prefix_text_files(self):
        if not self.check_if_directory():
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
        if not self.filter_string_var.get():
            self.update_image_file_count()
        for text_file in self.text_files:
            try:
                if not os.path.exists(text_file):
                    with open(text_file, 'w', encoding="utf-8") as file:
                        file.write(prefix_text)
                else:
                    with open(text_file, 'r+', encoding="utf-8") as file:
                        content = file.read()
                        file.seek(0, 0)
                        file.write(prefix_text + content)
            except Exception: pass
        self.cleanup_all_text_files(show_confirmation=False)
        self.show_pair()
        self.message_label.config(text="Prefix Text Complete!", bg="#6ca079", fg="white")


    def append_text_files(self):
        if not self.check_if_directory():
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
        if not self.filter_string_var.get():
            self.update_image_file_count()
        for text_file in self.text_files:
            try:
                if not os.path.exists(text_file):
                    with open(text_file, 'w', encoding="utf-8") as file:
                        file.write(append_text)
                else:
                    with open(text_file, 'a', encoding="utf-8") as file:
                        file.write(append_text)
            except Exception: pass
        self.cleanup_all_text_files(show_confirmation=False)
        self.show_pair()
        self.message_label.config(text="Append Text Complete!", bg="#6ca079", fg="white")


    def filter_text_image_pairs(self): # Filter
        if not self.check_if_directory():
            return
        if self.filter_empty_files.get() == False:
            self.revert_text_image_filter()
        filter_string = self.filter_string_var.get()
        if not filter_string and not self.filter_empty_files.get():
            return
        self.filtered_image_files = []
        self.filtered_text_files = []
        for image_file, text_file in zip(self.image_files, self.text_files):
            try:
                with open(text_file, 'r', encoding="utf-8") as file:
                    filedata = file.read()
                if self.filter_empty_files.get():
                    if not filedata.strip():
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
            except FileNotFoundError:
                if self.filter_empty_files.get():
                    self.filtered_image_files.append(image_file)
            except Exception: pass
        self.image_files = self.filtered_image_files
        self.text_files = self.filtered_text_files
        if hasattr(self, 'total_images_label'):
            self.total_images_label.config(text=f"of {len(self.image_files)}")
        self.current_index = 0
        self.show_pair()
        self.message_label.config(text="Filter Applied!", bg="#6ca079", fg="white")


    def revert_text_image_filter(self, clear=None): # Filter
        if clear:
            self.filter_string_var.set("")
            self.filter_use_regex = False
            self.regex_checkbutton.deselect()
        self.update_image_file_count()
        self.current_index = 0
        self.show_pair()
        self.message_label.config(text="Filter Cleared!", bg="#6ca079", fg="white")
        self.filter_empty_files.set(False)
        if self.filter_empty_files.get():
            self.toggle_filter_widgets(state=True)
        else:
            self.toggle_filter_widgets(state=False)


    def toggle_empty_files_filter(self): # Filter
        if self.filter_empty_files.get():
            self.image_index_entry.delete(0, "end")
            self.image_index_entry.insert(0, 1)
            self.filter_string_var.set("")
            self.filter_text_image_pairs()
            self.filter_use_regex = False
            self.regex_checkbutton.deselect()
            self.toggle_filter_widgets(state=True)
        else:
            self.revert_text_image_filter()
            self.toggle_filter_widgets(state=False)


    def toggle_filter_widgets(self, state): # Filter
            if state:
                for widget in [
                               self.filter_label,
                               self.filter_entry,
                               self.filter_button,
                               self.regex_checkbutton
                               ]:
                    widget.config(state="disabled")
            else:
                for widget in [
                               self.filter_label,
                               self.filter_entry,
                               self.filter_button,
                               self.regex_checkbutton
                               ]:
                    widget.config(state="normal")


    def delete_tag_under_mouse(self, event):
        if self.cleaning_text_var.get() == False:
            return
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
        self.text_box.tag_config("highlight", background="#fd8a8a")
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
#region - Image Tools


    def expand_image(self):
        if not self.check_if_directory():
            return
        self.check_working_directory()
        supported_formats = {".jpg", ".jpeg", ".png", ".jfif", ".jpg_large", ".bmp", ".webp"}
        filename = self.image_files[self.current_index]
        base_filename, file_extension = os.path.splitext(filename)
        if file_extension.lower() not in supported_formats:
            messagebox.showerror("Error", f"Unsupported filetype: {file_extension.upper()}")
            return
        new_filename = f"{base_filename}_ex{file_extension}"
        new_filepath = os.path.join(self.image_dir.get(), new_filename)
        if os.path.exists(new_filepath):
            messagebox.showerror("Error", f'Output file:\n\n{os.path.normpath(new_filename)}\n\nAlready exists.')
            return
        with Image.open(os.path.join(self.image_dir.get(), filename)) as img:
            width, height = img.size
            if width == height:
                messagebox.showwarning("Warning", "The image is already a square aspect ratio.")
                return
        confirmation = (
            "Are you sure you want to expand the current image?\n\n"
            "This tool works by expanding the shorter side to a square resolution divisible by 8 "
            "and stretching the pixels around the long side to fill the space.\n\n"
            "A new image will be saved in the same format and with '_ex' appended to the filename."
            )
        if not messagebox.askyesno("Confirmation", confirmation):
            return
        try:
            text_filename = f"{base_filename}.txt"
            text_filepath = os.path.join(self.image_dir.get(), text_filename)
            if os.path.exists(text_filepath):
                new_text_filename = f"{base_filename}_ex.txt"
                new_text_filepath = os.path.join(self.image_dir.get(), new_text_filename)
                shutil.copy2(text_filepath, new_text_filepath)
            with Image.open(os.path.join(self.image_dir.get(), filename)) as img:
                max_dim = max(width, height)
                new_img = Image.new("RGB", (max_dim, max_dim))
                x_offset = (max_dim - width) // 2
                y_offset = (max_dim - height) // 2
                new_img.paste(img, (x_offset, y_offset))
                np_img = numpy.array(new_img)
                np_img[:, :x_offset] = np_img[:, x_offset:x_offset+1]
                np_img[:, x_offset+width:] = np_img[:, x_offset+width-1:x_offset+width]
                np_img[:y_offset, :] = np_img[y_offset:y_offset+1, :]
                np_img[y_offset+height:, :] = np_img[y_offset+height-1:y_offset+height, :]
                filled_img = Image.fromarray(np_img)
                filled_img.save(new_filepath, quality=100 if file_extension in {".jpg", ".jpeg", ".jfif", ".jpg_large"} else 100)
                self.check_image_dir()
                index_value = int(self.image_files.index(new_filename))
                self.jump_to_image(index_value)
        except Exception as e:
            messagebox.showerror("Error", f'Failed to process {filename}. Reason: {e}')


    def rename_and_convert_pairs(self):
        if not self.check_if_directory():
            return
        try:
            confirmation = messagebox.askyesno("Confirm: Rename Files",
                "Are you sure you want to rename and convert all images and text files in the current directory?\n\n"
                "img-txt pairs will be saved to a 'Renamed Output' folder.\nNothing is overwritten.\n\n"
                "Images are converted to '.jpg' (except for '.gif' files) and then each pair is renamed in sequential order using padded zeros.\n\n"
                "Example input: aH15520.jpg, aH15520.txt\n"
                "Example output: 00001.jpg, 00001.txt"
                )
            if not confirmation:
                return
            self.check_working_directory()
            target_dir = os.path.join(self.image_dir.get(), "Renamed Output")
            os.makedirs(target_dir, exist_ok=True)
            files = sorted(f for f in os.listdir(self.image_dir.get()) if f.endswith(tuple([".txt", ".jpg", ".jpeg", ".png", ".jfif", ".jpg_large", ".webp", ".bmp", ".gif"])))
            counter = 1
            base_names = {}
            for filename in files:
                base_name, extension = os.path.splitext(filename)
                if extension == ".txt":
                    if base_name in base_names:
                        new_name = base_names[base_name] + extension
                    else:
                        new_name = str(counter).zfill(5) + extension
                        base_names[base_name] = str(counter).zfill(5)
                        counter += 1
                else:
                    if extension == ".gif":
                        new_name = str(counter).zfill(5) + extension
                    else:
                        new_name = str(counter).zfill(5) + ".jpg"
                    base_names[base_name] = str(counter).zfill(5)
                    counter += 1
                original_path = os.path.join(self.image_dir.get(), filename)
                new_path = os.path.join(target_dir, new_name)
                if extension in [".jpeg", ".png", ".jfif", ".jpg_large", ".webp", ".bmp"]:
                    img = Image.open(original_path)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.save(new_path, "JPEG", quality=100)
                else:
                    shutil.copy(original_path, new_path)
            set_path = messagebox.askyesno("Success", "Files renamed and converted successfully!\n\nDo you want to set the path to the output folder?")
            if set_path:
                self.image_dir.set(os.path.normpath(target_dir))
                self.set_working_directory()
        except FileNotFoundError:
            messagebox.showerror("Error", "The specified directory does not exist.")
        except PermissionError:
            messagebox.showerror("Error", "You do not have the necessary permissions to perform this operation.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")


    def rename_pairs(self):
        if not self.check_if_directory():
            return
        try:
            confirmation = messagebox.askyesno("Confirm: Rename Files",
                "Are you sure you want to rename all image and text files in the current directory?\n\n"
                "img-txt pairs will be saved to a 'Renamed Output' folder.\nNothing is overwritten.\n\n"
                "Each pair is renamed in sequential order using padded zeros.\n\n"
                "Example input: aH15520.jpg, aH15520.txt\n"
                "Example output: 00001.jpg, 00001.txt"
                )
            if not confirmation:
                return
            self.check_working_directory()
            target_dir = os.path.join(self.image_dir.get(), "Renamed Output")
            os.makedirs(target_dir, exist_ok=True)
            files = sorted(f for f in os.listdir(self.image_dir.get()) if f.endswith(tuple([".txt", ".jpg", ".jpeg", ".png", ".jfif", ".jpg_large", ".webp", ".bmp", ".gif"])))
            counter = 1
            base_names = {}
            for filename in files:
                base_name, extension = os.path.splitext(filename)
                if base_name in base_names:
                    new_name = base_names[base_name] + extension
                else:
                    new_name = str(counter).zfill(5) + extension
                    base_names[base_name] = str(counter).zfill(5)
                    counter += 1
                original_path = os.path.join(self.image_dir.get(), filename)
                new_path = os.path.join(target_dir, new_name)
                shutil.copy(original_path, new_path)
            set_path = messagebox.askyesno("Success", "Files renamed successfully!\n\nDo you want to set the path to the output folder?")
            if set_path:
                self.image_dir.set(os.path.normpath(target_dir))
                self.set_working_directory()
        except FileNotFoundError:
            messagebox.showerror("Error", "The specified directory does not exist.")
        except PermissionError:
            messagebox.showerror("Error", "You do not have the necessary permissions to perform this operation.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")


    def flip_current_image(self):
        filename = self.image_files[self.current_index]
        if filename.lower().endswith('.gif'):
            with Image.open(filename) as img:
                frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
                flipped_frames = [frame.transpose(Image.FLIP_LEFT_RIGHT) for frame in frames]
                durations = [frame.info.get('duration', 34) for frame in frames]
                first_frame = flipped_frames[0]
                rest_frames = flipped_frames[1:]
                first_frame.save(filename, append_images=rest_frames, save_all=True, duration=durations, loop=0)
        else:
            with Image.open(filename) as img:
                flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                flipped_img.save(filename)
        self.show_pair()


    def rotate_current_image(self):
        filename = self.image_files[self.current_index]
        if filename.lower().endswith('.gif'):
            with Image.open(filename) as img:
                frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
                rotated_frames = [frame.transpose(Image.ROTATE_270) for frame in frames]
                durations = [frame.info.get('duration', 34) for frame in frames]
                first_frame = rotated_frames[0]
                rest_frames = rotated_frames[1:]
                first_frame.save(filename, append_images=rest_frames, save_all=True, duration=durations, loop=0)
        else:
            with Image.open(filename) as img:
                rotated_img = img.transpose(Image.ROTATE_270)
                rotated_img.save(filename)
        self.show_pair()


    def resize_image(self):
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        window_x = root.winfo_x() + -200 + main_window_width // 2
        window_y = root.winfo_y() - 200 + main_window_height // 2
        filepath = self.image_files[self.current_index]
        resize_image.ResizeTool(self.master, filepath, window_x, window_y, self.update_pair, self.jump_to_image)


    def upscale_image(self):
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        window_x = root.winfo_x() + -135 + main_window_width // 2
        window_y = root.winfo_y() - 200 + main_window_height // 2
        filepath = self.image_files[self.current_index]
        upscale_image.Upscale(self.master, filepath, window_x, window_y, self.update_pair, self.jump_to_image)


    def batch_crop_images(self):
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        window_x = root.winfo_x() + -135 + main_window_width // 2
        window_y = root.winfo_y() - 200 + main_window_height // 2
        filepath = str(self.image_dir.get())
        batch_crop_images.BatchCrop(self.master, filepath, window_x, window_y)


    def open_crop_tool(self):
        filepath = self.image_files[self.current_index]
        if filepath.lower().endswith('.gif'):
            messagebox.showerror("Error", "Unsupported filetype: .GIF")
            return
        crop_image.Crop(self.master, filepath)


    def duplicate_pair(self):
        self.save_text_file()
        filename = self.image_files[self.current_index]
        base_filename, file_extension = os.path.splitext(filename)
        new_filename = f"{base_filename}_dup{file_extension}"
        shutil.copy2(filename, new_filename)
        text_filename = f"{base_filename}.txt"
        if os.path.exists(text_filename):
            new_text_filename = f"{base_filename}_dup.txt"
            shutil.copy2(text_filename, new_text_filename)
        self.update_pair("next")


    def batch_resize_images(self):
        self.check_working_directory()
        if os.path.isfile('./main/bin/batch_resize_images.py'):
            command = f'python ./main/bin/batch_resize_images.py --path "{self.image_dir.get()}"'
        else:
            command = f'./batch_resize_images.exe --path "{self.image_dir.get()}"'
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)


    def find_duplicate_files(self):
        self.check_working_directory()
        if os.path.isfile('./main/bin/find_dupe_file.py'):
            command = f'python ./main/bin/find_dupe_file.py --path "{self.image_dir.get()}"'
        else:
            command = f'./find_dupe_file.exe --path "{self.image_dir.get()}"'
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)


    def view_image_grid(self, event=None):
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        window_x = root.winfo_x() + -330 + main_window_width // 2
        window_y = root.winfo_y() - 300 + main_window_height // 2
        filepath = self.image_dir.get()
        image_grid.ImageGrid(self.master, filepath, window_x, window_y, self.jump_to_image)


#endregion
################################################################################################################################################
#region - Misc Functions


    def change_message_label(self, event=None):
        if self.auto_save_var.get():
            self.message_label.config(text="Changes are autosaved", bg="#5da9be", fg="white")
        else:
            text_file = self.text_files[self.current_index]
            try:
                with open(text_file, 'r', encoding="utf-8") as file:
                    file_content = file.read()
            except FileNotFoundError:
                file_content = ""
            if self.text_box.get("1.0", "end-1c") == file_content:
                self.message_label.config(text="No Change", bg="#f0f0f0", fg="black")
            else:
                self.message_label.config(text="Changes not saved", bg="#fd8a8a", fg="white")


    def disable_button(self, event):
        return "break"


    def toggle_always_on_top(self):
        current_state = root.attributes('-topmost')
        new_state = 0 if current_state == 1 else 1
        root.attributes('-topmost', new_state)


    def toggle_list_menu(self):
        if self.cleaning_text_var.get():
            self.optionsMenu.entryconfig("List View", state="normal")
        else:
            self.optionsMenu.entryconfig("List View", state="disabled")
            if self.list_mode_var.get():
                self.toggle_list_mode(skip=True)
            if self.message_label.cget("text") in ["No Change", "Saved", "Changes Saved!", "Text Files Cleaned up!", "Filter Cleared!", "Filter Applied!"]:
                if self.filepath_contains_images_var:
                    self.refresh_text_box()
            self.list_mode_var.set(False)


    def set_image_quality(self):
        quality_settings = {
            "High"  : (1536, "LANCZOS"),
            "Normal": (1280, "LANCZOS"),
            "Low"   : (768,  "LANCZOS")
            }
        var = self.image_qualtiy_var.get()
        if var in quality_settings:
            self.quality_max_size, self.quality_filter = quality_settings[var]
        self.refresh_image()


#endregion
################################################################################################################################################
#region - Window drag setup


    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
        self.image_preview.config(cursor="size")


    def stop_drag(self, event):
        self.drag_x = None
        self.drag_y = None
        self.image_preview.config(cursor="hand2")


    def dragging_window(self, event):
        if self.drag_x is not None and self.drag_y is not None:
            dx = event.x - self.drag_x
            dy = event.y - self.drag_y
            x = self.master.winfo_x() + dx
            y = self.master.winfo_y() + dy
            self.master.geometry(f"+{x}+{y}")


#endregion
################################################################################################################################################
#region - About Window


    def toggle_about_window(self):
        if self.about_window_open is not None:
            self.close_about_window()
        else:
            self.open_about_window()


    def open_about_window(self):
        self.about_window_open = AboutWindow(self.master)
        self.about_window_open.protocol("WM_DELETE_WINDOW", self.close_about_window)
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        main_window_x = root.winfo_x() - 425 + main_window_width // 2
        main_window_y = root.winfo_y() - 315 + main_window_height // 2
        self.about_window_open.geometry("+{}+{}".format(main_window_x, main_window_y))


    def close_about_window(self):
        self.about_window_open.destroy()
        self.about_window_open = None


#endregion
################################################################################################################################################
#region - Text Cleanup


    def cleanup_all_text_files(self, show_confirmation=True):
        if not self.check_if_directory():
            return
        if show_confirmation:
            user_confirmation = messagebox.askokcancel("Confirmation", "This operation will clean all text files from typos like:\nDuplicate tags, Extra commas, Extra spaces, trailing commas/spaces, commas without spaces, and more.\n\nExample Cleanup:\n  From: dog,solo,  ,happy  ,,\n       To: dog, solo, happy")
            if not user_confirmation:
                return
            self.message_label.config(text="Text Files Cleaned Up!", bg="#6ca079", fg="white")
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
        if self.cleaning_text_var.get():
            text = self.remove_duplicates(text)
            if self.list_mode_var.get():
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
        if self.list_mode_var.get():
            text = text.split('\n')
        else:
            text = text.split(',')
        text = [item.strip() for item in text]
        text = list(dict.fromkeys(text))
        if self.list_mode_var.get():
            text = '\n'.join(text)
        else:
            text = ','.join(text)
        return text


#endregion
################################################################################################################################################
#region -  Read and save settings


    def save_settings(self):
        try:
            def add_section(section_name):
                if not self.config.has_section(section_name):
                    self.config.add_section(section_name)
            add_section("Version")
            self.check_working_directory()
            self.config.set("Version", "app_version", VERSION)
            add_section("Path")
            self.config.set("Path", "last_directory", str(self.image_dir.get()))
            self.config.set("Path", "last_index", str(self.current_index))
            self.config.set("Path", "new_text_path", str(self.new_text_path))
            add_section("Autocomplete")
            self.config.set("Autocomplete", "csv_danbooru", str(self.csv_danbooru.get()))
            self.config.set("Autocomplete", "csv_derpibooru", str(self.csv_derpibooru.get()))
            self.config.set("Autocomplete", "csv_e621", str(self.csv_e621.get()))
            self.config.set("Autocomplete", "csv_english_dictionary", str(self.csv_english_dictionary.get()))
            self.config.set("Autocomplete", "suggestion_quantity", str(self.suggestion_quantity_var.get()))
            self.config.set("Autocomplete", "use_colored_suggestions", str(self.colored_suggestion_var.get()))
            add_section("Other")
            self.config.set("Other", "auto_save", str(self.auto_save_var.get()))
            self.config.set("Other", "cleaning_text", str(self.cleaning_text_var.get()))
            self.config.set("Other", "big_save_button", str(self.big_save_button_var.get()))
            self.config.set("Other", "highlighting_duplicates", str(self.highlight_selection_var.get()))
            with open("settings.cfg", "w", encoding="utf-8") as f:
                self.config.write(f)
        except (PermissionError, IOError) as e:
            messagebox.showerror("Error", f"An error occurred while saving the user settings.\n\n{e}")


    def read_settings(self):
        try:
            if os.path.exists("settings.cfg"):
                self.config.read("settings.cfg")
                if not self.is_current_version():
                    with open("settings.cfg", 'w', encoding="utf-8") as cfg_file:
                        cfg_file.write("")
                    return
                self.read_config_settings()
                if hasattr(self, 'text_box'):
                    self.show_pair()
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred.\n\n{e}")


    def is_current_version(self):
        return self.config.has_section("Version") and self.config.get("Version", "app_version", fallback=VERSION) == VERSION


    def read_config_settings(self):
        self.read_directory_settings()
        self.read_autocomplete_settings()
        self.read_other_settings()


    def read_directory_settings(self):
        last_directory = self.config.get("Path", "last_directory", fallback=None)
        if last_directory and os.path.exists(last_directory) and messagebox.askyesno("Confirmation", "Reload last directory?"):
            self.image_dir.set(last_directory)
            self.set_working_directory()
            self.set_text_file_path(str(self.config.get("Path", "new_text_path", fallback=last_directory)))
            last_index = int(self.config.get("Path", "last_index", fallback=1))
            num_files = len([name for name in os.listdir(last_directory) if os.path.isfile(os.path.join(last_directory, name))])
            self.jump_to_image(min(last_index, num_files))


    def read_autocomplete_settings(self):
        self.csv_danbooru.set(value=self.config.getboolean("Autocomplete", "csv_danbooru", fallback=True))
        self.csv_derpibooru.set(value=self.config.getboolean("Autocomplete", "csv_derpibooru", fallback=False))
        self.csv_e621.set(value=self.config.getboolean("Autocomplete", "csv_e621", fallback=False))
        self.csv_english_dictionary.set(value=self.config.getboolean("Autocomplete", "csv_english_dictionary", fallback=False))
        self.suggestion_quantity_var.set(value=self.config.getint("Autocomplete", "suggestion_quantity", fallback=4))
        self.colored_suggestion_var.set(value=self.config.getboolean("Autocomplete", "use_colored_suggestions", fallback=True))
        self.update_autocomplete_dictionary()


    def read_other_settings(self):
        self.auto_save_var.set(value=self.config.getboolean("Other", "auto_save", fallback=False))
        self.cleaning_text_var.set(value=self.config.getboolean("Other", "cleaning_text", fallback=True))
        self.big_save_button_var.set(value=self.config.getboolean("Other", "big_save_button", fallback=False))
        self.highlight_selection_var.set(value=self.config.getboolean("Other", "highlighting_duplicates", fallback=True))


#endregion
################################################################################################################################################
#region -  Save and close


    def save_text_file(self):
        try:
            if self.image_dir.get() != "Choose Directory..." and self.check_if_directory() and self.text_files:
                self.save_file()
                self.message_label.config(text="Saved", bg="#6ca079", fg="white")
                if self.cleaning_text_var.get():
                    self.save_file()
                self.show_pair()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error", f"An error occurred while saving the current text file.\n\n{e}")


    def save_file(self):
        text_file = self.text_files[self.current_index]
        text = self.text_box.get("1.0", "end-1c")
        if text == "None" or text == "":
            if os.path.exists(text_file):
                os.remove(text_file)
            return
        with open(text_file, "w+", encoding="utf-8") as f:
            if self.cleaning_text_var.get():
                text = self.cleanup_text(text)
            if self.list_mode_var.get():
                text = ', '.join(text.split('\n'))
            f.write(text)


    def on_closing(self):
        try:
            self.save_settings()
            self.delete_text_backup()
            self.check_working_directory()
            if os.path.isdir(os.path.join(self.image_dir.get(), 'Trash')):
                self.delete_trash_folder()
                self.check_saved_and_quit()
            else:
                self.check_saved_and_quit()
        except TclError: pass


    def check_saved_and_quit(self):
        if self.message_label.cget("text") in ["No Change", "Saved", "Changes Saved!", "Text Files Cleaned up!", "Filter Cleared!", "Filter Applied!"]:
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


#endregion
################################################################################################################################################
#region -  File Management


    def natural_sort(self, string):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', string)]


    def check_if_contains_images(self, directory):
        if any(fname.lower().endswith(('.jpg', '.jpeg', '.jpg_large', '.jfif', '.png', '.webp', '.bmp', '.gif')) for fname in os.listdir(directory)):
            self.filepath_contains_images_var = True
            return True
        else:
            self.filepath_contains_images_var = False
            messagebox.showwarning("No Images", "The selected directory does not contain any images.")
            return False


    def choose_working_directory(self):
        try:
            original_auto_save_var = None
            if hasattr(self, 'text_box'):
                original_auto_save_var = self.auto_save_var.get()
                if original_auto_save_var:
                    self.save_text_file()
            else:
                self.auto_save_var.set(value=False)
            directory = askdirectory()
            if directory and directory != self.image_dir.get():
                if self.check_if_contains_images(directory):
                    self.delete_text_backup()
                    self.image_dir.set(os.path.normpath(directory))
                    self.current_index = 0
                    self.load_pairs()
                    self.set_text_file_path(directory)
            if original_auto_save_var is not None:
                self.auto_save_var.set(original_auto_save_var)
        except Exception: return


    def set_working_directory(self, event=None):
        try:
            if self.auto_save_var.get():
                self.save_text_file()
            directory = self.directory_entry.get()
            self.image_dir.set(os.path.normpath(directory))
            self.current_index = 0
            self.load_pairs()
            self.set_text_file_path(directory)
        except FileNotFoundError:
            messagebox.showwarning("Invalid Directory", f"The system cannot find the path specified:\n\n{self.directory_entry.get()}")


    def open_directory(self, directory):
        try:
            if os.path.isdir(directory):
                os.startfile(directory)
        except Exception: return


    def open_current_directory(self, event=None):
        try:
            self.check_working_directory()
            os.startfile(self.image_dir.get())
        except Exception: return


    def open_current_image(self, event=None):
        if self.image_files:
            try:
                os.startfile(self.image_file)
            except Exception: return


    def check_working_directory(self):
        try:
            working_path = os.path.dirname(self.image_files[self.current_index])
            textbox_path = self.image_dir.get()
            if textbox_path == "Choose Directory...":
                return
            if textbox_path != working_path:
                self.directory_entry.delete(0, "end")
                self.directory_entry.insert(0, working_path)
        except IndexError: return


    def check_if_directory(self):
        if not os.path.isdir(self.image_dir.get()) or self.image_dir.get() == "Choose Directory...":
            return False
        return True


    def create_custom_dictionary(self):
        try:
            csv_filename = 'my_tags.csv'
            if not os.path.isfile(csv_filename):
                with open(csv_filename, 'w', newline='', encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(["### This is where you can create a custom dictionary of tags."])
                    writer.writerow(["### These tags will be loaded alongside the chosen autocomplete dictionary."])
                    writer.writerow(["### Tags near the top of the list have a higher priority than lower tags."])
                    writer.writerow([])
                    writer.writerow(["supercalifragilisticexpialidocious"])
            self.update_autocomplete_dictionary()
        except (PermissionError, IOError, TclError): return


    def add_to_custom_dictionary(self):
        try:
            selected_text = self.text_box.get("sel.first", "sel.last")
            with open('my_tags.csv', 'a', newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([selected_text])
            self.update_autocomplete_dictionary()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error", f"An error occurred while saving the selected to 'my_tags.csv'.\n\n{e}")


    def check_odd_files(self, filename):
        file_extension = os.path.splitext(filename)[1].lower()
        file_rename_dict = {".jpg_large": "jpg", ".jfif": "jpg"}
        return file_extension in file_rename_dict


    def rename_odd_files(self, filename):
        try:
            self.check_working_directory()
            file_extension = os.path.splitext(filename)[1].lower()
            file_rename_dict = {".jpg_large": "jpg", ".jfif": "jpg"}
            new_file_extension = file_rename_dict[file_extension]
            base_filename = os.path.splitext(filename)[0]
            new_filename = base_filename + "." + new_file_extension
            counter = 1
            while os.path.exists(os.path.join(self.image_dir.get(), new_filename)):
                new_filename = base_filename + "_" + str(counter).zfill(2) + "." + new_file_extension
                counter += 1
            os.rename(os.path.join(self.image_dir.get(), filename), os.path.join(self.image_dir.get(), new_filename))
            return new_filename
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error", f"An error occurred while renaming odd files.\n\n{e}")


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
                    self.message_label.config(text="Files Restored", bg="#6ca079", fg="white")
                except Exception: pass


    def backup_text_files(self):
        if not self.check_if_directory():
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
            try:
                backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
                if os.path.exists(backup_folder):
                    shutil.rmtree(backup_folder)
            except (PermissionError, IOError, TclError) as e:
                messagebox.showerror("Error", f"An error occurred while deleting the text backups.\n\n{e}")


    def delete_trash_folder(self):
        trash_dir = os.path.join(self.image_dir.get(), 'Trash')
        try:
            if os.path.exists(trash_dir):
                is_empty = not os.listdir(trash_dir)
                empty_status = "Empty" if is_empty else "Not Empty"
                if messagebox.askyesno("Trash Folder Found", f"A 'Trash' folder was found in the image directory. ({empty_status})\n\nWould you like to delete this folder?"):
                    self.check_working_directory()
                    shutil.rmtree(trash_dir)
            root.destroy()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error", f"An error occurred while deleting the trash folder.\n\n{e}")


    def delete_pair(self):
        if not self.check_if_directory():
            return
        try:
            if messagebox.askokcancel("Warning", "This will move the img-txt pair to a local trash folder.\n\nThe trash folder will be created in the selected directory."):
                if self.current_index < len(self.image_files):
                    trash_dir = os.path.join(os.path.dirname(self.image_files[self.current_index]), "Trash")
                    os.makedirs(trash_dir, exist_ok=True)
                    deleted_pair = []
                    for file_list in [self.image_files, self.text_files]:
                        if os.path.exists(file_list[self.current_index]):
                            trash_file = os.path.join(trash_dir, os.path.basename(file_list[self.current_index]))
                            try:
                                os.rename(file_list[self.current_index], trash_file)
                            except FileExistsError:
                                if not trash_file.endswith("txt"):
                                    if messagebox.askokcancel("Warning", "The file already exists in the trash. Do you want to overwrite it?"):
                                        os.remove(trash_file)
                                        os.rename(file_list[self.current_index], trash_file)
                                    else:
                                        return
                            deleted_pair.append((file_list, self.current_index, trash_file))
                            del file_list[self.current_index]
                    self.deleted_pairs.append(deleted_pair)
                    self.total_images_label.config(text=f"of {len(self.image_files)}")
                    if self.current_index >= len(self.image_files):
                        self.current_index = len(self.image_files) - 1
                    if self.current_index >= 1:
                        self.update_pair("prev")
                    else:
                        self.show_pair()
                    self.undo_state.set("normal")
                    self.toolsMenu.entryconfig("Undo Delete", state="normal")
                else: pass
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error", f"An error occurred while deleting the img-txt pair.\n\n{e}")


    def undo_delete_pair(self):
        if not (self.check_if_directory() and self.deleted_pairs):
            return
        try:
            self.check_working_directory()
            deleted_pair = self.deleted_pairs.pop()
            files_to_restore = [os.path.basename(trash_file) for _, _, trash_file in deleted_pair]
            if not messagebox.askyesno("Restore Files", "The following files will be restored:\n\n" + "\n".join(files_to_restore) + "\n\nDo you want to proceed?"):
                self.deleted_pairs.append(deleted_pair)
                return
            for file_list, index, trash_file in deleted_pair:
                original_path = os.path.join(self.image_dir.get(), os.path.basename(trash_file))
                shutil.move(trash_file, original_path)
                file_list.insert(index, original_path)
                if not original_path.endswith('.txt'):
                    self.check_image_dir()
                    index_value = int(self.image_files.index(original_path))
                    self.jump_to_image(index_value)
                else:
                    self.load_text_file(original_path)
            self.total_images_label.config(text=f"of {len(self.image_files)}")
            if not self.deleted_pairs:
                self.undo_state.set("disabled")
                self.toolsMenu.entryconfig("Undo Delete", state="disabled")
        except (PermissionError, ValueError, IOError, TclError) as e:
            messagebox.showerror("Error", f"An error occurred while restoring the img-txt pair.\n\n{e}")


#endregion
################################################################################################################################################
#region -  Framework


    def set_appid(self):
        myappid = 'ImgTxtViewer.Nenotriple'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


    def set_window_size(self, master):
        master.minsize(751, 396) # Width x Height
        window_width = 1280
        window_height = 681
        position_right = root.winfo_screenwidth()//2 - window_width//2
        position_top = root.winfo_screenheight()//2 - window_height//2
        root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")


root = Tk()
app = ImgTxtViewer(root)
app.toggle_always_on_top()
root.attributes('-topmost', 0)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.title(f"{VERSION} - img-txt Viewer")
app.read_settings()
root.mainloop()


#endregion
################################################################################################################################################
#region - Changelog


'''


[v1.94 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.94)

<details>
  <summary>Click here to view release notes!</summary>

  - New:
    - New option: `Toggle Zoom`, This allows you to hover the mouse over the current image and display a zoomed in preview.
      - Use the Mouse-Wheel to zoom in and out.
      - Use Shift+Mouse-Wheel to increase or decrease the popup size.


<br>


  - Fixed:
    - `Image Grid`, Fixed issue where supported file types were case sensitive, leading to images not appearing, and indexing issues.


<br>


  - Other changes:
    - Improved performance of Autocomplete by optimizing: data loading, similar names, string operations, and suggestion retrieval. Up to 50% faster than v1.92
    - `Image Grid`, Now reuses image cache across instances to speed up loading.


<br>


  - Project Changes:
    -

</details>

'''


#endregion
################################################################################################################################################
#region - Todo


'''


- Todo
  -


- Tofix
  - Toggle Zoom checkbutton state isn't being reflected in either menu when making changes.


'''

#endregion
