"""
########################################
#            IMG-TXT VIEWER            #
#   Version : v1.97                    #
#   Author  : github.com/Nenotriple    #
########################################

Description:
-------------
Display an image and text file side-by-side for easy manual caption editing.

More info here: https://github.com/Nenotriple/img-txt_viewer

"""


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
import zipfile
import subprocess


# Standard Library - GUI
from tkinter import (
    ttk, Tk, messagebox, filedialog, simpledialog,
    StringVar, BooleanVar, IntVar,
    Frame, PanedWindow, Menu, scrolledtext,
    Label, Text,
    Event, TclError
)


# Third-Party Libraries
import numpy
from TkToolTip.TkToolTip import TkToolTip as ToolTip
from PIL import Image, ImageTk, ImageSequence, UnidentifiedImageError


# Custom Libraries
from main.scripts import (
    about_img_txt_viewer,
    calculate_file_stats,
    batch_resize_images,
    custom_scrolledtext,
    batch_crop_images,
    settings_manager,
    batch_tag_edit,
    find_dupe_file,
    text_controller,
    upscale_image,
    resize_image,
    image_grid,
    edit_panel,
    CropUI,
)
from main.scripts.Autocomplete import SuggestionHandler
from main.scripts.PopUpZoom import PopUpZoom as PopUpZoom
from main.scripts.OnnxTagger import OnnxTagger as OnnxTagger
from main.scripts.ThumbnailPanel import ThumbnailPanel


#endregion
################################################################################################################################################
#region CLS: ImgTxtViewer


class ImgTxtViewer:
    def __init__(self, root):
        self.app_version = "v1.97"
        self.root = root
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
        self.about_window = about_img_txt_viewer.AboutWindow(self, self.root, self.blank_image)
        self.settings_manager = settings_manager.SettingsManager(self, self.root)
        self.stat_calculator = calculate_file_stats.CalculateFileStats(self, self.root)
        self.batch_resize_images = batch_resize_images.BatchResizeImages()
        self.edit_panel = edit_panel.EditPanel(self, self.root)
        self.batch_tag_edit = batch_tag_edit.BatchTagEdit()
        self.find_dupe_file = find_dupe_file.FindDupeFile()
        self.crop_ui = CropUI.CropInterface()
        self.onnx_tagger = OnnxTagger(self)
        self.autocomplete = SuggestionHandler(self)
        self.text_controller = text_controller.TextController(self, self.root)

        # Setup UI state
        self.ui_state = "ImgTxtViewer"

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
        self.toggle_zoom_var = None
        self.undo_state = StringVar(value="disabled")
        self.previous_window_size = (self.root.winfo_width(), self.root.winfo_height())
        self.initialize_text_pane = True

        # 'after()' Job IDs
        self.is_resizing_job_id = None
        self.delete_tag_job_id = None
        self.animation_job_id = None
        self.update_thumbnail_job_id = None

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
        self.app_settings_cfg = 'settings.cfg'
        self.my_tags_csv = 'my_tags.csv'
        self.onnx_models_dir = "onnx_models"
        self.image_dir = StringVar(value="Choose Directory...")
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
        self.quality_filter = Image.BILINEAR
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
        self.root.bind("<Control-f>", lambda event: self.toggle_highlight_all_duplicates())
        self.root.bind("<Control-s>", lambda event: self.save_text_file(highlight=True))
        self.root.bind("<Alt-Right>", lambda event: self.next_pair(event))
        self.root.bind("<Alt-Left>", lambda event: self.prev_pair(event))
        self.root.bind('<Shift-Delete>', lambda event: self.delete_pair())
        self.root.bind('<Configure>', self.handle_window_configure)
        self.root.bind('<F1>', lambda event: self.toggle_image_grid(event))
        self.root.bind('<F2>', lambda event: self.toggle_zoom_popup(event))
        self.root.bind('<F4>', lambda event: self.open_image_in_editor(event))
        self.root.bind('<Control-w>', lambda event: self.on_closing(event))

        # Display window size on resize:
        #self.root.bind("<Configure>", lambda event: print(f"\rWindow size (W,H): {event.width},{event.height}    ", end='') if event.widget == self.root else None, add="+")


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
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
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
        self.options_subMenu.add_checkbutton(label="Colored Suggestions", underline=1, variable=self.colored_suggestion_var, command=self.autocomplete.update_autocomplete_dictionary)
        self.options_subMenu.add_checkbutton(label="Highlight Selection", underline=0, variable=self.highlight_selection_var)
        self.options_subMenu.add_checkbutton(label="Add Comma After Tag", underline=0, variable=self.auto_insert_comma_var, command=self.append_comma_to_text)
        self.options_subMenu.add_checkbutton(label="Big Save Button", underline=0, variable=self.big_save_button_var, command=self.toggle_save_button_height)
        self.options_subMenu.add_checkbutton(label="List View", underline=0, variable=self.list_mode_var, command=self.toggle_list_mode)
        self.options_subMenu.add_separator()
        self.options_subMenu.add_checkbutton(label="Always On Top", underline=0, variable=self.always_on_top_var, command=self.set_always_on_top)
        self.options_subMenu.add_checkbutton(label="Toggle Zoom", accelerator="F2", variable=self.toggle_zoom_var, command=self.toggle_zoom_popup)
        self.options_subMenu.add_checkbutton(label="Toggle Thumbnail Panel", variable=self.thumbnails_visible, command=self.debounce_update_thumbnail_panel)
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
        dictionaryMenu.add_checkbutton(label="English Dictionary", underline=0, variable=self.csv_english_dictionary, command=self.autocomplete.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Danbooru", underline=0, variable=self.csv_danbooru, command=self.autocomplete.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Danbooru (Safe)", underline=0, variable=self.csv_danbooru_safe, command=self.autocomplete.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="Derpibooru", underline=0, variable=self.csv_derpibooru, command=self.autocomplete.update_autocomplete_dictionary)
        dictionaryMenu.add_checkbutton(label="e621", underline=0, variable=self.csv_e621, command=self.autocomplete.update_autocomplete_dictionary)
        dictionaryMenu.add_separator()
        dictionaryMenu.add_command(label="Clear Selection", underline=0, command=self.autocomplete.clear_dictionary_csv_selection)

        # Suggestion Threshold Menu
        suggestion_threshold_menu = Menu(autocompleteSettingsMenu, tearoff=0)
        autocompleteSettingsMenu.add_cascade(label="Threshold", underline=11, menu=suggestion_threshold_menu)
        for level in ["Slow", "Normal", "Fast", "Faster"]:
            suggestion_threshold_menu.add_radiobutton(label=level, variable=self.suggestion_threshold_var, value=level, command=self.autocomplete.set_suggestion_threshold)

        # Suggestion Quantity Menu
        suggestion_quantity_menu = Menu(autocompleteSettingsMenu, tearoff=0)
        autocompleteSettingsMenu.add_cascade(label="Quantity", underline=11, menu=suggestion_quantity_menu)
        for quantity in range(0, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(quantity), variable=self.suggestion_quantity_var, value=quantity, command=lambda suggestion_quantity=quantity: self.autocomplete.set_suggestion_quantity(suggestion_quantity))

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
        self.optionsMenu.add_command(label="Open MyTags File...", underline=1, command=lambda: self.open_textfile(self.my_tags_csv))


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
        self.individual_operations_menu.add_command(label="Crop...", underline=0, command=self.show_crop_ui)
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


#endregion
################################################################################################################################################
#region - Create Primary UI


    def create_primary_ui(self):
        # Create Notebook as the main container for UI widgets
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(expand=True, fill="both")
        # Create Notebook Tabs
        self.primary_tab = Frame(self.main_notebook)
        self.batch_tag_edit_tab = Frame(self.main_notebook)
        self.batch_resize_images_tab = Frame(self.main_notebook)
        self.find_dupe_file_tab = Frame(self.main_notebook)
        self.crop_ui_tab = Frame(self.main_notebook)
        self.main_notebook.add(self.primary_tab, text="Tagger")
        self.main_notebook.add(self.batch_tag_edit_tab, text="Tag-Editor")
        self.main_notebook.add(self.batch_resize_images_tab, text="Batch Resize")
        self.main_notebook.add(self.find_dupe_file_tab, text="Find Dupes")
        self.main_notebook.add(self.crop_ui_tab, text="Crop")
        # Build the primary UI within the 'Primary' tab
        self.setup_primary_frames(self.primary_tab)
        self.create_primary_widgets(self.primary_tab)


    def setup_primary_frames(self, container):
        # Configure the grid weights for the container tab
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        # primary_paned_window is used to contain the ImgTxtViewer UI.
        self.primary_paned_window = PanedWindow(container, orient="horizontal", sashwidth=6, bg="#d0d0d0", bd=0)
        self.primary_paned_window.grid(row=0, column=0, sticky="nsew")
        self.primary_paned_window.bind("<B1-Motion>", self.disable_button)
        # master_image_frame: exclusively used for the master_image_inner_frame and image_grid.
        self.master_image_frame = Frame(container)
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
        self.master_control_frame = Frame(container)
        self.primary_paned_window.add(self.master_control_frame, stretch="always")
        self.primary_paned_window.paneconfigure(self.master_control_frame, minsize=300)
        self.primary_paned_window.update()
        self.primary_paned_window.sash_place(0, 0, 0)


    def create_primary_widgets(self, container):
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
        self.view_menu.add_checkbutton(label="Toggle Zoom", accelerator="F2", variable=self.toggle_zoom_var, command=self.toggle_zoom_popup)
        self.view_menu.add_checkbutton(label="Toggle Thumbnail Panel", variable=self.thumbnails_visible, command=self.debounce_update_thumbnail_panel)
        self.view_menu.add_checkbutton(label="Toggle Edit Panel", variable=self.edit_panel_visible_var, command=self.edit_panel.toggle_edit_panel)
        self.view_menu.add_separator()
        self.view_menu.add_checkbutton(label="Vertical View", underline=0, variable=self.panes_swap_ns_var, command=self.swap_pane_orientation)
        self.view_menu.add_checkbutton(label="Swap img-txt Sides", underline=0, variable=self.panes_swap_ew_var, command=self.swap_pane_sides)
        image_quality_menu = Menu(self.optionsMenu, tearoff=0)
        self.view_menu.add_separator()
        self.view_menu.add_cascade(label="Image Display Quality", menu=image_quality_menu)
        for value in ["High", "Normal", "Low"]:
            image_quality_menu.add_radiobutton(label=value, variable=self.image_quality_var, value=value, command=self.set_image_quality)
        # Image Stats
        self.label_image_stats = Label(self.stats_frame, text="...")
        self.label_image_stats.grid(row=0, column=1, sticky="ew")
        self.label_image_stats_tooltip = ToolTip.create(self.label_image_stats, "...", 250, 6, 12)
        # Primary Image
        self.primary_display_image = Label(self.master_image_inner_frame, cursor="hand2")
        self.primary_display_image.grid(row=1, column=0, sticky="nsew")
        self.primary_display_image.bind("<Double-1>", lambda event: self.open_image(index=self.current_index, event=event))
        self.primary_display_image.bind('<Button-2>', self.open_image_directory)
        self.primary_display_image.bind("<MouseWheel>", self.mouse_scroll)
        self.primary_display_image.bind("<Button-3>", self.show_image_context_menu)
        self.primary_display_image.bind("<ButtonPress-1>", self.start_drag)
        self.primary_display_image.bind("<ButtonRelease-1>", self.stop_drag)
        self.primary_display_image.bind("<B1-Motion>", self.dragging_window)
        self.popup_zoom = PopUpZoom(self.primary_display_image)
        self.toggle_zoom_var = BooleanVar(value=self.popup_zoom.zoom_enabled.get())
        self.image_preview_tooltip = ToolTip.create(self.primary_display_image, "Right-Click for more\nMiddle-click to open in file explorer\nDouble-Click to open in your system image viewer\nALT+Left/Right or Mouse-Wheel to move between pairs", 1000, 6, 12)
        # Thumbnail Panel
        self.thumbnail_panel = ThumbnailPanel(master=self.master_image_inner_frame, parent=self)
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
        self.text_path_tooltip = ToolTip.create(self.text_path_indicator, "Text Path: Same as image path", 10, 6, 12)
        self.directory_entry = ttk.Entry(directory_frame, textvariable=self.image_dir)
        self.directory_entry.pack(side="left", fill="both", expand=True, pady=2)
        self.directory_entry.bind('<Return>', self.set_working_directory)
        self.directory_entry.bind("<Double-1>", lambda event: self.text_controller.custom_select_word_for_entry(event))
        self.directory_entry.bind("<Triple-1>", lambda event: self.text_controller.select_all_in_entry(event))
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
        self.browse_button = ttk.Button(directory_frame, text="Browse...", width=8, takefocus=False, command=self.choose_working_directory)
        self.browse_button.pack(side="left", pady=2)
        ToolTip.create(self.browse_button, "Right click to set an alternate path for text files", 250, 6, 12)
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
        self.save_button = ttk.Button(self.index_frame, text="Save", state="disabled", style="Blue.TButton", padding=(5, 5), takefocus=False, command=self.save_text_file)
        self.save_button.pack(side="left", pady=2, fill="x", expand=True)
        ToolTip.create(self.save_button, "CTRL+S to save\n\nRight-Click to make the save button larger", 1000, 6, 12)
        self.auto_save_checkbutton = ttk.Checkbutton(self.index_frame, width=10, text="Auto-save", state="disabled", variable=self.auto_save_var, takefocus=False, command=self.sync_title_with_content)
        self.auto_save_checkbutton.pack(side="left")
        ToolTip.create(self.auto_save_checkbutton, "Automatically save the current text file when:\nNavigating img-txt pairs, changing active directory, or closing the app", 1000, 6, 12)
        # Navigation Buttons
        nav_button_frame = Frame(self.master_control_frame)
        nav_button_frame.pack(fill="x", padx=2)
        self.next_button = ttk.Button(nav_button_frame, text="Next", width=12, state="disabled", takefocus=False, command=lambda: self.update_pair("next"))
        self.prev_button = ttk.Button(nav_button_frame, text="Previous", width=12, state="disabled", takefocus=False, command=lambda: self.update_pair("prev"))
        self.next_button.pack(side="right", fill="x", expand=True)
        self.prev_button.pack(side="right", fill="x", expand=True)
        ToolTip.create(self.next_button, "Hotkey: ALT+R\nHold shift to advance by 5", 1000, 6, 12)
        ToolTip.create(self.prev_button, "Hotkey: ALT+L\nHold shift to advance by 5", 1000, 6, 12)
        # Suggestion text
        self.suggestion_frame = Frame(self.master_control_frame, bg='#f0f0f0')
        self.suggestion_frame.pack(side="top", fill="x", pady=2)
        self.suggestion_textbox = Text(self.suggestion_frame, height=1, width=1, borderwidth=0, highlightthickness=0, bg='#f0f0f0', state="disabled", cursor="arrow")
        self.suggestion_textbox.pack(side="left", fill="x", expand=True)
        self.suggestion_textbox.bind("<Button-1>", self.disable_button)
        self.suggestion_textbox.bind("<B1-Motion>", self.disable_button)
        ToolTip.create(self.suggestion_textbox,
            "Color Codes:\n"
            "Danbooru:\n"
            "  - General tags: Black\n"
            "  - Artists: Red\n"
            "  - Copyright: Magenta\n"
            "  - Characters: Green\n"
            "  - Meta: Orange\n"
            "e621:\n"
            "  - General tags: Black\n"
            "  - Artists: Yellow\n"
            "  - Copyright: Magenta\n"
            "  - Characters: Green\n"
            "  - Species: Orange\n"
            "  - Meta: Red\n"
            "  - Lore: Green\n"
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
            "  - Original Content: Light-Pink",
            1000, 6, 12, justify="left"
        )
        # Suggestion Options
        self.suggestion_menubutton = ttk.Button(self.suggestion_frame, text="☰", takefocus=False, width=2, command=lambda: self.show_suggestion_context_menu(button=True))
        self.suggestion_menubutton.pack(side="right", padx=2)
        # Startup info text
        self.info_text = scrolledtext.ScrolledText(self.master_control_frame)
        self.info_text.pack(expand=True, fill="both")
        for header, section in zip(self.about_window.info_headers, self.about_window.info_content):
            self.info_text.insert("end", header + "\n", "header")
            self.info_text.insert("end", section + "\n", "section")
        self.info_text.tag_config("header", font=("Segoe UI", 9, "bold"))
        self.info_text.tag_config("section", font=("Segoe UI", 9))
        self.info_text.bind("<Button-3>", self.show_text_context_menu)
        self.info_text.config(state='disabled', wrap="word")


#endregion
################################################################################################################################################
#region - Text Box setup


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
            self.text_box = custom_scrolledtext.CustomScrolledText(self.text_frame, wrap="word", undo=True, maxundo=200, inactiveselectbackground="#0078d7")
            self.text_box.pack(side="top", expand="yes", fill="both")
            self.text_box.tag_configure("highlight", background="#5da9be", foreground="white")
            self.text_box.config(font=(self.font_var.get(), self.font_size_var.get()))
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
        self.text_pane.add(self.text_widget_frame, stretch="never")
        self.text_pane.paneconfigure(self.text_widget_frame)
        self.text_notebook = ttk.Notebook(self.text_widget_frame)
        self.text_notebook.bind("<<NotebookTabChanged>>", self.adjust_text_pane_height)
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


    def adjust_text_pane_height(self, event):
        tab_heights = {
            'S&R': 60,
            'Prefix': 60,
            'Append': 60,
            'AutoTag': 340,
            'Filter': 60,
            'Highlight': 60,
            'Font': 60,
            'MyTags': 340,
            'Stats': 340
        }
        selected_tab = event.widget.tab("current", "text")
        tab_height = 60 if self.initialize_text_pane else tab_heights.get(selected_tab, 60)
        self.initialize_text_pane = False
        if selected_tab == "MyTags":
            self.text_controller.refresh_all_tags_listbox(tags=self.stat_calculator.sorted_captions)
        self.text_pane.paneconfigure(self.text_widget_frame, height=tab_height)


    # --------------------------------------
    # Text Box Binds
    # --------------------------------------
    def set_text_box_binds(self):
        # Mouse binds
        self.text_box.bind("<Double-1>", lambda event: self.custom_select_word_for_text(event, self.text_box))
        self.text_box.bind("<Triple-1>", lambda event: self.custom_select_line_for_text(event, self.text_box))
        self.text_box.bind("<Button-1>", lambda event: (self.remove_tag(), self.autocomplete.clear_suggestions()))
        self.text_box.bind("<Button-2>", lambda event: (self.delete_tag_under_mouse(event), self.sync_title_with_content(event)))
        self.text_box.bind("<Button-3>", lambda event: (self.show_text_context_menu(event)))
        # Update the autocomplete suggestion label after every KeyRelease event.
        self.text_box.bind("<KeyRelease>", lambda event: (self.autocomplete.update_suggestions(event), self.sync_title_with_content(event), self.get_text_summary()))
        # Insert a newline after inserting an autocomplete suggestion when list_mode is active.
        self.text_box.bind('<comma>', self.autocomplete.insert_newline_listmode)
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


    # --------------------------------------
    # Text Box Context Menu
    # --------------------------------------
    def show_text_context_menu(self, event):
        if hasattr(self, 'text_box'):
            self.text_box.focus_set()
        widget_in_focus = root.focus_get()
        text_context_menu = Menu(root, tearoff=0)
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
                text_context_menu.add_command(label="Add to MyTags", state=select_state, command=lambda: self.add_to_custom_dictionary(origin="text_box"))
                text_context_menu.add_separator()
                text_context_menu.add_command(label="Highlight all Duplicates", accelerator="Ctrl+F", command=self.highlight_all_duplicates)
                text_context_menu.add_command(label="Next Empty Text File", accelerator="Ctrl+E", command=self.index_goto_next_empty)
                text_context_menu.add_separator()
                text_context_menu.add_checkbutton(label="Highlight Selection", variable=self.highlight_selection_var)
                text_context_menu.add_checkbutton(label="Clean-Text", variable=self.cleaning_text_var, command=self.toggle_list_menu)
                text_context_menu.add_checkbutton(label="List View", variable=self.list_mode_var, state=cleaning_state, command=self.toggle_list_mode)
            elif widget_in_focus == self.info_text:
                text_context_menu.add_command(label="Copy", command=lambda: widget_in_focus.event_generate('<<Copy>>'))
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
        self.image_context_menu.add_command(label="AutoTag", command=self.text_controller.interrogate_image_tags)
        self.image_context_menu.add_separator()
        # File
        self.image_context_menu.add_command(label="Duplicate img-txt pair", command=self.duplicate_pair)
        self.image_context_menu.add_command(label="Delete img-txt Pair", accelerator="Shift+Del", command=self.delete_pair)
        self.image_context_menu.add_command(label="Undo Delete", command=self.undo_delete_pair, state=self.undo_state.get())
        self.image_context_menu.add_separator()
        # Edit
        self.image_context_menu.add_command(label="Rename Pair", command=self.manually_rename_single_pair)
        self.image_context_menu.add_command(label="Upscale...", command=lambda: self.upscale_image(batch=False))
        self.image_context_menu.add_command(label="Resize...", command=self.resize_image)
        self.image_context_menu.add_command(label="Crop...", command=self.show_crop_ui)
        if not self.image_file.lower().endswith('.gif'):
            self.image_context_menu.add_command(label="Expand", command=self.expand_image)
        else:
            self.image_context_menu.add_command(label="Expand", state="disabled", command=self.expand_image)
        self.image_context_menu.add_command(label="Rotate", command=self.rotate_current_image)
        self.image_context_menu.add_command(label="Flip", command=self.flip_current_image)
        self.image_context_menu.add_separator()
        # Misc
        self.image_context_menu.add_checkbutton(label="Toggle Image-Grid", accelerator="F1", variable=self.is_image_grid_visible_var, command=self.toggle_image_grid)
        self.image_context_menu.add_checkbutton(label="Toggle Zoom", accelerator="F2", variable=self.toggle_zoom_var, command=self.toggle_zoom_popup)
        self.image_context_menu.add_checkbutton(label="Toggle Thumbnail Panel", variable=self.thumbnails_visible, command=self.debounce_update_thumbnail_panel)
        self.image_context_menu.add_checkbutton(label="Toggle Edit Panel", variable=self.edit_panel_visible_var, command=self.edit_panel.toggle_edit_panel)
        self.image_context_menu.add_checkbutton(label="Vertical View", underline=0, variable=self.panes_swap_ns_var, command=self.swap_pane_orientation)
        self.image_context_menu.add_checkbutton(label="Swap img-txt Sides", underline=0, variable=self.panes_swap_ew_var, command=self.swap_pane_sides)
        # Image Display Quality
        image_quality_menu = Menu(self.optionsMenu, tearoff=0)
        self.image_context_menu.add_cascade(label="Image Display Quality", menu=image_quality_menu)
        for value in ["High", "Normal", "Low"]:
            image_quality_menu.add_radiobutton(label=value, variable=self.image_quality_var, value=value, command=self.set_image_quality)
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
        dictionary_menu.add_checkbutton(label="English Dictionary", underline=0, variable=self.csv_english_dictionary, command=self.autocomplete.update_autocomplete_dictionary)
        dictionary_menu.add_checkbutton(label="Danbooru", underline=0, variable=self.csv_danbooru, command=self.autocomplete.update_autocomplete_dictionary)
        dictionary_menu.add_checkbutton(label="Danbooru (Safe)", underline=0, variable=self.csv_danbooru_safe, command=self.autocomplete.update_autocomplete_dictionary)
        dictionary_menu.add_checkbutton(label="Derpibooru", underline=0, variable=self.csv_derpibooru, command=self.autocomplete.update_autocomplete_dictionary)
        dictionary_menu.add_checkbutton(label="e621", underline=0, variable=self.csv_e621, command=self.autocomplete.update_autocomplete_dictionary)
        dictionary_menu.add_separator()
        dictionary_menu.add_command(label="Clear Selection", underline=0, command=self.autocomplete.clear_dictionary_csv_selection)
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
                self.text_controller.info_label.config(text=f"Characters: {char_count}  |  Words: {word_count}")
                return char_count, word_count
            return 0, 0
        except Exception:
            return 0, 0


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
        tool_commands = [
            "Batch Operations",
            "Edit Current pair",
            "Open Current Directory...",
            "Open Current Image...",
            "Edit Image...",
            "Next Empty Text File",
        ]
        options_commands = [
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
        self.view_menubutton.configure(state="normal")
        # Bindings
        self.suggestion_textbox.bind("<Button-3>", self.show_suggestion_context_menu)
        self.image_index_entry.bind("<Button-3>", self.open_index_context_menu)
        self.total_images_label.bind("<Button-3>", self.open_index_context_menu)
        self.index_pair_label.bind("<Button-3>", self.open_index_context_menu)


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


    def toggle_zoom_popup(self, event=None):
        new_state = not self.popup_zoom.zoom_enabled.get()
        self.popup_zoom.zoom_enabled.set(new_state)
        self.toggle_zoom_var.set(new_state)
        self.options_subMenu.entryconfig("Toggle Zoom", variable=self.toggle_zoom_var)
        if hasattr(self, 'image_context_menu'):
            self.image_context_menu.entryconfig("Toggle Zoom", variable=self.toggle_zoom_var)
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
        window_width = self.root.winfo_width()
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
        self.root.after_idle(self.configure_pane_position)


    def swap_pane_orientation(self, swap_state=None):
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
        if self.is_image_grid_visible_var.get():
            self.image_grid.reload_grid()


# --------------------------------------
# Thumbnail Panel
# --------------------------------------
    def debounce_update_thumbnail_panel(self, event=None):
        if not hasattr(self, 'thumbnail_panel'):
            return
        if self.update_thumbnail_job_id is not None:
            self.root.after_cancel(self.update_thumbnail_job_id)
        self.update_thumbnail_job_id = self.root.after(250, self.thumbnail_panel.update_panel)


#endregion
################################################################################################################################################
#region - Alt-UI Setup


    def show_batch_tag_edit(self, event=None):
        parent = self
        root = self.root
        text_files = self.text_files
        self.batch_tag_edit.setup_window(parent, root, text_files)


    def show_batch_resize_images(self, event=None):
        parent = self
        root = self.root
        path = self.image_dir.get()
        self.batch_resize_images.setup_window(parent, root, path)


    def show_find_dupe_file(self, event=None):
        parent = self
        root = self.root
        path = self.image_dir.get()
        self.find_dupe_file.setup_window(parent, root, path)


    def show_crop_ui(self):
        parent = self
        root = self.root
        path = self.image_dir.get()
        self.crop_ui.setup_window(parent, root, path)


# --------------------------------------
# Handle UI State
# --------------------------------------
    def toggle_alt_ui_menus(self, state):
        self.ui_state = state
        if state == "ImgTxtViewer":
            self.toggle_batch_ops_menu_items(all=True, state="normal")
            self.toggle_indiv_ops_menu_items(all=True, state="normal")
        else:
            self.toggle_batch_ops_menu_items(all=True, state="disabled")
            self.toggle_indiv_ops_menu_items(all=True, state="disabled")
            if state == "BatchTagEdit":
                self.toggle_batch_ops_menu_items(item="Batch Tag Edit...", state="normal")
            elif state == "BatchResizeImages":
                self.toggle_batch_ops_menu_items(item="Batch Resize Images...", state="normal")
            elif state == "FindDupeFile":
                self.toggle_batch_ops_menu_items(item="Find Duplicate Files...", state="normal")
            elif state == "CropUI":
                self.toggle_indiv_ops_menu_items(item="Crop...", state="normal")


    def toggle_batch_ops_menu_items(self, all=False, item=None, state="disabled", event=None):
        menu = self.batch_operations_menu
        menu_items = ["Batch Resize Images...", "Batch Tag Edit...", "Find Duplicate Files..."]
        if all:
            for item in menu_items:
                menu.entryconfig(item, state=state)
        else:
            if item in menu_items:
                menu.entryconfig(item, state=state)


    def toggle_indiv_ops_menu_items(self, all=False, item=None, state="disabled", event=None):
        menu = self.individual_operations_menu
        menu_items = ["Rename Pair", "Upscale...", "Crop...", "Resize...", "Expand", "Rotate", "Flip", "Duplicate img-txt Pair", "Delete img-txt Pair", "Undo Delete"]
        if all:
            for item in menu_items:
                menu.entryconfig(item, state=state)
        else:
            if item in menu_items:
                menu.entryconfig(item, state=state)


# --------------------------------------
# ImgTxtViewer states
# --------------------------------------
    def toggle_image_grid(self, event=None):
        if event is not None:
            self.is_image_grid_visible_var.set(not self.is_image_grid_visible_var.get())
        if self.master_image_inner_frame.winfo_viewable():
            self.master_image_inner_frame.grid_remove()
            self.image_grid.initialize()
            self.image_grid.grid()
            self.root.after(250, self.image_grid.reload_grid)
        else:
            self.refresh_image()
            self.image_grid.grid_remove()
            self.master_image_inner_frame.grid()


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
        self.root.after(100, lambda: self.remove_tag())


    def remove_tag(self):
        self.highlight_all_duplicates_var.set(False)
        for tag in self.text_box.tag_names():
            self.text_box.tag_remove(tag, "1.0", "end")


#endregion
################################################################################################################################################
#region - Primary Functions


    def load_pairs(self, silent=False):
        self.root.title(self.title)
        self.info_text.pack_forget()
        current_image_path = self.image_files[self.current_index] if self.image_files else None
        self.refresh_file_lists()
        self.enable_menu_options()
        self.create_text_box()
        self.restore_previous_index(current_image_path)
        if not silent:
            self.update_pair(save=False)
        else:
            self.update_pair(save=False, silent=True)
        self.configure_pane_position()
        self.stat_calculator.calculate_file_stats()


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
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")):
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


    def load_image_file(self, image_file, text_file):
        try:
            if not self.is_image_grid_visible_var.get():
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
            else:
                img = None
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
            if image is None:
                return text_file, None, None, None
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
        if self.animation_job_id is not None:
            self.root.after_cancel(self.animation_job_id)
            self.animation_job_id = None
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
                self.animation_job_id = self.root.after(delay, self.display_animated_gif)
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
            if not self.is_image_grid_visible_var.get():
                self.primary_display_image.config(width=max_img_width, height=max_img_height)
                self.original_image = image
                self.current_image = self.original_image.copy()
                self.current_max_img_height = max_img_height
                self.current_max_img_width = max_img_width
                self.primary_display_image.unbind("<Configure>")
                self.primary_display_image.bind("<Configure>", self.resize_and_scale_image_event)
            self.autocomplete.clear_suggestions()
            self.toggle_list_mode()
            self.highlight_custom_string()
            self.append_comma_to_text()
            self.highlight_all_duplicates_var.set(False)
            self.debounce_update_thumbnail_panel()
            self.get_text_summary()
            if self.is_image_grid_visible_var.get():
                self.image_grid.highlight_thumbnail(self.current_index)
        else:
            self.primary_display_image.unbind("<Configure>")


    def resize_and_scale_image_event(self, event):
        if not self.is_image_grid_visible_var.get():
            display_width = event.width if event.width else self.primary_display_image.winfo_width()
            display_height = event.height if event.height else self.primary_display_image.winfo_height()
            self.resize_and_scale_image(self.current_image, display_width, display_height, None, Image.NEAREST)


    def refresh_image(self):
        if self.image_files:
            self.display_image()
            self.debounce_update_thumbnail_panel()


    def debounce_refresh_image(self, event):
        if hasattr(self, 'text_box'):
            if self.is_resizing_job_id:
                self.root.after_cancel(self.is_resizing_job_id)
            if not self.is_image_grid_visible_var.get():
                self.is_resizing_job_id = self.root.after(250, self.refresh_image)
            else:
                self.is_resizing_job_id = self.root.after(250, self.image_grid.reload_grid)


    def handle_window_configure(self, event):  # Window resize
        if event.widget == self.root:
            current_size = (event.width, event.height)
            if current_size != self.previous_window_size:
                self.previous_window_size = current_size
                self.debounce_refresh_image(event)


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
        filename = (filename[:61] + '(...)') if len(filename) > 64 else filename
        return {"filename": filename, "resolution": f"{width} x {height}", "size": size_str, "color_mode": color_mode}


#endregion
################################################################################################################################################
#region - Navigation


    def update_pair(self, direction=None, save=True, step=1, silent=False):
        if self.image_dir.get() == "Choose Directory..." or len(self.image_files) == 0:
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
        self.update_total_image_label()


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
################################################################################################################################################
#region - Text Tools


    def delete_tag_under_mouse(self, event):
        def set_text_highlight(tag, color, start=None, end=None):
            self.text_box.tag_config(tag, background=color)
            if start and end:
                self.text_box.tag_add(tag, start, end)

        def delete_tag():
            if self.delete_tag_job_id is not None:
                self.text_box.delete(f"{line_start}+{start_of_clicked_tag}c", f"{line_start}+{end_of_clicked_tag}c")
                cleaned_text = self.cleanup_text(self.text_box.get("1.0", "end"))
                cleaned_text = '\n'.join([line for line in cleaned_text.split('\n') if line.strip() != ''])
                self.text_box.delete("1.0", "end")
                self.text_box.insert("1.0", cleaned_text)
                set_text_highlight("highlight", "#5da9be")
                try:
                    self.text_box.clipboard_get()
                except TclError: pass
                self.delete_tag_job_id = None
                self.sync_title_with_content()

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
        if self.delete_tag_job_id is not None:
            self.text_box.after_cancel(self.delete_tag_job_id)
        self.delete_tag_job_id = self.text_box.after(100, delete_tag)


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
                new_img = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
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
                index_value = self.image_files.index(new_filename)
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
        resize_image.ResizeTool(self.root, self, filepath, window_x, window_y, self.update_pair, self.jump_to_image)


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
        upscale_image.Upscale(self, self.root, filepath, batch, window_x, window_y)


    def batch_crop_images(self):
        main_window_width = root.winfo_width()
        main_window_height = root.winfo_height()
        window_x = root.winfo_x() + -155 + main_window_width // 2
        window_y = root.winfo_y() - 100 + main_window_height // 2
        filepath = str(self.image_dir.get())
        batch_crop_images.BatchCrop(self.root, filepath, window_x, window_y)


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
            messagebox.showerror("Error: open_image_in_editor()", str(e))
            self.set_external_image_editor_path()
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
                if os.path.isfile(app_path):
                    self.external_image_editor_path = app_path
                    messagebox.showinfo("Success", f"External image editor set to:\n\n{app_path}")
                else:
                    messagebox.showerror("Error", f"The selected path is not a valid file:\n\n{app_path}")
                    self.set_external_image_editor_path()
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


    def set_always_on_top(self, initial=False):
        if initial:
            self.always_on_top_var = BooleanVar(value=False)
        self.root.attributes('-topmost', self.always_on_top_var.get())


    def toggle_list_menu(self):
        if self.cleaning_text_var.get():
            self.options_subMenu.entryconfig("List View", state="normal")
        else:
            self.options_subMenu.entryconfig("List View", state="disabled")
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
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            self.root.geometry(f"{width}x{height}+{x}+{y}")

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
#region - Save and close


    def save_text_file(self, highlight=False):
        try:
            if self.image_dir.get() != "Choose Directory..." and self.check_if_directory() and self.text_files:
                file_saved = self._save_file()
                if self.cleaning_text_var.get() or self.list_mode_var.get():
                    self.refresh_text_box()
                if file_saved:
                    self.root.title(self.title)
                    if highlight:
                        self.save_button.configure(style="Blue+.TButton")
                        self.root.after(120, lambda: self.save_button.configure(style="Blue.TButton"))
                else:
                    self.root.title(self.title)
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: save_text_file()", f"An error occurred while saving the current text file.\n\n{e}")


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
        with open(self.my_tags_csv, 'r', encoding='utf-8') as file:
            content = self.remove_extra_newlines(file.read())
            tags = content.split('\n')
            self.text_controller.custom_dictionary_listbox.delete(0, 'end')
            for tag in tags:
                if tag.strip():
                    self.text_controller.custom_dictionary_listbox.insert('end', tag.strip())
            self.autocomplete.update_autocomplete_dictionary()


    def create_custom_dictionary(self, reset=False, refresh=True):
        try:
            csv_filename = self.my_tags_csv
            if reset or not os.path.isfile(csv_filename):
                with open(csv_filename, 'w', newline='', encoding="utf-8") as file:
                    file.write("")
                if refresh:
                    self.refresh_custom_dictionary()
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: create_custom_dictionary()", f"An error occurred while creating the custom dictionary file:\n\n{csv_filename}\n\n{e}")


    def add_to_custom_dictionary(self, origin):
        try:
            if origin == "text_box":
                selected_text = self.text_box.get("sel.first", "sel.last")
            elif origin == "auto_tag":
                selected_text = self.text_controller.auto_tag_listbox.get("active")
                selected_text = selected_text.split(':', 1)[-1].strip()
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


    def check_dir_for_img(self, directory):
        if any(fname.lower().endswith(('.jpg', '.jpeg', '.jpg_large', '.jfif', '.png', '.webp', '.bmp', '.gif')) for fname in os.listdir(directory)):
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
            if original_auto_save_var is not None:
                self.auto_save_var.set(original_auto_save_var)
        except Exception as e:
            messagebox.showwarning("Error", f"There was an unexpected issue setting the folder path:\n\n{e}")


    def get_initial_directory(self):
        initialdir = self.image_dir.get()
        if not initialdir or initialdir == "Choose Directory...":
            initialdir = self.settings_manager.config.get("Path", "last_img_directory", fallback=None)
            if not initialdir or not os.path.exists(initialdir):
                initialdir = os.path.dirname(__file__)
        if 'temp' in initialdir.lower():
            initialdir = os.path.expanduser("~")
        return initialdir


    def set_working_directory(self, silent=False, event=None):
        try:
            if self.auto_save_var.get():
                self.save_text_file()
            if hasattr(self, 'text_box'):
                self.text_controller.revert_text_image_filter(clear=True, silent=True)
            directory = self.directory_entry.get()
            if self.check_dir_for_img(directory):
                self.image_dir.set(os.path.normpath(directory))
                self.current_index = 0
                if not silent:
                    self.load_pairs()
                    self.set_text_file_path(directory)
                else:
                    self.load_pairs(silent=True)
                    self.set_text_file_path(directory, silent=True)
                self.jump_to_image(0)
        except FileNotFoundError:
            messagebox.showwarning("Invalid Directory", f"The system cannot find the path specified:\n\n{self.directory_entry.get()}")


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
                            with open(file_path, 'w', encoding='utf-8') as file:
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
                    messagebox.showerror("Error: restore_backup()", f"Something went wrong: {original_file}\n\n{str(e)}")
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
                    self._nav_after_delete(index)
                else:
                    pass
        except (PermissionError, IOError, TclError) as e:
            messagebox.showerror("Error: delete_pair()", f"An error occurred while deleting the img-txt pair.\n\n{e}")


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
                    index_value = int(self.image_files.index(original_path))
                    self.jump_to_image(index_value)
                else:
                    self.load_text_file(original_path)
            self.update_total_image_label()
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
        self.title = f"{self.app_version} - img-txt Viewer"
        self.root.title(self.title)
        self.root.minsize(545, 200) # Width x Height
        window_width = 1110
        window_height = 660
        position_right = root.winfo_screenwidth()//2 - window_width//2
        position_top = root.winfo_screenheight()//2 - window_height//2
        root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.additional_window_setup()


    def additional_window_setup(self):
        self.set_always_on_top(initial=True)
        self.root.attributes('-topmost', 0)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.set_custom_ttk_button_highlight_style()


    def set_icon(self):
        self.icon_path = os.path.join(self.application_path, "icon.ico")
        try:
            self.root.iconbitmap(self.icon_path)
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


    def set_custom_ttk_button_highlight_style(self):
        style = ttk.Style(self.root)
        style.configure("Highlighted.TButton", background="#005dd7")
        style.configure("Red.TButton", foreground="red")
        style.configure("Blue.TButton", foreground="blue")
        style.configure("Blue+.TButton", foreground="blue", background="#005dd7")


# --------------------------------------
# Mainloop
# --------------------------------------
root = Tk()
app = ImgTxtViewer(root)
root.mainloop()


#endregion
################################################################################################################################################
#region - Todo


'''


### Todo
-


### Tofix

-


  '''

#endregion
