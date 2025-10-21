"""
Name    :  IMG-TXT VIEWER
Version :  v1.99
Author  :  github.com/Nenotriple

Description:
-------------
Display an image and text file side-by-side for easy manual caption editing,
with other tools focused on LoRA training dataset creation and preparation.

More info here: https://github.com/Nenotriple/img-txt_viewer

"""


#region Imports


# Standard Library
import os
import re
import sys
import glob
import time
import shutil
import ctypes
import zipfile
import webbrowser
import subprocess


# Standard Library - GUI
from tkinter import (
    ttk, Tk, messagebox, filedialog,
    StringVar, BooleanVar, IntVar,
    Frame, PanedWindow, Menu,
    Label, Text,
    Event, TclError
)


# Third-Party Libraries
import numpy
from tkmarktext import TextPanel, TextWindow
from TkToolTip import TkToolTip as Tip
from PIL import Image, ImageTk, ImageSequence, UnidentifiedImageError


# Custom Libraries
from main.scripts import (
    calculate_file_stats,
    custom_simpledialog,
    custom_scrolledtext,
    batch_crop_images,
    settings_manager,
    text_controller,
    resize_image,
    entry_helper,
    image_grid,
    edit_panel,
    PyTrominos,
    HelpText,
)


# Tabbed tools
from main.scripts import (
    batch_resize_images,
    batch_image_edit,
    batch_tag_edit,
    find_dupe_file,
    batch_upscale,
    batch_rename,
    CropUI,
)

from main.scripts import frame_extractor
from main.scripts.image_zoom import ImageZoomWidget
import main.scripts.video_thumbnail_generator as vtg
from main.scripts.ThumbnailPanel import ThumbnailPanel
from main.scripts.Autocomplete import SuggestionHandler
from main.scripts.OnnxTagger import OnnxTagger as OnnxTagger
from main.scripts.find_replace_widget import FindReplaceEntry
from main.scripts.video_player_widget import VideoPlayerWidget


#endregion
#region ImgTxtViewer


class ImgTxtViewer:
    Tip.ANIMATION = "slide"
    Tip.SHOW_DELAY = 250
    Tip.PADX = 6
    Tip.PADY = 12
    def __init__(self, root: 'Tk'):
        self.app_version = "v1.99"
        self.root = root
        self.is_frozen, self.app_root_path, self.app_launch_path = self.get_app_path()
        self.set_appid()
        self.setup_window()
        self.set_icon()
        self.initial_class_setup()
        self.define_app_settings()
        self.create_menu_bar()
        self.create_primary_ui()
        self.settings_manager.read_settings()
        self.setup_general_binds()


#endregion
#region Setup

    def initial_class_setup(self):
        # Setup tools
        self.about_window = TextWindow(self.root)
        self.settings_manager = settings_manager.SettingsManager(self, self.root)
        self.stat_calculator = calculate_file_stats.CalculateFileStats(self, self.root)
        self.batch_resize_images = batch_resize_images.BatchResizeImages()
        self.batch_rename = batch_rename.BatchRename()
        self.batch_img_edit = batch_image_edit.BatchImgEdit()
        self.batch_upscale = batch_upscale.BatchUpscale()
        self.edit_panel = edit_panel.EditPanel(self, self.root)
        self.batch_tag_edit = batch_tag_edit.BatchTagEdit()
        self.find_dupe_file = find_dupe_file.FindDupeFile()
        self.crop_ui = CropUI.CropInterface()
        self.onnx_tagger = OnnxTagger(self)
        self.autocomplete = SuggestionHandler(self)
        self.text_controller = text_controller.TextController(self, self.root)
        self.entry_helper = entry_helper

        # Setup UI state
        self.ui_state = "ImgTxtViewer"
        self.current_ui_state = {"tab": "Tagger", "index": 0}
        self.current_text_notebook_tab = "S&R"
        self.text_widget_frame_dict = {}
        self.text_widget_tab_heights = {
            'S&R': 59,
            'Prefix': 59,
            'Append': 59,
            'AutoTag': 340,
            'Filter': 59,
            'Highlight': 59,
            'Font': 59,
            'MyTags': 340,
            'Stats': 340
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

        # Misc variables
        self.about_window_open = False
        self.panes_swap_ew_var = BooleanVar(value=False)
        self.panes_swap_ns_var = BooleanVar(value=False)
        self.text_modified_var = False
        self.filepath_contains_images_var = False
        self.undo_state = StringVar(value="disabled")
        self.previous_window_size = (self.root.winfo_width(), self.root.winfo_height())
        self.initialize_text_pane = True
        self.is_ffmpeg_installed = shutil.which("ffmpeg") is not None
        self.dir_placeholder_text = "Choose Directory..."

        # 'after()' Job IDs
        self.window_configure_job_id = None
        self.is_resizing_job_id = None
        self.delete_tag_job_id = None
        self.animation_job_id = None
        self.update_thumbnail_job_id = None

        # Image Resize Variables
        self.current_image: ImageTk.PhotoImage = None
        self.original_image: ImageTk.PhotoImage = None
        self.current_max_img_height = None
        self.current_max_img_width = None

        # GIF animation variables
        self.gif_frames = []
        self.gif_frame_cache = {}
        self.frame_durations = []
        self.current_frame = 0
        self.current_gif_frame_image = None

        # Video variables
        self.video_thumb_dict = {}

        # Color Palette
        self.pastel_colors = [
            "#a2d2ff", "#ffafcf", "#aec3ae", "#ebe3d5", "#beadfa",
            "#cdf5fd", "#fdcedf", "#c3edc0", "#d6c7ae", "#dfccfb",
            "#c0dbea", "#f2d8d8", "#cbffa9", "#f9f3cc", "#acb1d6",
            "#a1ccd1", "#dba39a", "#c4d7b2", "#ffd9b7", "#d9acf5",
            "#7895b2", "#ff8787", "#90a17d", "#f8c4b4", "#af7ab3"
        ]   # Blue     Pink       Green      Brown      Purple

        # Image Grid
        self.is_image_grid_visible_var = BooleanVar(value=False)


# --------------------------------------
# Settings
# --------------------------------------
    def define_app_settings(self):
        # Misc Settings
        app_path = self.get_direct_app_path()
        self.app_settings_cfg = os.path.join(app_path, "settings.cfg")
        self.my_tags_yml = os.path.join(app_path, "my_tags.yaml")
        self.onnx_models_dir = os.path.join(app_path, "models", "onnx_models")
        self.ncnn_models_dir = os.path.join(app_path, "models", "ncnn_models")
        self.image_dir = StringVar(value=self.dir_placeholder_text)
        self.restore_last_path_var = BooleanVar(value=True)
        self.restore_last_window_size_var = BooleanVar(value=True)
        self.restore_last_text_pane_heights_var = BooleanVar(value=True)
        self.text_dir = ""
        self.external_image_editor_path = "mspaint"
        self.always_on_top_var = BooleanVar(value=False)
        self.big_save_button_var = BooleanVar(value=True)
        self.auto_insert_comma_var = BooleanVar(value=True)

        # Font Settings
        self.font_var = StringVar(value="Courier New")
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
        self.search_and_replace_regex_var = BooleanVar(value=False)

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
        self.thumbnails_visible = BooleanVar(value=True)
        self.thumbnail_width = IntVar(value=50)

        # Edit Panel
        self.edit_panel_visible_var = BooleanVar(value=False)

        # Image Quality
        self.image_quality_var = StringVar(value="Normal")
        self.quality_max_size = 1280
        self.quality_filter = Image.Resampling.BILINEAR
        Image.MAX_IMAGE_PIXELS = 300000000  # ~(17320x17320)px

        # Autocomplete
        self.csv_danbooru = BooleanVar(value=False)
        self.csv_danbooru_safe = BooleanVar(value=False)
        self.csv_derpibooru = BooleanVar(value=False)
        self.csv_e621 = BooleanVar(value=False)
        self.csv_english_dictionary = BooleanVar(value=False)
        self.colored_suggestion_var = BooleanVar(value=True)
        self.suggestion_quantity_var = IntVar(value=4)
        self.suggestion_threshold_var = StringVar(value="Normal")
        self.last_word_match_var = BooleanVar(value=False)


# --------------------------------------
# Bindings
# --------------------------------------
    def setup_general_binds(self):
        #self.root.bind("<Control-f>", lambda event: self.toggle_highlight_all_duplicates())
        self.root.bind("<Control-s>", lambda event: self.save_text_file(highlight=True))
        self.root.bind("<Alt-Right>", lambda event: self.next_pair(event))
        self.root.bind("<Alt-Left>", lambda event: self.prev_pair(event))
        self.root.bind('<Shift-Delete>', lambda event: self.delete_pair())
        self.root.bind('<F1>', lambda event: self.toggle_image_grid(event))
        self.root.bind('<F4>', lambda event: self.open_image_in_editor(event))
        self.root.bind('<Control-w>', lambda event: self.on_closing(event))


#endregion
#region Menubar

    def create_menu_bar(self):
        self.initialize_menu()
        self.create_file_menu()
        self.create_edit_menu()
        self.create_tools_menu()
        self.create_options_menu()


    def initialize_menu(self):
        # Main
        self.main_menu_bar = Menu(self.root)
        self.root.config(menu=self.main_menu_bar)
        # File
        self.fileMenu = Menu(self.main_menu_bar, tearoff=0)
        self.main_menu_bar.add_cascade(label="File", menu=self.fileMenu)
        # Edit
        self.editMenu = Menu(self.main_menu_bar, tearoff=0)
        self.main_menu_bar.add_cascade(label="Edit", menu=self.editMenu)
        # Tools
        self.toolsMenu = Menu(self.main_menu_bar, tearoff=0)
        self.main_menu_bar.add_cascade(label="Tools", menu=self.toolsMenu)
        # Options
        self.optionsMenu = Menu(self.main_menu_bar, tearoff=0)
        self.main_menu_bar.add_cascade(label="Options", menu=self.optionsMenu)
        # About
        self.main_menu_bar.add_command(label="About", command=self.open_about_window)


    def create_file_menu(self):
        # Directory Operations
        self.fileMenu.add_command(label="Select Directory...", command=self.choose_working_directory)
        self.fileMenu.add_command(label="Open Current Directory...", state="disable", command=self.open_image_directory)
        self.fileMenu.add_command(label="Refresh Files", state="disabled", command=self.refresh_files)
        self.fileMenu.add_separator()
        # File Operations
        self.fileMenu.add_command(label="Open Current Image...", state="disable", command=self.open_image)
        self.fileMenu.add_command(label="Open Text File...", state="disable", command=self.open_textfile)
        self.fileMenu.add_command(label="Edit Image...", state="disable", accelerator="F4", command=self.open_image_in_editor)
        self.fileMenu.add_separator()
        # Archive Operations
        self.fileMenu.add_command(label="Zip Dataset...", state="disable", command=self.archive_dataset)
        self.fileMenu.add_separator()
        # Exit
        self.fileMenu.add_command(label="Exit", accelerator="Ctrl+W", command=self.on_closing)


    def create_edit_menu(self):
        # Text Operations
        self.editMenu.add_command(label="Save Text", state="disable", accelerator="Ctrl+S", command=self.save_text_file)
        self.editMenu.add_command(label="Cleanup All Text Files...", state="disable", command=self.cleanup_all_text_files)
        self.editMenu.add_command(label="Create Blank Text Pairs...", state="disable", command=self.create_blank_text_files)
        self.editMenu.add_separator()
        # File Operations
        self.editMenu.add_command(label="Rename Pair", state="disable", command=self.manually_rename_single_pair)
        self.editMenu.add_command(label="Duplicate Pair", state="disable", command=self.duplicate_pair)
        self.editMenu.add_command(label="Delete Pair", state="disable", accelerator="Shift+Del", command=self.delete_pair)
        self.editMenu.add_command(label="Undo Delete", state="disable", command=self.undo_delete_pair)
        self.editMenu.add_separator()
        # Navigation
        self.editMenu.add_command(label="Next Empty Text File", state="disable", accelerator="Ctrl+E", command=self.index_goto_next_empty)
        self.editMenu.add_command(label="Random File", state="disable", accelerator="Ctrl+R", command=self.index_goto_random)
        self.editMenu.add_separator()
        # Settings Files
        self.editMenu.add_command(label="Open Settings File...", command=lambda: self.open_textfile(self.app_settings_cfg))
        self.editMenu.add_command(label="Open MyTags File...", command=lambda: self.open_textfile(self.my_tags_yml))


    def create_options_menu(self):
        # Text Options
        self.text_options_menu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Text Options", state="disable", menu=self.text_options_menu)
        self.text_options_menu.add_checkbutton(label="Clean-Text", variable=self.cleaning_text_var, command=self.toggle_list_menu)
        self.text_options_menu.add_checkbutton(label="Auto-Delete Blank Files", variable=self.auto_delete_blank_files_var)
        self.text_options_menu.add_checkbutton(label="Highlight Selection", variable=self.highlight_selection_var)
        self.text_options_menu.add_checkbutton(label="Add Comma After Tag", variable=self.auto_insert_comma_var, command=self.append_comma_to_text)
        self.text_options_menu.add_checkbutton(label="List View", variable=self.list_mode_var, command=self.toggle_list_mode)
        self.text_options_menu.add_checkbutton(label="Auto-save", variable=self.auto_save_var, command=self.sync_title_with_content)
        # Loading Order Menu
        load_order_menu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Loading Order", state="disable", menu=load_order_menu)
        # Loading Order Options
        order_options = ["Name (default)", "File size", "Date created", "Extension", "Last Access time", "Last write time"]
        for option in order_options:
            load_order_menu.add_radiobutton(label=option, variable=self.load_order_var, value=option, command=self.load_pairs)
        # Loading Order Direction
        load_order_menu.add_separator()
        load_order_menu.add_radiobutton(label="Ascending", variable=self.reverse_load_order_var, value=False, command=self.load_pairs)
        load_order_menu.add_radiobutton(label="Descending", variable=self.reverse_load_order_var, value=True, command=self.load_pairs)
        # Autocomplete Settings Menu
        autocompleteSettingsMenu = Menu(self.optionsMenu, tearoff=0)
        self.optionsMenu.add_cascade(label="Autocomplete", state="disable", menu=autocompleteSettingsMenu)
        # Suggestion Dictionary Menu
        dictionaryMenu = Menu(autocompleteSettingsMenu, tearoff=0)
        autocompleteSettingsMenu.add_cascade(label="Dictionary", menu=dictionaryMenu)
        dictionaryMenu.add_checkbutton(label="English Dictionary", variable=self.csv_english_dictionary, command=self.autocomplete.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Danbooru", variable=self.csv_danbooru, command=self.autocomplete.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Danbooru (Safe)", variable=self.csv_danbooru_safe, command=self.autocomplete.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Derpibooru", variable=self.csv_derpibooru, command=self.autocomplete.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="e621", variable=self.csv_e621, command=self.autocomplete.update_autocomplete_dictionary)
        dictionaryMenu.add_separator()
        dictionaryMenu.add_command(label="Clear Selection", command=self.autocomplete.clear_dictionary_csv_selection)
        # Suggestion Threshold Menu
        suggestion_threshold_menu = Menu(autocompleteSettingsMenu, tearoff=0)
        autocompleteSettingsMenu.add_cascade(label="Threshold", menu=suggestion_threshold_menu)
        for level in ["Slow", "Normal", "Fast", "Faster"]:
            suggestion_threshold_menu.add_radiobutton(label=level, variable=self.suggestion_threshold_var, value=level, command=self.autocomplete.set_suggestion_threshold)
        # Suggestion Quantity Menu
        suggestion_quantity_menu = Menu(autocompleteSettingsMenu, tearoff=0)
        autocompleteSettingsMenu.add_cascade(label="Quantity", menu=suggestion_quantity_menu)
        for quantity in range(0, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(quantity), variable=self.suggestion_quantity_var, value=quantity, command=lambda suggestion_quantity=quantity: self.autocomplete.set_suggestion_quantity(suggestion_quantity))
        # Match Mode Menu
        match_mode_menu = Menu(autocompleteSettingsMenu, tearoff=0)
        autocompleteSettingsMenu.add_cascade(label="Match Mode", menu=match_mode_menu)
        match_modes = {"Match Whole String": False, "Match Last Word": True}
        for mode, value in match_modes.items():
            match_mode_menu.add_radiobutton(label=mode, variable=self.last_word_match_var, value=value)
        self.optionsMenu.add_separator()
        # Set external editor
        self.optionsMenu.add_command(label="Set Default External Image Editor...", state="disable", command=self.set_external_image_editor_path)
        self.optionsMenu.add_separator()
        # Restore last path on startup
        self.optionsMenu.add_checkbutton(label="Restore Last Path", state="disable", variable=self.restore_last_path_var)
        # Restore last window and Windowpane geometry on startup
        self.optionsMenu.add_checkbutton(label="Restore Last Window Size", state="disable", variable=self.restore_last_window_size_var)
        # Restore last text pane heights when switching tabs
        self.optionsMenu.add_checkbutton(label="Restore Last Text Pane Heights", state="disable", variable=self.restore_last_text_pane_heights_var)
        # Reset Settings
        self.optionsMenu.add_separator()
        self.optionsMenu.add_command(label="Reset All Settings", state="disable", command=self.settings_manager.reset_settings)
        self.optionsMenu.add_command(label="Reset Window and Tab Size", state="disable", command=self.reset_window_geometry)



    def create_tools_menu(self):
        # Batch Operations
        self.batch_operations_menu = Menu(self.toolsMenu, tearoff=0)
        self.toolsMenu.add_cascade(label="Batch Operations", state="disable", menu=self.batch_operations_menu)
        self.batch_operations_menu.add_command(label="Batch Crop Images...", command=self.batch_crop_images)
        self.batch_operations_menu.add_separator()
        self.batch_operations_menu.add_command(label="Trim Excess Tags...", command=self.batch_trim_tags)
        self.batch_operations_menu.add_command(label="Create Wildcard From Text Files...", command=self.collate_captions)
        self.batch_operations_menu.add_separator()
        self.batch_operations_menu.add_command(label="Clear All Text Files...", command=lambda: self.delete_all_text_or_files(delete_file=False))
        self.batch_operations_menu.add_command(label="Delete All Text Files...", command=lambda: self.delete_all_text_or_files(delete_file=True))
        self.batch_operations_menu.add_separator()
        self.batch_operations_menu.add_command(label="Check File Pair Collisions...", command=self.check_file_pair_collisions)
        # Edit Current Pair
        self.individual_operations_menu = Menu(self.toolsMenu, tearoff=0)
        self.toolsMenu.add_cascade(label="Edit Current Pair", state="disable", menu=self.individual_operations_menu)
        self.individual_operations_menu.add_command(label="Upscale...", command=lambda: self.create_batch_upscale_ui(show=True, quick_swap=True))
        self.individual_operations_menu.add_command(label="Crop...", command=lambda: self.create_crop_ui(show=True, refresh=True))
        self.individual_operations_menu.add_command(label="Resize...", command=self.resize_image)
        self.individual_operations_menu.add_command(label="Expand", command=self.expand_image)
        self.individual_operations_menu.add_command(label="Rotate", command=self.rotate_current_image)
        self.individual_operations_menu.add_command(label="Flip", command=self.flip_current_image)
        self.individual_operations_menu.add_separator()
        self.individual_operations_menu.add_command(label="AutoTag", command=self.text_controller.auto_tag.interrogate_image_tags)
        self.individual_operations_menu.add_separator()
        self.individual_operations_menu.add_command(label="Extract GIF/Video Frames...", command=lambda: frame_extractor.extract_frames(self))


    def enable_menu_options(self):
        tool_commands = [
            "Batch Operations",
            "Edit Current Pair"
        ]
        file_commands = [
            "Open Current Directory...",
            "Refresh Files",
            "Open Current Image...",
            "Open Text File...",
            "Edit Image...",
            "Zip Dataset..."
        ]
        edit_commands = [
            "Save Text",
            "Cleanup All Text Files...",
            "Create Blank Text Pairs...",
            "Rename Pair",
            "Duplicate Pair",
            "Delete Pair",
            #"Undo Delete",
            "Next Empty Text File",
            "Random File"
        ]
        options_commands = [
            "Text Options",
            "Loading Order",
            "Autocomplete",
            "Set Default External Image Editor...",
            "Restore Last Path",
            "Restore Last Window Size",
            "Restore Last Text Pane Heights",
            "Reset All Settings",
            "Reset Window and Tab Size"
        ]
        for t_command in tool_commands:
            self.toolsMenu.entryconfig(t_command, state="normal")
        for f_command in file_commands:
            self.fileMenu.entryconfig(f_command, state="normal")
        for e_command in edit_commands:
            self.editMenu.entryconfig(e_command, state="normal")
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
        self.view_menubutton.configure(state="normal")
        # Bindings
        self.suggestion_textbox.bind("<Button-3>", self.show_suggestion_context_menu)
        self.image_index_entry.bind("<Button-3>", self.open_index_context_menu)
        self.total_images_label.bind("<Button-3>", self.open_index_context_menu)
        self.index_pair_label.bind("<Button-3>", self.open_index_context_menu)


#endregion
#region Create Primary UI


    def create_primary_ui(self):
        # The main container for UI widgets and Alt-UI tabs
        self.create_main_notebook()
        # Build the primary UI within the 'Primary' tab
        self.setup_primary_frames()
        self.create_primary_widgets()


    def create_main_notebook(self):
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(expand=True, fill="both")
        self.main_notebook.bind("<<NotebookTabChanged>>", self.on_altui_tab_change)
        # Create Notebook Tabs
        self.primary_tab = Frame(self.main_notebook)
        self.batch_tag_edit_tab = Frame(self.main_notebook)
        self.crop_ui_tab = Frame(self.main_notebook)
        self.batch_upscale_tab = Frame(self.main_notebook)
        self.batch_resize_images_tab = Frame(self.main_notebook)
        self.batch_rename_tab = Frame(self.main_notebook)
        self.batch_img_edit_tab = Frame(self.main_notebook)
        self.find_dupe_file_tab = Frame(self.main_notebook)
        # Add Tabs to Notebook
        self.main_notebook.add(self.primary_tab, text="Tagger")
        self.main_notebook.add(self.batch_tag_edit_tab, text="Tag-Editor")
        self.main_notebook.add(self.crop_ui_tab, text="Crop")
        self.main_notebook.add(self.batch_upscale_tab, text="Batch Upscale")
        self.main_notebook.add(self.batch_resize_images_tab, text="Batch Resize")
        self.main_notebook.add(self.batch_rename_tab, text="Batch Rename")
        self.main_notebook.add(self.batch_img_edit_tab, text="Batch Img Edit")
        self.main_notebook.add(self.find_dupe_file_tab, text="Find Duplicates")
        # Disable all but the primary tab
        self.toggle_main_notebook_state("disable")


    def setup_primary_frames(self):
        # Configure the grid weights for the container tab
        self.primary_tab.grid_rowconfigure(0, weight=1)
        self.primary_tab.grid_columnconfigure(0, weight=1)
        # primary_paned_window is used to contain the ImgTxtViewer UI.
        self.primary_paned_window = PanedWindow(self.primary_tab, orient="horizontal", sashwidth=6, bg="#d0d0d0", bd=0)
        self.primary_paned_window.grid(row=0, column=0, sticky="nsew")
        self.primary_paned_window.bind("<B1-Motion>", self.disable_button)
        # master_image_frame: exclusively used for the master_image_inner_frame and image_grid.
        self.master_image_frame = Frame(self.primary_tab)
        self.master_image_frame.grid_rowconfigure(0, weight=0)  # stats frame row
        self.master_image_frame.grid_rowconfigure(1, weight=1)  # image frame row
        self.master_image_frame.grid_columnconfigure(0, weight=1)
        self.primary_paned_window.add(self.master_image_frame, stretch="always")
        self.master_image_inner_frame = Frame(self.master_image_frame)
        self.master_image_inner_frame.grid(row=1, column=0, sticky="nsew")
        self.master_image_inner_frame.grid_columnconfigure(0, weight=1)
        self.master_image_inner_frame.grid_rowconfigure(1, weight=1)
        self.image_grid = image_grid.ImageGrid(self.master_image_frame, self)
        self.image_grid.grid(row=1, column=0, sticky="nsew")
        self.image_grid.grid_remove()
        # master_control_frame serves as a container for all primary UI frames (except the master image frame)
        self.master_control_frame = Frame(self.primary_tab)
        self.primary_paned_window.add(self.master_control_frame, stretch="always")
        self.primary_paned_window.paneconfigure(self.master_control_frame, minsize=300)
        self.primary_paned_window.update()
        self.primary_paned_window.sash_place(0, 0, 0)


    def create_primary_widgets(self):
        # Image stats
        self.stats_frame = Frame(self.master_image_frame)
        self.stats_frame.grid(row=0, column=0, sticky="new")
        self.stats_frame.grid_columnconfigure(1, weight=1)
        # View Menu
        self.view_menubutton = ttk.Menubutton(self.stats_frame, text="View", state="disable")
        self.view_menubutton.grid(row=0, column=0)
        self.view_menu = Menu(self.view_menubutton, tearoff=0)
        self.view_menubutton.config(menu=self.view_menu)
        self.view_menu.add_checkbutton(label="Toggle Image-Grid", accelerator="F1", variable=self.is_image_grid_visible_var, command=self.toggle_image_grid)
        self.view_menu.add_checkbutton(label="Toggle Thumbnail Panel", variable=self.thumbnails_visible, command=self.debounce_update_thumbnail_panel)
        self.view_menu.add_checkbutton(label="Toggle Edit Panel", variable=self.edit_panel_visible_var, command=self.edit_panel.toggle_edit_panel)
        self.view_menu.add_separator()
        self.view_menu.add_checkbutton(label="Always On Top", variable=self.always_on_top_var, command=self.set_always_on_top)
        self.view_menu.add_checkbutton(label="Big Save Button", variable=self.big_save_button_var, command=self.toggle_save_button_height)
        self.view_menu.add_separator()
        self.view_menu.add_checkbutton(label="UI: Vertical View", variable=self.panes_swap_ns_var, command=self.swap_pane_orientation)
        self.view_menu.add_checkbutton(label="UI: Swap img-txt Sides", variable=self.panes_swap_ew_var, command=self.swap_pane_sides)
        image_quality_menu = Menu(self.view_menu, tearoff=0)
        self.view_menu.add_separator()
        self.view_menu.add_cascade(label="Image Display Quality", menu=image_quality_menu)
        for value in ["High", "Normal", "Low"]:
            image_quality_menu.add_radiobutton(label=value, variable=self.image_quality_var, value=value, command=self.set_image_quality)
        # Image Stats
        self.label_image_stats = Label(self.stats_frame, text="...")
        self.label_image_stats.grid(row=0, column=1, sticky="ew")
        self.label_image_stats_tooltip = Tip.create(widget=self.label_image_stats, text="...")
        ttk.Separator(self.stats_frame, orient="horizontal").grid(row=2, column=0, columnspan=2, sticky="ew")
        # Primary Image
        self.primary_display_image = ImageZoomWidget(self.master_image_inner_frame, on_render_done=self.on_imagezoomwidget_render)
        self.primary_display_image.grid(row=1, column=0, sticky="nsew")
        self.primary_display_image.canvas.bind("<Double-1>", lambda event: self.open_image(index=self.current_index, event=event))
        self.primary_display_image.canvas.bind("<Shift-MouseWheel>", self.mousewheel_nav)
        self.primary_display_image.canvas.bind("<Button-3>", self.show_image_context_menu)
        # Video Player
        self.video_player = VideoPlayerWidget(master=self.master_image_inner_frame)
        self.video_player.grid(row=1, column=0, sticky="nsew")
        self.video_player.grid_remove()
        # Thumbnail Panel
        self.thumbnail_panel = ThumbnailPanel(master=self.master_image_inner_frame, app=self)
        self.thumbnail_panel.grid(row=3, column=0, sticky="ew")
        # Edit Image Panel
        self.edit_image_panel = Frame(self.master_image_inner_frame, relief="ridge", bd=1)
        self.edit_image_panel.grid(row=2, column=0, sticky="ew")
        self.edit_image_panel.grid_remove()
        # Directory Selection
        directory_frame = Frame(self.master_control_frame)
        directory_frame.pack(side="top", fill="x", padx=(0,2))
        self.text_path_indicator = Label(directory_frame)
        self.text_path_indicator.pack(side="left", fill="y", pady=2)
        self.text_path_tooltip = Tip.create(widget=self.text_path_indicator, text="Text Path: Same as image path", show_delay=10)
        self.directory_entry = ttk.Entry(directory_frame, textvariable=self.image_dir)
        self.directory_entry.pack(side="left", fill="both", expand=True, pady=2)
        self.directory_entry.bind('<Return>', self.set_working_directory)
        self.directory_entry.bind('<FocusOut>', self.check_image_dir)
        _, self.dir_context_menu, _ = self.entry_helper.bind_helpers(self.directory_entry)
        self.directory_entry_tooltip = Tip.create(widget=self.directory_entry, text="...", padx=1, pady=2, origin="widget", widget_anchor="sw")
        self.dir_context_menu.add_command(label="Set Text File Path...", state="disabled", command=self.set_text_file_path)
        self.dir_context_menu.add_command(label="Reset Text Path To Image Path", state="disabled", command=lambda: self.set_text_file_path(self.image_dir.get()))
        self.browse_button = ttk.Button(directory_frame, text="Browse...", width=8, takefocus=False, command=self.choose_working_directory)
        self.browse_button.pack(side="left", pady=2)
        Tip.create(widget=self.browse_button, text="Right click to set an alternate path for text files")
        self.browse_context_menu = Menu(self.browse_button, tearoff=0)
        self.browse_context_menu.add_command(label="Set Text File Path...", state="disabled", command=self.set_text_file_path)
        self.browse_context_menu.add_command(label="Reset Text Path To Image Path", state="disabled", command=lambda: self.set_text_file_path(self.image_dir.get()))
        self.browse_button.bind("<Button-3>", self.open_browse_context_menu)
        self.open_button = ttk.Button(directory_frame, text="Open", width=8, takefocus=False, command=lambda: self.open_directory(self.directory_entry.get()))
        self.open_button.pack(side="left", pady=2)
        # Image Index
        self.index_frame = Frame(self.master_control_frame, relief="raised")
        self.index_frame.pack(side="top", fill="x", padx=2)
        self.index_pair_label = Label(self.index_frame, text="Pair", state="disabled")
        self.index_pair_label.pack(side="left")
        self.image_index_entry = ttk.Entry(self.index_frame, width=5, state="disabled")
        self.image_index_entry.pack(side="left")
        self.image_index_entry.bind("<Return>", self.jump_to_image)
        self.image_index_entry.bind("<MouseWheel>", self.mousewheel_nav)
        self.image_index_entry.bind("<Up>", self.next_pair)
        self.image_index_entry.bind("<Down>", self.prev_pair)
        self.entry_helper.bind_undo_stack(self.image_index_entry)
        self.index_context_menu = Menu(self.directory_entry, tearoff=0)
        self.index_context_menu.add_command(label="First", command=lambda: self.index_goto(0))
        self.index_context_menu.add_command(label="Last", command=lambda: self.index_goto(len(self.image_files)))
        self.index_context_menu.add_command(label="Random", accelerator="Ctrl+R", command=self.index_goto_random)
        self.index_context_menu.add_command(label="Next Empty", accelerator="Ctrl+E", command=self.index_goto_next_empty)
        self.total_images_label = Label(self.index_frame, text=f"of {len(self.image_files)}", state="disabled")
        self.total_images_label.pack(side="left")
        # Save Button
        self.save_button = ttk.Button(self.index_frame, text="Save", state="disabled", style="Blue.TButton", padding=(5, 5), takefocus=False, command=self.save_text_file)
        self.save_button.pack(side="left", pady=2, fill="x", expand=True)
        Tip.create(widget=self.save_button, text="CTRL+S to save")
        self.auto_save_checkbutton = ttk.Checkbutton(self.index_frame, width=10, text="Auto-save", state="disabled", variable=self.auto_save_var, takefocus=False, command=self.sync_title_with_content)
        self.auto_save_checkbutton.pack(side="left")
        Tip.create(widget=self.auto_save_checkbutton, text="Automatically save the current text file when:\nNavigating img-txt pairs, changing active directory, or closing the app")
        # Navigation Buttons
        nav_button_frame = Frame(self.master_control_frame)
        nav_button_frame.pack(fill="x", padx=2)
        self.next_button = ttk.Button(nav_button_frame, text="Next", width=12, state="disabled", takefocus=False, command=lambda: self.update_pair("next"))
        self.prev_button = ttk.Button(nav_button_frame, text="Previous", width=12, state="disabled", takefocus=False, command=lambda: self.update_pair("prev"))
        self.next_button.pack(side="right", fill="x", expand=True)
        self.prev_button.pack(side="right", fill="x", expand=True)
        Tip.create(widget=self.next_button, text="Hotkey: ALT+R\nHold shift to advance by 5")
        Tip.create(widget=self.prev_button, text="Hotkey: ALT+L\nHold shift to advance by 5")
        # Suggestion text
        self.suggestion_frame = Frame(self.master_control_frame, bg='#f0f0f0')
        self.suggestion_frame.pack(side="top", fill="x", pady=2)
        self.suggestion_textbox = Text(self.suggestion_frame, height=1, width=1, borderwidth=0, highlightthickness=0, bg='#f0f0f0', state="disabled", cursor="arrow")
        self.suggestion_textbox.pack(side="left", fill="x", expand=True)
        self.suggestion_textbox.bind("<Button-1>", self.disable_button)
        self.suggestion_textbox.bind("<B1-Motion>", self.disable_button)
        Tip.create(widget=self.suggestion_textbox,
            text=["Color Codes:",
            "Danbooru:\n"
            "  - General tags: Black\n"
            "  - Artists: Red\n"
            "  - Copyright: Magenta\n"
            "  - Characters: Green\n"
            "  - Meta: Orange",
            "e621:\n"
            "  - General tags: Black\n"
            "  - Artists: Yellow\n"
            "  - Copyright: Magenta\n"
            "  - Characters: Green\n"
            "  - Species: Orange\n"
            "  - Meta: Red\n"
            "  - Lore: Green",
            "Derpibooru:\n"
            "  - General tags: Black\n"
            "  - Official Content: Yellow\n"
            "  - Species: Light-Orange\n"
            "  - Original Content: Pink\n"
            "  - Rating: Blue\n"
            "  - Body Type: Gray\n"
            "  - Character: Teal\n"
            "  - Original Content: Light-Purple\n"
            "  - Error: Red\n"
            "  - Official Content: Dark-Orange\n"
            "  - Original Content: Light-Pink"],
            justify="left"
        )
        # Suggestion Options
        self.suggestion_menubutton = ttk.Button(self.suggestion_frame, text="☰", takefocus=False, width=2, command=lambda: self.show_suggestion_context_menu(button=True))
        self.suggestion_menubutton.pack(side="right", padx=2)
        # Startup info text
        self.info_text = TextPanel(self.master_control_frame, text=HelpText.IMG_TXT_VIEWER_ABOUT, rich_text=True)
        self.info_text.pack(expand=True, fill="both")


#endregion
#region Text Box setup


    # --------------------------------------
    # Text Pane
    # --------------------------------------
    def create_text_pane(self):
        if not hasattr(self, 'text_pane'):
            self.text_pane = PanedWindow(self.master_control_frame, orient="vertical", sashwidth=6, bg="#d0d0d0", bd=0)
            self.text_pane.pack(side="bottom", fill="both", expand=1)


    # --------------------------------------
    # Text Box
    # --------------------------------------
    def create_text_box(self):
        self.create_text_pane()
        if not hasattr(self, 'text_frame'):
            self.text_frame = Frame(self.master_control_frame)
            self.text_pane.add(self.text_frame, stretch="always")
            self.text_pane.paneconfigure(self.text_frame, minsize=80)
            self.text_frame.grid_rowconfigure(1, weight=1)
            self.text_frame.grid_columnconfigure(0, weight=1)
            # Create Text Box
            self.text_box = custom_scrolledtext.CustomScrolledText(self.text_frame, wrap="word", undo=True, maxundo=200, inactiveselectbackground="#0078d7")
            self.text_box.grid(row=1, column=0, sticky="nsew")
            self.text_box.tag_configure("highlight", background="#5da9be", foreground="white")
            self.text_box.config(font=(self.font_var.get(), self.font_size_var.get()))
            # Create FindReplaceEntry
            self.find_replace_widget = FindReplaceEntry(self.text_frame, self.text_box)
            self.find_replace_widget.grid(row=0, column=0, sticky="ew")
            self.find_replace_widget.grid_remove()
            self.set_text_box_binds()
            self.get_default_font()
            self.primary_paned_window.unbind("<B1-Motion>")
            self.primary_paned_window.bind('<ButtonRelease-1>', self.snap_sash_to_half)
        if not hasattr(self, 'text_widget_frame'):
            self.create_text_control_frame()


    # --------------------------------------
    # Text Widget Frame
    # --------------------------------------
    def create_text_control_frame(self):
        self.text_widget_frame = Frame(self.master_control_frame)
        self.text_widget_frame.bind("<Configure>", self.on_text_widget_frame_configure)
        self.text_pane.add(self.text_widget_frame, stretch="never")
        self.text_pane.paneconfigure(self.text_widget_frame, height=self.text_widget_tab_heights.get('S&R', 59))
        self.text_notebook = ttk.Notebook(self.text_widget_frame)
        self.text_notebook.bind("<<NotebookTabChanged>>", self.on_text_notebook_tab_change)
        self.tab1 = Frame(self.text_notebook)
        self.tab2 = Frame(self.text_notebook)
        self.tab3 = Frame(self.text_notebook)
        self.tab4 = Frame(self.text_notebook)
        self.tab5 = Frame(self.text_notebook)
        self.tab6 = Frame(self.text_notebook)
        self.tab7 = Frame(self.text_notebook)
        self.tab8 = Frame(self.text_notebook)
        self.tab9 = Frame(self.text_notebook)
        self.text_notebook.add(self.tab1, text='S&R')
        self.text_notebook.add(self.tab2, text='Prefix')
        self.text_notebook.add(self.tab3, text='Append')
        self.text_notebook.add(self.tab4, text='AutoTag')
        self.text_notebook.add(self.tab5, text='Filter')
        self.text_notebook.add(self.tab6, text='Highlight')
        self.text_notebook.add(self.tab7, text='Font')
        self.text_notebook.add(self.tab8, text='MyTags')
        self.text_notebook.add(self.tab9, text='Stats')
        self.text_notebook.pack(fill='both', expand=True)
        self.text_controller.create_search_and_replace_widgets_tab1()
        self.text_controller.create_prefix_text_widgets_tab2()
        self.text_controller.create_append_text_widgets_tab3()
        self.text_controller.create_auto_tag_widgets_tab4()
        self.text_controller.create_filter_text_image_pairs_widgets_tab5()
        self.text_controller.create_custom_active_highlight_widgets_tab6()
        self.text_controller.create_font_widgets_tab7()
        self.text_controller.create_custom_dictionary_widgets_tab8()
        self.text_controller.create_stats_widgets_tab9()
        #self.text_widget_frame.bind("<Configure>", lambda event: print(f"text_widget_frame height: {event.height}"))


    def on_text_notebook_tab_change(self, event):
        self.check_image_dir()
        previous_tab = self.current_text_notebook_tab
        self.current_text_notebook_tab = event.widget.tab("current", "text")
        self.save_text_pane_state(tab_name=previous_tab)
        self.config_text_pane_for_tab()
        self.update_mytags_tab()
        self.initialize_text_pane = False
        tabs_to_disable = ['S&R', 'Prefix', 'Append', 'Filter', 'Highlight', 'Font']
        if self.current_text_notebook_tab in tabs_to_disable:
            self.text_pane.bind("<B1-Motion>", self.disable_button)
        else:
            self.text_pane.unbind("<B1-Motion>")


    def on_text_widget_frame_configure(self, event):
        self.text_widget_frame_dict[self.current_text_notebook_tab] = event.height


    def save_text_pane_state(self, tab_name=None):
        if not self.initialize_text_pane:
            height = self.text_widget_frame.winfo_height()
            tab = tab_name if tab_name is not None else self.current_text_notebook_tab
            self.text_widget_frame_dict[tab] = height


    def config_text_pane_for_tab(self, reset=False):
        tab_height = self.text_widget_tab_heights.get(self.current_text_notebook_tab, 59)
        if not self.text_widget_frame_dict:
            height = tab_height
        else:
            if self.restore_last_text_pane_heights_var.get():
                height = self.text_widget_frame_dict.get(self.current_text_notebook_tab, tab_height)
            else:
                height = tab_height
        if reset:
            self.text_widget_frame_dict = self.text_widget_tab_heights.copy()
            height = self.text_widget_tab_heights.get(self.current_text_notebook_tab, 59)
        self.text_pane.paneconfigure(self.text_widget_frame, height=height)


    def update_mytags_tab(self):
        selected_tab = self.text_notebook.tab("current", "text")
        if selected_tab == "MyTags":
            self.text_controller.my_tags.refresh_all_tags_listbox()


    # --------------------------------------
    # Text Box Binds
    # --------------------------------------
    def set_text_box_binds(self):
        # Mouse binds
        self.text_box.bind("<Button-1>", lambda _: (self.remove_tag(), self.autocomplete.clear_suggestions()))
        self.text_box.bind("<Button-2>", lambda e: (self.delete_tag_under_mouse(e), self.sync_title_with_content(e)))
        self.text_box.bind("<Button-3>", lambda e: (self.show_text_context_menu(e)))
        # Update the autocomplete suggestion label after every KeyRelease.
        self.text_box.bind("<KeyRelease>", lambda e: (self.autocomplete.update_suggestions(e), self.sync_title_with_content(e), self.get_text_summary(), self.find_replace_widget.perform_search()))
        # Insert a newline after inserting an autocomplete suggestion when list_mode is active.
        self.text_box.bind('<comma>', self.autocomplete.insert_newline_listmode)
        # Highlight duplicates when selecting text with keyboard or mouse.
        self.text_box.bind("<Shift-Right>", lambda e: self.highlight_duplicates(e, mouse=False))
        self.text_box.bind("<Shift-Left>", lambda e: self.highlight_duplicates(e, mouse=False))
        self.text_box.bind("<ButtonRelease-1>", self.highlight_duplicates)
        # Removes highlights when these keys are pressed.
        self.text_box.bind("<Up>", self.remove_highlight, add="+")
        self.text_box.bind("<Down>", self.remove_highlight, add="+")
        self.text_box.bind("<Left>", self.remove_highlight, add="+")
        self.text_box.bind("<Right>", self.remove_highlight, add="+")
        self.text_box.bind("<BackSpace>", lambda _: (self.remove_highlight(), self.sync_title_with_content()))
        # Update the title status whenever a key is pressed.
        self.text_box.bind("<Key>", lambda e: self.sync_title_with_content(e))
        # Disable normal button behavior
        self.text_box.bind("<Tab>", self.disable_button)
        self.text_box.bind("<Alt_L>", self.disable_button)
        self.text_box.bind("<Alt_R>", self.disable_button)
        # Show next empty text file
        self.text_box.bind("<Control-e>", self.index_goto_next_empty)
        # Show random img-txt pair
        self.text_box.bind("<Control-r>", self.index_goto_random)
        # Delete previous word with Ctrl+Backspace
        self.text_box.bind("<Control-BackSpace>", self.delete_word_before_cursor)
        # Display FindReplaceEntry
        self.text_box.bind("<Control-f>", self.find_replace_widget.show_widget)
        # Refresh text box
        #self.text_box.bind("<F5>", lambda e: self.refresh_text_box())


    # --------------------------------------
    # Text Box Context Menu
    # --------------------------------------
    def show_text_context_menu(self, event):
        if hasattr(self, 'text_box'):
            self.text_box.focus_set()
        widget_in_focus = self.root.focus_get()
        text_context_menu = Menu(self.root, tearoff=0)
        if widget_in_focus == getattr(self, 'text_box', None):
            widget_in_focus.focus_set()
            select_state = "disabled"
            cleaning_state = "normal" if self.cleaning_text_var.get() else "disabled"
            try:
                selected_text = self.text_box.get("sel.first", "sel.last")
                if len(selected_text) >= 3:
                    select_state = "normal"
            except TclError:
                pass
            text_context_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: (widget_in_focus.event_generate('<<Cut>>'), self.sync_title_with_content()))
            text_context_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: (widget_in_focus.event_generate('<<Copy>>')))
            text_context_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: (widget_in_focus.event_generate('<<Paste>>'), self.sync_title_with_content()))
            text_context_menu.add_command(label="Delete", accelerator="Del", command=lambda: (widget_in_focus.event_generate('<<Clear>>'), self.sync_title_with_content()))
            text_context_menu.add_command(label="Refresh", command=self.refresh_text_box)
            text_context_menu.add_separator()
            text_context_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: (widget_in_focus.event_generate('<<Undo>>'), self.sync_title_with_content()))
            text_context_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: (widget_in_focus.event_generate('<<Redo>>'), self.sync_title_with_content()))
            text_context_menu.add_separator()
            text_context_menu.add_command(label="Open Text Directory...", command=self.open_text_directory)
            text_context_menu.add_command(label="Open Text File...", command=self.open_textfile)
            text_context_menu.add_command(label="Add to MyTags", state=select_state, command=lambda: self.text_controller.my_tags.add_to_custom_dictionary(origin="text_box"))
            text_context_menu.add_separator()
            text_context_menu.add_command(label="Highlight all Duplicates", accelerator="Ctrl+F", command=self.highlight_all_duplicates)
            text_context_menu.add_command(label="Next Empty Text File", accelerator="Ctrl+E", command=self.index_goto_next_empty)
            text_context_menu.add_separator()
            text_context_menu.add_checkbutton(label="Highlight Selection", variable=self.highlight_selection_var)
            text_context_menu.add_checkbutton(label="Clean-Text", variable=self.cleaning_text_var, command=self.toggle_list_menu)
            text_context_menu.add_checkbutton(label="List View", variable=self.list_mode_var, state=cleaning_state, command=self.toggle_list_mode)
        text_context_menu.tk_popup(event.x_root, event.y_root)


    # --------------------------------------
    # Image Context Menu
    # --------------------------------------
    def show_image_context_menu(self, event):
        self.image_context_menu = Menu(self.root, tearoff=0)
        # Open
        self.image_context_menu.add_command(label="Open Current Directory...", command=self.open_image_directory)
        self.image_context_menu.add_command(label="Open Current Image...", command=self.open_image)
        self.image_context_menu.add_command(label="Edit Image...", accelerator="F4", command=self.open_image_in_editor)
        self.image_context_menu.add_command(label="AutoTag", command=self.text_controller.auto_tag.interrogate_image_tags)
        self.image_context_menu.add_separator()
        # File
        self.image_context_menu.add_command(label="Duplicate img-txt pair", command=self.duplicate_pair)
        self.image_context_menu.add_command(label="Delete img-txt Pair", accelerator="Shift+Del", command=self.delete_pair)
        self.image_context_menu.add_command(label="Undo Delete", command=self.undo_delete_pair, state=self.undo_state.get())
        self.image_context_menu.add_separator()
        # Edit
        self.image_context_menu.add_command(label="Rename Pair", command=self.manually_rename_single_pair)
        self.image_context_menu.add_command(label="Upscale...", command=lambda: self.create_batch_upscale_ui(show=True, quick_swap=True))
        self.image_context_menu.add_command(label="Resize...", command=self.resize_image)
        self.image_context_menu.add_command(label="Crop...", command=lambda: self.create_crop_ui(show=True, refresh=True))
        self.image_context_menu.add_separator()
        self.image_context_menu.add_command(label="Expand", command=self.expand_image)
        self.image_context_menu.add_command(label="Rotate", command=self.rotate_current_image)
        self.image_context_menu.add_command(label="Flip", command=self.flip_current_image)
        self.image_context_menu.tk_popup(event.x_root, event.y_root)


    # --------------------------------------
    # Suggestion Context Menu
    # --------------------------------------
    def show_suggestion_context_menu(self, event=None, button=False):
        suggestion_context_menu = Menu(self.root, tearoff=0)
        suggestion_context_menu.add_command(label="Suggestion Options", state="disabled")
        suggestion_context_menu.add_separator()
        # Selected Dictionary
        dictionary_menu = Menu(suggestion_context_menu, tearoff=0)
        suggestion_context_menu.add_cascade(label="Dictionary", menu=dictionary_menu)
        dictionary_menu.add_checkbutton(label="English Dictionary", variable=self.csv_english_dictionary, command=self.autocomplete.update_autocomplete_dictionary)
        dictionary_menu.add_checkbutton(label="Danbooru", variable=self.csv_danbooru, command=self.autocomplete.update_autocomplete_dictionary)
        dictionary_menu.add_checkbutton(label="Danbooru (Safe)", variable=self.csv_danbooru_safe, command=self.autocomplete.update_autocomplete_dictionary)
        dictionary_menu.add_checkbutton(label="Derpibooru", variable=self.csv_derpibooru, command=self.autocomplete.update_autocomplete_dictionary)
        dictionary_menu.add_checkbutton(label="e621", variable=self.csv_e621, command=self.autocomplete.update_autocomplete_dictionary)
        dictionary_menu.add_separator()
        dictionary_menu.add_command(label="Clear Selection", command=self.autocomplete.clear_dictionary_csv_selection)
        # Suggestion Threshold
        suggestion_threshold_menu = Menu(suggestion_context_menu, tearoff=0)
        suggestion_context_menu.add_cascade(label="Threshold", menu=suggestion_threshold_menu)
        threshold_levels = ["Slow", "Normal", "Fast", "Faster"]
        for level in threshold_levels:
            suggestion_threshold_menu.add_radiobutton(label=level, variable=self.suggestion_threshold_var, value=level, command=self.autocomplete.set_suggestion_threshold)
        # Suggestion Quantity
        suggestion_quantity_menu = Menu(suggestion_context_menu, tearoff=0)
        suggestion_context_menu.add_cascade(label="Quantity", menu=suggestion_quantity_menu)
        for quantity in range(0, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(quantity), variable=self.suggestion_quantity_var, value=quantity, command=lambda suggestion_quantity=quantity: self.autocomplete.set_suggestion_quantity(suggestion_quantity))
        # Match Mode
        match_mode_menu = Menu(suggestion_context_menu, tearoff=0)
        suggestion_context_menu.add_cascade(label="Match Mode", menu=match_mode_menu)
        match_modes = {"Match Whole String": False, "Match Last Word": True}
        for mode, value in match_modes.items():
            match_mode_menu.add_radiobutton(label=mode, variable=self.last_word_match_var, value=value)
        # Position
        x, y = (event.x_root, event.y_root) if not button else (self.suggestion_menubutton.winfo_rootx(), self.suggestion_menubutton.winfo_rooty())
        suggestion_context_menu.tk_popup(x, y)


    # --------------------------------------
    # Misc UI logic
    # --------------------------------------


    def get_default_font(self):
        self.current_font = self.text_box.cget("font")
        self.current_font_name = self.text_box.tk.call("font", "actual", self.current_font, "-family")
        self.current_font_size = self.text_box.tk.call("font", "actual", self.current_font, "-size")
        self.default_font = self.current_font_name
        self.default_font_size = self.current_font_size


    def get_text_summary(self):
        try:
            if hasattr(self, 'text_box'):
                text_content = self.text_box.get("1.0", "end-1c")
                char_count = len(text_content)
                word_count = len([word for word in text_content.split() if word.strip()])
                self.text_controller.stats_info_lbl.config(text=f"Characters: {char_count}  |  Words: {word_count}")
                return char_count, word_count
            return 0, 0
        except Exception:
            return 0, 0


# --------------------------------------
# Browse button context menu
# --------------------------------------
    def open_browse_context_menu(self, event):
        try:
            self.browse_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.browse_context_menu.grab_release()


    def set_text_file_path(self, path=None, silent=False):
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
        if not silent:
            self.show_pair()
        self.update_text_path_indicator()


    def update_text_path_indicator(self):
        if os.path.normpath(self.text_dir) != os.path.normpath(self.image_dir.get()):
            self.text_path_indicator.config(bg="#5da9be")
            self.text_path_tooltip.config(text=f"Text Path: {os.path.normpath(self.text_dir)}")
        else:
            self.text_path_indicator.config(bg="#f0f0f0")
            self.text_path_tooltip.config(text="Text Path: Same as image path")


#endregion
#region Additional UI Setup


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
    def toggle_save_button_height(self, event=None, reset=None):
        if reset:
            self.big_save_button_var.set(True)
            self.save_button.config(padding=(5, 5))
            return
        else:
            if self.big_save_button_var.get():
                self.save_button.config(padding=(5, 5))
            else:
                self.save_button.config(padding=(1, 1))


# --------------------------------------
# PanedWindow
# --------------------------------------
    def configure_pane_position(self):
        window_width = self.root.winfo_width()
        self.primary_paned_window.sash_place(0, window_width // 2, 0)
        self.configure_pane()


    def swap_pane_sides(self, swap_state=None, center=True):
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
        if center:
            self.root.after_idle(self.configure_pane_position)


    def swap_pane_orientation(self, swap_state=None, center=True):
        if swap_state is None:
            swap_state = self.panes_swap_ns_var.get()
        else:
            self.panes_swap_ns_var.set(swap_state)
        new_orient = 'vertical' if swap_state else 'horizontal'
        self.primary_paned_window.configure(orient=new_orient)
        if new_orient == 'horizontal':
            self.root.minsize(0, 200)
        else:
            self.root.minsize(200, 0)
        if center:
            self.root.after_idle(self.configure_pane_position)


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


    def get_windowpane_state(self, windowpane: 'PanedWindow') -> dict:
        self.root.update_idletasks()
        windowpane.update_idletasks()
        sash_x, sash_y = windowpane.sash_coord(0)
        orient = windowpane.cget("orient")
        if orient == 'vertical':
            total_length = windowpane.winfo_height()
            fallback = self.root.winfo_height()
            position = sash_y
        else:
            total_length = windowpane.winfo_width()
            fallback = self.root.winfo_width()
            position = sash_x
        if total_length <= 1:
            total_length = fallback
        if total_length > 1:
            try:
                ratio = float(position) / float(total_length)
            except ZeroDivisionError:
                ratio = 0.5
        else:
            ratio = 0.5
        ratio = max(0.0, min(1.0, float(ratio)))
        return {
            "ratio": ratio,
            "position": float(position),
            "length": float(total_length) if total_length else 0.0,
            "orient": orient,
        }


    def set_windowpane_state(self, windowpane: 'PanedWindow', state: dict):
        if not isinstance(state, dict):
            return
        orient = state.get("orient")
        orient = orient if orient in ("horizontal", "vertical") else windowpane.cget("orient")
        windowpane.configure(orient=orient)
        if orient == "horizontal":
            self.root.minsize(0, 200)
        else:
            self.root.minsize(200, 0)

        def apply_position():
            if orient == "vertical":
                total_length = windowpane.winfo_height()
                fallback = self.root.winfo_height()
            else:
                total_length = windowpane.winfo_width()
                fallback = self.root.winfo_width()
            if total_length <= 1:
                total_length = state.get("length") or fallback or 0
            ratio = state.get("ratio")
            position = state.get("position")
            try:
                if ratio is not None and total_length:
                    ratio = max(0.0, min(1.0, float(ratio)))
                    position = ratio * total_length
            except (TypeError, ValueError):
                pass
            if position is None:
                ref_length = state.get("length")
                ref_ratio = state.get("ratio")
                if ref_length not in (None, 0) and state.get("position") is not None:
                    try:
                        ref_ratio = state["position"] / ref_length
                    except (TypeError, ZeroDivisionError):
                        ref_ratio = None
                if ref_ratio is not None and total_length:
                    position = ref_ratio * total_length
            if position is None:
                position = total_length / 2
            try:
                position = max(0, min(total_length, int(position)))
            except (TypeError, ValueError):
                position = total_length // 2
            if orient == "vertical":
                windowpane.sash_place(0, 0, position)
            else:
                windowpane.sash_place(0, position, 0)
            self.configure_pane()
            windowpane.after(250, self.refresh_image)

        self.root.after_idle(apply_position)


# --------------------------------------
# Thumbnail Panel
# --------------------------------------
    def debounce_update_thumbnail_panel(self, event=None):
        if not hasattr(self, 'thumbnail_panel'):
            return
        if self.update_thumbnail_job_id is not None:
            self.root.after_cancel(self.update_thumbnail_job_id)
        self.update_thumbnail_job_id = self.root.after(50, self.thumbnail_panel.update_panel)


#endregion
#region Alt-UI Setup


    def toggle_main_notebook_state(self, state):
        tabs = [
            self.batch_tag_edit_tab,
            self.crop_ui_tab,
            self.batch_upscale_tab,
            self.batch_resize_images_tab,
            self.batch_rename_tab,
            self.batch_img_edit_tab,
            self.find_dupe_file_tab,
        ]
        if state == "normal":
            for tab in tabs:
                self.main_notebook.tab(tab, state="normal")
        else:
            for tab in tabs:
                self.main_notebook.tab(tab, state="disabled")


    def on_altui_tab_change(self, event):
        if self.image_dir.get() == self.dir_placeholder_text or len(self.image_files) == 0:
            self.main_notebook.select(self.primary_tab)
            return
        self.check_image_dir()
        selected_tab_index = self.main_notebook.index(self.main_notebook.select())
        tab_name = self.main_notebook.tab(selected_tab_index, "text")
        self.current_ui_state = {"tab": tab_name, "index": selected_tab_index}
        tab_states = {
            "Tagger": "ImgTxtViewer",
            "Tag-Editor": "BatchTagEdit",
            "Crop": "CropUI",
            "Batch Upscale": "BatchUpscale",
            "Batch Resize": "BatchResize",
            "Batch Rename": "BatchRename",
            "Batch Img Edit": "BatchImgEdit",
            "Find Duplicates": "FindDupeFile",
        }
        self.ui_state = tab_states.get(tab_name)
        if self.ui_state == "ImgTxtViewer":
            pass
        elif self.ui_state == "BatchTagEdit":
            self.create_batch_tag_edit_ui(show=True)
        elif self.ui_state == "CropUI":
            self.create_crop_ui(show=True)
        elif self.ui_state == "BatchUpscale":
            self.create_batch_upscale_ui(show=True)
        elif self.ui_state == "BatchResize":
            self.create_batch_resize_images_ui(show=True)
        elif self.ui_state == "BatchRename":
            self.create_batch_rename_ui(show=True)
        elif self.ui_state == "BatchImgEdit":
            self.create_batch_img_edit_ui(show=True)
        elif self.ui_state == "FindDupeFile":
            self.create_find_dupe_file_ui(show=True)
        self.update_menu_state()
        self.update_ui_binds()


    def update_menu_state(self):
        if not self.ui_state == "ImgTxtViewer":
            self.main_menu_bar.entryconfig("File", state="disable")
            self.main_menu_bar.entryconfig("Edit", state="disable")
            self.main_menu_bar.entryconfig("Options", state="disable")
            self.main_menu_bar.entryconfig("Tools", state="disable")
        else:
            self.main_menu_bar.entryconfig("File", state="normal")
            self.main_menu_bar.entryconfig("Edit", state="normal")
            self.main_menu_bar.entryconfig("Options", state="normal")
            self.main_menu_bar.entryconfig("Tools", state="normal")


    def update_ui_binds(self):
        bindings = [
            "<Control-f>",
            "<Control-s>",
            "<Alt-Right>",
            "<Alt-Left>",
            "<Shift-Delete>",
            "<Configure>",
            "<F1>",
            "<F2>",
            "<F4>",
        ]
        if self.ui_state == "ImgTxtViewer":
            self.root.bind("<Control-f>", self.find_replace_widget.show_widget)
            self.root.bind("<Control-s>", lambda event: self.save_text_file(highlight=True))
            self.root.bind("<Alt-Right>", lambda event: self.next_pair(event))
            self.root.bind("<Alt-Left>", lambda event: self.prev_pair(event))
            self.root.bind('<Shift-Delete>', lambda event: self.delete_pair())
            self.root.bind('<F1>', lambda event: self.toggle_image_grid(event))
            self.root.bind('<F4>', lambda event: self.open_image_in_editor(event))
        else:
            for binding in bindings:
                self.root.unbind(binding)


    def create_ui_tab(self, ui_component, ui_tab, extra_args=None, show=False, refresh=False):
        app = self
        root = self.root
        if ui_component.app is None:
            if extra_args is not None:
                ui_component.setup_window(app, root, *extra_args)
            else:
                ui_component.setup_window(app, root)
        if show:
            self.main_notebook.select(ui_tab)
            if hasattr(ui_component, 'working_dir') and ui_component.working_dir != self.image_dir.get():
                ui_component.set_working_directory(self.image_dir.get())
                return
            if refresh:
                ui_component.refresh_tab()


    def create_batch_tag_edit_ui(self, show=False):
        self.create_ui_tab(self.batch_tag_edit, self.batch_tag_edit_tab, show=show)


    def create_crop_ui(self, show=False, refresh=False):
        self.create_ui_tab(self.crop_ui, self.crop_ui_tab, show=show, refresh=refresh)


    def create_batch_upscale_ui(self, show=False, quick_swap=False):
        self.create_ui_tab(self.batch_upscale, self.batch_upscale_tab, show=show)
        if quick_swap:
            self.batch_upscale.set_working_directory(self.image_dir.get(), batch=False)


    def create_batch_resize_images_ui(self, show=False):
        self.create_ui_tab(self.batch_resize_images, self.batch_resize_images_tab, extra_args=(self.image_dir.get(),), show=show)


    def create_batch_rename_ui(self, show=False):
        self.create_ui_tab(self.batch_rename, self.batch_rename_tab, show=show)


    def create_batch_img_edit_ui(self, show=False):
        self.create_ui_tab(self.batch_img_edit, self.batch_img_edit_tab, show=show)


    def create_find_dupe_file_ui(self, show=False):
        self.create_ui_tab(self.find_dupe_file, self.find_dupe_file_tab, show=show)


# --------------------------------------
# ImgTxtViewer states
# --------------------------------------
    def toggle_image_grid(self, event=None):
        if event is not None:
            self.is_image_grid_visible_var.set(not self.is_image_grid_visible_var.get())
        if not self.is_image_grid_visible_var.get():
            self.refresh_image()
            self.image_grid.grid_remove()
            self.master_image_inner_frame.grid()
        else:
            if self.master_image_inner_frame.winfo_viewable():
                self.master_image_inner_frame.grid_remove()
                self.image_grid.initialize()
                self.image_grid.grid()
                self.root.after(250, self.image_grid.reload_grid)


#endregion
#region TextBox Highlights


    def highlight_duplicates(self, event=None, mouse=True):
        if not self.highlight_selection_var.get():
            return
        self.text_box.after_idle(self._highlight_duplicates, mouse)


    def _highlight_duplicates(self, mouse=False):
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


    def remove_highlight(self, event=None):
        self.text_box.tag_remove("highlight", "1.0", "end")
        self.root.after(100, lambda: self.remove_custom_tags())


    def remove_custom_tags(self):
        self.highlight_all_duplicates_var.set(False)
        for tag in self.text_box.tag_names():
            if tag not in ["sel", "highlight"]:
                self.text_box.tag_remove(tag, "1.0", "end")


    def remove_tag(self):
        self.highlight_all_duplicates_var.set(False)
        for tag in self.text_box.tag_names():
            self.text_box.tag_remove(tag, "1.0", "end")


#endregion
#region Primary Functions


    def load_pairs(self, silent=False):
        self.root.title(self.title)
        self.info_text.pack_forget()
        current_image_path = self.image_files[self.current_index] if self.image_files else None
        self.refresh_file_lists()
        self.update_video_thumbnails()
        self.enable_menu_options()
        self.create_text_box()
        self.restore_previous_index(current_image_path)
        if not silent:
            self.update_pair(save=False)
        else:
            self.update_pair(save=False, silent=True)
        self.configure_pane_position()
        self.stat_calculator.calculate_file_stats()
        self.directory_entry_tooltip.config(text=f"Directory: {self.image_dir.get()}")


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
        if not self.text_controller.filter_is_active:
            self.original_image_files = list(self.image_files)
            self.original_text_files = list(self.text_files)
        self.update_total_image_label()
        self.prev_num_files = len(files_in_dir)


    def update_video_thumbnails(self):
        if not self.is_ffmpeg_installed:
            return
        self.video_thumb_dict = vtg.generate_video_thumbnails(file_paths=self.image_files)


    def update_total_image_label(self):
        if hasattr(self, 'total_images_label'):
            if not self.text_controller.filter_is_active:
                self.total_images_label.config(text=f"of {len(self.image_files)}")
            else:
                self.total_images_label.config(text=f"of {len(self.text_controller.filtered_image_files)}")


    def validate_files(self, files_in_dir):
        odd_files_exist = any(self.check_odd_files(filename) for filename in files_in_dir)
        if odd_files_exist and messagebox.askyesno("Confirmation", ".jfif, or .jpg_large files detected.\n\nIt's recommended to convert these files to .jpg for compatibility.\n\nDo you want to proceed?"):
            for filename in files_in_dir:
                if self.check_odd_files(filename):
                    self.rename_odd_files(filename)
        for filename in files_in_dir:
            extensions = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"]
            if self.is_ffmpeg_installed:
                extensions.append(".mp4")
            if str(filename).lower().endswith(tuple(extensions)):
                image_file_path = os.path.join(self.image_dir.get(), filename)
                self.image_files.append(image_file_path)
                text_filename = os.path.splitext(filename)[0] + ".txt"
                text_file_path = os.path.join(self.text_dir, text_filename)
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


    def display_image(self):
        try:
            if self.animation_job_id is not None:
                self.root.after_cancel(self.animation_job_id)
                self.animation_job_id = None
            self.image_file = self.image_files[self.current_index]
            text_file = self.text_files[self.current_index] if self.current_index < len(self.text_files) else None
            file_extension = os.path.splitext(self.image_file)[1].lower()
            # 1. Regular images
            if file_extension not in ('.gif', '.mp4'):
                self.video_player.grid_remove()
                self.primary_display_image.grid(row=1, column=0, sticky="nsew")
                self.primary_display_image.load_image(self.image_file)
                if self.edit_panel_visible_var.get():
                    self.edit_panel.toggle_edit_panel_widgets("normal")
                image = self.primary_display_image.get_image(original=False)
                self.update_imageinfo()
                return text_file, image, None, None
            # 2. MP4 and GIF images
            elif self.is_ffmpeg_installed and file_extension in ('.mp4', '.gif'):
                self.primary_display_image.grid_remove()
                self.display_mp4_video()
                if self.edit_panel_visible_var.get():
                    self.edit_panel.toggle_edit_panel_widgets("disabled")
                self.update_videoinfo()
                return text_file, None, None, None
        except ValueError:
            self.check_image_dir()


    def display_mp4_video(self):
        if self.is_image_grid_visible_var.get():
            return
        self.primary_display_image.grid_remove()
        self.video_player.destroy_player()
        play_image = os.path.join(self.app_root_path, "main", "play.png")
        pause_image = os.path.join(self.app_root_path, "main", "pause.png")
        loading_image = os.path.join(self.app_root_path, "main", "loading.png")
        self.video_player = VideoPlayerWidget(master=self.master_image_inner_frame, app=self, play_image=play_image, pause_image=pause_image, loading_image=loading_image)
        self.video_player.grid(row=1, column=0, sticky="nsew")
        # Keep video info updated when player/widget is resized
        try:
            self.video_player.bind("<Configure>", lambda e: self.update_videoinfo())
        except Exception:
            pass
        # Schedule an initial update after geometry settle
        self.root.after(100, lambda: self.update_videoinfo())
        try:
            self.video_player.load_video(file_path=self.image_file)
        except Exception as e:
            messagebox.showerror("Error: app.display_mp4_video()", f"Failed to load video:\n{str(e)}")


    def show_pair(self):
        if self.image_files:
            text_file, image, max_img_width, max_img_height = self.display_image()
            self.load_text_file(text_file)
            if not self.is_image_grid_visible_var.get() and image is not None:
                self.primary_display_image.config(width=max_img_width, height=max_img_height)
                self.original_image = image
                self.current_image = self.original_image.copy()
                self.current_max_img_height = max_img_height
                self.current_max_img_width = max_img_width
            self.autocomplete.clear_suggestions()
            self.toggle_list_mode()
            self.highlight_custom_string()
            self.append_comma_to_text()
            self.highlight_all_duplicates_var.set(False)
            self.debounce_update_thumbnail_panel()
            self.get_text_summary()
            if self.is_image_grid_visible_var.get():
                self.image_grid.highlight_thumbnail(self.current_index)
            self.find_replace_widget.perform_search()
            self.update_mytags_tab()


    def refresh_image(self):
        if self.image_files:
            self.display_image()
            self.debounce_update_thumbnail_panel()


    def debounce_refresh_image(self, event=None):
        if not self.image_files:
            return
        if self.image_file.lower().endswith((".mp4")):
            return
        if self.ui_state != "ImgTxtViewer":
            return
        if hasattr(self, 'text_box'):
            if self.is_resizing_job_id:
                self.root.after_cancel(self.is_resizing_job_id)
            if not self.is_image_grid_visible_var.get():
                self.is_resizing_job_id = self.root.after(250, self.refresh_image)


    def on_imagezoomwidget_render(self):
        current_percent = int(self.primary_display_image.image_mgr.scale * 100)
        self.update_imageinfo(current_percent)


    def update_videoinfo(self, image_file=None):
        if not self.is_ffmpeg_installed or not self.image_files:
            return
        image_file = image_file if image_file else self.image_file
        if image_file.lower().endswith((".mp4", ".gif")):
            video_data = self.video_thumb_dict.get(image_file)
            original_width = original_height = None
            framerate = None
            if video_data:
                original_width, original_height = video_data.get('resolution', (None, None))
                framerate = video_data.get('framerate')
            if image_file.lower().endswith('.gif') and (not original_width or not original_height):
                try:
                    with Image.open(image_file) as im:
                        original_width, original_height = im.size
                        duration = im.info.get('duration')
                        if duration and not framerate:
                            framerate = 1000.0 / duration if duration > 0 else None
                except Exception:
                    original_width = original_height = None
            if original_width and original_height:
                file_size = os.path.getsize(image_file)
                size_kb = file_size / 1024
                size_str = f"{round(size_kb)} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 2)} MB"
                filename = os.path.basename(image_file)
                _filename = (filename[:40] + '(...)') if len(filename) > 45 else filename
                framerate_str = f"{framerate:.2f} fps" if framerate else "Unknown fps"
                try:
                    if hasattr(self, "video_player") and self.video_player.winfo_ismapped():
                        disp_w = self.video_player.winfo_width()
                        disp_h = self.video_player.winfo_height()
                    elif hasattr(self, "primary_display_image") and self.primary_display_image.winfo_ismapped():
                        disp_w = self.primary_display_image.winfo_width()
                        disp_h = self.primary_display_image.winfo_height()
                    else:
                        disp_w = getattr(self, "video_player", None).winfo_width() if hasattr(self, "video_player") else 0
                        disp_h = getattr(self, "video_player", None).winfo_height() if hasattr(self, "video_player") else 0
                except Exception:
                    disp_w = disp_h = 0
                if disp_w <= 1:
                    disp_w = self.master_image_inner_frame.winfo_width() if hasattr(self, "master_image_inner_frame") else 0
                if disp_h <= 1:
                    disp_h = self.master_image_inner_frame.winfo_height() if hasattr(self, "master_image_inner_frame") else 0
                try:
                    if original_width and original_height and disp_w and disp_h:
                        scale = min(float(disp_w) / original_width, float(disp_h) / original_height)
                    elif original_width and disp_w:
                        scale = float(disp_w) / original_width
                    else:
                        scale = 1.0
                except Exception:
                    scale = 1.0
                percent_scale = max(1, int(scale * 100))
                self.label_image_stats.config(text=f"  |  {_filename}  |  {original_width} x {original_height}  |  {percent_scale}%  |  {size_str}  |  {framerate_str}", anchor="w")
                self.label_image_stats_tooltip.config(text=f"Filename: {filename}\nResolution: {original_width} x {original_height}\nScale: {percent_scale}%\nFramerate: {framerate_str}\nSize: {size_str}")
                return {"filename": filename, "resolution": f"{original_width} x {original_height}", "framerate": framerate_str, "size": size_str, "scale": f"{percent_scale}%"}
            else:
                return self.on_imagezoomwidget_render()


    def update_imageinfo(self, percent_scale=100):
        if self.image_files:
            self.image_file = self.image_files[self.current_index]
            if self.image_file not in self.image_info_cache:
                self.image_info_cache[self.image_file] = self.get_image_info(self.image_file)
            image_info = self.image_info_cache[self.image_file]
            self.label_image_stats.config(text=f"  |  {image_info['filename']}  |  {image_info['resolution']}  |  {percent_scale}%  |  {image_info['size']}  |  {image_info['color_mode']}", anchor="w")
            self.label_image_stats_tooltip.config(text=f"Filename: {image_info['filename']}\nResolution: {image_info['resolution']}\nSize: {image_info['size']}\nColor Mode: {image_info['color_mode']}")


    def get_image_info(self, image_file):
        try:
            with Image.open(image_file) as image:
                width, height = image.size
                color_mode = image.mode
        except (FileNotFoundError, UnidentifiedImageError):
            return {"filename": "Image not found", "resolution": "0 x 0", "size": "0 KB", "color_mode": "N/A"}
        size = os.path.getsize(image_file)
        size_kb = size / 1024
        size_str = f"{round(size_kb)} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 2)} MB"
        filename = os.path.basename(image_file)
        filename = (filename[:40] + '(...)') if len(filename) > 45 else filename
        return {"filename": filename, "resolution": f"{width} x {height}", "size": size_str, "color_mode": color_mode}


#endregion
#region Navigation


    def update_pair(self, direction=None, save=True, step=1, silent=False):
        if self.image_dir.get() == self.dir_placeholder_text or len(self.image_files) == 0:
            return
        self.check_image_dir()
        if not self.text_modified_var:
            self.root.title(self.title)
        self.text_box.config(undo=False)
        self.text_box.edit_reset()
        if self.auto_save_var.get() and save:
            self.save_text_file()
        if len(self.image_files) > 0:
            if direction == 'next':
                self.current_index = (self.current_index + step) % len(self.image_files)
            elif direction == 'prev':
                self.current_index = (self.current_index - step) % len(self.image_files)
            if not silent:
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


    def check_image_dir(self, event=None):
        self.check_working_directory()
        try:
            num_files_in_dir = len(os.listdir(self.image_dir.get()))
        except Exception:
            return
        if num_files_in_dir != self.prev_num_files:
            self.update_image_file_count()
            self.prev_num_files = num_files_in_dir


    def update_image_file_count(self):
        extensions = ['.jpg', '.jpeg', '.jpg_large', '.jfif', '.png', '.webp', '.bmp', '.gif']
        if self.is_ffmpeg_installed:
            extensions.append('.mp4')
            self.update_video_thumbnails()
        self.image_files = [file for ext in extensions for file in glob.glob(f"{self.image_dir.get()}/*{ext}")]
        self.image_files.sort(key=self.get_file_sort_key(), reverse=self.reverse_load_order_var.get())
        self.text_files = [os.path.splitext(file)[0] + '.txt' for file in self.image_files]
        self.update_total_image_label()


    def mousewheel_nav(self, event):
        current_time = time.time()
        scroll_debounce_time = 0.05
        if current_time - self.last_scroll_time < scroll_debounce_time:
            return
        self.last_scroll_time = current_time
        step = 1
        if event.delta > 0:
            self.update_pair('next', step=step)
        else:
            self.update_pair('prev', step=step)


    def get_image_index_by_filename(self, filename):
        search_name = os.path.basename(filename) if os.path.sep in filename else filename
        for i, img_path in enumerate(self.image_files):
            if os.path.basename(img_path) == search_name:
                return i
        if os.path.sep in filename and search_name != filename:
            for i, img_path in enumerate(self.image_files):
                if os.path.basename(img_path) == search_name:
                    return i
        return -1


#endregion
#region Text Options


    def refresh_text_box(self):
        self.check_working_directory()
        if not self.check_dir_for_img(self.image_dir.get()):
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
                self.root.title(self.title)
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


    def append_comma_to_text(self):
        text = self.text_box.get("1.0", "end-1c")
        if self.auto_insert_comma_var.get():
            if text and not text.endswith(", ") and not self.list_mode_var.get():
                self.text_box.insert("end", ", ")
        else:
            if text.endswith(", "):
                self.text_box.delete("end-3c", "end-1c")


#endregion
#region Text Tools


    def delete_tag_under_mouse(self, event):
        if not self.cleaning_text_var.get():
            return
        text_box = self.text_box
        cursor_index = text_box.index(f"@{event.x},{event.y}")
        column_index = int(cursor_index.split('.')[1])
        line_start = text_box.index(f"{cursor_index} linestart")
        line_end = text_box.index(f"{cursor_index} lineend")
        line_text = text_box.get(line_start, line_end)
        tag_chunk_pattern = re.compile(r'[^,]+')
        match_span = None
        for match in tag_chunk_pattern.finditer(line_text):
            start, end = match.span()
            if start <= column_index <= end:
                match_span = (start, end)
                break
        if match_span is None:
            return
        start_offset, end_offset = match_span
        highlight_start = f"{line_start}+{start_offset}c"
        highlight_end = f"{line_start}+{end_offset}c"
        text_box.tag_config("highlight", background="#ff5d5d")
        text_box.tag_add("highlight", highlight_start, highlight_end)
        text_box.update_idletasks()

        def delete_tag(event_release=None):
            text_box.delete(highlight_start, highlight_end)
            raw_text = text_box.get("1.0", "end-1c")
            cleaned_text = self.cleanup_text(raw_text)
            normalized_text = '\n'.join(line for line in cleaned_text.split('\n') if line.strip())
            if normalized_text != raw_text:
                text_box.delete("1.0", "end")
                text_box.insert("1.0", normalized_text)
            text_box.tag_config("highlight", background="#5da9be")
            self.delete_tag_job_id = None
            self.sync_title_with_content()
            text_box.tag_remove("highlight", "1.0", "end")

        def on_release(event_release):
            text_box.unbind("<ButtonRelease-2>")
            delete_tag(event_release)

        text_box.bind("<ButtonRelease-2>", on_release)


    def delete_word_before_cursor(self, event=None):
        current_pos = self.text_box.index("insert")
        line, col = map(int, current_pos.split("."))
        if col == 0:
            if line > 1:
                self.text_box.delete(f"{line-1}.end", current_pos)
                return "break"
            return None
        line_text = self.text_box.get(f"{line}.0", current_pos)
        i = col - 1
        while i >= 0 and line_text[i].isspace():
            i -= 1
        while i >= 0 and not line_text[i].isspace():
            i -= 1
        word_start = f"{line}.{i + 1}"
        self.text_box.delete(word_start, current_pos)
        return "break"


    def collate_captions(self):
        if not self.check_if_directory():
            return
        initial_filename = os.path.basename(os.path.normpath(self.image_dir.get())) + "_wildcard" + ".txt"
        output_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Save Combined Captions As", initialfile=initial_filename, initialdir=self.image_dir.get())
        if not output_file:
            return
        try:
            with open(output_file, "w", encoding="utf-8") as outfile:
                for text_file in self.text_files:
                    if os.path.isfile(text_file):
                        with open(text_file, "r", encoding="utf-8") as infile:
                            content = infile.read().strip()
                            if content:
                                outfile.write(content + "\n")
        except Exception as e:
            messagebox.showerror("Error: app.collate_captions()", f"An error occurred while collating captions:\n\n{e}")
            return
        if messagebox.askyesno("Success", f"All captions have been combined into:\n\n{output_file}.\n\nDo you want to open the output directory?"):
            os.startfile(os.path.dirname(output_file))


    def delete_all_text_or_files(self, delete_file=False):
        if not self.check_if_directory():
            return
        if delete_file:
            confirm = messagebox.askyesno("Delete All Text Files", "This will permanently delete ALL text files in the current directory.\n\nAre you sure you want to continue?")
            if not confirm:
                return
            deleted_count = 0
            for text_file in self.text_files:
                try:
                    if os.path.exists(text_file):
                        os.remove(text_file)
                        deleted_count += 1
                except Exception as e:
                    messagebox.showerror("Error: app.delete_all_text_or_files()", f"Failed to delete {text_file}:\n{e}")
            messagebox.showinfo("Done", f"Deleted {deleted_count} text files.")
        else:
            confirm = messagebox.askyesno("Clear All Text Files", "This will erase the contents of ALL text files in the current directory.\n\nAre you sure you want to continue?")
            if not confirm:
                return
            cleared_count = 0
            for text_file in self.text_files:
                try:
                    if os.path.exists(text_file):
                        with open(text_file, "w", encoding="utf-8") as f:
                            f.write("")
                        cleared_count += 1
                except Exception as e:
                    messagebox.showerror("Error: app.delete_all_text_or_files()", f"Failed to clear {text_file}:\n{e}")
            messagebox.showinfo("Done", f"Cleared {cleared_count} text files.")
        self.refresh_file_lists()
        self.show_pair()


    def batch_trim_tags(self, max_tags=None):
        if not self.check_if_directory():
            return
        if max_tags is None:
            max_tags = custom_simpledialog.askinteger("Trim Tags", "Keep how many tags per file?", initialvalue=0, minvalue=0, parent=self.root)
            if max_tags is None:
                return
        if max_tags < 0:
            messagebox.showerror("Invalid Input", "Please enter a non-negative integer.")
            return
        if not messagebox.askyesno("Confirm Trim", f"This will trim all text files so each contains at most {max_tags} tags.\n\nProceed?"):
            return
        updated = 0
        total_tags = 0
        total_removed = 0
        total_remaining = 0
        for text_file in list(self.text_files):
            try:
                if not os.path.isfile(text_file):
                    continue
                with open(text_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if not content:
                    continue
                if self.list_mode_var.get():
                    tags = [t.strip() for t in content.splitlines() if t.strip()]
                else:
                    tags = [t.strip() for t in re.split(r'[,\n]+', content) if t.strip()]
                num_tags = len(tags)
                total_tags += num_tags
                if num_tags <= max_tags:
                    total_remaining += num_tags
                    continue
                new_tags = tags[:max_tags]
                new_content = '\n'.join(new_tags) if self.list_mode_var.get() else ', '.join(new_tags)
                with open(text_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                updated += 1
                removed = num_tags - len(new_tags)
                total_removed += removed
                total_remaining += len(new_tags)
            except Exception as e:
                messagebox.showerror("Error: app.batch_trim_tags()", f"Failed to trim {text_file}:\n{e}")
        self.refresh_file_lists()
        self.show_pair()
        msg = (f"Trimmed {updated} file(s) to {max_tags} tag(s) each.\n\n"
                f"Total tags before trimming: {total_tags}\n"
                f"Total tags removed: {total_removed}\n"
                f"Total tags remaining: {total_remaining}")
        messagebox.showinfo("Done", msg)


    def check_file_pair_collisions(self, directory=None, file_path=None, show_dialog="all"):
        if isinstance(show_dialog, bool):
            show_dialog_mode = "all" if show_dialog else "none"
        elif isinstance(show_dialog, str):
            show_dialog_mode = show_dialog.lower()
            if show_dialog_mode not in ("all", "collision", "none"):
                show_dialog_mode = "all"
        else:
            show_dialog_mode = "all"
        show_any_dialog = show_dialog_mode != "none"
        if file_path:
            if not os.path.isfile(file_path):
                if show_any_dialog:
                    messagebox.showwarning("File Not Found", f"The specified file was not found:\n\n{file_path}")
                return []
            directory = os.path.dirname(os.path.abspath(file_path))
            target_base = os.path.splitext(os.path.basename(file_path))[0]
        else:
            target_base = None
            directory = directory or self.image_dir.get()
        if not os.path.isdir(directory):
            return []
        extensions = ['.jpg', '.jpeg', '.jpg_large', '.jfif', '.png', '.webp', '.bmp', '.gif', '.mp4']
        try:
            all_files = os.listdir(directory)
        except Exception:
            return []
        groups = {}
        for fname in all_files:
            _, ext = os.path.splitext(fname)
            ext = ext.lower()
            if ext in extensions:
                base = os.path.splitext(fname)[0]
                groups.setdefault(base, []).append(fname)
        collisions = []
        items_to_check = {target_base: groups.get(target_base, [])} if target_base is not None else groups
        for base, fnames in items_to_check.items():
            exts = {os.path.splitext(f)[1].lower() for f in fnames}
            if len(fnames) > 1 and len(exts) > 1:
                collisions.append({
                    "basename": base,
                    "files": [os.path.join(directory, f) for f in fnames],
                    "extensions": sorted(exts)
                })
        if show_any_dialog:
            if collisions:
                lines = []
                for c in collisions:
                    lines.append(f"{c['basename']} -> {', '.join(c['extensions'])}")
                    for p in c['files']:
                        lines.append(f"  - {os.path.basename(p)}")
                    lines.append("")
                title = "File Pair Collisions Detected"
                if target_base:
                    title = f"Collisions for: {target_base}"
                message = (
                    "Some files in the selected directory share the same basename but have different file extensions.\n\n"
                    "Because the text pair uses the basename + .txt, only one text file can be associated with that basename.\n"
                    "This will cause text collisions. To avoid this, rename each file so every image/video has a unique basename.\n\n"
                    "The following basenames have multiple filetype associations:\n\n"
                    + "\n".join(lines))
                messagebox.showwarning(title, message)
            else:
                if show_dialog_mode == "all":
                    if target_base:
                        messagebox.showinfo("File Pair Collisions", f"No file pair collisions detected for: {target_base}")
                    else:
                        messagebox.showinfo("File Pair Collisions", "No file pair collisions detected.")
        return collisions


#endregion
#region Image Tools


    def expand_image(self):
        if not self.check_if_directory():
            return
        self.check_working_directory()
        ext_map = {".jpg": "JPEG", ".jpeg": "JPEG", ".jfif": "JPEG", ".jpg_large": "JPEG", ".png": "PNG", ".bmp": "BMP", ".webp": "WEBP" }
        src_path = self.image_files[self.current_index]
        src_basename = os.path.basename(src_path)
        base_filename, file_extension = os.path.splitext(src_basename)
        if file_extension.lower() not in ext_map:
            messagebox.showwarning("Unsupported Filetype", f"Expanding {file_extension.upper()} is not supported.")
            return
        new_basename = f"{base_filename}_ex{file_extension}"
        new_filepath = os.path.join(os.path.dirname(src_path), new_basename)
        if os.path.exists(new_filepath):
            messagebox.showwarning("File Exists", f'Output file:\n\n{os.path.normpath(new_basename)}\n\nAlready exists.')
            return
        confirmation = ("Are you sure you want to expand the current image?\n\n"
                        "This tool works by expanding the shorter side to a square resolution divisible by 8 and stretching the pixels around the long side to fill the space.\n\n"
                        "A new image will be saved in the same format and with '_ex' appended to the filename.")
        if not messagebox.askyesno("Expand Image", confirmation):
            return
        try:
            with Image.open(src_path) as img:
                width, height = img.size
                if width == height:
                    messagebox.showwarning("Warning", "The image is already a square aspect ratio.")
                    return
                side = max(width, height)
                if side % 8 != 0:
                    side += (8 - (side % 8))
                left = (side - width) // 2
                right = side - width - left
                top = (side - height) // 2
                bottom = side - height - top
                preserve_mode = img.mode
                if preserve_mode not in ("RGB", "RGBA", "L"):
                    working_img = img.convert("RGB")
                    preserve_mode = "RGB"
                else:
                    working_img = img.copy()
                np_img = numpy.array(working_img)
                if np_img.ndim == 2:
                    pad_spec = ((top, bottom), (left, right))
                else:
                    pad_spec = ((top, bottom), (left, right), (0, 0))
                padded = numpy.pad(np_img, pad_spec, mode="edge")
                filled_img = Image.fromarray(padded)
                save_format = ext_map.get(file_extension.lower(), img.format)
                save_kwargs = {}
                if save_format == "JPEG":
                    save_kwargs["quality"] = 95
                    save_kwargs["subsampling"] = 0
                filled_img.save(new_filepath, format=save_format, **save_kwargs)
            text_candidates = [os.path.join(os.path.dirname(src_path), f"{base_filename}.txt")]
            if getattr(self, "text_dir", ""):
                text_candidates.append(os.path.join(self.text_dir, f"{base_filename}.txt"))
            for txt in text_candidates:
                if os.path.exists(txt):
                    shutil.copy2(txt, os.path.join(os.path.dirname(new_filepath), f"{base_filename}_ex.txt"))
                    break
            self.check_image_dir()
            index_value = self.get_image_index_by_filename(new_basename)
            if index_value != -1:
                self.jump_to_image(index_value)
            self.thumbnail_panel.refresh_thumbnails()
        except Exception as e:
            messagebox.showerror("Error: app.expand_image()", f'Failed to process {src_basename}. Reason: {e}')


    def flip_current_image(self):
        if self.image_file.lower().endswith('.mp4'):
            messagebox.showwarning("Unsupported Filetype", "Flipping MP4's is not supported.")
            return
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
        self.thumbnail_panel.refresh_thumbnails()


    def rotate_current_image(self):
        if self.image_file.lower().endswith('.mp4'):
            messagebox.showwarning("Unsupported Filetype", "Rotating MP4's is not supported.")
            return
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
        self.thumbnail_panel.refresh_thumbnails()


    def resize_image(self):
        if self.image_file.lower().endswith('.mp4'):
            messagebox.showwarning("Unsupported Filetype", "Resizing MP4's is not supported.")
            return
        main_window_width = self.root.winfo_width()
        main_window_height = self.root.winfo_height()
        window_x = self.root.winfo_x() + -200 + main_window_width // 2
        window_y = self.root.winfo_y() - 200 + main_window_height // 2
        filepath = self.image_files[self.current_index]
        resize_image.ResizeTool(self.root, self, filepath, window_x, window_y, self.update_pair, self.jump_to_image)


    def batch_crop_images(self):
        main_window_width = self.root.winfo_width()
        main_window_height = self.root.winfo_height()
        window_x = self.root.winfo_x() + -155 + main_window_width // 2
        window_y = self.root.winfo_y() - 100 + main_window_height // 2
        filepath = str(self.image_dir.get())
        total_images = len(self.image_files)
        batch_crop_images.BatchCrop(self.root, filepath, total_images, window_x, window_y)


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


    def open_image_in_editor(self, event=None, index=None):
        if self.image_file.lower().endswith('.mp4'):
            messagebox.showwarning("Unsupported Filetype", "MP4 not supported.\n\nSelect an image and try again.")
            return
        try:
            if self.image_files:
                app_path = self.external_image_editor_path
                if app_path != "mspaint":
                    if not os.path.isfile(app_path):
                        raise FileNotFoundError(f"The specified image editor was not found:\n\n{app_path}")
                image_index = index if index is not None else self.current_index
                image_path = self.image_files[image_index]
                subprocess.Popen([app_path, image_path])
        except FileNotFoundError as e:
            messagebox.showerror("Error: app.open_image_in_editor()", str(e))
            self.set_external_image_editor_path()
        except PermissionError as e:
            messagebox.showerror("Error: app.open_image_in_editor()", f"Permission denied: {e}")
        except Exception as e:
            messagebox.showerror("Error: app.open_image_in_editor()", f"An error occurred while opening the image in the editor:\n\n{e}")


    def set_external_image_editor_path(self):
        response = messagebox.askyesnocancel("Set External Image Editor", f"Current external image editor is set to:\n\n{self.external_image_editor_path}\n\nDo you want to change it? (Yes/No)\n\nPress (Cancel) to reset to default (MS Paint).")
        if response is None:  # Cancel, reset
            self.external_image_editor_path = "mspaint"
            messagebox.showinfo("Reset", "External image editor path has been reset to mspaint.")
        elif response:  # Yes, set path
            app_path = filedialog.askopenfilename(title="Select Default Image Editor", filetypes=[("Executable or Python Script", "*.exe;*.py;*.pyw")])
            if app_path:
                if os.path.isfile(app_path):
                    self.external_image_editor_path = app_path
                    messagebox.showinfo("Success", f"External image editor set to:\n\n{app_path}")
                else:
                    messagebox.showerror("Error: app.set_external_image_editor_path()", f"The selected path is not a valid file:\n\n{app_path}")
                    self.set_external_image_editor_path()
        else:  # No
            return


#endregion
#region Misc Functions


    def sync_title_with_content(self, event=None):
        if event and self.ignore_key_event(event):
            return
        else:
            if self.current_index < len(self.text_files):
                text_file = self.text_files[self.current_index]
                try:
                    with open(text_file, "r", encoding="utf-8") as file:
                        file_content = file.read()
                except FileNotFoundError:
                    file_content = ""
                if self.text_box.get("1.0", "end-1c") == file_content:
                    self.root.title(self.title)
                else:
                    self.root.title(self.title + " ⚪")


    def disable_button(self, event):
        return "break"


    def ignore_key_event(self, event):
        if event.keysym in ("Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"):
            return True
        if event.state & 0x4 and event.keysym == 's':  # CTRL+S
            return True
        return False


    def set_always_on_top(self):
        if self.always_on_top_var.get():
            self.root.attributes('-topmost', True)
        else:
            self.root.attributes('-topmost', False)


    def toggle_list_menu(self):
        if self.cleaning_text_var.get():
            self.text_options_menu.entryconfig("List View", state="normal")
        else:
            self.text_options_menu.entryconfig("List View", state="disabled")
            if self.list_mode_var.get():
                self.toggle_list_mode(skip=True)
            if not self.root.title().endswith(" ⚪"):
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
#region About Window


    def open_about_window(self):
        self.about_window.open_window(text=HelpText.IMG_TXT_VIEWER_ABOUT, footer=self._create_about_footer, title="About - img-txt Viewer", geometry="850x650", icon=self.blank_image)


    def _create_about_footer(self, parent):
        def open_game():
            game = PyTrominos.PyTrominosGame(self.root, icon_path=self.icon_path)
            game.run()
        github_url = "https://github.com/Nenotriple/img-txt_viewer"
        footer = Frame(parent)
        footer.pack(fill="x")
        url_button = ttk.Button(footer, text=f"{github_url}", command=lambda: webbrowser.open(f"{github_url}"))
        url_button.pack(side="left", fill="x", padx=10, ipadx=10)
        Tip.create(widget=url_button, text="Click this button to open the repo in your default browser", show_delay=10)
        game_button = ttk.Button(footer, text=f"Play PyTrominos!", command=open_game)
        game_button.pack(side="left", fill="x", padx=10, ipadx=10)
        Tip.create(widget=game_button, text="Click this button to play PyTrominos", show_delay=10)
        made_by_label = Label(footer, text=f"{self.app_version} - img-txt_viewer - Created by: Nenotriple (2023-2025)", font=("Segoe UI", 10))
        made_by_label.pack(side="right", padx=10, pady=10)
        Tip.create(widget=made_by_label, text="🤍Thank you for using my app!🤍 (^‿^)", show_delay=10)
        return footer


#endregion
#region Text Cleanup


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
            if show_confirmation:
                messagebox.showinfo("Success", "All text files have been cleaned!")
        except Exception as e:
            messagebox.showerror("Error: app.cleanup_all_text_files()", f"An unexpected error occurred: {str(e)}")
        self.show_pair()


    def cleanup_text(self, text, bypass=False):
        if self.cleaning_text_var.get() or bypass:
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


    def remove_duplicate_CSV_captions(self, text: "str"):
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
#region Save and close


    def save_text_file(self, highlight=False):
        try:
            if self.image_dir.get() != self.dir_placeholder_text and self.check_if_directory() and self.text_files:
                collision = self.check_file_pair_collisions(file_path=self.image_files[self.current_index], show_dialog="collision")
                if collision:
                    messagebox.showwarning("Save Collision", "The text file will be saved, but be aware that multiple files share the same basename. This will cause text pair collisions.\n\nTo avoid this, rename each file so every image/video has a unique basename.")
                file_saved = self._save_file()
                if self.cleaning_text_var.get() or self.list_mode_var.get():
                    self.refresh_text_box()
                if file_saved:
                    self.root.title(self.title)
                    self.update_mytags_tab()
                    if highlight:
                        self.save_button.configure(style="Blue+.TButton")
                        self.root.after(120, lambda: self.save_button.configure(style="Blue.TButton"))
                else:
                    self.root.title(self.title)
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: app.save_text_file()", f"An error occurred while saving the current text file.\n\n{e}")


    def _save_file(self):
        if not self.text_files or self.current_index >= len(self.text_files):
            return False
        text_file = self.text_files[self.current_index]
        if not text_file:
            return False
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
        try:
            with open(text_file, "w+", encoding="utf-8") as file:
                file.write(text)
        except (IOError, PermissionError):
            return False
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
        if not self.root.title().endswith(" ⚪"):
            self.root.destroy()
        elif self.auto_save_var.get():
            self.cleanup_all_text_files(show_confirmation=False)
            self.save_text_file()
            self.root.destroy()
        else:
            try:
                if messagebox.askyesno("Quit", "Quit without saving?"):
                    self.root.destroy()
            except Exception: pass


#endregion
#region File Management


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


    def check_dir_for_img(self, directory):
        extensions = ['.jpg', '.jpeg', '.jpg_large', '.jfif', '.png', '.webp', '.bmp', '.gif']
        if self.is_ffmpeg_installed:
            extensions.append('.mp4')
            self.update_video_thumbnails()
        if any(str(fname).lower().endswith(tuple(extensions)) for fname in os.listdir(directory)):
            self.filepath_contains_images_var = True
            return True
        else:
            messagebox.showwarning("No Images", "The selected directory does not contain any images.")
            self.filepath_contains_images_var = False
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
            initialdir = self.get_initial_directory()
            directory = filedialog.askdirectory(initialdir=initialdir)
            if directory and directory != self.image_dir.get():
                if hasattr(self, 'text_box'):
                    self.text_controller.revert_text_image_filter(clear=True, silent=True)
                if self.check_dir_for_img(directory):
                    self.delete_text_backup()
                    self.image_dir.set(os.path.normpath(directory))
                    self.current_index = 0
                    self.load_pairs()
                    self.set_text_file_path(directory)
                    self.toggle_main_notebook_state("normal")
            if original_auto_save_var is not None:
                self.auto_save_var.set(original_auto_save_var)
        except Exception as e:
            messagebox.showwarning("Error", f"There was an unexpected issue setting the folder path:\n\n{e}")


    def get_initial_directory(self):
        initialdir = self.image_dir.get()
        if not initialdir or initialdir == self.dir_placeholder_text:
            initialdir = self.settings_manager.config.get("Path", "last_img_directory", fallback=None)
            if not initialdir or not os.path.exists(initialdir):
                initialdir = os.path.dirname(__file__)
        if 'temp' in initialdir.lower():
            initialdir = os.path.expanduser("~")
        return initialdir


    def set_working_directory(self, event=None, path=None, silent=False):
        try:
            directory = path if path is not None else self.directory_entry.get()
            if not self.check_dir_for_img(directory):
                return
            if self.auto_save_var.get():
                self.save_text_file()
            if hasattr(self, 'text_box'):
                self.text_controller.revert_text_image_filter(clear=True, silent=True)
            self.image_dir.set(os.path.normpath(directory))
            self.current_index = 0
            if not silent:
                self.load_pairs()
                self.set_text_file_path(directory)
            else:
                self.load_pairs(silent=True)
                self.set_text_file_path(directory, silent=True)
            self.jump_to_image(0)
            self.toggle_main_notebook_state("normal")
        except FileNotFoundError:
            messagebox.showwarning("Invalid Directory", f"The system cannot find the path specified:\n\n{directory}")


    def refresh_files(self):
        path = os.path.dirname(self.image_files[self.current_index])
        index = self.current_index
        self.set_working_directory(path=path)
        self.jump_to_image(index)
        messagebox.showinfo("Refresh", f"Files have been refreshed from:\n\n{path}")


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
            working_path = os.path.normcase(os.path.normpath(os.path.abspath(os.path.dirname(self.image_files[self.current_index]))))
            textbox_path = os.path.normcase(os.path.normpath(os.path.abspath(self.image_dir.get())))
            if textbox_path == self.dir_placeholder_text:
                return
            if textbox_path != working_path:
                self.directory_entry.delete(0, "end")
                self.directory_entry.insert(0, working_path)
        except IndexError:
            return


    def check_if_directory(self):
        if not os.path.isdir(self.image_dir.get()) or self.image_dir.get() == self.dir_placeholder_text:
            return False
        return True


    def check_odd_files(self, filename):
        file_extension = os.path.splitext(filename)[1].lower()
        file_rename_dict = {".jpg_large": "jpg", ".jfif": "jpg"}
        return file_extension in file_rename_dict


    def archive_dataset(self):
        if not messagebox.askokcancel("Zip Dataset", "This will create an archive of the current folder. Only images, videos, and text files will be archived.\n\nPress OK to set the zip name and output path."):
            return
        folder_path = self.image_dir.get()
        zip_filename = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip files", "*.zip")], title="Save As", initialdir=folder_path, initialfile="dataset.zip")
        if not zip_filename:
            return
        allowed_extensions = [".txt", ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".jfif", ".jpg_large", ".mp4"]
        file_list = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if any(file.lower().endswith(ext) for ext in allowed_extensions)]
        num_images = sum(1 for file in file_list if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.jfif', '.jpg_large')))
        num_videos = sum(1 for file in file_list if file.lower().endswith('.mp4'))
        num_texts = sum(1 for file in file_list if file.lower().endswith('.txt'))
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_STORED) as zip_file:
            for file_path in file_list:
                archive_name = os.path.relpath(file_path, folder_path)
                zip_file.write(file_path, archive_name)
        messagebox.showinfo("Success", f"The archive has been successfully zipped!\nNumber of image files: {num_images}\nNumber of video files: {num_videos}\nNumber of text files: {num_texts}")


    def manually_rename_single_pair(self):
        if not self.check_if_directory():
            return
        if self.current_index >= len(self.image_files):
            messagebox.showerror("Error: app.manually_rename_single_pair()", "No valid image selected.")
            return
        image_file = self.image_files[self.current_index]
        current_image_name = os.path.basename(image_file)
        text_file = self.text_files[self.current_index] if self.current_index < len(self.text_files) and os.path.exists(self.text_files[self.current_index]) else None
        current_text_name = os.path.basename(text_file) if text_file else "(No associated text file)"
        new_name = custom_simpledialog.askstring("Rename", "Enter the new name for the pair (without extension):", initialvalue=os.path.splitext(current_image_name)[0])
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
            self.update_video_thumbnails()
            self.show_pair()
            new_index = self.image_files.index(new_image_file)
            self.jump_to_image(new_index)
        except PermissionError as e:
            messagebox.showerror("Error: app.manually_rename_single_pair()", f"Permission denied while renaming files: {e}")
        except FileNotFoundError as e:
            messagebox.showerror("Error: app.manually_rename_single_pair()", f"File not found: {e}")
        except Exception as e:
            messagebox.showerror("Error: app.manually_rename_single_pair()", f"An unexpected error occurred: {e}")


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
            messagebox.showerror("Error: app.rename_odd_files()", f"An error occurred while renaming odd files.\n\n{e}")


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
                            with open(file_path, 'w', encoding='utf-8') as file:
                                pass  # Create file
                            created_count += 1
                    messagebox.showinfo("Success", f"Created {created_count} blank text files!")
        except Exception as e:
            messagebox.showerror("Error: app.create_blank_text_files()", f"Failed to create file: {file_path}\n\n{str(e)}")


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
                    with open(os.path.join(backup_dir, backup_file), 'r', encoding='utf-8') as file:
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
                except Exception as e:
                    messagebox.showerror("Error: app.restore_backup()", f"Something went wrong: {original_file}\n\n{str(e)}")
        messagebox.showinfo("Success", "All text files have been restored from the latest backup!")
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
                with open(new_backup, 'w', encoding='utf-8') as f:
                    f.write("!DELETEME!")


    def delete_text_backup(self):
        if self.text_files:
            try:
                backup_folder = os.path.join(os.path.dirname(self.text_files[0]), 'text_backup')
                if os.path.exists(backup_folder):
                    shutil.rmtree(backup_folder)
            except (PermissionError, IOError, TclError) as e:
                messagebox.showerror("Error: app.delete_text_backup()", f"An error occurred while deleting the text backups.\n\n{e}")


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
            self.root.destroy()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: app.delete_trash_folder()", f"An error occurred while deleting the trash folder.\n\n{e}")


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
                                shutil.move(file_list[index], trash_file)
                            except FileExistsError:
                                if not trash_file.endswith("txt"):
                                    if messagebox.askokcancel("Warning", "The file already exists in the trash. Do you want to overwrite it?"):
                                        os.remove(trash_file)
                                        shutil.move(file_list[index], trash_file)
                                    else:
                                        return
                            deleted_pair.append((file_list, index, trash_file))
                            del file_list[index]
                    self.deleted_pairs.append(deleted_pair)
                    self._nav_after_delete(index)
                    self.undo_state.set("normal")
                    self.editMenu.entryconfig("Undo Delete", state="normal")
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
                                messagebox.showerror("Error: app.delete_pair()", f"An error occurred while deleting the img-txt pair.\n\n{e}")
                                return
                            deleted_pair.append((file_list, index, None))
                            del file_list[index]
                    self.deleted_pairs = [pair for pair in self.deleted_pairs if pair != deleted_pair]
                    self._nav_after_delete(index)
                else:
                    pass
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: app.delete_pair()", f"An error occurred while deleting the img-txt pair.\n\n{e}")


    def _nav_after_delete(self, index):
        self.update_total_image_label()
        if index >= len(self.image_files):
            self.current_index = max(0, len(self.image_files) - 1)
            self.jump_to_image(self.current_index)
        else:
            self.show_pair()


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
                    index_value = self.image_files.index(original_path)
                    self.jump_to_image(index_value)
                else:
                    self.load_text_file(original_path)
            self.update_total_image_label()
            if not self.deleted_pairs:
                self.undo_state.set("disabled")
                self.editMenu.entryconfig("Undo Delete", state="disabled")
        except (PermissionError, ValueError, IOError, TclError) as e:
            messagebox.showerror("Error: app.undo_delete_pair()", f"An error occurred while restoring the img-txt pair.\n\n{e}")


#endregion
#region Framework


    def set_appid(self):
        myappid = 'ImgTxtViewer.Nenotriple'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


    def setup_window(self, geometry=None):
        self.title = f"{self.app_version} - img-txt Viewer"
        self.root.title(self.title)
        self.root.minsize(545, 200) # Width x Height
        if geometry:
            window_width = geometry.get("width")
            window_height = geometry.get("height")
            position_right = geometry.get("x")
            position_top = geometry.get("y")
            state = geometry.get("maximized")
            self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
            if state:
                self.root.state('zoomed')
        else:
            window_width = 1110
            window_height = 660
            position_right = self.root.winfo_screenwidth()//2 - window_width//2
            position_top = self.root.winfo_screenheight()//2 - window_height//2
            self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.additional_window_setup()


    def additional_window_setup(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.set_custom_ttk_button_highlight_style()


    def set_icon(self):
        self.icon_path = os.path.join(self.app_root_path, "main", "icon.ico")
        try:
            self.root.iconbitmap(self.icon_path)
        except TclError: pass
        # Blank image (app icon)
        self.icon_path = os.path.join(self.app_root_path, "main", "icon.ico")
        with Image.open(self.icon_path) as img:
            self.blank_image = ImageTk.PhotoImage(img)


    def get_app_path(self):
        if getattr(sys, 'frozen', False):
            is_frozen = True
            root_path = sys._MEIPASS
            launch_path = os.getcwd()
        else:
            is_frozen = False
            root_path = os.path.dirname(__file__)
            launch_path = os.getcwd()
        return is_frozen, root_path, launch_path


    def get_direct_app_path(self):
        if self.is_frozen:
            app_path = self.app_launch_path
        else:
            app_path = self.app_root_path
        return app_path


    def set_custom_ttk_button_highlight_style(self):
        style = ttk.Style(self.root)
        style.configure("Highlighted.TButton", background="#005dd7")
        style.configure("Red.TButton", foreground="red")
        style.configure("Blue.TButton", foreground="blue")
        style.configure("Blue+.TButton", foreground="blue", background="#005dd7")


    def get_window_geometry(self):
        self.root.update_idletasks()
        geometry = self.root.winfo_geometry()
        # If the window is maximized on Windows, state() returns 'zoomed'
        try:
            state = self.root.state()
        except Exception:
            state = None
        if state == "zoomed":
            # Fall back to screen dimensions for maximized state
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()
            return {
                "geometry": geometry,
                "width": int(width),
                "height": int(height),
                "x": 0,
                "y": 0,
                "maximized": True,
            }
        # Normal parsing (allow negative offsets for snapped windows)
        match = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geometry)
        if match:
            width, height, x_offset, y_offset = match.groups()
            return {
                "geometry": geometry,
                "width": int(width),
                "height": int(height),
                "x": int(x_offset),
                "y": int(y_offset),
                "maximized": False,
            }
        # Fallback: use widget geometry functions which work for snapped/odd layouts
        return {
            "geometry": geometry,
            "width": int(self.root.winfo_width()),
            "height": int(self.root.winfo_height()),
            "x": int(self.root.winfo_rootx()),
            "y": int(self.root.winfo_rooty()),
            "maximized": False,
        }


    def reset_window_geometry(self):
        self.setup_window()
        self.always_on_top_var.set(value=False)
        self.set_always_on_top()
        self.panes_swap_ew_var.set(value=False)
        self.panes_swap_ns_var.set(value=False)
        self.swap_pane_sides(swap_state=False)
        self.swap_pane_orientation(swap_state=False)
        self.config_text_pane_for_tab(reset=True)
        self.root.update_idletasks()


# --------------------------------------
# Mainloop
# --------------------------------------
root = Tk()
app = ImgTxtViewer(root)
root.mainloop()
