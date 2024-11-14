"""This module contains the SettingsManager class, which is responsible for saving and loading user settings."""

# Standard Library
import os
import configparser

# Standard Library - GUI
from tkinter import messagebox

# --------------------------------------
# Class: SettingsManager
# --------------------------------------
class SettingsManager:
    def __init__(self, parent, root, version):
        self.parent = parent
        self.root = root
        self.version = version

        self.config = configparser.ConfigParser()
        self.edit_panel = self.parent.edit_panel


# --------------------------------------
# Save
# --------------------------------------
    def save_settings(self):
        """Saves the current user settings to a file."""
        try:
            self._read_existing_settings()
            self._save_version_settings()
            self._save_path_settings()
            self._save_window_settings()
            self._save_autocomplete_settings()
            #self._save_ONNX_settings()
            self._save_other_settings()
            self.write_settings_to_file()
        except (PermissionError, IOError) as e:
            messagebox.showerror("Error: save_settings()", f"An error occurred while saving the user settings.\n\n{e}")


    def _read_existing_settings(self):
        if os.path.exists(self.parent.app_settings_cfg):
            self.config.read(self.parent.app_settings_cfg)


    def _add_section(self, section_name):
        if not self.config.has_section(section_name):
            self.config.add_section(section_name)


    def _verify_filepath(self, path):
        return os.path.exists(path)


    def _save_version_settings(self):
        self._add_section("Version")
        self.parent.check_working_directory()
        self.config.set("Version", "app_version", self.version)


    def _save_path_settings(self):
        self._add_section("Path")
        last_img_directory = str(self.parent.image_dir.get())
        last_txt_directory = str(os.path.normpath(self.parent.text_dir))
        # Image directory
        if self._verify_filepath(last_img_directory):
            self.config.set("Path", "last_img_directory", last_img_directory)
        # Text directory
        if self._verify_filepath(last_txt_directory) and last_txt_directory != ".":
            self.config.set("Path", "last_txt_directory", last_txt_directory)
        # External image editor
        self.config.set("Path", "external_image_editor_path", str(self.parent.external_image_editor_path))
        # Index and load order
        self.config.set("Path", "last_index", str(self.parent.current_index))
        self.config.set("Path", "load_order", str(self.parent.load_order_var.get()))
        self.config.set("Path", "reverse_load_order", str(self.parent.reverse_load_order_var.get()))


    def _save_window_settings(self):
        self._add_section("Window")
        self.config.set("Window", "panes_swap_ew_var", str(self.parent.panes_swap_ew_var.get()))
        self.config.set("Window", "panes_swap_ns_var", str(self.parent.panes_swap_ns_var.get()))
        self.config.set("Window", "always_on_top_var", str(self.parent.always_on_top_var.get()))


    def _save_autocomplete_settings(self):
        self._add_section("Autocomplete")
        self.config.set("Autocomplete", "csv_danbooru", str(self.parent.csv_danbooru.get()))
        self.config.set("Autocomplete", "csv_danbooru_safe", str(self.parent.csv_danbooru_safe.get()))
        self.config.set("Autocomplete", "csv_derpibooru", str(self.parent.csv_derpibooru.get()))
        self.config.set("Autocomplete", "csv_e621", str(self.parent.csv_e621.get()))
        self.config.set("Autocomplete", "csv_english_dictionary", str(self.parent.csv_english_dictionary.get()))
        self.config.set("Autocomplete", "suggestion_quantity", str(self.parent.suggestion_quantity_var.get()))
        self.config.set("Autocomplete", "use_colored_suggestions", str(self.parent.colored_suggestion_var.get()))
        self.config.set("Autocomplete", "suggestion_threshold", str(self.parent.suggestion_threshold_var.get()))
        self.config.set("Autocomplete", "last_word_match", str(self.parent.last_word_match_var.get()))


    #def _save_ONNX_settings(self):
    #    self._add_section("ONNX")
    #    self.config.set("ONNX", "ONNX_model", str(self.parent.onnx_model_var.get()))
    #    self.config.set("ONNX", "general_threshold", str(self.parent.general_threshold_var.get()))
    #    self.config.set("ONNX", "character_threshold", str(self.parent.character_threshold_var.get()))
    #    self.config.set("ONNX", "custom_exclude_tags", str(self.parent.custom_exclude_tags_var.get()))
    #    self.config.set("ONNX", "exclude_current_tags", str(self.parent.exclude_current_tags_var.get()))


    def _save_other_settings(self):
        self._add_section("Other")
        self.config.set("Other", "auto_save", str(self.parent.auto_save_var.get()))
        self.config.set("Other", "cleaning_text", str(self.parent.cleaning_text_var.get()))
        self.config.set("Other", "big_save_button", str(self.parent.big_save_button_var.get()))
        self.config.set("Other", "highlighting_duplicates", str(self.parent.highlight_selection_var.get()))
        self.config.set("Other", "truncate_stat_captions", str(self.parent.truncate_stat_captions_var.get()))
        self.config.set("Other", "process_image_stats", str(self.parent.process_image_stats_var.get()))
        self.config.set("Other", "use_mytags", str(self.parent.use_mytags_var.get()))
        self.config.set("Other", "auto_delete_blank_files", str(self.parent.auto_delete_blank_files_var.get()))
        self.config.set("Other", "thumbnails_visible", str(self.parent.thumbnails_visible.get()))
        self.config.set("Other", "edit_panel_visible", str(self.parent.edit_panel_visible_var.get()))
        self.config.set("Other", "image_quality", str(self.parent.image_quality_var.get()))
        self.config.set("Other", "font", str(self.parent.font_var.get()))
        self.config.set("Other", "font_size", str(self.parent.font_size_var.get()))
        self.config.set("Other", "list_mode", str(self.parent.list_mode_var.get()))


    def write_settings_to_file(self):
        """Writes the current settings to the configuration file."""
        with open(self.parent.app_settings_cfg, "w", encoding="utf-8") as f:
            self.config.write(f)


# --------------------------------------
# Read
# --------------------------------------
    def read_settings(self):
        """Reads the user settings from the configuration file."""
        try:
            if os.path.exists(self.parent.app_settings_cfg):
                self.config.read(self.parent.app_settings_cfg)
                if not self._is_current_version():
                    self.reset_settings()
                    return
                self._read_config_settings()
                if hasattr(self.parent, 'text_box'):
                    self.parent.show_pair()
            else:
                self.parent.prompt_first_time_setup()
        except Exception as e:
            messagebox.showerror("Error: read_settings()", f"An unexpected error occurred.\n\n{e}")


    def _is_current_version(self):
        return self.config.has_section("Version") and self.config.get("Version", "app_version", fallback=self.version) == self.version


    def _read_config_settings(self):
        if not self._read_directory_settings():
            return
        #self.read_window_settings()
        self._read_autocomplete_settings()
        #self._read_ONNX_settings()
        self._read_other_settings()


    def _read_directory_settings(self):
        last_img_directory = self.config.get("Path", "last_img_directory", fallback=None)
        if last_img_directory and os.path.exists(last_img_directory) and messagebox.askyesno("Confirmation", "Reload last directory?"):
            self.external_image_editor_path = self.config.get("Path", "external_image_editor_path", fallback="mspaint")
            self.parent.load_order_var.set(value=self.config.get("Path", "load_order", fallback="Name (default)"))
            self.parent.reverse_load_order_var.set(value=self.config.getboolean("Path", "reverse_load_order", fallback=False))
            self.parent.image_dir.set(last_img_directory)
            self.parent.set_working_directory()
            self.parent.set_text_file_path(str(self.config.get("Path", "last_txt_directory", fallback=last_img_directory)))
            last_index = int(self.config.get("Path", "last_index", fallback=1))
            num_files = len([name for name in os.listdir(last_img_directory) if os.path.isfile(os.path.join(last_img_directory, name))])
            self.parent.jump_to_image(min(last_index, num_files))
            return True
        return False


    def _read_window_settings(self):
        self.parent.panes_swap_ew_var.set(value=self.config.getboolean("Window", "panes_swap_ew_var", fallback=False))
        self.parent.panes_swap_ns_var.set(value=self.config.getboolean("Window", "panes_swap_ns_var", fallback=False))
        self.parent.swap_pane_sides(swap_state=self.parent.panes_swap_ew_var.get())
        self.parent.swap_pane_orientation(swap_state=self.parent.panes_swap_ns_var.get())
        self.parent.always_on_top_var.set(value=self.config.getboolean("Window", "always_on_top_var", fallback=False))
        self.parent.set_always_on_top()


    def _read_autocomplete_settings(self):
        self.parent.csv_danbooru.set(value=self.config.getboolean("Autocomplete", "csv_danbooru", fallback=True))
        self.parent.csv_danbooru_safe.set(value=self.config.getboolean("Autocomplete", "csv_danbooru_safe", fallback=False))
        self.parent.csv_derpibooru.set(value=self.config.getboolean("Autocomplete", "csv_derpibooru", fallback=False))
        self.parent.csv_e621.set(value=self.config.getboolean("Autocomplete", "csv_e621", fallback=False))
        self.parent.csv_english_dictionary.set(value=self.config.getboolean("Autocomplete", "csv_english_dictionary", fallback=False))
        self.parent.suggestion_quantity_var.set(value=self.config.getint("Autocomplete", "suggestion_quantity", fallback=4))
        self.parent.colored_suggestion_var.set(value=self.config.getboolean("Autocomplete", "use_colored_suggestions", fallback=True))
        self.parent.suggestion_threshold_var.set(value=self.config.get("Autocomplete", "suggestion_threshold", fallback="Normal"))
        self.parent.last_word_match_var.set(value=self.config.getboolean("Autocomplete", "last_word_match", fallback=False))
        self.parent.update_autocomplete_dictionary()


    #def _read_ONNX_settings(self):
    #    self.parent.onnx_model_var.set(value=self.config.get("ONNX", "ONNX_model", fallback=""))
    #    self.parent.general_threshold_var.set(value=self.config.getfloat("ONNX", "general_threshold", fallback=0.35))
    #    self.parent.character_threshold_var.set(value=self.config.getfloat("ONNX", "character_threshold", fallback=0.8))
    #    self.parent.custom_exclude_tags_var.set(value=self.config.get("ONNX", "custom_exclude_tags", fallback=""))
    #    self.parent.exclude_current_tags_var.set(value=self.config.getboolean("ONNX", "exclude_current_tags", fallback=False))


    def _read_other_settings(self):
        self.parent.auto_save_var.set(value=self.config.getboolean("Other", "auto_save", fallback=False))
        self.parent.cleaning_text_var.set(value=self.config.getboolean("Other", "cleaning_text", fallback=True))
        self.parent.big_save_button_var.set(value=self.config.getboolean("Other", "big_save_button", fallback=True))
        self.parent.highlight_selection_var.set(value=self.config.getboolean("Other", "highlighting_duplicates", fallback=True))
        self.parent.truncate_stat_captions_var.set(value=self.config.getboolean("Other", "truncate_stat_captions", fallback=True))
        self.parent.process_image_stats_var.set(value=self.config.getboolean("Other", "process_image_stats", fallback=False))
        self.parent.use_mytags_var.set(value=self.config.getboolean("Other", "use_mytags", fallback=True))
        self.parent.auto_delete_blank_files_var.set(value=self.config.getboolean("Other", "auto_delete_blank_files", fallback=False))
        self.parent.thumbnails_visible.set(value=self.config.getboolean("Other", "thumbnails_visible", fallback=True))
        self.parent.edit_panel_visible_var.set(value=self.config.getboolean("Other", "edit_panel_visible", fallback=False))
        self.edit_panel.toggle_edit_panel()
        self.parent.image_quality_var.set(value=self.config.get("Other", "image_quality", fallback="Normal"))
        self.parent.set_image_quality()
        self.parent.font_var.set(value=self.config.get("Other", "font", fallback="Courier New"))
        self.parent.font_size_var.set(value=self.config.getint("Other", "font_size", fallback=10))
        self.parent.text_box.config(font=(self.parent.font_var.get(), self.parent.font_size_var.get()))
        self.parent.list_mode_var.set(value=self.config.getboolean("Other", "list_mode", fallback=False))


# --------------------------------------
# Reset
# --------------------------------------
    def reset_settings(self):
        """Resets all settings to their default values."""
        if not messagebox.askokcancel("Confirm Reset", "Reset all settings to their default parameters?"):
            return
        # Path
        self.parent.set_text_file_path(str(self.parent.image_dir.get()))
        self.parent.load_order_var.set(value="Name (default)")
        self.parent.reverse_load_order_var.set(value=False)
        # Autocomplete
        self.parent.csv_danbooru.set(value=True)
        self.parent.csv_danbooru_safe.set(value=False)
        self.parent.csv_derpibooru.set(value=False)
        self.parent.csv_e621.set(value=False)
        self.parent.csv_english_dictionary.set(value=False)
        self.parent.colored_suggestion_var.set(value=True)
        self.parent.suggestion_quantity_var.set(value=4)
        self.parent.suggestion_threshold_var.set(value="Normal")
        self.parent.last_word_match_var.set(value=False)
        # ONNX
        #self.parent.onnx_model_var.set(value="")
        #self.parent.general_threshold_var.set(value=0.35)
        #self.parent.character_threshold_var.set(value=0.8)
        #self.parent.custom_exclude_tags_var.set(value="")
        #self.parent.exclude_current_tags_var.set(value=False)
        # Other
        self.parent.clear_search_and_replace_tab()
        self.parent.prefix_entry.delete(0, 'end')
        self.parent.append_entry.delete(0, 'end')
        self.parent.revert_text_image_filter(clear=True)
        self.parent.clear_highlight_tab()
        self.parent.list_mode_var.set(value=False)
        self.parent.toggle_list_mode()
        self.parent.cleaning_text_var.set(value=True)
        self.parent.auto_save_var.set(value=False)
        self.parent.toggle_save_button_height(reset=True)
        self.parent.highlight_selection_var.set(value=True)
        self.parent.highlight_all_duplicates_var.set(value=False)
        self.parent.toggle_highlight_all_duplicates()
        self.parent.truncate_stat_captions_var.set(value=True)
        self.parent.process_image_stats_var.set(value=False)
        self.parent.use_mytags_var.set(value=True)
        self.parent.auto_delete_blank_files_var.set(value=False)
        self.parent.external_image_editor_path = "mspaint"
        self.parent.image_quality_var.set(value="Normal")
        self.parent.set_image_quality()
        # Window
        self.parent.always_on_top_var.set(value=False)
        self.parent.set_always_on_top()
        self.parent.panes_swap_ew_var.set(value=False)
        self.parent.panes_swap_ns_var.set(value=False)
        self.parent.swap_pane_sides(swap_state=False)
        self.parent.swap_pane_orientation(swap_state=False)
        self.parent.setup_window()
        # Font and text_box
        if hasattr(self.parent, 'text_box'):
            self.parent.font_var.set(value="Courier New")
            self.parent.font_size_var.set(value=10)
            self.parent.size_scale.set(value=10)
            self.parent.font_size_label.config(text=f"Size: 10")
            current_text = self.parent.text_box.get("1.0", "end-1c")
            self.parent.text_box.config(font=(self.parent.default_font, self.parent.default_font_size))
        self.parent.load_pairs()
        if hasattr(self.parent, 'text_box'):
            self.parent.text_box.delete("1.0", "end")
            self.parent.text_box.insert("1.0", current_text)
        if messagebox.askyesno("Confirm Reset", "Reset 'My Tags' to default?"):
            with open(self.parent.app_settings_cfg, 'w', encoding="utf-8") as cfg_file:
                cfg_file.write("")
            self.parent.create_custom_dictionary(reset=True)
        # Extra panels
        self.parent.thumbnails_visible.set(value=True)
        self.parent.update_thumbnail_panel()
        self.parent.edit_panel_visible_var.set(value=False)
        self.edit_panel.toggle_edit_panel()
        # Title
        self.parent.sync_title_with_content()
        # Guided setup
        self.parent.prompt_first_time_setup()
