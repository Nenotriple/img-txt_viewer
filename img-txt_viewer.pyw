"""
########################################
#            IMG-TXT VIEWER            #
#   Version : v1.96                    #
#   Author  : github.com/Nenotriple    #
########################################

Description:
-------------
Display an image and text file side-by-side for easy manual caption editing.

More info here: https://github.com/Nenotriple/img-txt_viewer

"""


VERSION = "v1.96"


################################################################################################################################################
#region - Imports


# Standard Library
import os
import re
import csv
import sys
import glob
import time
import shutil
import ctypes
import pickle
import zipfile
import itertools
import statistics
import subprocess
from functools import partial
from collections import defaultdict, Counter


# Standard Library - GUI
import tkinter.font
from tkinter.scrolledtext import ScrolledText
from tkinter import (ttk, Tk, Toplevel, messagebox, filedialog, simpledialog,
                     StringVar, BooleanVar, IntVar,
                     Frame, PanedWindow, Menu,
                     Label, Text,
                     Event, TclError
                     )


# Third-Party Libraries
import numpy
from TkToolTip.TkToolTip import TkToolTip as ToolTip
from PIL import (Image, ImageTk, ImageSequence,
                 ImageOps, UnidentifiedImageError
                 )


# Custom Libraries
from main.scripts import (about_img_txt_viewer,
                          settings_manager,
                          upscale_image,
                          crop_image,
                          batch_crop_images,
                          resize_image,
                          image_grid,
                          batch_tag_edit,
                          batch_resize_images,
                          find_dupe_file,
                          edit_panel
                          )
from main.scripts.PopUpZoom import PopUpZoom as PopUpZoom


#endregion
################################################################################################################################################
#region CLS: Autocomplete


class Autocomplete:
    def __init__(self, data_file, include_my_tags=True):
        # Data
        self.data_file = data_file
        self.my_tags_csv = 'my_tags.csv'

        # Settings
        self.max_suggestions = 4
        self.suggestion_threshold = 115000
        self.include_my_tags = include_my_tags

        # Cache
        self.autocomplete_dict, self.similar_names_dict = None, None
        self.previous_text = None
        self.previous_suggestions = None
        self.previous_pattern = None
        self.previous_threshold_results = {}
        self.single_letter_cache = {}

        # Load Data
        self._load_data()
        self._precache_single_letter_suggestions()


    # --------------------------------------
    # Load/Read Data
    # --------------------------------------
    def _load_data(self):
        """Load autocomplete data, only if not already cached."""
        if not self.autocomplete_dict:
            self.autocomplete_dict, self.similar_names_dict = self.load_autocomplete_data()


    def load_autocomplete_data(self):
        """Load the autocomplete data from CSV files."""
        application_path = self._get_application_path()
        data_file_path = os.path.join(application_path, "main/dict", self.data_file)
        additional_file_path = os.path.join(application_path, self.my_tags_csv)
        autocomplete_data = {}
        similar_names_dict = defaultdict(list)
        self._read_csv(data_file_path, autocomplete_data, similar_names_dict)
        if self.include_my_tags and os.path.isfile(additional_file_path):
            self._read_csv(additional_file_path, autocomplete_data, similar_names_dict, include_classifier_id=False)
        return autocomplete_data, similar_names_dict


    def _get_application_path(self):
        """Get the application path for the autocomplete data files."""
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))


    def _read_csv(self, file_path, data, similar_names_dict, include_classifier_id=True):
        """Read the CSV file and populate the data dictionary."""
        if os.path.isfile(file_path):
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and not row[0].startswith('###'):
                        true_name = row[0]
                        classifier_id = row[1] if include_classifier_id and len(row) > 1 else ''
                        similar_names = row[3].split(',') if len(row) > 3 else []
                        if true_name in data and not include_classifier_id:
                            data[true_name][1].extend(similar_names)
                        else:
                            data[true_name] = (classifier_id, similar_names)
                        for sim_name in similar_names:
                            similar_names_dict[sim_name].append(true_name)


    # --------------------------------------
    # Pre-Cache Single-Letter Suggestions
    # --------------------------------------
    def _precache_single_letter_suggestions(self):
        """Pre-cache suggestions for all single-letter inputs (a-z, 0-9)."""
        dictionary_file_path = os.path.join(self._get_application_path(), "main/dict", self.data_file)
        if not os.path.exists(dictionary_file_path):
            return
        dictionary_name = os.path.splitext(self.data_file)[0]
        cache_dir = os.path.join(self._get_application_path(), 'main/dict/cache')
        cache_file = os.path.join(cache_dir, f'{dictionary_name}_pre-cache')
        cache_timestamp_file = os.path.join(cache_dir, f'{dictionary_name}_pre-cache-timestamp')
        os.makedirs(cache_dir, exist_ok=True)

        cache_is_stale = True
        if os.path.exists(cache_file) and os.path.exists(cache_timestamp_file):
            with open(cache_timestamp_file, 'r') as f:
                cache_timestamp_str = f.read().strip()
                if cache_timestamp_str:
                    cache_timestamp = float(cache_timestamp_str)
                    dictionary_timestamp = os.path.getmtime(dictionary_file_path)
                    if cache_timestamp >= dictionary_timestamp:
                        cache_is_stale = False
        if not cache_is_stale:
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    self.single_letter_cache = pickle.load(f)
        else:
            for char in "abcdefghijklmnopqrstuvwxyz0123456789":
                pattern = self._compile_pattern(char)
                suggestions = self._get_or_cache_threshold_results(pattern)
                self.single_letter_cache[char] = self._sort_suggestions(suggestions, char)
            with open(cache_file, 'wb') as f:
                pickle.dump(self.single_letter_cache, f)
            with open(cache_timestamp_file, 'w') as f:
                f.write(str(os.path.getmtime(dictionary_file_path)))


    # --------------------------------------
    # Get Suggestions
    # --------------------------------------
    def get_suggestion(self, text):
        """Main entry point to get suggestions based on input text."""
        self._load_data()
        if not self.autocomplete_dict:
            return None
        if len(text) == 1 and text in self.single_letter_cache:
            return self.single_letter_cache[text][:self.max_suggestions]
        if text == self.previous_text:
            return self.previous_suggestions[:self.max_suggestions]
        text_with_underscores = text.replace(" ", "_")
        pattern = self._compile_pattern(text_with_underscores)
        suggestions = self._get_or_cache_threshold_results(pattern)
        self._include_similar_name_suggestions(pattern, suggestions)
        sorted_suggestions = self._sort_suggestions(suggestions, text_with_underscores)
        self._cache_suggestions(text, sorted_suggestions, pattern)
        return sorted_suggestions[:self.max_suggestions]


    def _compile_pattern(self, text):
        """Compile the regex pattern with support for wildcard matching."""
        text_with_asterisks = re.escape(text).replace("\\*", ".*")
        return re.compile(text_with_asterisks)


    def _get_or_cache_threshold_results(self, pattern):
        """Cache and retrieve results for threshold-based searches."""
        cache_key = (pattern.pattern, self.suggestion_threshold)
        if cache_key in self.previous_threshold_results:
            return self.previous_threshold_results[cache_key]
        results = self._find_matching_names(pattern, self.suggestion_threshold)
        self.previous_threshold_results[cache_key] = results
        return results


    def _find_matching_names(self, pattern, threshold):
        """Find matching names in the main data based on the regex pattern."""
        return {
            true_name: (classifier_id, similar_names)
            for true_name, (classifier_id, similar_names)
            in itertools.islice(self.autocomplete_dict.items(), threshold)
            if pattern.match(true_name)
            }


    def _include_similar_name_suggestions(self, pattern, suggestions):
        """Include suggestions based on similar names matching the pattern."""
        for sim_name, true_names in self.similar_names_dict.items():
            if pattern.match(sim_name):
                for true_name in true_names:
                    suggestions[true_name] = self.autocomplete_dict[true_name]


    def _sort_suggestions(self, suggestions, text):
        """Sort suggestions based on their matching score."""
        return sorted(suggestions.items(), key=lambda x: self.get_score(x[0], text), reverse=True)


    def _cache_suggestions(self, text, sorted_suggestions, pattern):
        """Cache the current suggestions for potential reuse."""
        self.previous_text = text
        self.previous_suggestions = sorted_suggestions
        self.previous_pattern = pattern


    # --------------------------------------
    # Score Calculation
    # --------------------------------------
    def get_score(self, suggestion, text):
        """Calculate a score for the suggestion based on its similarity to the input text."""
        score = 0
        if suggestion == text:
            return len(text) * 2
        for suggestion_char, input_char in zip(suggestion, text):
            if suggestion_char == input_char:
                score += 1
            else:
                break
        classifier_id, _ = self.autocomplete_dict.get(suggestion, ('', []))
        if not classifier_id and suggestion.startswith(text[:3]):
            score += 1
        return score


#endregion
################################################################################################################################################
#region CLS: ImgTxtViewer


class ImgTxtViewer:
    def __init__(self, master):
        self.master = master
        self.application_path = self.get_app_path()
        self.set_appid()
        self.setup_window()
        self.set_icon()
        self.initial_class_setup()
        self.define_app_settings()
        self.setup_general_binds()
        self.create_menu_bar()
        self.create_primary_ui()
        self.settings_manager.read_settings()

#endregion
################################################################################################################################################
#region - Setup

    def initial_class_setup(self):
        # Setup tools
        self.caption_counter = Counter()
        self.autocomplete = Autocomplete
        self.batch_tag_edit = batch_tag_edit.BatchTagEdit()
        self.batch_resize_images = batch_resize_images.BatchResizeImages()
        self.find_dupe_file = find_dupe_file.FindDupeFile()
        self.edit_panel = edit_panel.EditPanel(self, self.master)
        self.about_window = about_img_txt_viewer.AboutWindow(self, self.master, VERSION, self.blank_image)
        self.settings_manager = settings_manager.SettingsManager(self, self.master, VERSION)

        # Setup UI state
        self.ui_state = {
            "ImgTxtViewer": True,
            "BatchTagEdit": False,
            "BatchResizeImages": False,
            "FindDupeFile": False,
            }

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
        self.image_info_cache = {}
        self.thumbnail_cache = {}

        # Misc variables
        self.about_window_open = False
        self.panes_swap_ew_var = BooleanVar(value=False)
        self.panes_swap_ns_var = BooleanVar(value=False)
        self.text_modified_var = False
        self.is_alt_arrow_pressed = False
        self.filepath_contains_images_var = False
        self.is_resizing_id = None
        self.toggle_zoom_var = None
        self.undo_state = StringVar(value="disabled")
        self.previous_window_size = (self.master.winfo_width(), self.master.winfo_height())
        self.delete_tag_job = None

        # Image Resize Variables
        self.current_image = None # ImageTk.PhotoImage object
        self.original_image = None # ImageTk.PhotoImage object
        self.current_max_img_height = None
        self.current_max_img_width = None

        # GIF animation variables
        self.gif_frames = []
        self.gif_frame_cache = {}
        self.frame_durations = []
        self.current_frame = 0
        self.current_gif_frame_image = None
        self.animation_job = None

        # Color Palette
        self.pastel_colors = [
            "#a2d2ff", "#ffafcf", "#aec3ae", "#ebe3d5", "#beadfa",
            "#cdf5fd", "#fdcedf", "#c3edc0", "#d6c7ae", "#dfccfb",
            "#c0dbea", "#f2d8d8", "#cbffa9", "#f9f3cc", "#acb1d6",
            "#a1ccd1", "#dba39a", "#c4d7b2", "#ffd9b7", "#d9acf5",
            "#7895b2", "#ff8787", "#90a17d", "#f8c4b4", "#af7ab3"
            ]# Blue     Pink       Green      Brown      Purple


# --------------------------------------
# Settings
# --------------------------------------
    def define_app_settings(self):
        # Misc Settings
        self.app_settings_cfg = 'settings.cfg'
        self.my_tags_csv = 'my_tags.csv'
        self.image_dir = StringVar(value="Choose Directory...")
        self.text_dir = ""
        self.external_image_editor_path = "mspaint"
        self.always_on_top_var = BooleanVar(value=False)
        self.big_save_button_var = BooleanVar(value=True)

        # Font Settings
        self.font_var = StringVar()
        self.font_size_var = IntVar(value=10)

        # List Mode Settings
        self.list_mode_var = BooleanVar(value=False)
        self.cleaning_text_var = BooleanVar(value=True)

        # Auto Save Settings
        self.auto_save_var = BooleanVar(value=False)
        self.auto_delete_blank_files_var = BooleanVar(value=False)

        # Highlight Settings
        self.highlight_selection_var = BooleanVar(value=True)
        self.highlight_use_regex_var = BooleanVar(value=False)
        self.highlight_all_duplicates_var = BooleanVar(value=False)
        self.truncate_stat_captions_var = BooleanVar(value=True)
        self.search_and_replace_regex = BooleanVar(value=False)

        # Image Stats Settings
        self.process_image_stats_var = BooleanVar(value=False)
        self.use_mytags_var = BooleanVar(value=True)

        # Filter Settings
        self.filter_empty_files_var = BooleanVar(value=False)
        self.filter_use_regex_var = BooleanVar(value=False)

        # Load Order Settings
        self.load_order_var = StringVar(value="Name (default)")
        self.reverse_load_order_var = BooleanVar(value=False)

        # Thumbnail Panel
        self.update_thumbnail_id = None
        self.thumbnails_visible = BooleanVar(value=True)
        self.thumbnail_width = IntVar(value=50)

        # Edit Panel
        self.edit_panel_visible_var = BooleanVar(value=False)
        self.edit_slider_dict = {"Brightness": 0, "Contrast": 0, "AutoContrast": 0, "Highlights": 0, "Shadows": 0, "Saturation": 0, "Sharpness": 0, "Hue": 0, "Color Temperature": 0}
        self.edit_last_slider_dict = {}
        self.edit_is_reverted_var = False
        self.edit_cumulative_var = BooleanVar(value=False)

        # Image Quality
        self.image_quality_var = StringVar(value="Normal")
        self.quality_max_size = 1280
        self.quality_filter = Image.BILINEAR
        Image.MAX_IMAGE_PIXELS = 300000000  # ~(17320x17320)px

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


# --------------------------------------
# Bindings
# --------------------------------------
    def setup_general_binds(self):
        self.master.bind("<Control-f>", lambda event: self.toggle_highlight_all_duplicates())
        self.master.bind("<Control-s>", lambda event: self.save_text_file())
        self.master.bind("<Alt-Right>", lambda event: self.next_pair(event))
        self.master.bind("<Alt-Left>", lambda event: self.prev_pair(event))
        self.master.bind('<Shift-Delete>', lambda event: self.delete_pair())
        self.master.bind('<Configure>', self.handle_window_configure)
        self.master.bind('<F1>', lambda event: self.toggle_zoom_popup(event))
        self.master.bind('<F2>', lambda event: self.open_image_grid(event))
        self.master.bind('<F4>', lambda event: self.open_image_in_editor(event))
        self.master.bind('<F5>', lambda event: self.show_batch_tag_edit(event))
        self.master.bind('<Control-w>', lambda event: self.on_closing(event))

        # Display window size on resize:
        #self.master.bind("<Configure>", lambda event: print(f"\rWindow size (W,H): {event.width},{event.height}    ", end='') if event.widget == self.master else None, add="+")


#endregion
################################################################################################################################################
#region - Menubar

    def create_menu_bar(self):
        self.initialize_menu()
        self.create_options_menu()
        self.create_tools_menu()


# --------------------------------------
# Initialize Menu Bar
# --------------------------------------
    def initialize_menu(self):
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


# --------------------------------------
# Options
# --------------------------------------
    def create_options_menu(self):
        # Options
        self.options_subMenu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Options", underline=0, state="disable", menu=self.options_subMenu)
        self.options_subMenu.add_checkbutton(label="Clean-Text", underline=0, variable=self.cleaning_text_var, command=self.toggle_list_menu)
        self.options_subMenu.add_checkbutton(label="Auto-Delete Blank Files", underline=0, variable=self.auto_delete_blank_files_var)
        self.options_subMenu.add_checkbutton(label="Colored Suggestions", underline=1, variable=self.colored_suggestion_var, command=self.update_autocomplete_dictionary)
        self.options_subMenu.add_checkbutton(label="Highlight Selection", underline=0, variable=self.highlight_selection_var)
        self.options_subMenu.add_checkbutton(label="Big Save Button", underline=0, variable=self.big_save_button_var, command=self.toggle_save_button_height)
        self.options_subMenu.add_checkbutton(label="List View", underline=0, variable=self.list_mode_var, command=self.toggle_list_mode)
        self.options_subMenu.add_separator()
        self.options_subMenu.add_checkbutton(label="Always On Top", underline=0, variable=self.always_on_top_var, command=self.set_always_on_top)
        self.options_subMenu.add_checkbutton(label="Toggle Zoom", accelerator="F1", variable=self.toggle_zoom_var, command=self.toggle_zoom_popup)
        self.options_subMenu.add_checkbutton(label="Toggle Thumbnail Panel", variable=self.thumbnails_visible, command=self.update_thumbnail_panel)
        self.options_subMenu.add_checkbutton(label="Toggle Edit Panel", variable=self.edit_panel_visible_var, command=self.edit_panel.toggle_edit_panel)
        self.options_subMenu.add_checkbutton(label="Vertical View", underline=0, variable=self.panes_swap_ns_var, command=self.swap_pane_orientation)
        self.options_subMenu.add_checkbutton(label="Swap img-txt Sides", underline=0, variable=self.panes_swap_ew_var, command=self.swap_pane_sides)
        self.options_subMenu.add_command(label="Set Default Image Editor", underline=0, command=self.set_external_image_editor_path)


        # Image Display Quality Menu
        image_quality_menu = Menu(self.options_subMenu, tearoff=0)
        self.options_subMenu.add_cascade(label="Image Display Quality", underline=1, menu=image_quality_menu)
        for value in ["High", "Normal", "Low"]:
            image_quality_menu.add_radiobutton(label=value, variable=self.image_quality_var, value=value, command=self.set_image_quality)


# --------------------------------------
# Loading Order
# --------------------------------------
        # Loading Order Menu
        load_order_menu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Loading Order", underline=6, state="disable", menu=load_order_menu)


        # Loading Order Options
        order_options = ["Name (default)", "File size", "Date created", "Extension", "Last Access time", "Last write time"]
        for option in order_options:
            load_order_menu.add_radiobutton(label=option, variable=self.load_order_var, value=option, command=self.load_pairs)


        # Loading Order Direction
        load_order_menu.add_separator()
        load_order_menu.add_radiobutton(label="Ascending", variable=self.reverse_load_order_var, value=False, command=self.load_pairs)
        load_order_menu.add_radiobutton(label="Descending", variable=self.reverse_load_order_var, value=True, command=self.load_pairs)


# --------------------------------------
# Autocomplete
# --------------------------------------
        # Autocomplete Settings Menu
        autocompleteSettingsMenu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Autocomplete", underline=11, state="disable", menu=autocompleteSettingsMenu)


        # Suggestion Dictionary Menu
        dictionaryMenu = Menu(autocompleteSettingsMenu, tearoff=0)
        autocompleteSettingsMenu.add_cascade(label="Dictionary", underline=11, menu=dictionaryMenu)
        dictionaryMenu.add_checkbutton(label="English Dictionary", underline=0, variable=self.csv_english_dictionary, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Danbooru", underline=0, variable=self.csv_danbooru, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Derpibooru", underline=0, variable=self.csv_derpibooru, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="e621", underline=0, variable=self.csv_e621, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_separator()
        dictionaryMenu.add_command(label="Clear Selection", underline=0, command=self.clear_dictionary_csv_selection)


        # Suggestion Threshold Menu
        suggestion_threshold_menu = Menu(autocompleteSettingsMenu, tearoff=0)
        autocompleteSettingsMenu.add_cascade(label="Threshold", underline=11, menu=suggestion_threshold_menu)
        for level in ["Slow", "Normal", "Fast", "Faster"]:
            suggestion_threshold_menu.add_radiobutton(label=level, variable=self.suggestion_threshold_var, value=level, command=self.set_suggestion_threshold)


        # Suggestion Quantity Menu
        suggestion_quantity_menu = Menu(autocompleteSettingsMenu, tearoff=0)
        autocompleteSettingsMenu.add_cascade(label="Quantity", underline=11, menu=suggestion_quantity_menu)
        for quantity in range(0, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(quantity), variable=self.suggestion_quantity_var, value=quantity, command=lambda suggestion_quantity=quantity: self.set_suggestion_quantity(suggestion_quantity))


        # Match Mode Menu
        match_mode_menu = Menu(autocompleteSettingsMenu, tearoff=0)
        autocompleteSettingsMenu.add_cascade(label="Match Mode", menu=match_mode_menu)
        match_modes = {"Match Whole String": False, "Match Last Word": True}
        for mode, value in match_modes.items():
            match_mode_menu.add_radiobutton(label=mode, variable=self.last_word_match_var, value=value)


# --------------------------------------
# Open/Reset Settings
# --------------------------------------
        # Settings Menu
        self.optionsMenu.add_separator()
        self.optionsMenu.add_command(label="Reset Settings", underline=1, state="disable", command=self.settings_manager.reset_settings)
        self.optionsMenu.add_command(label="Open Settings File...", underline=1, command=lambda: self.open_textfile(self.app_settings_cfg))
        self.optionsMenu.add_command(label="Open My Tags File...", underline=1, command=lambda: self.open_textfile(self.my_tags_csv))


# --------------------------------------
# Batch Operations
# --------------------------------------
    def create_tools_menu(self):
        self.batch_operations_menu = Menu(self.toolsMenu, tearoff=0)
        self.toolsMenu.add_cascade(label="Batch Operations", underline=0, state="disable", menu=self.batch_operations_menu)
        self.batch_operations_menu.add_command(label="Batch Rename And/Or Convert...", underline=3, command=self.rename_and_convert_pairs)
        self.batch_operations_menu.add_command(label="Batch Resize Images...", underline=10, command=self.show_batch_resize_images)
        self.batch_operations_menu.add_command(label="Batch Crop Images...", underline=8, command=self.batch_crop_images)
        self.batch_operations_menu.add_command(label="Batch Tag Edit...", underline=0, accelerator="F5", command=self.show_batch_tag_edit)
        self.batch_operations_menu.add_command(label="Batch Upscale...", underline=0, command=lambda: self.upscale_image(batch=True))
        self.batch_operations_menu.add_separator()
        self.batch_operations_menu.add_command(label="Zip Dataset...", underline=0, command=self.archive_dataset)
        self.batch_operations_menu.add_command(label="Find Duplicate Files...", underline=0, command=self.show_find_dupe_file)
        self.batch_operations_menu.add_command(label="Cleanup All Text Files...", underline=1, command=self.cleanup_all_text_files)
        self.batch_operations_menu.add_command(label="Create Blank Text Pairs...", underline=0, command=self.create_blank_text_files)
        self.batch_operations_menu.add_command(label="Create Wildcard From Captions...", underline=0, command=self.collate_captions)


# --------------------------------------
# Individual Operations
# --------------------------------------
        self.individual_operations_menu = Menu(self.toolsMenu, tearoff=0)
        self.toolsMenu.add_cascade(label="Edit Current pair", underline=0, state="disable", menu=self.individual_operations_menu)
        self.individual_operations_menu.add_command(label="Rename Pair", underline=0, command=self.manually_rename_single_pair)
        self.individual_operations_menu.add_command(label="Upscale...", underline=0, command=lambda: self.upscale_image(batch=False))
        self.individual_operations_menu.add_command(label="Crop...", underline=0, command=self.open_crop_tool)
        self.individual_operations_menu.add_command(label="Resize...", underline=0, command=self.resize_image)
        self.individual_operations_menu.add_command(label="Expand", underline=1, command=self.expand_image)
        self.individual_operations_menu.add_command(label="Rotate", underline=1, command=self.rotate_current_image)
        self.individual_operations_menu.add_command(label="Flip", underline=1, command=self.flip_current_image)
        self.individual_operations_menu.add_separator()
        self.individual_operations_menu.add_command(label="Duplicate img-txt Pair", underline=2, command=self.duplicate_pair)
        self.individual_operations_menu.add_command(label="Delete img-txt Pair", accelerator="Shift+Del", command=self.delete_pair)
        self.individual_operations_menu.add_command(label="Undo Delete", underline=0, state="disable", command=self.undo_delete_pair)


# --------------------------------------
# Misc
# --------------------------------------
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Open Current Directory...", state="disable", underline=13, command=self.open_image_directory)
        self.toolsMenu.add_command(label="Open Current Image...", state="disable", underline=13, command=self.open_image)
        self.toolsMenu.add_command(label="Edit Image...", state="disable", underline=6, accelerator="F4", command=self.open_image_in_editor)
        self.toolsMenu.add_separator()
        self.toolsMenu.add_command(label="Next Empty Text File", state="disable", accelerator="Ctrl+E", command=self.index_goto_next_empty)
        self.toolsMenu.add_command(label="Open Image-Grid...", state="disable", accelerator="F2", underline=11, command=self.open_image_grid)


#endregion
################################################################################################################################################
#region - Create Primary UI


    def create_primary_ui(self):
        self.setup_primary_frames()
        self.create_primary_widgets()


    def setup_primary_frames(self):
        # Configure the grid weights for the master window frame
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # primary_paned_window : is used to contain the ImgTxtViewer UI.
        self.primary_paned_window = PanedWindow(self.master, orient="horizontal", sashwidth=6, bg="#d0d0d0", bd=0)
        self.primary_paned_window.grid(row=0, column=0, sticky="nsew")
        self.primary_paned_window.bind('<ButtonRelease-1>', self.snap_sash_to_half)


        # master_image_frame : is exclusively used for the displayed image, thumbnails, image info.
        self.master_image_frame = Frame(self.master)
        self.master_image_frame.bind('<Configure>', lambda event: self.debounce_update_thumbnail_panel(event))
        self.master_image_frame.grid_rowconfigure(1, weight=1)
        self.master_image_frame.grid_columnconfigure(0, weight=1)
        self.primary_paned_window.add(self.master_image_frame, stretch="always")


        # master_control_frame : serves as a container for all primary UI frames, with the exception of the master_image_frame.
        self.master_control_frame = Frame(self.master)
        self.primary_paned_window.add(self.master_control_frame, stretch="always")
        self.primary_paned_window.paneconfigure(self.master_control_frame, minsize=300)
        self.primary_paned_window.update()
        self.primary_paned_window.sash_place(0, 0, 0)


    def create_primary_widgets(self):
        # Image stats
        self.stats_frame = Frame(self.master_image_frame)
        self.stats_frame.grid(row=0, column=0, sticky="ew")
        self.label_image_stats = Label(self.stats_frame, text="...")
        self.label_image_stats.grid(row=0, column=0, sticky="ew")


        # Primary Image
        self.primary_display_image = Label(self.master_image_frame, cursor="hand2")
        self.primary_display_image.grid(row=1, column=0, sticky="nsew")
        self.primary_display_image.bind("<Double-1>", lambda event: self.open_image(index=self.current_index, event=event))
        self.primary_display_image.bind('<Button-2>', self.open_image_directory)
        self.primary_display_image.bind("<MouseWheel>", self.mouse_scroll)
        self.primary_display_image.bind("<Button-3>", self.show_imageContext_menu)
        self.primary_display_image.bind("<ButtonPress-1>", self.start_drag)
        self.primary_display_image.bind("<ButtonRelease-1>", self.stop_drag)
        self.primary_display_image.bind("<B1-Motion>", self.dragging_window)
        self.popup_zoom = PopUpZoom(self.primary_display_image)
        self.toggle_zoom_var = BooleanVar(value=self.popup_zoom.zoom_enabled.get())
        self.image_preview_tooltip = ToolTip.create(self.primary_display_image, "Right-Click for more\nMiddle-click to open in file explorer\nDouble-Click to open in your system image viewer\nALT+Left/Right or Mouse-Wheel to move between pairs", 1000, 6, 12)


        # Thumbnail Panel
        self.set_custom_ttk_button_highlight_style()
        self.thumbnail_panel = Frame(self.master_image_frame)
        self.thumbnail_panel.grid(row=3, column=0, sticky="ew")
        self.thumbnail_panel.bind("<MouseWheel>", self.mouse_scroll)


        # Edit Image Panel
        self.edit_image_panel = Frame(self.master_image_frame, relief="ridge", bd=1)
        self.edit_image_panel.grid(row=2, column=0, sticky="ew")
        self.edit_image_panel.grid_remove()


        # Directory Selection
        directory_frame = Frame(self.master_control_frame)
        directory_frame.pack(side="top", fill="x", padx=(0,2))
        self.text_path_indicator = Label(directory_frame)
        self.text_path_indicator.pack(side="left", fill="y", pady=2)
        self.text_path_tooltip = ToolTip.create(self.text_path_indicator, "Text Path: Same as image path", 10, 6, 12)
        self.directory_entry = ttk.Entry(directory_frame, textvariable=self.image_dir)
        self.directory_entry.pack(side="left", fill="both", expand=True, pady=2)
        self.directory_entry.bind('<Return>', self.set_working_directory)
        self.directory_entry.bind("<Double-1>", lambda event: self.custom_select_word_for_entry(event, self.directory_entry))
        self.directory_entry.bind("<Triple-1>", lambda event: self.select_all_in_entry(event, self.directory_entry))
        self.directory_entry.bind("<Button-3>", self.open_directory_context_menu)
        self.directory_entry.bind("<Button-1>", self.clear_directory_entry_on_click)
        self.dir_context_menu = Menu(self.directory_entry, tearoff=0)
        self.dir_context_menu.add_command(label="Cut", command=self.directory_cut)
        self.dir_context_menu.add_command(label="Copy", command=self.directory_copy)
        self.dir_context_menu.add_command(label="Paste", command=self.directory_paste)
        self.dir_context_menu.add_command(label="Delete", command=self.directory_delete)
        self.dir_context_menu.add_command(label="Clear", command=self.directory_clear)
        self.dir_context_menu.add_separator()
        self.dir_context_menu.add_command(label="Set Text File Path...", state="disabled", command=self.set_text_file_path)
        self.dir_context_menu.add_command(label="Reset Text Path To Image Path", state="disabled", command=lambda: self.set_text_file_path(self.image_dir.get()))
        self.browse_button = ttk.Button(directory_frame, text="Browse...", width=8, command=self.choose_working_directory)
        self.browse_button.pack(side="left", pady=2)
        ToolTip.create(self.browse_button, "Right click to set an alternate path for text files", 250, 6, 12)
        self.browse_context_menu = Menu(self.browse_button, tearoff=0)
        self.browse_context_menu.add_command(label="Set Text File Path...", state="disabled", command=self.set_text_file_path)
        self.browse_context_menu.add_command(label="Reset Text Path To Image Path", state="disabled", command=lambda: self.set_text_file_path(self.image_dir.get()))
        self.browse_button.bind("<Button-3>", self.open_browse_context_menu)
        self.open_button = ttk.Button(directory_frame, text="Open", width=8, command=lambda: self.open_directory(self.directory_entry.get()))
        self.open_button.pack(side="left", pady=2)


        # Image Index
        self.index_frame = Frame(self.master_control_frame, relief="raised")
        self.index_frame.pack(side="top", fill="x", padx=2)
        self.index_pair_label = Label(self.index_frame, text="Pair", state="disabled")
        self.index_pair_label.pack(side="left")
        self.image_index_entry = ttk.Entry(self.index_frame, width=5, state="disabled")
        self.image_index_entry.pack(side="left")
        self.image_index_entry.bind("<Return>", self.jump_to_image)
        self.image_index_entry.bind("<MouseWheel>", self.mouse_scroll)
        self.image_index_entry.bind("<Up>", self.next_pair)
        self.image_index_entry.bind("<Down>", self.prev_pair)
        self.index_context_menu = Menu(self.directory_entry, tearoff=0)
        self.index_context_menu.add_command(label="First", command=lambda: self.index_goto(0))
        self.index_context_menu.add_command(label="Last", command=lambda: self.index_goto(len(self.image_files)))
        self.index_context_menu.add_command(label="Random", accelerator="Ctrl+R", command=self.index_goto_random)
        self.index_context_menu.add_command(label="Next Empty", accelerator="Ctrl+E", command=self.index_goto_next_empty)
        self.total_images_label = Label(self.index_frame, text=f"of {len(self.image_files)}", state="disabled")
        self.total_images_label.pack(side="left")


        # Save Button
        self.save_button = ttk.Button(self.index_frame, text="Save", state="disabled", style="Blue.TButton", padding=(5, 5), command=self.save_text_file)
        self.save_button.pack(side="left", pady=2, fill="x", expand=True)
        ToolTip.create(self.save_button, "CTRL+S to save\n\nRight-Click to make the save button larger", 1000, 6, 12)
        self.auto_save_checkbutton = ttk.Checkbutton(self.index_frame, width=10, text="Auto-save", state="disabled", variable=self.auto_save_var, command=self.sync_title_with_content)
        self.auto_save_checkbutton.pack(side="left")


        # Navigation Buttons
        nav_button_frame = Frame(self.master_control_frame)
        nav_button_frame.pack(fill="x", padx=2)
        self.next_button = ttk.Button(nav_button_frame, text="Next--->", width=12, state="disabled", command=lambda: self.update_pair("next"))
        self.prev_button = ttk.Button(nav_button_frame, text="<---Previous", width=12, state="disabled", command=lambda: self.update_pair("prev"))
        self.next_button.pack(side="right", fill="x", expand=True)
        self.prev_button.pack(side="right", fill="x", expand=True)
        ToolTip.create(self.next_button, "Hotkey: ALT+R\nHold shift to advance by 5", 1000, 6, 12)
        ToolTip.create(self.prev_button, "Hotkey: ALT+L\nHold shift to advance by 5", 1000, 6, 12)


        # Suggestion text
        self.suggestion_textbox = Text(self.master_control_frame, height=1, borderwidth=0, highlightthickness=0, bg='#f0f0f0', state="disabled", cursor="arrow")
        self.suggestion_textbox.pack(side="top", fill="x", pady=4)
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
        for header, section in zip(self.about_window.info_headers, self.about_window.info_content):
            self.info_text.insert("end", header + "\n", "header")
            self.info_text.insert("end", section + "\n", "section")
        self.info_text.tag_config("header", font=("Segoe UI", 9, "bold"))
        self.info_text.tag_config("section", font=("Segoe UI", 9))
        self.info_text.bind("<Button-3>", self.show_textContext_menu)
        self.info_text.config(state='disabled', wrap="word")


#endregion
################################################################################################################################################
#region - Text Box setup


    def create_text_pane(self):
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
            self.get_default_font()
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
        self.tab8 = Frame(self.text_notebook)
        self.text_notebook.add(self.tab1, text='S&R')
        self.text_notebook.add(self.tab2, text='Prefix')
        self.text_notebook.add(self.tab3, text='Append')
        self.text_notebook.add(self.tab4, text='Filter')
        self.text_notebook.add(self.tab5, text='Highlight')
        self.text_notebook.add(self.tab6, text='Font')
        self.text_notebook.add(self.tab7, text='My Tags')
        self.text_notebook.add(self.tab8, text='Stats', )
        self.text_notebook.pack(fill='both', expand=True)
        self.create_search_and_replace_widgets_tab1()
        self.create_prefix_text_widgets_tab2()
        self.create_append_text_widgets_tab3()
        self.create_filter_text_image_pairs_widgets_tab4()
        self.create_custom_active_highlight_widgets_tab5()
        self.create_font_widgets_tab6()
        self.create_custom_dictionary_widgets_tab7()
        self.create_stats_widgets_tab8()


    def create_search_and_replace_widgets_tab1(self):
        self.tab1_frame = Frame(self.tab1)
        self.tab1_frame.pack(side='top', fill='both')
        self.tab1_button_frame = Frame(self.tab1_frame)
        self.tab1_button_frame.pack(side='top', fill='x')
        self.search_label = Label(self.tab1_button_frame, width=8, text="Search:")
        self.search_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.search_label, "Enter the EXACT text you want to search for", 200, 6, 12)
        self.search_entry = ttk.Entry(self.tab1_button_frame, textvariable=self.search_string_var, width=4)
        self.search_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.search_entry.bind("<Double-1>", lambda event: self.custom_select_word_for_entry(event, self.search_entry))
        self.search_entry.bind("<Triple-1>", lambda event: self.select_all_in_entry(event, self.search_entry))
        self.replace_label = Label(self.tab1_button_frame, width=8, text="Replace:")
        self.replace_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.replace_label, "Enter the text you want to replace the searched text with\n\nLeave empty to replace with nothing (delete)", 200, 6, 12)
        self.replace_entry = ttk.Entry(self.tab1_button_frame, textvariable=self.replace_string_var, width=4)
        self.replace_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.replace_entry.bind("<Double-1>", lambda event: self.custom_select_word_for_entry(event, self.replace_entry))
        self.replace_entry.bind("<Triple-1>", lambda event: self.select_all_in_entry(event, self.replace_entry))
        self.replace_entry.bind('<Return>', lambda event: self.search_and_replace())
        self.replace_button = ttk.Button(self.tab1_button_frame, text="Go!", width=5, command=self.search_and_replace)
        self.replace_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.replace_button, "Text files will be backup up", 200, 6, 12)
        self.clear_button = ttk.Button(self.tab1_button_frame, text="Clear", width=5, command=self.clear_search_and_replace_tab)
        self.clear_button.pack(side='left', anchor="n", pady=4)
        self.undo_button = ttk.Button(self.tab1_button_frame, text="Undo", width=5, command=self.restore_backup)
        self.undo_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.undo_button, "Revert last action", 200, 6, 12)
        self.regex_search_replace_checkbutton = ttk.Checkbutton(self.tab1_button_frame, text="Regex", variable=self.search_and_replace_regex)
        self.regex_search_replace_checkbutton.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.undo_button, "Use Regular Expressions in 'Search'", 200, 6, 12)
        self.tab1_text_frame = Frame(self.tab1_frame, borderwidth=0)
        self.tab1_text_frame.pack(side='top', fill="both")
        description_textbox = ScrolledText(self.tab1_text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0", "Use this tool to search for a string of text across all text files in the selected directory.\n\n"
                                   "If a match is found, it will be replaced exactly with the given text.\n\n"
                                   "Example:\n"
                                   "Search for: the big brown dog\n"
                                   "Replace with: the big red dog\n\n"
                                   "This will replace all instances of 'the big brown dog' with 'the big red dog'.\n\n"
                                   "If a filter is applied, only text files that match the filter will be affected.")
        description_textbox.config(state="disabled", wrap="word")


    def clear_search_and_replace_tab(self):
        self.search_entry.delete(0, 'end')
        self.replace_entry.delete(0, 'end')
        self.search_and_replace_regex.set(False)


    def create_prefix_text_widgets_tab2(self):
        self.tab2_frame = Frame(self.tab2)
        self.tab2_frame.pack(side='top', fill='both')
        self.tab2_button_frame = Frame(self.tab2_frame)
        self.tab2_button_frame.pack(side='top', fill='x')
        self.prefix_label = Label(self.tab2_button_frame, width=8, text="Prefix:")
        self.prefix_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.prefix_label, "Enter the text you want to insert at the START of all text files\n\nCommas will be inserted as needed", 200, 6, 12)
        self.prefix_entry = ttk.Entry(self.tab2_button_frame, textvariable=self.prefix_string_var)
        self.prefix_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.prefix_entry.bind("<Double-1>", lambda event: self.custom_select_word_for_entry(event, self.prefix_entry))
        self.prefix_entry.bind("<Triple-1>", lambda event: self.select_all_in_entry(event, self.prefix_entry))
        self.prefix_entry.bind('<Return>', lambda event: self.prefix_text_files())
        self.prefix_button = ttk.Button(self.tab2_button_frame, text="Go!", width=5, command=self.prefix_text_files)
        self.prefix_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.prefix_button, "Text files will be backup up", 200, 6, 12)
        self.clear_button = ttk.Button(self.tab2_button_frame, text="Clear", width=5, command=self.clear_prefix_tab)
        self.clear_button.pack(side='left', anchor="n", pady=4)
        self.undo_button = ttk.Button(self.tab2_button_frame, text="Undo", width=5, command=self.restore_backup)
        self.undo_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.undo_button, "Revert last action", 200, 6, 12)
        self.tab2_text_frame = Frame(self.tab2_frame, borderwidth=0)
        self.tab2_text_frame.pack(side='top', fill="both")
        description_textbox = ScrolledText(self.tab2_text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0", "Use this tool to prefix all text files in the selected directory with the entered text.\n\n"
                                   "This means that the entered text will appear at the start of each text file.\n\n"
                                   "If a filter is applied, only text files that match the filter will be affected.")
        description_textbox.config(state="disabled", wrap="word")


    def clear_prefix_tab(self):
        self.prefix_entry.delete(0, 'end')


    def create_append_text_widgets_tab3(self):
        self.tab3_frame = Frame(self.tab3)
        self.tab3_frame.pack(side='top', fill='both')
        self.tab3_button_frame = Frame(self.tab3_frame)
        self.tab3_button_frame.pack(side='top', fill='x')
        self.append_label = Label(self.tab3_button_frame, width=8, text="Append:")
        self.append_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.append_label, "Enter the text you want to insert at the END of all text files\n\nCommas will be inserted as needed", 200, 6, 12)
        self.append_entry = ttk.Entry(self.tab3_button_frame, textvariable=self.append_string_var)
        self.append_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.append_entry.bind("<Double-1>", lambda event: self.custom_select_word_for_entry(event, self.append_entry))
        self.append_entry.bind("<Triple-1>", lambda event: self.select_all_in_entry(event, self.append_entry))
        self.append_entry.bind('<Return>', lambda event: self.append_text_files())
        self.append_button = ttk.Button(self.tab3_button_frame, text="Go!", width=5, command=self.append_text_files)
        self.append_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.append_button, "Text files will be backup up", 200, 6, 12)
        self.clear_button = ttk.Button(self.tab3_button_frame, text="Clear", width=5, command=self.clear_append_tab)
        self.clear_button.pack(side='left', anchor="n", pady=4)
        self.undo_button = ttk.Button(self.tab3_button_frame, text="Undo", width=5, command=self.restore_backup)
        self.undo_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.undo_button, "Revert last action", 200, 6, 12)
        self.tab3_text_frame = Frame(self.tab3_frame, borderwidth=0)
        self.tab3_text_frame.pack(side='top', fill="both")
        description_textbox = ScrolledText(self.tab3_text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0", "Use this tool to append all text files in the selected directory with the entered text.\n\n"
                                   "This means that the entered text will appear at the end of each text file.\n\n"
                                   "If a filter is applied, only text files that match the filter will be affected.")
        description_textbox.config(state="disabled", wrap="word")


    def clear_append_tab(self):
        self.append_entry.delete(0, 'end')


    def create_filter_text_image_pairs_widgets_tab4(self):
        self.tab4_frame = Frame(self.tab4)
        self.tab4_frame.pack(side='top', fill='both')
        self.tab4_button_frame = Frame(self.tab4_frame)
        self.tab4_button_frame.pack(side='top', fill='x')
        self.filter_label = Label(self.tab4_button_frame, width=8, text="Filter:")
        self.filter_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.filter_label, "Enter the EXACT text you want to filter by\nThis will filter all img-txt pairs based on the provided text, see below for more info", 200, 6, 12)
        self.filter_entry = ttk.Entry(self.tab4_button_frame, width=11, textvariable=self.filter_string_var)
        self.filter_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.filter_entry.bind("<Double-1>", lambda event: self.custom_select_word_for_entry(event, self.filter_entry))
        self.filter_entry.bind("<Triple-1>", lambda event: self.select_all_in_entry(event, self.filter_entry))
        self.filter_entry.bind('<Return>', lambda event: self.filter_text_image_pairs())
        self.filter_button = ttk.Button(self.tab4_button_frame, text="Go!", width=5, command=self.filter_text_image_pairs)
        self.filter_button.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.filter_button, "Text files will be filtered based on the entered text", 200, 6, 12)
        self.revert_filter_button = ttk.Button(self.tab4_button_frame, text="Clear", width=5, command=lambda: (self.revert_text_image_filter(clear=True)))
        self.revert_filter_button.pack(side='left', anchor="n", pady=4)
        self.revert_filter_button_tooltip = ToolTip.create(self.revert_filter_button, "Clear any filtering applied", 200, 6, 12)
        self.regex_filter_checkbutton = ttk.Checkbutton(self.tab4_button_frame, text="Regex", variable=self.filter_use_regex_var)
        self.regex_filter_checkbutton.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.regex_filter_checkbutton, "Use Regular Expressions for filtering", 200, 6, 12)
        self.empty_files_checkbutton = ttk.Checkbutton(self.tab4_button_frame, text="Empty", variable=self.filter_empty_files_var, command=self.toggle_empty_files_filter)
        self.empty_files_checkbutton.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.empty_files_checkbutton, "Check this to show only empty text files\n\nImages without a text pair are also considered as empty", 200, 6, 12)
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
        self.tab5_frame = Frame(self.tab5)
        self.tab5_frame.pack(side='top', fill='both')
        self.tab5_button_frame = Frame(self.tab5_frame)
        self.tab5_button_frame.pack(side='top', fill='x')
        self.custom_label = Label(self.tab5_button_frame, width=8, text="Highlight:")
        self.custom_label.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.custom_label, "Enter the text you want to highlight\nUse ' + ' to highlight multiple strings of text\n\nExample: dog + cat", 200, 6, 12)
        self.custom_entry = ttk.Entry(self.tab5_button_frame, textvariable=self.custom_highlight_string_var)
        self.custom_entry.pack(side='left', anchor="n", pady=4, fill='both', expand=True)
        self.custom_entry.bind("<Double-1>", lambda event: self.custom_select_word_for_entry(event, self.custom_entry))
        self.custom_entry.bind("<Triple-1>", lambda event: self.select_all_in_entry(event, self.custom_entry))
        self.custom_entry.bind('<KeyRelease>', lambda event: self.highlight_custom_string())
        self.highlight_button = ttk.Button(self.tab5_button_frame, text="Go!", width=5, command=self.highlight_custom_string)
        self.highlight_button.pack(side='left', anchor="n", pady=4)
        self.clear_button = ttk.Button(self.tab5_button_frame, text="Clear", width=5, command=self.clear_highlight_tab)
        self.clear_button.pack(side='left', anchor="n", pady=4)
        self.regex_highlight_checkbutton = ttk.Checkbutton(self.tab5_button_frame, text="Regex", variable=self.highlight_use_regex_var)
        self.regex_highlight_checkbutton.pack(side='left', anchor="n", pady=4)
        ToolTip.create(self.regex_highlight_checkbutton, "Use Regular Expressions for highlighting text", 200, 6, 12)
        self.tab5_text_frame = Frame(self.tab5_frame, borderwidth=0)
        self.tab5_text_frame.pack(side='top', fill="both")
        description_textbox = ScrolledText(self.tab5_text_frame, bg="#f0f0f0")
        description_textbox.pack(side='bottom', fill='both')
        description_textbox.insert("1.0", "Enter the text you want to highlight each time you move to a new img-txt pair.\n\n"
                                   "Use ' + ' to highlight multiple strings of text\n\n"
                                   "Example: dog + cat")
        description_textbox.config(state="disabled", wrap="word")


    def clear_highlight_tab(self):
        self.custom_entry.delete(0, 'end')
        self.highlight_use_regex_var.set(False)


    def create_font_widgets_tab6(self, event=None):
        def set_font_and_size(font, size):
            if font and size:
                size = int(size)
                self.text_box.config(font=(font, size))
                self.font_size_tab6.config(text=f"Size: {size}")
        def reset_to_defaults():
            self.font_var.set(self.default_font)
            self.size_scale.set(self.default_font_size)
            set_font_and_size(self.default_font, self.default_font_size)
        font_label = Label(self.tab6, width=8, text="Font:")
        font_label.pack(side="left", anchor="n", pady=4)
        ToolTip.create(font_label, "Recommended Fonts: Courier New, Ariel, Consolas, Segoe UI", 200, 6, 12)
        font_box = ttk.Combobox(self.tab6, textvariable=self.font_var, width=4, takefocus=False, state="readonly", values=list(tkinter.font.families()))
        font_box.set(self.current_font_name)
        font_box.bind("<<ComboboxSelected>>", lambda event: set_font_and_size(self.font_var.get(), self.size_scale.get()))
        font_box.pack(side="left", anchor="n", pady=4, fill="x", expand=True)
        self.font_size_tab6 = Label(self.tab6, text=f"Size: {self.font_size_var.get()}", width=14)
        self.font_size_tab6.pack(side="left", anchor="n", pady=4)
        ToolTip.create(self.font_size_tab6, "Default size: 10", 200, 6, 12)
        self.size_scale = ttk.Scale(self.tab6, from_=6, to=24, variable=self.font_size_var, takefocus=False)
        self.size_scale.set(self.current_font_size)
        self.size_scale.bind("<B1-Motion>", lambda event: set_font_and_size(self.font_var.get(), self.size_scale.get()))
        self.size_scale.pack(side="left", anchor="n", pady=4, fill="x", expand=True)
        reset_button = ttk.Button(self.tab6, text="Reset", width=5, takefocus=False, command=reset_to_defaults)
        reset_button.pack(side="left", anchor="n", pady=4)


    def create_custom_dictionary_widgets_tab7(self):
        def save():
            with open(self.my_tags_csv, 'w') as file:
                content  = self.remove_extra_newlines(self.custom_dictionary_textbox.get("1.0", "end-1c"))
                file.write(content)
                self.master.after(100, self.refresh_custom_dictionary)
        self.create_custom_dictionary()
        self.tab7_frame = Frame(self.tab7)
        self.tab7_frame.pack(side='top', fill='both', expand=True)
        self.tab7_button_frame = Frame(self.tab7_frame)
        self.tab7_button_frame.pack(side='top', fill='x', pady=4)
        self.tab7_label = Label(self.tab7_button_frame, text="^^^Expand this frame^^^")
        self.tab7_label.pack(side='left')
        ToolTip.create(self.tab7_label, "Click and drag the gray bar up to reveal the text box", 200, 6, 12)
        self.open_mytags_button = ttk.Button(self.tab7_button_frame, width=10, text="Open", takefocus=False, command=lambda: self.open_textfile("my_tags.csv"))
        self.open_mytags_button.pack(side='right', fill='x')
        ToolTip.create(self.open_mytags_button, "Open the 'my_tags.csv' file in your default system app.", 200, 6, 12)
        self.save_mytags_button = ttk.Button(self.tab7_button_frame, width=10, text="Save", takefocus=False, command=save)
        self.save_mytags_button.pack(side='right', fill='x')
        ToolTip.create(self.save_mytags_button, "Save the contents of the textbox to 'my_tags.csv'", 200, 6, 12)
        self.use_mytags_checkbutton = ttk.Checkbutton(self.tab7_button_frame, text="Use My Tags", variable=self.use_mytags_var, takefocus=False, command=self.refresh_custom_dictionary)
        self.use_mytags_checkbutton.pack(side='right', fill='x')
        ToolTip.create(self.use_mytags_checkbutton, "Enable or disable these tags for use with autocomplete.", 200, 6, 12)
        self.tab7_frame2 = Frame(self.tab7_frame)
        self.tab7_frame2.pack(side='top', fill='both')
        tab7_info_label = Text(self.tab7_frame2, bg="#f0f0f0")
        tab7_info_label.pack(side='top', fill="both", expand=True)
        tab7_info_label.insert("1.0", "Create a custom dictionary of tags.\n"
                                      "Use newlines to separate tags.")
        tab7_info_label.config(state="disabled", wrap="word", height=3)
        self.custom_dictionary_textbox = ScrolledText(self.tab7_frame2, wrap="word")
        self.custom_dictionary_textbox.pack(side='top', fill='both', expand=True)
        with open(self.my_tags_csv, 'r') as file:
            content = self.remove_lines_starting_with_hashes(self.remove_extra_newlines(file.read()))
            self.custom_dictionary_textbox.insert('end', content)
        self.custom_dictionary_textbox.configure(undo=True)


    def create_stats_widgets_tab8(self):
        self.tab8_frame = Frame(self.tab8)
        self.tab8_frame.pack(fill='both', expand=True)
        self.tab8_button_frame = Frame(self.tab8_frame)
        self.tab8_button_frame.pack(side='top', fill='x', pady=4)
        self.tab8_label = Label(self.tab8_button_frame, text="^^^Expand this frame^^^")
        self.tab8_label.pack(side='left')
        self.tab8_refresh_stats_button = ttk.Button(self.tab8_button_frame, width=10, text="Refresh", takefocus=False, command=lambda: self.calculate_file_stats(manual_refresh=True))
        self.tab8_refresh_stats_button.pack(side='right')
        ToolTip.create(self.tab8_refresh_stats_button, "Refresh the file stats", 200, 6, 12)
        self.tab8_truncate_checkbutton = ttk.Checkbutton(self.tab8_button_frame, text="Truncate Captions", takefocus=False, variable=self.truncate_stat_captions_var)
        self.tab8_truncate_checkbutton.pack(side='right')
        ToolTip.create(self.tab8_truncate_checkbutton, "Limit the displayed captions if they exceed either 8 words or 50 characters", 200, 6, 12)
        self.tab8_process_images_checkbutton = ttk.Checkbutton(self.tab8_button_frame, text="Process Image Stats", takefocus=False, variable=self.process_image_stats_var)
        self.tab8_process_images_checkbutton.pack(side='right')
        ToolTip.create(self.tab8_process_images_checkbutton, "Enable/Disable image stat processing (Can be slow with many HD images)", 200, 6, 12)
        self.tab8_stats_textbox = ScrolledText(self.tab8_frame, wrap="word", state="disabled")
        self.tab8_stats_textbox.pack(fill='both', expand=True)


    def set_text_box_binds(self):
        # Mouse binds
        self.text_box.bind("<Double-1>", lambda event: self.custom_select_word_for_text(event, self.text_box))
        self.text_box.bind("<Triple-1>", lambda event: self.custom_select_line_for_text(event, self.text_box))
        self.text_box.bind("<Button-1>", lambda event: (self.remove_tag(), self.clear_suggestions()))
        self.text_box.bind("<Button-2>", lambda event: (self.delete_tag_under_mouse(event), self.sync_title_with_content(event)))
        self.text_box.bind("<Button-3>", lambda event: (self.show_textContext_menu(event)))
        # Update the autocomplete suggestion label after every KeyRelease event.
        self.text_box.bind("<KeyRelease>", lambda event: (self.update_suggestions(event), self.sync_title_with_content(event)))
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
        self.text_box.bind("<BackSpace>", lambda event: (self.remove_highlight(), self.sync_title_with_content()))
        # Update the title status whenever a key is pressed.
        self.text_box.bind("<Key>", lambda event: self.sync_title_with_content(event))
        # Disable normal button behavior
        self.text_box.bind("<Tab>", self.disable_button)
        self.text_box.bind("<Alt_L>", self.disable_button)
        self.text_box.bind("<Alt_R>", self.disable_button)
        # Show next empty text file
        self.text_box.bind("<Control-e>", self.index_goto_next_empty)
        # Show random img-txt pair
        self.text_box.bind("<Control-r>", self.index_goto_random)
        # Refresh text box
        #self.text_box.bind("<F5>", lambda event: self.refresh_text_box())


    # Text context menu
    def show_textContext_menu(self, event):
        if hasattr(self, 'text_box'):
            self.text_box.focus_set()
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
                textContext_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: (widget_in_focus.event_generate('<<Cut>>'), self.sync_title_with_content()))
                textContext_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: (widget_in_focus.event_generate('<<Copy>>')))
                textContext_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: (widget_in_focus.event_generate('<<Paste>>'), self.sync_title_with_content()))
                textContext_menu.add_command(label="Delete", accelerator="Del", command=lambda: (widget_in_focus.event_generate('<<Clear>>'), self.sync_title_with_content()))
                textContext_menu.add_command(label="Refresh", command=self.refresh_text_box)
                textContext_menu.add_separator()
                textContext_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: (widget_in_focus.event_generate('<<Undo>>'), self.sync_title_with_content()))
                textContext_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: (widget_in_focus.event_generate('<<Redo>>'), self.sync_title_with_content()))
                textContext_menu.add_separator()
                textContext_menu.add_command(label="Open Text Directory...", command=self.open_text_directory)
                textContext_menu.add_command(label="Open Text File...", command=self.open_textfile)
                textContext_menu.add_command(label="Add Selected Text to My Tags", state=select_state, command=self.add_to_custom_dictionary)
                textContext_menu.add_separator()
                textContext_menu.add_command(label="Highlight all Duplicates", accelerator="Ctrl+F", command=self.highlight_all_duplicates)
                textContext_menu.add_command(label="Next Empty Text File", accelerator="Ctrl+E", command=self.index_goto_next_empty)
                textContext_menu.add_separator()
                textContext_menu.add_checkbutton(label="Highlight Selection", variable=self.highlight_selection_var)
                textContext_menu.add_checkbutton(label="Clean-Text", variable=self.cleaning_text_var, command=self.toggle_list_menu)
                textContext_menu.add_checkbutton(label="List View", variable=self.list_mode_var, state=cleaning_state, command=self.toggle_list_mode)
            elif widget_in_focus == self.info_text:
                textContext_menu.add_command(label="Copy", command=lambda: widget_in_focus.event_generate('<<Copy>>'))
            textContext_menu.tk_popup(event.x_root, event.y_root)


    # Image context menu
    def show_imageContext_menu(self, event):
        self.imageContext_menu = Menu(self.master, tearoff=0)
        # Open
        self.imageContext_menu.add_command(label="Open Current Directory...", command=self.open_image_directory)
        self.imageContext_menu.add_command(label="Open Current Image...", command=self.open_image)
        self.imageContext_menu.add_command(label="Open Image-Grid...", accelerator="F2", command=self.open_image_grid)
        self.imageContext_menu.add_command(label="Edit Image...", accelerator="F4", command=self.open_image_in_editor)
        self.imageContext_menu.add_separator()
        # File
        self.imageContext_menu.add_command(label="Duplicate img-txt pair", command=self.duplicate_pair)
        self.imageContext_menu.add_command(label="Delete img-txt Pair", accelerator="Shift+Del", command=self.delete_pair)
        self.imageContext_menu.add_command(label="Undo Delete", command=self.undo_delete_pair, state=self.undo_state.get())
        self.imageContext_menu.add_separator()
        # Edit
        self.imageContext_menu.add_command(label="Rename Pair", command=self.manually_rename_single_pair)
        self.imageContext_menu.add_command(label="Upscale...", command=lambda: self.upscale_image(batch=False))
        self.imageContext_menu.add_command(label="Resize...", command=self.resize_image)
        if not self.image_file.lower().endswith('.gif'):
            self.imageContext_menu.add_command(label="Crop...", command=self.open_crop_tool)
            self.imageContext_menu.add_command(label="Expand", command=self.expand_image)
        else:
            self.imageContext_menu.add_command(label="Crop...", state="disabled", command=self.open_crop_tool)
            self.imageContext_menu.add_command(label="Expand", state="disabled", command=self.expand_image)
        self.imageContext_menu.add_command(label="Rotate", command=self.rotate_current_image)
        self.imageContext_menu.add_command(label="Flip", command=self.flip_current_image)
        self.imageContext_menu.add_separator()
        # Misc
        self.imageContext_menu.add_checkbutton(label="Toggle Zoom", accelerator="F1", variable=self.toggle_zoom_var, command=self.toggle_zoom_popup)
        self.imageContext_menu.add_checkbutton(label="Toggle Thumbnail Panel", variable=self.thumbnails_visible, command=self.update_thumbnail_panel)
        self.imageContext_menu.add_checkbutton(label="Toggle Edit Panel", variable=self.edit_panel_visible_var, command=self.edit_panel.toggle_edit_panel)
        self.imageContext_menu.add_checkbutton(label="Vertical View", underline=0, variable=self.panes_swap_ns_var, command=self.swap_pane_orientation)
        self.imageContext_menu.add_checkbutton(label="Swap img-txt Sides", underline=0, variable=self.panes_swap_ew_var, command=self.swap_pane_sides)
        # Image Display Quality
        image_quality_menu = Menu(self.optionsMenu, tearoff=0)
        self.imageContext_menu.add_cascade(label="Image Display Quality", menu=image_quality_menu)
        for value in ["High", "Normal", "Low"]:
            image_quality_menu.add_radiobutton(label=value, variable=self.image_quality_var, value=value, command=self.set_image_quality)
        self.imageContext_menu.tk_popup(event.x_root, event.y_root)


    # Suggestion context menu
    def show_suggestionContext_menu(self, event):
        suggestionContext_menu = Menu(self.master, tearoff=0)
        # Selected Dictionary
        dictionaryMenu = Menu(suggestionContext_menu, tearoff=0)
        suggestionContext_menu.add_cascade(label="Dictionary", menu=dictionaryMenu)
        dictionaryMenu.add_checkbutton(label="English Dictionary", underline=0, variable=self.csv_english_dictionary, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Danbooru", underline=0, variable=self.csv_danbooru, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Derpibooru", underline=0, variable=self.csv_derpibooru, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="e621", underline=0, variable=self.csv_e621, command=self.update_autocomplete_dictionary)
        dictionaryMenu.add_separator()
        dictionaryMenu.add_command(label="Clear Selection", underline=0, command=self.clear_dictionary_csv_selection)
        # Suggestion Threshold
        suggestion_threshold_menu = Menu(suggestionContext_menu, tearoff=0)
        suggestionContext_menu.add_cascade(label="Threshold", menu=suggestion_threshold_menu)
        threshold_levels = ["Slow", "Normal", "Fast", "Faster"]
        for level in threshold_levels:
            suggestion_threshold_menu.add_radiobutton(label=level, variable=self.suggestion_threshold_var, value=level, command=self.set_suggestion_threshold)
        # Suggestion Quantity
        suggestion_quantity_menu = Menu(suggestionContext_menu, tearoff=0)
        suggestionContext_menu.add_cascade(label="Quantity", menu=suggestion_quantity_menu)
        for quantity in range(0, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(quantity), variable=self.suggestion_quantity_var, value=quantity, command=lambda suggestion_quantity=quantity: self.set_suggestion_quantity(suggestion_quantity))
        # Match Mode
        match_mode_menu = Menu(suggestionContext_menu, tearoff=0)
        suggestionContext_menu.add_cascade(label="Match Mode", menu=match_mode_menu)
        match_modes = {"Match Whole String": False, "Match Last Word": True}
        for mode, value in match_modes.items():
            match_mode_menu.add_radiobutton(label=mode, variable=self.last_word_match_var, value=value)
        suggestionContext_menu.tk_popup(event.x_root, event.y_root)


    def custom_select_word_for_text(self, event, text_widget):
        widget = text_widget
        separators = " ,.-|()[]<>\\/\"'{}:;!@#$%^&*+=~`?"
        click_index = widget.index(f"@{event.x},{event.y}")
        line, char_index = map(int, click_index.split("."))
        line_text = widget.get(f"{line}.0", f"{line}.end")
        if char_index >= len(line_text):
            return "break"
        if line_text[char_index] in separators:
            widget.tag_remove("sel", "1.0", "end")
            widget.tag_add("sel", f"{line}.{char_index}", f"{line}.{char_index + 1}")
        else:
            word_start = char_index
            while word_start > 0 and line_text[word_start - 1] not in separators:
                word_start -= 1
            word_end = char_index
            while word_end < len(line_text) and line_text[word_end] not in separators:
                word_end += 1
            widget.tag_remove("sel", "1.0", "end")
            widget.tag_add("sel", f"{line}.{word_start}", f"{line}.{word_end}")
        widget.mark_set("insert", f"{line}.{char_index + 1}")
        return "break"


    def custom_select_line_for_text(self, event, text_widget):
        widget = text_widget
        click_index = widget.index(f"@{event.x},{event.y}")
        line, _ = map(int, click_index.split("."))
        widget.tag_remove("sel", "1.0", "end")
        widget.tag_add("sel", f"{line}.0", f"{line}.end")
        widget.mark_set("insert", f"{line}.0")
        return "break"


    def custom_select_word_for_entry(self, event, entry_widget):
        widget = entry_widget
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


    def select_all_in_entry(self, event, entry_widget):
        entry_widget.selection_range(0, 'end')
        return "break"


    def get_default_font(self):
        self.current_font = self.text_box.cget("font")
        self.current_font_name = self.text_box.tk.call("font", "actual", self.current_font, "-family")
        self.current_font_size = self.text_box.tk.call("font", "actual", self.current_font, "-size")
        self.default_font = self.current_font_name
        self.default_font_size = self.current_font_size


#endregion
################################################################################################################################################
#region - Additional Interface Setup


# --------------------------------------
# Browse button context menu
# --------------------------------------
    def open_browse_context_menu(self, event):
        try:
            self.browse_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.browse_context_menu.grab_release()


    def set_text_file_path(self, path=None):
        if path == None:
            self.text_dir = filedialog.askdirectory()
        else:
            self.text_dir = path
        if not self.text_dir:
            return
        self.text_files = []
        for image_file in self.image_files:
            text_filename = os.path.splitext(os.path.basename(image_file))[0] + ".txt"
            text_file_path = os.path.join(self.text_dir, text_filename)
            if not os.path.exists(text_file_path):
                self.new_text_files.append(text_filename)
            self.text_files.append(text_file_path)
        self.show_pair()
        self.update_text_path_indicator()


    def update_text_path_indicator(self):
        if os.path.normpath(self.text_dir) != os.path.normpath(self.image_dir.get()):
            self.text_path_indicator.config(bg="#5da9be")
            self.text_path_tooltip.config(f"Text Path: {os.path.normpath(self.text_dir)}", 10, 6, 12)
        else:
            self.text_path_indicator.config(bg="#f0f0f0")
            self.text_path_tooltip.config("Text Path: Same as image path", 10, 6, 12)


# --------------------------------------
# Directory entry context menu helpers
# --------------------------------------
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


# --------------------------------------
# Index entry context menu helpers
# --------------------------------------
    def open_index_context_menu(self, event):
        try:
            self.index_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.index_context_menu.grab_release()


    def index_goto(self, index=None):
        self.image_index_entry.delete(0, "end")
        self.image_index_entry.insert(0, 1)
        self.jump_to_image(index)


    def index_goto_random(self, event=None):
        total_images = len(self.image_files)
        random_index = self.current_index
        while random_index == self.current_index:
            random_index = numpy.random.randint(total_images)
        self.image_index_entry.delete(0, "end")
        self.image_index_entry.insert(0, random_index + 1)
        self.jump_to_image(random_index)


    def index_goto_next_empty(self, event=None):
        if not self.check_if_directory():
            return
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


# --------------------------------------
# Misc setup
# --------------------------------------
    def enable_menu_options(self):
        tool_commands =       [
                             "Batch Operations",
                             "Edit Current pair",
                             "Open Current Directory...",
                             "Open Current Image...",
                             "Edit Image...",
                             "Next Empty Text File",
                             "Open Image-Grid...",
                             ]
        options_commands =   [
                              "Options",
                              "Loading Order",
                              "Autocomplete",
                              "Reset Settings"
                              ]
        for t_command in tool_commands:
            self.toolsMenu.entryconfig(t_command, state="normal")
        for o_command in options_commands:
            self.optionsMenu.entryconfig(o_command, state="normal")
        self.browse_context_menu.entryconfig("Set Text File Path...", state="normal")
        self.browse_context_menu.entryconfig("Reset Text Path To Image Path", state="normal")
        self.dir_context_menu.entryconfig("Set Text File Path...", state="normal")
        self.dir_context_menu.entryconfig("Reset Text Path To Image Path", state="normal")
        self.index_pair_label.configure(state="normal")
        self.image_index_entry.configure(state="normal")
        self.total_images_label.configure(state="normal")
        self.save_button.configure(state="normal")
        self.next_button.configure(state="normal")
        self.prev_button.configure(state="normal")
        self.auto_save_checkbutton.configure(state="normal")
        # Bindings
        self.suggestion_textbox.bind("<Button-3>", self.show_suggestionContext_menu)
        self.image_index_entry.bind("<Button-3>", self.open_index_context_menu)
        self.total_images_label.bind("<Button-3>", self.open_index_context_menu)
        self.index_pair_label.bind("<Button-3>", self.open_index_context_menu)


    def toggle_save_button_height(self, event=None, reset=None):
        if reset:
            self.big_save_button_var.set(True)
            self.save_button.config(padding=(1, 1))
            return
        else:
            if self.big_save_button_var.get():
                self.save_button.config(padding=(5, 5))
            else:
                self.save_button.config(padding=(1, 1))


    def toggle_zoom_popup(self, event=None):
        new_state = not self.popup_zoom.zoom_enabled.get()
        self.popup_zoom.zoom_enabled.set(new_state)
        self.toggle_zoom_var.set(new_state)
        self.options_subMenu.entryconfig("Toggle Zoom", variable=self.toggle_zoom_var)
        if hasattr(self, 'imageContext_menu'):
            self.imageContext_menu.entryconfig("Toggle Zoom", variable=self.toggle_zoom_var)
        state, text = ("disabled", "") if new_state else ("normal", "Double-Click to open in system image viewer \n\nMiddle click to open in file explorer\n\nALT+Left/Right or Mouse-Wheel to move between img-txt pairs")
        self.image_preview_tooltip.config(state=state, text=text)
        if new_state:
            self.popup_zoom.update_zoom(event)
        else:
            self.popup_zoom.hide_zoom(event)


# --------------------------------------
# PanedWindow
# --------------------------------------
    def configure_pane_position(self):
        window_width = self.master.winfo_width()
        self.primary_paned_window.sash_place(0, window_width // 2, 0)
        self.configure_pane()


    def swap_pane_sides(self, swap_state=None):
        if swap_state is None:
            swap_state = self.panes_swap_ew_var.get()
        else:
            self.panes_swap_ew_var.set(swap_state)
        self.primary_paned_window.remove(self.master_image_frame)
        self.primary_paned_window.remove(self.master_control_frame)
        if swap_state:
            self.primary_paned_window.add(self.master_control_frame)
            self.primary_paned_window.add(self.master_image_frame)
        else:
            self.primary_paned_window.add(self.master_image_frame)
            self.primary_paned_window.add(self.master_control_frame)
        self.master.after_idle(self.configure_pane_position)


    def swap_pane_orientation(self, swap_state=None):
        if swap_state is None:
            swap_state = self.panes_swap_ns_var.get()
        else:
            self.panes_swap_ns_var.set(swap_state)
        new_orient = 'vertical' if swap_state else 'horizontal'
        self.primary_paned_window.configure(orient=new_orient)
        if new_orient == 'horizontal':
            self.master.minsize(0, 200)
        else:
            self.master.minsize(200, 0)
        self.master.after_idle(self.configure_pane_position)


    def snap_sash_to_half(self, event):
        total_width = self.primary_paned_window.winfo_width()
        half_point = total_width // 2
        sash_pos = self.primary_paned_window.sash_coord(0)[0]
        snap_threshold = 75
        if abs(sash_pos - half_point) < snap_threshold:
            self.primary_paned_window.sash_place(0, half_point, 0)
        self.configure_pane()
        self.primary_paned_window.after(250, self.refresh_image)


    def configure_pane(self):
        self.primary_paned_window.paneconfigure(self.master_image_frame, minsize=200, stretch="always")
        self.primary_paned_window.paneconfigure(self.master_control_frame, minsize=200, stretch="always")


#endregion
################################################################################################################################################
#region - Alt-UI Setup


    def show_batch_tag_edit(self, event=None):
        parent = self
        root = self.master
        version = VERSION
        menu = self.batch_operations_menu
        text_files = self.text_files
        self.batch_tag_edit.setup_window(parent, root, version, menu, text_files)
        self.update_ui_state("BatchTagEdit")


    def show_batch_resize_images(self, event=None):
        parent = self
        root = self.master
        version = VERSION
        menu = self.batch_operations_menu
        path = self.image_dir.get()
        self.batch_resize_images.setup_window(parent, root, version, menu, path)
        self.update_ui_state("BatchResizeImages")


    def show_find_dupe_file(self, event=None):
        parent = self
        root = self.master
        version = VERSION
        menu = self.batch_operations_menu
        path = self.image_dir.get()
        self.find_dupe_file.setup_window(parent, root, version, menu, path)
        self.update_ui_state("FindDupeFile")


# --------------------------------------
# Handle Primary Paned Window
# --------------------------------------
    def show_primary_paned_window(self, event=None):
        self.primary_paned_window.grid()
        self.update_ui_state("ImgTxtViewer")


    def hide_primary_paned_window(self, event=None):
        self.primary_paned_window.grid_remove()


# --------------------------------------
# Handle UI State
# --------------------------------------
    def toggle_alt_ui_menus(self):
        menu = self.batch_operations_menu
        menu_items = {
            "BatchResizeImages": "Batch Resize Images...",
            "BatchTagEdit": "Batch Tag Edit...",
            "FindDupeFile": "Find Duplicate Files..."
            }
        if self.ui_state.get("ImgTxtViewer", False):
            for menu_label in menu_items.values():
                menu.entryconfig(menu_label, state="normal")
        else:
            for key, state in self.ui_state.items():
                menu_label = menu_items.get(key)
                if menu_label:
                    if state:
                        menu.entryconfig(menu_label, state="normal")
                    else:
                        menu.entryconfig(menu_label, state="disabled")


    def update_ui_state(self, key):
        for k in self.ui_state:
            self.ui_state[k] = False
        if key in self.ui_state:
            self.ui_state[key] = True
        self.toggle_alt_ui_menus()


#endregion
################################################################################################################################################
#region - Thumbnail Panel


    def debounce_update_thumbnail_panel(self, event):
        if self.update_thumbnail_id is not None:
            self.master.after_cancel(self.update_thumbnail_id)
        self.update_thumbnail_id = self.master.after(250, self.update_thumbnail_panel)


    def update_thumbnail_panel(self):
        # Clear only if necessary
        if len(self.thumbnail_panel.winfo_children()) != len(self.image_files):
            for widget in self.thumbnail_panel.winfo_children():
                widget.destroy()
        if not self.thumbnails_visible.get() or not self.image_files:
            self.thumbnail_panel.grid_remove()
            return
        self.thumbnail_panel.grid()
        thumbnail_width = self.thumbnail_width.get()
        panel_width = self.thumbnail_panel.winfo_width() or self.master_image_frame.winfo_width()
        num_thumbnails = max(1, panel_width // (thumbnail_width + 10))
        # Handle edge cases: Adjust start index to avoid wrapping
        half_visible = num_thumbnails // 2
        if self.current_index < half_visible:
            # If near the start, display from the first image
            start_index = 0
        elif self.current_index >= len(self.image_files) - half_visible:
            # If near the end, shift the view back to fit thumbnails
            start_index = max(0, len(self.image_files) - num_thumbnails)
        else:
            # Otherwise, center the current index
            start_index = self.current_index - half_visible
        # Ensure the correct number of thumbnails are displayed
        total_thumbnails = min(len(self.image_files), num_thumbnails)
        thumbnail_buttons = []
        for thumbnail_index in range(total_thumbnails):
            index = start_index + thumbnail_index
            image_file = self.image_files[index]
            # Use cached image info or load it if not present
            if image_file not in self.image_info_cache:
                self.image_info_cache[image_file] = self.get_image_info(image_file)
            image_info = self.image_info_cache[image_file]
            # Generate or retrieve cached thumbnail
            cache_key = (image_file, thumbnail_width)
            thumbnail_photo = self.thumbnail_cache.get(cache_key)
            if not thumbnail_photo:
                with Image.open(image_file) as img:
                    img.thumbnail((thumbnail_width, thumbnail_width), self.quality_filter)
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")
                    padded_img = ImageOps.pad(img, (thumbnail_width, thumbnail_width), color=(0, 0, 0, 0))
                    thumbnail_photo = ImageTk.PhotoImage(padded_img)
                    self.thumbnail_cache[cache_key] = thumbnail_photo
            # Create the thumbnail button
            thumbnail_button = ttk.Button(self.thumbnail_panel, image=thumbnail_photo, cursor="hand2", command=lambda idx=index: self.jump_to_image(idx))
            thumbnail_button.image = thumbnail_photo
            # Highlight the current index
            if index == self.current_index:
                thumbnail_button.config(style="Highlighted.TButton")
            # Bind events
            thumbnail_button.bind("<Button-3>", lambda event, btn=thumbnail_button, idx=index:self.show_thumbContext_menu(btn, event, idx))
            thumbnail_button.bind("<MouseWheel>", self.mouse_scroll)
            ToolTip.create(thumbnail_button, f"#{index + 1} | {image_info['filename']} | {image_info['resolution']} | "f"{image_info['size']} | {image_info['color_mode']}", delay=100, pady=-25, origin='widget')
            # Add to the list of thumbnail buttons
            thumbnail_buttons.append(thumbnail_button)
        # Display the thumbnails
        for thumbnail_index, button in enumerate(thumbnail_buttons):
            button.grid(row=0, column=thumbnail_index)
        self.thumbnail_panel.update_idletasks()


    def show_thumbContext_menu(self, thumbnail_button, event, index):
        thumb_menu = Menu(thumbnail_button, tearoff=0)
        # Open Image
        thumb_menu.add_command(label="Open Image", command=lambda: self.open_image(index=index))
        thumb_menu.add_command(label="Delete Pair", command=lambda: self.delete_pair(index=index))
        thumb_menu.add_command(label="Edit Image", command=lambda: self.open_image_in_editor(index=index))
        thumb_menu.add_separator()
        # Toggle Thumbnail Panel
        thumb_menu.add_checkbutton(label="Toggle Thumbnail Panel", variable=self.thumbnails_visible, command=self.update_thumbnail_panel)
        # Thumbnail Size
        thumbnail_size_menu = Menu(thumb_menu, tearoff=0)
        thumb_menu.add_cascade(label="Thumbnail Size", menu=thumbnail_size_menu)
        thumbnail_sizes = {"Small": 25, "Medium": 50, "Large": 100}
        for label, size in thumbnail_sizes.items():
            thumbnail_size_menu.add_radiobutton(label=label, variable=self.thumbnail_width, value=size, command=self.update_thumbnail_panel)
        thumb_menu.tk_popup(event.x_root, event.y_root)


    def set_custom_ttk_button_highlight_style(self):
        style = ttk.Style(self.master)
        style.configure("Highlighted.TButton", background="#005dd7")
        style.configure("Red.TButton", foreground="red")
        style.configure("Blue.TButton", foreground="blue")


#endregion
################################################################################################################################################
#region - Autocomplete


### Display Suggestions ##################################################


    def handle_suggestion_event(self, event):
        keysym = event.keysym
        if keysym == "Tab":
            if self.selected_suggestion_index < len(self.suggestions):
                selected_suggestion = self.suggestions[self.selected_suggestion_index]
                if isinstance(selected_suggestion, tuple):
                    selected_suggestion = selected_suggestion[0]
                self.insert_selected_suggestion(selected_suggestion.strip())
            self.clear_suggestions()
        elif keysym in ("Alt_L", "Alt_R"):
            if self.suggestions and not self.is_alt_arrow_pressed:
                self.selected_suggestion_index = (self.selected_suggestion_index - 1) % len(self.suggestions) if keysym == "Alt_R" else (self.selected_suggestion_index + 1) % len(self.suggestions)
                self.highlight_suggestions()
            self.is_alt_arrow_pressed = False
        elif keysym in ("Up", "Down", "Left", "Right") or event.char == ",":
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
        def on_mouse_hover(tag_name, highlight, event=None):
            if highlight:
                self.suggestion_textbox.tag_config(tag_name, relief='raised', borderwidth=1)
                self.suggestion_textbox.config(cursor="hand2")
            else:
                self.suggestion_textbox.tag_config(tag_name, relief='flat', borderwidth=0)
                self.suggestion_textbox.config(cursor="")
        self.suggestion_textbox.config(state='normal')
        self.suggestion_textbox.delete('1.0', 'end')
        configured_colors = set()
        num_suggestions = len(self.suggestions)
        for index, (suggestion_text, classifier_id) in enumerate(self.suggestions):
            classifier_id = classifier_id[0]
            color_index = int(classifier_id) % len(self.suggestion_colors) if classifier_id and classifier_id.isdigit() else 0
            suggestion_color = self.suggestion_colors[color_index]
            bullet_symbol = "⚫" if index == self.selected_suggestion_index else "⚪"
            tag_name = f"suggestion_tag_{index}"
            self.suggestion_textbox.insert('end', bullet_symbol)
            self.suggestion_textbox.insert('end', f" {suggestion_text} ", (tag_name, suggestion_color))
            if suggestion_color not in configured_colors:
                self.suggestion_textbox.tag_config(suggestion_color, foreground=suggestion_color, font=('Segoe UI', '9'))
                configured_colors.add(suggestion_color)
            self.suggestion_textbox.tag_bind(tag_name, '<Button-1>', partial(self.on_suggestion_click, index))
            self.suggestion_textbox.tag_bind(tag_name, '<Enter>', partial(on_mouse_hover, tag_name, True))
            self.suggestion_textbox.tag_bind(tag_name, '<Leave>', partial(on_mouse_hover, tag_name, False))
            if index < num_suggestions - 1:
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


    def on_suggestion_click(self, suggestion_index, event=None):
        selected_suggestion, _ = self.suggestions[suggestion_index]
        self.insert_selected_suggestion(selected_suggestion.strip())
        self.clear_suggestions()


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
            self.autocomplete = Autocomplete("None", include_my_tags=self.use_mytags_var.get())
        else:
            self.autocomplete = Autocomplete(self.selected_csv_files[0], include_my_tags=self.use_mytags_var.get())
            for csv_file in self.selected_csv_files[1:]:
                self.autocomplete.autocomplete_dict.update(Autocomplete(csv_file).autocomplete_dict, include_my_tags=self.use_mytags_var.get())
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
#region - TextBox Highlights


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
        color_dict = {}
        for word in selected_words:
            if len(word) < 3:
                continue
            pattern = re.escape(word)
            matches = [match for match in re.finditer(pattern, self.text_box.get("1.0", "end"))]
            if len(matches) > 1:
                if word not in color_dict and self.pastel_colors:
                    color = self.pastel_colors.pop(0)
                    color_dict[word] = color
                    self.text_box.tag_config(word, background=color_dict[word], foreground="black")
                for match in matches:
                    start = match.start()
                    end = match.end()
                    self.text_box.tag_add(word, f"1.0 + {start} chars", f"1.0 + {end} chars")


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
        color_dict = {}
        for word in set(words):
            if len(word) < 3 or words.count(word) == 1:
                continue
            if word not in color_dict and self.pastel_colors:
                color = self.pastel_colors.pop(0)
                color_dict[word] = color
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
            self.remove_tag()
            if not self.custom_highlight_string_var.get():
                return
            words = self.custom_highlight_string_var.get().split('+')
            for i, word in enumerate(words):
                pattern = word.strip()
                if len(pattern) < 2:
                    continue
                color = f"{self.pastel_colors[i % len(self.pastel_colors)]}"
                tag_name = f"highlight_{i}"
                self.text_box.tag_config(tag_name, background=color)
                if self.highlight_use_regex_var.get():
                    matches = [match for match in re.finditer(pattern, self.text_box.get("1.0", "end"))]
                else:
                    pattern = re.escape(pattern)
                    matches = [match for match in re.finditer(pattern, self.text_box.get("1.0", "end"))]
                if matches:
                    for match in matches:
                        start = match.start()
                        end = match.end()
                        self.text_box.tag_add(tag_name, f"1.0 + {start} chars", f"1.0 + {end} chars")


    def remove_highlight(self):
        self.text_box.tag_remove("highlight", "1.0", "end")
        self.master.after(100, lambda: self.remove_tag())


    def remove_tag(self):
        self.highlight_all_duplicates_var.set(False)
        for tag in self.text_box.tag_names():
            self.text_box.tag_remove(tag, "1.0", "end")


#endregion
################################################################################################################################################
#region - Primary Functions


    def load_pairs(self):
        self.master.title(self.title)
        self.info_text.pack_forget()
        current_image_path = self.image_files[self.current_index] if self.image_files else None
        self.refresh_file_lists()
        self.enable_menu_options()
        self.create_text_box()
        self.restore_previous_index(current_image_path)
        self.update_pair(save=False)
        self.configure_pane_position()
        self.calculate_file_stats()


    def restore_previous_index(self, current_image_path):
        if current_image_path:
            try:
                self.current_index = self.image_files.index(current_image_path)
            except ValueError:
                self.current_index = 0


    def refresh_file_lists(self):
        self.image_files = []
        self.text_files = []
        self.new_text_files = []
        sort_key = self.get_file_sort_key()
        files_in_dir = sorted(os.listdir(self.image_dir.get()), key=sort_key, reverse=self.reverse_load_order_var.get())
        self.validate_files(files_in_dir)
        self.original_image_files = list(self.image_files)
        self.original_text_files = list(self.text_files)
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
            with Image.open(image_file) as img:
                self.original_image_size = img.size
                max_size = (self.quality_max_size, self.quality_max_size)
                img.thumbnail(max_size, self.quality_filter)
                if img.format == 'GIF':
                    self.gif_frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
                    self.frame_durations = [frame.info['duration'] for frame in ImageSequence.Iterator(img)]
                else:
                    self.gif_frames = [img.copy()]
                    self.frame_durations = [None]
        except (FileNotFoundError, UnidentifiedImageError):
            self.update_image_file_count()
            self.image_files.remove(image_file)
            if text_file in self.text_files:
                self.text_files.remove(text_file)
            return
        return img


    def display_image(self):
        try:
            self.image_file = self.image_files[self.current_index]
            text_file = self.text_files[self.current_index] if self.current_index < len(self.text_files) else None
            image = self.load_image_file(self.image_file, text_file)
            resize_event = Event()
            resize_event.height = self.primary_display_image.winfo_height()
            resize_event.width = self.primary_display_image.winfo_width()
            resized_image, resized_width, resized_height = self.resize_and_scale_image(image, resize_event.width, resize_event.height, resize_event)
            if image.format == 'GIF':
                self.frame_iterator = iter(self.gif_frames)
                self.current_frame_index = 0
                self.display_animated_gif()
                if self.edit_panel_visible_var.get():
                    self.edit_panel.toggle_edit_panel_widgets("disabled")
            else:
                self.frame_iterator = None
                self.current_frame_index = 0
                if self.edit_panel_visible_var.get():
                    self.edit_panel.toggle_edit_panel_widgets("normal")
            self.popup_zoom.set_image(image=image, path=self.image_file)
            self.popup_zoom.set_resized_image(resized_image, resized_width, resized_height)
            self.current_image = resized_image
            return text_file, image, resize_event.width, resize_event.height
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
                scale_factor = min(self.primary_display_image.winfo_width() / start_width, self.primary_display_image.winfo_height() / start_height)
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
                self.primary_display_image.config(image=self.current_gif_frame_image)
                self.primary_display_image.image = self.current_gif_frame_image
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
        aspect_ratio = start_width / start_height
        if event is not None:
            scale_factor = min(event.width / start_width, event.height / start_height)
        else:
            scale_factor = min(max_img_width / start_width, max_img_height / start_height)
        new_width = min(int(start_width * scale_factor), max_img_width)
        new_height = int(new_width / aspect_ratio)
        if new_height > max_img_height:
            new_height = max_img_height
            new_width = int(new_height * aspect_ratio)
        resized_image = input_image.resize((new_width, new_height), quality_filter)
        output_image = ImageTk.PhotoImage(resized_image)
        self.primary_display_image.config(image=output_image)
        self.primary_display_image.image = output_image
        percent_scale = int((new_width / start_width) * 100)
        self.update_imageinfo(percent_scale)
        return resized_image, new_width, new_height


    def show_pair(self):
        if self.image_files:
            text_file, image, max_img_width, max_img_height = self.display_image()
            self.load_text_file(text_file)
            self.primary_display_image.config(width=max_img_width, height=max_img_height)
            self.original_image = image
            self.current_image = self.original_image.copy()
            self.current_max_img_height = max_img_height
            self.current_max_img_width = max_img_width
            self.primary_display_image.unbind("<Configure>")
            self.primary_display_image.bind("<Configure>", self.resize_and_scale_image_event)
            self.toggle_list_mode()
            self.clear_suggestions()
            self.highlight_custom_string()
            self.highlight_all_duplicates_var.set(False)
            self.update_thumbnail_panel()
        else:
            self.primary_display_image.unbind("<Configure>")


    def resize_and_scale_image_event(self, event):
        display_width = event.width if event.width else self.primary_display_image.winfo_width()
        display_height = event.height if event.height else self.primary_display_image.winfo_height()
        self.resize_and_scale_image(self.current_image, display_width, display_height, None, Image.NEAREST)


    def refresh_image(self):
        if self.image_files:
            self.display_image()
            self.update_thumbnail_panel()


    def debounce_refresh_image(self, event):
        if hasattr(self, 'text_box'):
            if self.is_resizing_id:
                root.after_cancel(self.is_resizing_id)
            self.is_resizing_id = root.after(250, self.refresh_image)


    def handle_window_configure(self, event):  # Window resize
        if event.widget == self.master:
            current_size = (event.width, event.height)
            if current_size != self.previous_window_size:
                self.previous_window_size = current_size
                self.debounce_refresh_image(event)


    def update_imageinfo(self, percent_scale):
        if self.image_files:
            self.image_file = self.image_files[self.current_index]
            if self.image_file not in self.image_info_cache:
                self.image_info_cache[self.image_file] = self.get_image_info(self.image_file)
            image_info = self.image_info_cache[self.image_file]
            self.label_image_stats.config(text=f"{image_info['filename']}  |  {image_info['resolution']}  |  {percent_scale}%  |  {image_info['size']}  |  {image_info['color_mode']}", anchor="w")


    def get_image_info(self, image_file):
        with Image.open(image_file) as image:
            width, height = image.size
            color_mode = image.mode
        size = os.path.getsize(image_file)
        size_kb = size / 1024
        size_str = f"{round(size_kb)} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 2)} MB"
        filename = os.path.basename(image_file)
        filename = (filename[:61] + '(...)') if len(filename) > 64 else filename
        return {"filename": filename, "resolution": f"{width} x {height}", "size": size_str, "color_mode": color_mode}


#endregion
################################################################################################################################################
#region - Navigation


    def update_pair(self, direction=None, save=True, step=1):
        if self.image_dir.get() == "Choose Directory..." or len(self.image_files) == 0:
            return
        self.is_alt_arrow_pressed = True
        self.check_image_dir()
        if not self.text_modified_var:
            self.master.title(self.title)
        self.text_box.config(undo=False)
        self.text_box.edit_reset()
        if self.auto_save_var.get() and save:
            self.save_text_file()
        if len(self.image_files) > 0:
            if direction == 'next':
                self.current_index = (self.current_index + step) % len(self.image_files)
            elif direction == 'prev':
                self.current_index = (self.current_index - step) % len(self.image_files)
            self.show_pair()
            self.image_index_entry.delete(0, "end")
            self.image_index_entry.insert(0, f"{self.current_index + 1}")


    def next_pair(self, event=None, step=1):
        self.check_working_directory()
        if event is not None and event.state & 0x0001:  # Check if SHIFT is held
            step = 5
        self.update_pair('next', step=step)


    def prev_pair(self, event=None, step=1):
        self.check_working_directory()
        if event is not None and event.state & 0x0001:  # Check if SHIFT is held
            step = 5
        self.update_pair('prev', step=step)


    def jump_to_image(self, index=None, event=None):
        try:
            self.check_image_dir()
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
                pass
            self.image_index_entry.delete(0, "end")
            self.image_index_entry.insert(0, index + 1)
        except ValueError:
            self.image_index_entry.delete(0, "end")
            self.image_index_entry.insert(0, self.current_index + 1)


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
        self.image_files.sort(key=self.get_file_sort_key(), reverse=self.reverse_load_order_var.get())
        self.text_files = [os.path.splitext(file)[0] + '.txt' for file in self.image_files]
        self.total_images_label.config(text=f"of {len(self.image_files)}")


    def mouse_scroll(self, event):
        if self.popup_zoom.zoom_enabled.get():
            return
        current_time = time.time()
        scroll_debounce_time = 0.05
        if current_time - self.last_scroll_time < scroll_debounce_time:
            return
        self.last_scroll_time = current_time
        step = 5 if event.state & 0x0001 else 1  # Check if SHIFT is held
        if event.delta > 0:
            self.update_pair('next', step=step)
        else:
            self.update_pair('prev', step=step)

#endregion
################################################################################################################################################
#region - Text Options


    def refresh_text_box(self):
        self.check_working_directory()
        if not self.check_if_contains_images(self.image_dir.get()):
            return
        text_file = self.text_files[self.current_index]
        if text_file and os.path.isfile(text_file):
            with open(text_file, "r", encoding="utf-8") as f:
                file_content = f.read()
            text_box_content = self.text_box.get("1.0", "end-1c")
            if file_content != text_box_content:
                self.text_box.delete("1.0", "end")
                self.text_box.insert("end", file_content)
                self.text_modified_var = False
                self.master.title(self.title)
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
#region - Text Tools


    def search_and_replace(self):
        if not self.check_if_directory():
            return
        search_string = self.search_string_var.get()
        replace_string = self.replace_string_var.get()
        if not search_string:
            return
        confirm = messagebox.askokcancel("Search and Replace", "This will replace all occurrences of the text\n\n{}\n\nWith\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(search_string, replace_string))
        if not confirm:
            return
        self.backup_text_files()
        if not self.filter_string_var.get():
            self.update_image_file_count()
        for text_file in self.text_files:
            try:
                with open(text_file, 'r', encoding="utf-8") as file:
                    filedata = file.read()
                if self.search_and_replace_regex.get():
                    filedata = re.sub(search_string, replace_string, filedata)
                else:
                    filedata = filedata.replace(search_string, replace_string)
                with open(text_file, 'w', encoding="utf-8") as file:
                    file.write(filedata)
            except Exception as e:
                messagebox.showerror("Error: search_and_replace()", f"An error occurred while trying to replace text in {text_file}.\n\n{e}")
        self.cleanup_all_text_files(show_confirmation=False)
        self.show_pair()
        messagebox.showinfo("Search and Replace", "Search and Replace completed successfully.")


    def prefix_text_files(self):
        if not self.check_if_directory():
            return
        prefix_text = self.prefix_string_var.get()
        if not prefix_text:
            return
        if not prefix_text.endswith(', '):
            prefix_text += ', '
        confirm = messagebox.askokcancel("Prefix", "This will prefix all text files with:\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(prefix_text))
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
            except Exception as e:
                messagebox.showerror("Error: prefix_text_files()", f"An error occurred while trying to prefix text in {text_file}.\n\n{e}")
        self.cleanup_all_text_files(show_confirmation=False)
        self.show_pair()
        messagebox.showinfo("Prefix", "Prefix completed successfully.")


    def append_text_files(self):
        if not self.check_if_directory():
            return
        append_text = self.append_string_var.get()
        if not append_text:
            return
        if not append_text.startswith(', '):
            append_text = ', ' + append_text
        confirm = messagebox.askokcancel("Append", "This will append all text files with:\n\n{}\n\nA backup will be created before making changes.\n\nDo you want to proceed?".format(append_text))
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
            except Exception as e:
                messagebox.showerror("Error: append_text_files()", f"An error occurred while trying to append text in {text_file}.\n\n{e}")
        self.cleanup_all_text_files(show_confirmation=False)
        self.show_pair()
        messagebox.showinfo("Append", "Append completed successfully.")


    def filter_text_image_pairs(self):  # Filter
        if not self.check_if_directory():
            return
        if not self.filter_empty_files_var.get():
            self.revert_text_image_filter()
        filter_string = self.filter_string_var.get()
        if not filter_string and not self.filter_empty_files_var.get():
            self.image_index_entry.delete(0, "end")
            self.image_index_entry.insert(0, "1")
            return
        self.filtered_image_files = []
        self.filtered_text_files = []
        for image_file in self.image_files:
            text_file = os.path.splitext(image_file)[0] + ".txt"
            filedata = ""
            try:
                with open(text_file, 'r', encoding="utf-8") as file:
                    filedata = file.read()
            except FileNotFoundError:
                text_file = text_file
            if self.filter_empty_files_var.get():
                if not filedata.strip():
                    self.filtered_image_files.append(image_file)
                    self.filtered_text_files.append(text_file)
            else:
                if self.filter_use_regex_var.get():
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
        self.image_files = self.filtered_image_files
        self.text_files = self.filtered_text_files
        if hasattr(self, 'total_images_label'):
            self.total_images_label.config(text=f"of {len(self.image_files)}")
        self.current_index = 0
        self.show_pair()
        messagebox.showinfo("Filter", f"Filter applied successfully.\n\n{len(self.image_files)} images found.")
        self.revert_filter_button.config(style="Red.TButton")
        self.revert_filter_button_tooltip.config(text="Filter is active\n\nClear any filtering applied")
        if not self.image_files:
            self.image_index_entry.delete(0, "end")
            self.image_index_entry.insert(0, "0")
            self.primary_display_image.config(image=self.blank_image)
            self.text_box.delete("1.0", "end")
            self.label_image_stats.config(text="No image! -- Check filters?", anchor="w")


    def revert_text_image_filter(self, clear=None): # Filter
        if clear:
            self.filter_string_var.set("")
            self.filter_use_regex_var.set(False)
            self.image_index_entry.delete(0, "end")
            self.image_index_entry.insert(0, "1")
        self.update_image_file_count()
        self.current_index = 0
        self.show_pair()
        messagebox.showinfo("Filter", "Filter has been cleared.")
        self.revert_filter_button.config(style="")
        self.revert_filter_button_tooltip.config(text="Filter is inactive\n\nClear any filtering applied")
        self.filter_empty_files_var.set(False)
        if self.filter_empty_files_var.get():
            self.toggle_filter_widgets(state=True)
        else:
            self.toggle_filter_widgets(state=False)


    def toggle_empty_files_filter(self): # Filter
        if self.filter_empty_files_var.get():
            self.image_index_entry.delete(0, "end")
            self.image_index_entry.insert(0, 1)
            self.filter_string_var.set("")
            self.filter_text_image_pairs()
            self.filter_use_regex_var.set(False)
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
                               self.regex_filter_checkbutton
                               ]:
                    widget.config(state="disabled")
            else:
                for widget in [
                               self.filter_label,
                               self.filter_entry,
                               self.filter_button,
                               self.regex_filter_checkbutton
                               ]:
                    widget.config(state="normal")


    def delete_tag_under_mouse(self, event):
        def set_text_highlight(tag, color, start=None, end=None):
            self.text_box.tag_config(tag, background=color)
            if start and end:
                self.text_box.tag_add(tag, start, end)

        def delete_tag():
            if self.delete_tag_job is not None:
                self.text_box.delete(f"{line_start}+{start_of_clicked_tag}c", f"{line_start}+{end_of_clicked_tag}c")
                cleaned_text = self.cleanup_text(self.text_box.get("1.0", "end"))
                cleaned_text = '\n'.join([line for line in cleaned_text.split('\n') if line.strip() != ''])
                self.text_box.delete("1.0", "end")
                self.text_box.insert("1.0", cleaned_text)
                set_text_highlight("highlight", "#5da9be")
                self.text_box.clipboard_get()
                self.delete_tag_job = None

        def get_cursor_and_line_text():
            cursor_pos = self.text_box.index(f"@{event.x},{event.y}")
            line_start = self.text_box.index(f"{cursor_pos} linestart")
            line_end = self.text_box.index(f"{cursor_pos} lineend")
            line_text = self.text_box.get(line_start, line_end)
            return cursor_pos, line_start, line_end, line_text

        def find_clicked_tag(line_text, cursor_pos):
            tags = [(match.group().strip(), match.start(), match.end()) for match in re.finditer(r'[^,]+', line_text)]
            for tag, start, end in tags:
                if start <= int(cursor_pos.split('.')[1]) <= end:
                    return tag, start, end
            return None, None, None

        if not self.cleaning_text_var.get():
            return
        cursor_pos, line_start, line_end, line_text = get_cursor_and_line_text()
        clicked_tag, start_of_clicked_tag, end_of_clicked_tag = find_clicked_tag(line_text, cursor_pos)
        if clicked_tag is None:
            return
        set_text_highlight("highlight", "#fd8a8a", f"{line_start}+{start_of_clicked_tag}c", f"{line_start}+{end_of_clicked_tag}c")
        self.text_box.update_idletasks()
        if self.delete_tag_job is not None:
            self.text_box.after_cancel(self.delete_tag_job)
        self.delete_tag_job = self.text_box.after(100, delete_tag)


    def collate_captions(self):
        if not self.check_if_directory():
            return
        initial_filename = os.path.basename(os.path.normpath(self.image_dir.get())) + ".txt"
        output_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Save Combined Captions As", initialfile=initial_filename, initialdir=self.image_dir.get())
        if not output_file:
            return
        try:
            with open(output_file, "w", encoding="utf-8") as outfile:
                for text_file in self.text_files:
                    if os.path.isfile(text_file):
                        with open(text_file, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read().strip() + "\n")
        except Exception as e:
            messagebox.showerror("Error: collate_captions()", f"An error occurred while collating captions:\n\n{e}")
            return
        if messagebox.askyesno("Success", f"All captions have been combined into:\n\n{output_file}.\n\nDo you want to open the output directory?"):
            os.startfile(os.path.dirname(output_file))


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
            messagebox.showerror("Error: expand_image()", f"Unsupported filetype: {file_extension.upper()}")
            return
        new_filename = f"{base_filename}_ex{file_extension}"
        new_filepath = os.path.join(self.image_dir.get(), new_filename)
        if os.path.exists(new_filepath):
            messagebox.showerror("Error: expand_image()", f'Output file:\n\n{os.path.normpath(new_filename)}\n\nAlready exists.')
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
        if not messagebox.askyesno("Expand Image", confirmation):
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
            messagebox.showerror("Error: expand_image()", f'Failed to process {filename}. Reason: {e}')


    def rename_and_convert_pairs(self):
        if not self.check_if_directory():
            return
        try:
            convert_confirmation = messagebox.askyesnocancel("Confirm: Rename and Convert Files",
                "Do you want to convert images as well?\n\n"
                "Yes: Rename and convert all images and text files.\n"
                "No: Only rename files.\n"
                "Cancel: Cancel the operation."
                )
            if convert_confirmation is None:
                return
            self.check_working_directory()
            target_dir = os.path.join(self.image_dir.get(), "Renamed Output")
            os.makedirs(target_dir, exist_ok=True)
            files = sorted(f for f in os.listdir(self.image_dir.get()) if f.endswith(tuple([".txt", ".jpg", ".jpeg", ".png", ".jfif", ".jpg_large", ".webp", ".bmp", ".gif"])))
            base_names = {}
            for filename in files:
                base_name, extension = os.path.splitext(filename)
                if base_name not in base_names:
                    base_names[base_name] = str(len(base_names) + 1).zfill(5)
                new_base_name = base_names[base_name]
                if extension == ".txt":
                    new_name = new_base_name + extension
                else:
                    if extension == ".gif" or convert_confirmation == False:
                        new_name = new_base_name + extension
                    else:
                        new_name = new_base_name + ".jpg"
                original_path = os.path.join(self.image_dir.get(), filename)
                new_path = os.path.join(target_dir, new_name)
                if convert_confirmation and extension in [".jpeg", ".png", ".jfif", ".jpg_large", ".webp", ".bmp"]:
                    with Image.open(original_path) as img:
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
            messagebox.showerror("Error: rename_and_convert_pairs()", "The specified directory does not exist.")
        except PermissionError:
            messagebox.showerror("Error: rename_and_convert_pairs()", "You do not have the necessary permissions to perform this operation.")
        except Exception as e:
            messagebox.showerror("Error: rename_and_convert_pairs()", f"An unexpected error occurred: {str(e)}")


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
        resize_image.ResizeTool(self.master, self, filepath, window_x, window_y, self.update_pair, self.jump_to_image)


    def upscale_image(self, batch):
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        if batch:
            x_offset = -225
            y_offset = 300
        else:
            x_offset = -135
            y_offset = 200
        window_x = root.winfo_x() + x_offset + main_window_width // 2
        window_y = root.winfo_y() - y_offset + main_window_height // 2
        filepath = self.image_files[self.current_index]
        upscale_image.Upscale(self, self.master, filepath, batch, window_x, window_y)


    def batch_crop_images(self):
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        window_x = root.winfo_x() + -155 + main_window_width // 2
        window_y = root.winfo_y() - 100 + main_window_height // 2
        filepath = str(self.image_dir.get())
        batch_crop_images.BatchCrop(self.master, filepath, window_x, window_y)


    def open_crop_tool(self):
        filepath = self.image_files[self.current_index]
        if filepath.lower().endswith('.gif'):
            messagebox.showerror("Error: open_crop_tool()", "Unsupported filetype: .GIF")
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


    def open_image_grid(self, event=None):
        if not self.image_files:
            return
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        window_x = root.winfo_x() + -330 + main_window_width // 2
        window_y = root.winfo_y() - 300 + main_window_height // 2
        image_grid.ImageGrid(self.master, self, window_x, window_y, self.jump_to_image)


    def open_image_in_editor(self, event=None, index=None):
        try:
            if self.image_files:
                app_path = self.external_image_editor_path
                image_index = index if index is not None else self.current_index
                image_path = self.image_files[image_index]
                subprocess.Popen([app_path, image_path])
        except FileNotFoundError:
            messagebox.showerror("Error: open_image_in_editor()", f"The specified image editor was not found:\n\n{app_path}")
        except PermissionError as e:
            messagebox.showerror("Error: open_image_in_editor()", f"Permission denied: {e}")
        except Exception as e:
            messagebox.showerror("Error: open_image_in_editor()", f"An error occurred while opening the image in the editor:\n\n{e}")


    def set_external_image_editor_path(self):
        response = messagebox.askyesnocancel("Set External Image Editor", f"Current external image editor is set to:\n\n{self.external_image_editor_path}\n\nDo you want to change it? (Yes/No)\n\nPress (Cancel) to reset to default (MS Paint).")
        if response is None:  # Cancel, reset
            self.external_image_editor_path = "mspaint"
            messagebox.showinfo("Reset", "External image editor path has been reset to mspaint.")
        elif response:  # Yes, set path
            app_path = filedialog.askopenfilename(title="Select Default Image Editor", filetypes=[("Executable or Python Script", "*.exe;*.py;*.pyw")])
            if app_path:
                self.external_image_editor_path = app_path
                messagebox.showinfo("Success", f"External image editor set to:\n\n{app_path}")
        else:  # No
            return


#endregion
################################################################################################################################################
#region - Misc Functions


    def sync_title_with_content(self, event=None):
        if event and self.ignore_key_event(event):
            return
        else:
            if self.current_index < len(self.text_files):
                text_file = self.text_files[self.current_index]
                try:
                    with open(text_file, 'r', encoding="utf-8") as file:
                        file_content = file.read()
                except FileNotFoundError:
                    file_content = ""
                if self.text_box.get("1.0", "end-1c") == file_content:
                    self.master.title(self.title)
                else:
                    self.master.title(self.title + " ⚪")


    def disable_button(self, event):
        return "break"


    def ignore_key_event(self, event):
        if event.keysym in ("Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"):
            return True
        if event.state & 0x4 and event.keysym == 's':  # CTRL+S
            return True
        return False


    def set_always_on_top(self, initial=False):
        if initial:
            self.always_on_top_var = BooleanVar(value=False)
        root.attributes('-topmost', self.always_on_top_var.get())


    def toggle_list_menu(self):
        if self.cleaning_text_var.get():
            self.options_subMenu.entryconfig("List View", state="normal")
        else:
            self.options_subMenu.entryconfig("List View", state="disabled")
            if self.list_mode_var.get():
                self.toggle_list_mode(skip=True)
            if not self.master.title().endswith(" ⚪"):
                if self.filepath_contains_images_var:
                    self.refresh_text_box()
            self.list_mode_var.set(False)


    def set_image_quality(self):
        quality_settings = {
            "High"  : (1536, Image.LANCZOS),
            "Normal": (1280, Image.BILINEAR),
            "Low"   : (768,  Image.NEAREST)
            }
        var = self.image_quality_var.get()
        if var in quality_settings:
            self.quality_max_size, self.quality_filter = quality_settings[var]
        self.refresh_image()


#endregion
################################################################################################################################################
#region - Calculate File Stats


    def calculate_file_stats(self, manual_refresh=None):
        self.caption_counter.clear()
        total_chars = total_words = total_captions = 0
        total_sentences = total_paragraphs = 0
        total_text_filesize = total_image_filesize = 0
        word_counter, char_counter = Counter(), Counter()
        image_resolutions_counter, aspect_ratios_counter = Counter(), Counter()
        unique_words, image_formats, longest_words = set(), set(), set()
        word_lengths, sentence_lengths = [], []
        file_word_counts, file_char_counts, file_caption_counts = [], [], []
        square_images = portrait_images = landscape_images = total_ppi = 0
        _, num_txt_files, num_img_files, formatted_total_files = self.filter_and_update_textfiles()

        # Process text files
        for text_file in self.text_files:
            try:
                filedata, words, sentences, paragraphs, captions = self.process_text_file(text_file)
                total_chars += len(filedata)
                total_words += len(words)
                word_counter.update(words)
                unique_words.update(words)
                char_counter.update(filedata)
                word_lengths.extend(len(word) for word in words)
                total_sentences += len(sentences)
                sentence_lengths.extend(len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences)
                total_paragraphs += len(paragraphs)
                self.update_caption_counter(captions)
                captions_count = len(captions)
                total_captions += captions_count
                file_word_counts.append((os.path.basename(text_file), len(words)))
                file_char_counts.append((os.path.basename(text_file), len(filedata)))
                file_caption_counts.append((os.path.basename(text_file), captions_count))
                for word in words:
                    longest_words.add(word)
                    if len(longest_words) > 5:
                        longest_words = set(sorted(longest_words, key=len, reverse=True)[:5])
                total_text_filesize += os.path.getsize(text_file)
            except FileNotFoundError: pass
            except Exception as e:
                messagebox.showerror("Error: calculate_file_stats()", f"An error occurred while processing {os.path.basename(text_file)}:\n\n{e}")

        # Process image files
        if self.process_image_stats_var.get():
            for image_file in self.image_files:
                try:
                    width, height, dpi, aspect_ratio, image_format = self.process_image_file(image_file)
                    total_image_filesize += os.path.getsize(image_file)
                    image_formats.add(image_format)
                    total_ppi += dpi[0]
                    image_resolutions_counter[(width, height)] += 1
                    aspect_ratios_counter[round(aspect_ratio, 2)] += 1
                    if aspect_ratio == 1:
                        square_images += 1
                    elif aspect_ratio > 1:
                        landscape_images += 1
                    else:
                        portrait_images += 1
                except FileNotFoundError: pass
                except Exception as e:
                    messagebox.showerror("Error: calculate_file_stats()", f"An error occurred while processing {os.path.basename(image_file)}:\n\n{e}")

        # Calculate averages
        avg_chars = total_chars / num_txt_files if num_txt_files > 0 else 0
        avg_words = total_words / num_txt_files if num_txt_files > 0 else 0
        avg_captions = total_captions / num_txt_files if num_txt_files > 0 else 0
        avg_ppi = total_ppi / num_img_files if num_img_files > 0 else 0
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        median_word_length = statistics.median(word_lengths) if word_lengths else 0
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

        # Format statistics
        most_common_words = word_counter.most_common(50)
        most_common_words = sorted(most_common_words, key=lambda x: (-x[1], x[0].lower()))
        formatted_common_words = "\n".join([f"{count:03}x, {word}" for word, count in most_common_words])
        most_common_chars = char_counter.most_common()
        formatted_common_chars = "\n".join([f"{count:03}x, {char}" for char, count in most_common_chars])
        self.sorted_captions = self.get_sorted_captions()
        formatted_captions = self.get_formatted_captions(self.sorted_captions)
        sorted_resolutions = sorted(image_resolutions_counter.items(), key=lambda x: (-x[1], -(x[0][0] * x[0][1])))
        formatted_resolutions = "\n".join([f"{count:03}x, {res[0]}x{res[1]}" for res, count in sorted_resolutions])
        sorted_aspect_ratios = sorted(aspect_ratios_counter.items(), key=lambda x: (-x[1], x[0]))
        formatted_aspect_ratios = "\n".join([f"{count:03}x, {aspect_ratio}" for aspect_ratio, count in sorted_aspect_ratios])
        formatted_longest_words = "\n".join([f"- {word}" for word in sorted(longest_words, key=lambda x: (-len(x), x.lower()))])
        top_5_files_words = sorted(file_word_counts, key=lambda x: (-x[1], x[0].lower()))[:5]
        formatted_top_5_files_words = "\n".join([f"{count}x, {file}" for file, count in top_5_files_words])
        top_5_files_chars = sorted(file_char_counts, key=lambda x: (-x[1], x[0].lower()))[:5]
        formatted_top_5_files_chars = "\n".join([f"{count}x, {file}" for file, count in top_5_files_chars])
        top_5_files_captions = sorted(file_caption_counts, key=lambda x: (-x[1], x[0].lower()))[:5]
        formatted_top_5_files_captions = "\n".join([f"{count}x, {file}" for file, count in top_5_files_captions])
        word_page_count = total_words / 500 if total_words > 0 else 0
        formatted_filepath = os.path.normpath(self.image_dir.get())
        formatted_total_filesize = self.format_filesize(total_image_filesize + total_text_filesize)
        stats = {
            'filepath': formatted_filepath,
            'formatted_total_files': formatted_total_files,
            'total_text_filesize': self.format_filesize(total_text_filesize),
            'total_image_filesize': self.format_filesize(total_image_filesize),
            'total_filesize': formatted_total_filesize,
            'total_chars': total_chars,
            'total_words': total_words,
            'word_page_count': word_page_count,
            'total_captions': total_captions,
            'total_sentences': total_sentences,
            'total_paragraphs': total_paragraphs,
            'unique_words': unique_words,
            'avg_chars': avg_chars,
            'avg_words': avg_words,
            'avg_captions': avg_captions,
            'avg_word_length': avg_word_length,
            'median_word_length': median_word_length,
            'avg_sentence_length': avg_sentence_length,
            'image_formats': image_formats,
            'square_images': square_images,
            'portrait_images': portrait_images,
            'landscape_images': landscape_images,
            'avg_ppi': avg_ppi,
            'formatted_resolutions': formatted_resolutions,
            'formatted_aspect_ratios': formatted_aspect_ratios,
            'formatted_top_5_files_words': formatted_top_5_files_words,
            'formatted_top_5_files_chars': formatted_top_5_files_chars,
            'formatted_top_5_files_captions': formatted_top_5_files_captions,
            'formatted_longest_words': formatted_longest_words,
            'formatted_common_words': formatted_common_words,
            'formatted_common_chars': formatted_common_chars,
            'formatted_captions': formatted_captions
        }
        stats_text = self.format_stats_text(stats)
        self.update_tab8_textbox(stats_text, manual_refresh)


    def format_stats_text(self, stats):
        stats_text = (
            f"{stats['filepath']}\n\n"
            f"--- File Summary ---\n"
            f"Total Files: {stats['formatted_total_files']}\n"
            f"Total Text Filesize: {stats['total_text_filesize']}\n"
            f"Total Image Filesize: {stats['total_image_filesize']}\n"
            f"Total Filesize: {stats['total_filesize']}\n"

            f"\n--- Text Statistics ---\n"
            f"Total Characters: {stats['total_chars']}\n"
            f"Total Words: {stats['total_words']} ({stats['word_page_count']:.2f} pages)\n"
            f"Total Captions: {stats['total_captions']}\n"
            f"Total Sentences: {stats['total_sentences']}\n"
            f"Total Paragraphs: {stats['total_paragraphs']}\n"
            f"Unique Words: {len(stats['unique_words'])}\n"

            f"\n--- Average Text Statistics ---\n"
            f"Average Characters per File: {stats['avg_chars']:.2f}\n"
            f"Average Words per File: {stats['avg_words']:.2f}\n"
            f"Average Captions per File: {stats['avg_captions']:.2f}\n"
            f"Average Word Length: {stats['avg_word_length']:.2f}\n"
            f"Median Word Length: {stats['median_word_length']:.2f}\n"
            f"Average Sentence Length: {stats['avg_sentence_length']:.2f}\n"

            f"\n--- Image Information ---\n"
            f"Image File Formats: {', '.join(stats['image_formats'])}\n"
            f"Square Images: {stats['square_images']}\n"
            f"Portrait Images: {stats['portrait_images']}\n"
            f"Landscape Images: {stats['landscape_images']}\n"
            f"Average PPI for All Images: {stats['avg_ppi']:.2f}\n"

            f"\n--- Image Resolutions ---\n"
            f"{stats['formatted_resolutions']}\n"
            f"\n--- Image Aspect Ratios ---\n"
            f"{stats['formatted_aspect_ratios']}\n"
            f"\n--- Top 5 Files by Word Count ---\n"
            f"{stats['formatted_top_5_files_words']}\n"
            f"\n--- Top 5 Files by Character Count ---\n"
            f"{stats['formatted_top_5_files_chars']}\n"
            f"\n--- Top 5 Files by Caption Count ---\n"
            f"{stats['formatted_top_5_files_captions']}\n"
            f"\n--- Top 5 Longest Words ---\n"
            f"{stats['formatted_longest_words']}\n"
            f"\n--- Top 50 Most Common Words ---\n"
            f"{stats['formatted_common_words']}\n"
            f"\n--- Character Occurrence ---\n"
            f"{stats['formatted_common_chars']}\n"
            f"\n--- Unique Captions ---\n"
            f"{stats['formatted_captions']}\n"
        )
        return stats_text


    def update_caption_counter(self, captions):
        for caption in captions:
            caption_words = caption.split()
            if self.truncate_stat_captions_var.get() and (len(caption_words) > 8 or len(caption) > 50):
                caption = ' '.join(caption_words[:8]) + "..." if len(caption_words) > 8 else caption[:50] + "..."
            self.caption_counter[caption] += 1


    def get_sorted_captions(self):
        sorted_captions = self.caption_counter.most_common()
        return sorted(sorted_captions, key=lambda x: (-x[1], x[0].lower()))


    def get_formatted_captions(self, sorted_captions):
        return "\n".join([f"{count:03}x, {caption}" for caption, count in sorted_captions])


    def filter_and_update_textfiles(self):
        self.text_files = [text_file for text_file in self.text_files if os.path.exists(text_file)]
        num_txt_files, num_img_files = len(self.text_files), len(self.image_files)
        num_total_files = num_img_files + num_txt_files
        formatted_total_files = f"{num_total_files} (Text: {num_txt_files}, Images: {num_img_files})"
        self.refresh_file_lists()
        return num_total_files, num_txt_files, num_img_files, formatted_total_files


    def format_filesize(self, size):
        if size >= 1_000_000:
            return f"{size} bytes ({size / 1_000_000:.2f} MB)"
        elif size >= 1_000:
            return f"{size} bytes ({size / 1_000:.2f} KB)"
        else:
            return f"{size} bytes"


    def process_text_file(self, text_file):
        with open(text_file, 'r', encoding="utf-8") as file:
            filedata = file.read()
        words = re.findall(r'\b\w+\b', filedata.lower())
        sentences = re.split(r'[.!?]', filedata)
        paragraphs = filedata.split('\n\n')
        captions = [cap.strip() for cap in filedata.split(',')]
        return filedata, words, sentences, paragraphs, captions


    def process_image_file(self, image_file):
        with Image.open(image_file) as image:
            diagonal_inches = 10
            width, height = image.size
            dpi = image.info.get('dpi', (0, 0))
            if isinstance(dpi, tuple) and len(dpi) == 2:
                try:
                    dpi = (float(dpi[0]), float(dpi[1]))
                    if dpi[0] == 0 or dpi[1] == 0:
                        raise ValueError("Invalid DPI value")
                except ValueError:
                    diagonal_pixels = (width**2 + height**2)**0.5
                    dpi = (diagonal_pixels / diagonal_inches, diagonal_pixels / diagonal_inches)
            else:
                diagonal_pixels = (width**2 + height**2)**0.5
                dpi = (diagonal_pixels / diagonal_inches, diagonal_pixels / diagonal_inches)
            aspect_ratio = width / height
        return width, height, dpi, aspect_ratio, image.format


    def update_tab8_textbox(self, stats_text, manual_refresh=None):
        self.tab8_stats_textbox.config(state="normal")
        self.tab8_stats_textbox.delete("1.0", "end")
        self.tab8_stats_textbox.insert("1.0", stats_text)
        self.tab8_stats_textbox.config(state="disabled")
        if manual_refresh:
            messagebox.showinfo("Stats Calculated", "Stats have been updated!")


#endregion
################################################################################################################################################
#region - Window drag setup


    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
        self.primary_display_image.config(cursor="size")


    def stop_drag(self, event):
        self.drag_x = None
        self.drag_y = None
        self.primary_display_image.config(cursor="hand2")


    def dragging_window(self, event):
        if self.drag_x is not None and self.drag_y is not None:
            dx = event.x - self.drag_x
            dy = event.y - self.drag_y
            x = self.master.winfo_x() + dx
            y = self.master.winfo_y() + dy
            width = self.master.winfo_width()
            height = self.master.winfo_height()
            self.master.geometry(f"{width}x{height}+{x}+{y}")

#endregion
################################################################################################################################################
#region - About Window


    def toggle_about_window(self):
        if self.about_window_open:
            self.about_window.close_about_window()
            self.about_window_open = False
        else:
            self.about_window.create_about_window()
            self.about_window_open = True



#endregion
################################################################################################################################################
#region - Text Cleanup


    def cleanup_all_text_files(self, show_confirmation=True):
        if not self.check_if_directory():
            return
        if show_confirmation:
            user_confirmation = messagebox.askokcancel("Clean-Text", "This operation will clean all text files from typos like:\nDuplicate tags, Extra commas, Extra spaces, trailing commas/spaces, commas without spaces, and more.\n\nExample Cleanup:\n  From: dog,solo,  ,happy  ,,\n       To: dog, solo, happy")
            if not user_confirmation:
                return
        try:
            for text_file in self.text_files:
                if os.path.exists(text_file):
                    with open(text_file, "r+", encoding="utf-8") as f:
                        text = f.read().strip()
                        cleaned_text = self.cleanup_text(text)
                        f.seek(0)
                        f.write(cleaned_text)
                        f.truncate()
            messagebox.showinfo("Success", "All text files have been cleaned!")
        except Exception as e:
            messagebox.showerror("Error: cleanup_all_text_files()", f"An unexpected error occurred: {str(e)}")
        self.show_pair()


    def cleanup_text(self, text):
        if self.cleaning_text_var.get():
            text = self.remove_duplicate_CSV_captions(text)
            if self.list_mode_var.get():
                text = re.sub(r'\.\s', '\n', text)  # Replace period and space with newline
                text = re.sub(' *\n *', '\n', text)  # Replace spaces around newlines with a single newline
            else:
                text = re.sub(r'\.\s', ', ', text)  # Replace period and space with comma and space
                text = re.sub(' *, *', ',', text)  # Replace spaces around commas with a single comma
            text = re.sub(' +', ' ', text)  # Replace multiple spaces with a single space
            text = re.sub(",+", ",", text)  # Replace multiple commas with a single comma
            text = re.sub(",(?=[^\s])", ", ", text)  # Add a space after a comma if it's not already there
            text = re.sub(r'\\\\+', r'\\', text)  # Replace multiple backslashes with a single backslash
            text = re.sub(",+$", "", text)  # Remove trailing commas
            text = re.sub(" +$", "", text)  # Remove trailing spaces
            text = text.strip(",")  # Remove leading and trailing commas
            text = text.strip()  # Remove leading and trailing spaces
        return text


    def remove_duplicate_CSV_captions(self, text):
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
#region - User Setup


    def prompt_first_time_setup(self):
        dict_var = StringVar(value="English Dictionary")
        last_word_match_var = StringVar(value="Match Last Word")
        match_modes = {"Match Whole String": False, "Match Last Word": True}
        dictionaries = ["English Dictionary", "Danbooru", "e621", "Derpibooru"]

        def save_and_continue(close=False, back=False):
            selected_dict = dict_var.get()
            self.csv_danbooru.set(selected_dict == "Danbooru")
            self.csv_derpibooru.set(selected_dict == "Derpibooru")
            self.csv_e621.set(selected_dict == "e621")
            self.csv_english_dictionary.set(selected_dict == "English Dictionary")
            self.last_word_match_var.set(match_modes.get(last_word_match_var.get(), False))
            if close:
                save_and_close()
            elif back:
                clear_widgets()
                create_dictionary_selection_widgets()
                setup_window.geometry("400x200")
            else:
                self.settings_manager.save_settings()
                clear_widgets()
                setup_last_word_match_frame()
                setup_window.geometry("400x250")

        def clear_widgets():
            for widget in setup_window.winfo_children():
                widget.destroy()

        def setup_last_word_match_frame():
            options = [
                ("Match only the last word", "Matches only the last word typed.\nExample: Typing 'blue sky' matches 'sky'.", "Match Last Word"),
                ("Match entire tag", "Matches the entire tag, including multiple words.\nExample: Typing 'blue sky' matches 'blue sky'.", "Match Whole String")
            ]
            Label(setup_window, text="Select tag matching method").pack(pady=5)
            ttk.Separator(setup_window, orient="horizontal").pack(fill="x", padx=5, pady=5)
            for text, description, value in options:
                ttk.Radiobutton(setup_window, text=text, variable=last_word_match_var, value=value).pack(pady=5)
                Label(setup_window, text=description).pack(pady=5)
            ttk.Separator(setup_window, orient="horizontal").pack(fill="x", padx=5, pady=5)
            ttk.Button(setup_window, text="Back", width=10, command=lambda: save_and_continue(back=True)).pack(side="left", anchor="w", pady=5, padx=10)
            ttk.Button(setup_window, text="Done", width=10, command=lambda: save_and_continue(close=True)).pack(side="right", anchor="e", pady=5, padx=10)

        def save_and_close():
            self.settings_manager.save_settings()
            setup_window.destroy()
            self.update_autocomplete_dictionary()

        def create_setup_window():
            setup_window = Toplevel(self.master)
            setup_window.title("First Time Setup")
            setup_window.iconphoto(False, self.blank_image)
            window_width, window_height = 400, 200
            position_right = root.winfo_screenwidth() // 2 - window_width // 2
            position_top = root.winfo_screenheight() // 2 - window_height // 2
            setup_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
            setup_window.resizable(False, False)
            setup_window.grab_set()
            setup_window.protocol("WM_DELETE_WINDOW", save_and_close)
            return setup_window

        def create_dictionary_selection_widgets():
            Label(setup_window, text="Please pick your preferred autocomplete dictionary").pack(pady=5)
            ttk.Separator(setup_window, orient="horizontal").pack(fill="x", padx=5, pady=5)
            frame = Frame(setup_window)
            frame.pack(padx=5, pady=5)
            for i, dictionary in enumerate(dictionaries):
                ttk.Radiobutton(frame, text=dictionary, variable=dict_var, value=dictionary).grid(row=i // 2, column=i % 2, padx=5, pady=5)
            ttk.Separator(setup_window, orient="horizontal").pack(fill="x", padx=5, pady=5)
            Label(setup_window, text="The autocomplete dictionary and settings can be changed at any time.").pack(pady=5)
            ttk.Button(setup_window, text="Next", width=10, command=save_and_continue).pack(side="bottom", anchor="e", pady=5, padx=10)

        setup_window = create_setup_window()
        create_dictionary_selection_widgets()


#endregion
################################################################################################################################################
#region - Save and close


    def save_text_file(self):
        try:
            if self.image_dir.get() != "Choose Directory..." and self.check_if_directory() and self.text_files:
                file_saved = self._save_file()
                if self.cleaning_text_var.get() or self.list_mode_var.get():
                    self.refresh_text_box()
                if file_saved:
                    self.master.title(self.title)
                else:
                    self.master.title(self.title)
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: save_text_file()", f"An error occurred while saving the current text file.\n\n{e}")


    def _save_file(self):
        text_file = self.text_files[self.current_index]
        text = self.text_box.get("1.0", "end-1c")
        if os.path.exists(text_file):
            with open(text_file, "r", encoding="utf-8") as file:
                if text == file.read():
                    return False
        if text in {"None", ""}:
            if self.auto_delete_blank_files_var.get():
                if os.path.exists(text_file):
                    os.remove(text_file)
            else:
                with open(text_file, "w+", encoding="utf-8") as file:
                    file.write("")
            return True
        if self.cleaning_text_var.get():
            text = self.cleanup_text(text)
        if self.list_mode_var.get():
            text = ', '.join(text.split('\n'))
        with open(text_file, "w+", encoding="utf-8") as file:
            file.write(text)
        return True


    def on_closing(self, event=None):
        try:
            self.settings_manager.save_settings()
            self.delete_text_backup()
            self.check_working_directory()
            if os.path.isdir(os.path.join(self.image_dir.get(), 'Trash')):
                self.delete_trash_folder()
                self.check_saved_and_quit()
            else:
                self.check_saved_and_quit()
        except TclError: pass


    def check_saved_and_quit(self):
        if not self.master.title().endswith(" ⚪"):
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
#region - Custom Dictionary


    def refresh_custom_dictionary(self):
        with open(self.my_tags_csv, 'r') as file:
            content = self.remove_extra_newlines(file.read())
            self.custom_dictionary_textbox.delete("1.0", 'end')
            self.custom_dictionary_textbox.insert('end', content)
            self.update_autocomplete_dictionary()


    def create_custom_dictionary(self, reset=False):
        try:
            csv_filename = self.my_tags_csv
            if reset or not os.path.isfile(csv_filename):
                with open(csv_filename, 'w', newline='', encoding="utf-8") as file:
                    file.write("")
                self.refresh_custom_dictionary()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: create_custom_dictionary()", f"An error occurred while creating the custom dictionary file:\n\n{csv_filename}\n\n{e}")


    def add_to_custom_dictionary(self):
        try:
            selected_text = self.text_box.get("sel.first", "sel.last")
            with open(self.my_tags_csv, 'a', newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([selected_text])
            self.refresh_custom_dictionary()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: add_to_custom_dictionary()", f"An error occurred while saving the selected to 'my_tags.csv'.\n\n{e}")


    def remove_extra_newlines(self, text):
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if line.strip() != '']
        result = '\n'.join(cleaned_lines)
        if not result.endswith('\n'):
            result += '\n'
        return result


    def remove_lines_starting_with_hashes(self, text):
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if not line.strip().startswith('###')]
        return '\n'.join(cleaned_lines)


#endregion
################################################################################################################################################
#region - File Management


    def natural_sort(self, string):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', string)]


    def get_file_sort_key(self):
        if self.load_order_var.get() == "Name (default)":
            sort_key = self.natural_sort
        elif self.load_order_var.get() == "File size":
            sort_key = lambda x: os.path.getsize(os.path.join(self.image_dir.get(), x))
        elif self.load_order_var.get() == "Date created":
            sort_key = lambda x: os.path.getctime(os.path.join(self.image_dir.get(), x))
        elif self.load_order_var.get() == "Extension":
            sort_key = lambda x: os.path.splitext(x)[1]
        elif self.load_order_var.get() == "Last Access time":
            sort_key = lambda x: os.path.getatime(os.path.join(self.image_dir.get(), x))
        elif self.load_order_var.get() == "Last write time":
            sort_key = lambda x: os.path.getmtime(os.path.join(self.image_dir.get(), x))
        return sort_key


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
                original_auto_save_var = self.auto_save_var.get()
                self.auto_save_var.set(value=False)
            directory = filedialog.askdirectory()
            if directory and directory != self.image_dir.get():
                if hasattr(self, 'text_box'):
                    self.revert_text_image_filter(clear=True)
                if self.check_if_contains_images(directory):
                    self.delete_text_backup()
                    self.image_dir.set(os.path.normpath(directory))
                    self.current_index = 0
                    self.load_pairs()
                    self.set_text_file_path(directory)
            if original_auto_save_var is not None:
                self.auto_save_var.set(original_auto_save_var)
        except Exception as e:
            messagebox.showwarning("Error", f"There was an unexpected issue setting the folder path:\n\n{e}")


    def set_working_directory(self, event=None):
        try:
            if self.auto_save_var.get():
                self.save_text_file()
            if hasattr(self, 'text_box'):
                self.revert_text_image_filter(clear=True)
            directory = self.directory_entry.get()
            if self.check_if_contains_images(directory):
                self.image_dir.set(os.path.normpath(directory))
                self.current_index = 0
                self.load_pairs()
                self.set_text_file_path(directory)
            else:
                if hasattr(self, 'image_file'):
                    self.image_dir.set(os.path.dirname(self.image_file))
                    self.set_working_directory()
        except FileNotFoundError:
            messagebox.showwarning("Invalid Directory", f"The system cannot find the path specified:\n\n{self.directory_entry.get()}")
            if hasattr(self, 'image_file'):
                self.image_dir.set(os.path.dirname(self.image_file))
                self.set_working_directory()


    def open_directory(self, directory):
        try:
            if directory == os.path.dirname(self.image_file):
                subprocess.run(['explorer', '/select,', self.image_file])
            else:
                if os.path.isdir(directory):
                    os.startfile(directory)
        except Exception: return


    def open_text_directory(self, event=None):
        try:
            self.check_working_directory()
            if self.text_files:
                subprocess.run(['explorer', '/select,', os.path.normpath(self.text_files[self.current_index])])
            else:
                os.startfile(os.path.dirname(self.text_files[self.current_index]))
        except Exception: return


    def open_image_directory(self, event=None):
        try:
            self.check_working_directory()
            if self.image_files:
                subprocess.run(['explorer', '/select,', self.image_file])
            else:
                os.startfile(self.image_dir.get())
        except Exception: return


    def open_image(self, path=None, index=None, event=None):
        if path is not None:
            try:
                os.startfile(path)
            except Exception: return
        elif index is not None:
            try:
                os.startfile(self.image_files[index])
            except Exception: return
        elif self.image_files:
            try:
                os.startfile(self.image_file)
            except Exception: return


    def open_textfile(self, text_file=None, event=None):
        if text_file is not None:
            try:
                os.startfile(text_file)
            except Exception: return
        elif self.text_files:
            try:
                os.startfile(self.text_files[self.current_index])
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


    def check_odd_files(self, filename):
        file_extension = os.path.splitext(filename)[1].lower()
        file_rename_dict = {".jpg_large": "jpg", ".jfif": "jpg"}
        return file_extension in file_rename_dict


    def archive_dataset(self):
        if not messagebox.askokcancel("Zip Dataset", "This will create an archive of the current folder. Only images and text files will be archived.\n\nPress OK to set the zip name and output path."):
            return
        folder_path = self.image_dir.get()
        zip_filename = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip files", "*.zip")], title="Save As", initialdir=folder_path, initialfile="dataset.zip")
        if not zip_filename:
            return
        allowed_extensions = [".txt", ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".jfif", ".jpg_large"]
        file_list = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if any(file.lower().endswith(ext) for ext in allowed_extensions)]
        num_images = sum(1 for file in file_list if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.jfif', '.jpg_large')))
        num_texts = sum(1 for file in file_list if file.lower().endswith('.txt'))
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_STORED) as zip_file:
            for file_path in file_list:
                archive_name = os.path.relpath(file_path, folder_path)
                zip_file.write(file_path, archive_name)
        messagebox.showinfo("Success", f"The archive has been successfully zipped!\nNumber of image files: {num_images}\nNumber of text files: {num_texts}")


    def manually_rename_single_pair(self):
        if not self.check_if_directory():
            return
        if self.current_index >= len(self.image_files):
            messagebox.showerror("Error: manually_rename_single_pair()", "No valid image selected.")
            return
        image_file = self.image_files[self.current_index]
        current_image_name = os.path.basename(image_file)
        text_file = self.text_files[self.current_index] if self.current_index < len(self.text_files) and os.path.exists(self.text_files[self.current_index]) else None
        current_text_name = os.path.basename(text_file) if text_file else "(No associated text file)"
        new_name = simpledialog.askstring("Rename", "Enter the new name for the pair (without extension):", initialvalue=os.path.splitext(current_image_name)[0])
        if not new_name:
            return
        new_image_name = new_name + os.path.splitext(image_file)[1]
        new_text_name = new_name + os.path.splitext(text_file)[1] if text_file else "(No associated text file)"
        confirm_message = (
            f"Current:\n"
            f"{current_image_name}\n"
            f"{current_text_name}\n\n"
            f"New:\n"
            f"{new_image_name}\n"
            f"{new_text_name}\n\n"
            "Are you sure you want to rename the files?"
        )
        if not messagebox.askokcancel("Confirm Rename", confirm_message):
            return
        try:
            new_image_file = os.path.join(os.path.dirname(image_file), new_image_name)
            new_text_file = os.path.join(os.path.dirname(text_file), new_text_name) if text_file else None
            os.rename(image_file, new_image_file)
            if text_file:
                os.rename(text_file, new_text_file)
            self.image_files[self.current_index] = new_image_file
            if text_file:
                self.text_files[self.current_index] = new_text_file
            messagebox.showinfo("Success", "The pair has been renamed successfully.")
            self.refresh_file_lists()
            self.show_pair()
            new_index = self.image_files.index(new_image_file)
            self.jump_to_image(new_index)
        except PermissionError as e:
            messagebox.showerror("Error: manually_rename_single_pair()", f"Permission denied while renaming files: {e}")
        except FileNotFoundError as e:
            messagebox.showerror("Error: manually_rename_single_pair()", f"File not found: {e}")
        except Exception as e:
            messagebox.showerror("Error: manually_rename_single_pair()", f"An unexpected error occurred: {e}")


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
            messagebox.showerror("Error: rename_odd_files()", f"An error occurred while renaming odd files.\n\n{e}")


    def create_blank_text_files(self):
        try:
            count = sum(1 for file_path in self.text_files if not os.path.exists(file_path))
            if count == 0:
                messagebox.showinfo("No Action Needed", "All images already have a text pair.\nNo blank text files will be created!")
            else:
                confirm = messagebox.askyesno("Create Blank Text Pairs", f"This will create {count} blank text files for all un-paired images.\n\nContinue?")
                if confirm:
                    created_count = 0
                    for file_path in self.text_files:
                        if not os.path.exists(file_path):
                            with open(file_path, 'w') as file:
                                pass  # Create file
                            created_count += 1
                    messagebox.showinfo("Success", f"Created {created_count} blank text files!")
        except Exception as e:
            messagebox.showerror("Error: create_blank_text_files()", f"Failed to create file: {file_path}\n\n{str(e)}")


    def restore_backup(self):
        backup_dir = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
        if not os.path.exists(backup_dir):
            return
        confirm = messagebox.askokcancel("Restore Backup", "This will restore all text files in the selected directory from the latest backup.\n\nDo you want to proceed?")
        if not confirm:
            return
        for backup_file in os.listdir(backup_dir):
            if backup_file.endswith(".bak"):
                original_file = os.path.join(os.path.dirname(backup_dir), os.path.splitext(backup_file)[0] + ".txt")
                try:
                    with open(os.path.join(backup_dir, backup_file), 'r') as file:
                        content = file.read()
                    if content == "!DELETEME!":
                        if os.path.exists(original_file):
                            os.remove(original_file)
                        os.remove(os.path.join(backup_dir, backup_file))
                        continue
                    if os.path.exists(original_file):
                        os.remove(original_file)
                    shutil.copy2(os.path.join(backup_dir, backup_file), original_file)
                    os.rename(original_file, original_file.replace('.bak', '.txt'))
                    os.utime(original_file, (time.time(), time.time()))
                    os.remove(os.path.join(backup_dir, backup_file))
                    messagebox.showinfo("Success", "All text files have been restored from the latest backup!")
                except Exception:
                    pass
        self.refresh_text_box()


    def backup_text_files(self):
        if not self.check_if_directory():
            return
        backup_dir = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        for text_file in self.text_files:
            base = os.path.splitext(text_file)[0]
            new_backup = os.path.join(backup_dir, os.path.basename(base) + ".bak")
            if os.path.exists(text_file):
                shutil.copy2(text_file, new_backup)
            else:
                with open(new_backup, 'w') as f:
                    f.write("!DELETEME!")


    def delete_text_backup(self):
        if self.text_files:
            try:
                backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
                if os.path.exists(backup_folder):
                    shutil.rmtree(backup_folder)
            except (PermissionError, IOError, TclError) as e:
                messagebox.showerror("Error: delete_text_backup()", f"An error occurred while deleting the text backups.\n\n{e}")


    def delete_trash_folder(self):
        trash_dir = os.path.join(self.image_dir.get(), 'Trash')
        try:
            if os.path.exists(trash_dir):
                files_in_trash = os.listdir(trash_dir)
                is_empty = not files_in_trash
                if is_empty:
                    self.check_working_directory()
                    shutil.rmtree(trash_dir)
                else:
                    num_files = len(files_in_trash)
                    if messagebox.askyesno("Trash Folder Found", f"A local Trash folder was found in the image directory.\n\n{num_files} - file(s) found\n\nWould you like to delete this folder?"):
                        self.check_working_directory()
                        shutil.rmtree(trash_dir)
            root.destroy()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: delete_trash_folder()", f"An error occurred while deleting the trash folder.\n\n{e}")


    def delete_pair(self, index=None):
        if not self.check_if_directory():
            return
        if index is None:
            index = self.current_index
        try:
            image_file = os.path.basename(self.image_files[index])
            text_file_exists = os.path.exists(self.text_files[index]) if index < len(self.text_files) else False
            text_file = os.path.basename(self.text_files[index]) if text_file_exists else "N/A"
            confirm = messagebox.askyesnocancel("Confirm Delete", f"Image file: {image_file}\nText file: {text_file}\n\nSend to local trash folder (Yes, Keep)\n\nDelete permanently (No, Destroy)\n\nor cancel?")
            if confirm is None:  # Cancel
                return
            elif confirm:  # Yes, Trash
                if index < len(self.image_files):
                    trash_dir = os.path.join(os.path.dirname(self.image_files[index]), "Trash")
                    os.makedirs(trash_dir, exist_ok=True)
                    deleted_pair = []
                    for file_list in [self.image_files, self.text_files]:
                        if os.path.exists(file_list[index]):
                            trash_file = os.path.join(trash_dir, os.path.basename(file_list[index]))
                            try:
                                os.rename(file_list[index], trash_file)
                            except FileExistsError:
                                if not trash_file.endswith("txt"):
                                    if messagebox.askokcancel("Warning", "The file already exists in the trash. Do you want to overwrite it?"):
                                        os.remove(trash_file)
                                        os.rename(file_list[index], trash_file)
                                    else:
                                        return
                            deleted_pair.append((file_list, index, trash_file))
                            del file_list[index]
                    self.deleted_pairs.append(deleted_pair)
                    self.total_images_label.config(text=f"of {len(self.image_files)}")
                    if index >= len(self.image_files):
                        index = len(self.image_files) - 1
                    if index >= 1:
                        self.update_pair(direction="prev", save=False)
                    else:
                        self.show_pair()
                    self.undo_state.set("normal")
                    self.individual_operations_menu.entryconfig("Undo Delete", state="normal")
                else:
                    pass
            else:  # No, Recycle
                if index < len(self.image_files):
                    deleted_pair = []
                    for file_list in [self.image_files, self.text_files]:
                        if os.path.exists(file_list[index]):
                            try:
                                os.remove(file_list[index])
                            except (PermissionError, IOError) as e:
                                messagebox.showerror("Error: delete_pair()", f"An error occurred while deleting the img-txt pair.\n\n{e}")
                                return
                            deleted_pair.append((file_list, index, None))
                            del file_list[index]
                    self.deleted_pairs = [pair for pair in self.deleted_pairs if pair != deleted_pair]
                    self.total_images_label.config(text=f"of {len(self.image_files)}")
                    if index >= len(self.image_files):
                        index = len(self.image_files) - 1
                    if index >= 1:
                        self.update_pair(direction="prev", save=False)
                    else:
                        self.show_pair()
                else:
                    pass
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: delete_pair()", f"An error occurred while deleting the img-txt pair.\n\n{e}")


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
                self.individual_operations_menu.entryconfig("Undo Delete", state="disabled")
        except (PermissionError, ValueError, IOError, TclError) as e:
            messagebox.showerror("Error: undo_delete_pair()", f"An error occurred while restoring the img-txt pair.\n\n{e}")


#endregion
################################################################################################################################################
#region - Framework


    def set_appid(self):
        myappid = 'ImgTxtViewer.Nenotriple'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


    def setup_window(self):
        self.title = f"{VERSION} - img-txt Viewer"
        self.master.title(self.title)
        self.master.minsize(545, 200) # Width x Height
        window_width = 1110
        window_height = 660
        position_right = root.winfo_screenwidth()//2 - window_width//2
        position_top = root.winfo_screenheight()//2 - window_height//2
        root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.additional_window_setup()


    def additional_window_setup(self):
        self.set_always_on_top(initial=True)
        self.master.attributes('-topmost', 0)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)


    def set_icon(self):
        self.icon_path = os.path.join(self.application_path, "icon.ico")
        try:
            self.master.iconbitmap(self.icon_path)
        except TclError: pass
        # Blank image (app icon)
        self.icon_path = os.path.join(self.application_path, "icon.ico")
        with Image.open(self.icon_path) as img:
            self.blank_image = ImageTk.PhotoImage(img)


    def get_app_path(self):
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        elif __file__:
            return os.path.dirname(__file__)
        return ""


# --------------------------------------
# Mainloop
# --------------------------------------
root = Tk()
app = ImgTxtViewer(root)
root.mainloop()


#endregion
################################################################################################################################################
#region - Changelog


'''


[💾v1.96](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.96)


<details>
  <summary>Release Notes for v1.96</summary>


**v1.96 Changes**  |  https://github.com/Nenotriple/img-txt_viewer/compare/v1.95...v1.96


This release incorporates several new features, including a reworked Batch Tag Edit tool, a Thumbnail Panel for quick navigation, and an Edit Image Panel for adjusting image properties. Additionally, numerous bugs have been fixed, such as issues with the Delete Pair tool, image quality degradation, and memory leaks.

Many aspects of the script have been refactored to be more modular and better handle additional tools and features.

The app now targets Windows 11, and while it doesn't offer an complete `Aero` theme, many widgets have been updated to utilize a more modern theme where appropriate.

Starting from this release, the `Lite` version will no longer be provided. All tools are now built-in.

---

### New:
- `Batch Tag Delete` has been renamed to `Batch Tag Edit`.
  - This tool has been completely reworked to allow for more versatile tag editing.
  - The interface is now more convenient and user-friendly, allowing you to see all pending changes before committing them.
  - It is no longer supported as a standalone tool.
- `Batch Resize Images`:
  - No longer a standalone tool, the tool has been integrated into the main app.
  - NEW: A timer is now displayed in the bottom row.
  - FIXED: The following resize modes not working/causing an error: `Longer Side`, and `Height`
  - FIXED: The resize operation is now threaded, allowing the app to remain responsive during the resizing process.
- `Find Duplicate Files`: No longer a standalone tool, the tool has been integrated into the main app.
- New feature `Thumbnail Panel`: Displayed below the current image for quick navigation.
- New feature `Edit Image Panel`: Enabled from the options/image menu, this section allows you to edit the `Brightness`, `Contrast`, `Saturation`, `Sharpness`, `Highlights`, and `Shadows` of the current image.
- New feature `Edit Image...`: Open the current image in an external editor, the default is MS Paint.
  - Running `Set Default Image Editor` will open a dialog to select the executable (or `.py`, `.pyw`) path to use as the default image editor.
  - This should work with any app that accepts a file path as a launch argument. (GIMP, Krita, Photoshop, etc.)
- New tool `Create Wildcard From Captions`: Combine all image captions into a single text file, each set of image captions separated by a newline.
- Added `Copy` command to the right-click textbox context menu.
- Added `Last` to the index entry right-click context menu to quickly jump to the last img-txt pair.
 - Added two additional upscale models: `AnimeSharp-4x` and `UltraSharp-4x`.
- Additional NCNN upscale models can now be loaded by placing them in the `models` directory.
- Now you can insert a suggestion by simply clicking it.
- A quick guided setup will run on the app's first launch, or if the settings file is deleted/reset.
  - This will set the preferred autocomplete dictionaries and matching settings.
- You can now press `CTRL+W` to close the current window.

<br>


### Fixed:
- Fixed issue where the `Delete Pair` tool would overwrite the next index with the deleted text. #31
- Fixed an issue that was degrading the quality of the displayed image and not respecting the `Image Display Quality` setting.
- Fixed a memory leak that could occur whenever the primary image is displayed.
- Fixed Next/Previous button not properly displaying their relief when clicked.
- Fixed an issue where landscape images were improperly scaled, leading to an incorrect aspect ratio.
  - Additionally, large landscape images now scale to fit the window frame better.
- Fixed `Open Text Directory...` not respecting the actual filepath if set by `Set Text File Path...`.
- Fixed issue where the file lists were not updated when using the internal function "jump_to_image()".
- Fixed an issue where the `alt text path` could be set to `.` when declining to reload the last directory.
- Fixed a bug where the window height would enlarge slightly when dragging the window from by the displayed image.
- Fixed the following tools not respecting the `Loading Order > Descending` setting, causing them to jump to the wrong index.
  - `Image Grid`, `Upscale Image`, `Resize Image`
- Potential fix for the `Stats > PPI` calculation returning "0.00".
- if `clean-text` is enabled: The primary text box is now properly refreshed when saving.
- Fixed an issue where deleting tags that are substring of another tag using middle-mouse-click caused an error and did not remove the tag. #38
- Fixed an issue where the system clipboard would become unresponsive after deleting a tag with the middle mouse button. #38


<br>


### Other changes:
- Autocomplete suggestions are now cached, so re-typing the same words returns suggestions quicker.
    - Some pre-caching is done for Autocomplete suggestions, which does slow down the initial launch slightly.
- Using `Open Current Directory...` will now automatically select the current image in the file explorer. #30
  - The `Open` button will also select the current image if the path being opened is the same as the image path.
- The Image info (the stats displayed above the image) is now cached for quicker access.
- `Zip Dataset...` Now only zips images and text files in the selected directory, omitting subfolders.
- The `Options`, and `Tools` menus have been reorganized.
- The color mode is now displayed in the image info panel.
- You can now close the `Crop Image` window with the `Escape` key.
- The message box is now removed.
  - You can now check the title for a visual indicator of the text state.
  - All tools that used the message box for notifications now use a message popup.
- Custom and duplicate highlights now use a range of pastel colors.
- I have switched to Windows 11, so that's now the target operating system for this project. You may notice some UI changes.
  - Widgets are now made with ttk (when appropriate) for better styling on Windows 11.


<br>


### Project Changes:
- `Upscale`, `Batch Upscale`: v1.05:
  - FIXED: Prevent the app from hanging while upscaling a GIF.
  - Batch Upscale: Added a label to display the number of images upscaled and the total number of images.
  - Batch Upscale: Added a timer and ETA label to show the total time taken and the estimated time remaining.
  - Batch Upscale: Entry path ToolTips are now updated when the path is changed.
  - Widgets are now made with ttk (when appropriate) for better styling on Windows 11.
- `TkToolTip`: v1.06:
  - NEW: `justify` parameter: Configure text justification in the tooltip. (Default is "center")
  - NEW: `wraplength` parameter: Configure the maximum line width for text wrapping. (Default is 0, which disables wrapping)
  - NEW: `fade_in` and `fade_out` parameters: Configure fade-in and fade-out times. (Default is 75ms)
  - NEW: `origin` parameter: Configure the origin point of the tooltip. (Default is "mouse")
  - FIXED: Issue where the underlying widget would be impossible to interact with after hiding the tooltip.
  - CHANGE: Now uses `TkDefaultFont` instead of Tahoma as the default font for the tooltip text.
  - CHANGE: The default background color is now "#ffffee", less yellow and more "off-white".
- `PopUpZoom`v1.02:
  - New: `Rounded Corners` The popup now supports rounded corners. (Default: 30px)
- `Batch Crop`(v1.03), `Resize Images`(v1.02), `Image Grid`(v1.04):
  - Widgets are now made with ttk (when appropriate) for better styling on Windows 11.


</details>
<br>

'''


#endregion
################################################################################################################################################
#region - Todo


'''


- Todo
  - (Med) Go through all tools that touch text files and make sure they work with alt-text paths.

  - (Low) Find Dupe Files, could/should automatically move captions if they are found.

  - (Very Low) Create a `Danbooru (safe)` autocomplete dictionary. (I have no idea how to effectively filter the naughty words.)


- Tofix

  - (High) The Autocomplete dictionary is not correctly set when running the initial guided setup.
    - It always sets to Danbooru, the UI will show the correct dictionary, but the actual dictionary is not set.
    - The entire class needs an overhaul on how the settings are adjusted, and how the dictionaries are selected for loading.
      - The Autocomplete class should have a set of functions to handle updating the settings and loading the dictionaries.
      - The entire class is sometimes being treated like a single function, which is probably causing these issues with the dictionary not being set correctly.

  - (Med) Image info, and thumbnail cache doesn't update when the image is changed.
    - This is because the cache is built using the filename as the key.
    - The cache dictionary should include the hash of the image file to ensure it's up-to-date.
    - All cache for that image should be cleared when the hash changes.

  - (low) When reloading the last directory: The whole process is messy and should be made more modular.
    - set_working_directory(), set_text_file_path(), jump_to_image(); need to be optimized.
    - When reloading the last directory, the displayed image is resized like 8 times because of repeated calls to show_pair() and display_image(), etc.

  - (low) When restoring the previous directory: The first image index is initially loaded, and then the last view image is loaded.

  - (Low) Sometimes after navigating (perhaps only when using the ALT+Arrow-keys bind), the suggestion navigation fails to register on the first press of ALT.
    - Related to how (Alt-L, and Alt-R) are bound to disable_button()

  - (Low) Running "Crop" Doesn't update the file lists when closing the crop window.

  - (Low) Sometimes when an image is loaded it isn't refreshed.

  - THUMBNAILS:
    - (Low) A 'TypeError' error can occur when using the Mouse Wheel while scrolling over the thumbnail panel.
            - It appears to be related to the ToolTip binding.


  '''

#endregion
