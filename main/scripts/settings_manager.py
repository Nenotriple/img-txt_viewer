"""This module contains the SettingsManager class, which is responsible for saving and loading user settings."""


#endregion
################################################################################################################################################
#region Imports


# Standard Library
import os
import traceback
import configparser


# Standard Library - GUI
from tkinter import ttk, Toplevel, messagebox, StringVar, BooleanVar, Frame, Label


#endregion
################################################################################################################################################
#region CLS SettingsManager


class SettingsManager:
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root
        self.version = self.parent.app_version

        self.config = configparser.ConfigParser()


#endregion
################################################################################################################################################
#region Save


    def save_settings(self):
        """Saves the current user settings to a file."""
        try:
            self._read_existing_settings()
            self._save_version_settings()
            self._save_path_settings()
            self._save_window_settings()
            self._save_autocomplete_settings()
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
        self.config.set("Other", "thumbnail_width", str(self.parent.thumbnail_width.get()))
        self.config.set("Other", "edit_panel_visible", str(self.parent.edit_panel_visible_var.get()))
        self.config.set("Other", "image_quality", str(self.parent.image_quality_var.get()))
        self.config.set("Other", "font", str(self.parent.font_var.get()))
        self.config.set("Other", "font_size", str(self.parent.font_size_var.get()))
        self.config.set("Other", "list_mode", str(self.parent.list_mode_var.get()))


    def write_settings_to_file(self):
        """Writes the current settings to the configuration file."""
        with open(self.parent.app_settings_cfg, "w", encoding="utf-8") as f:
            self.config.write(f)


#endregion
################################################################################################################################################
#region Read


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
                self.prompt_first_time_setup()
        except Exception as e:
            error_message = traceback.format_exc()
            if messagebox.askokcancel("Error: read_settings()", f"An unexpected error occurred.\n\n{e}\n\n{error_message}\n\nPress OK to copy the error message to the clipboard."):
                self.root.clipboard_clear()
                self.root.clipboard_append(error_message)
                self.root.update()


    def _is_current_version(self):
        return self.config.has_section("Version") and self.config.get("Version", "app_version", fallback=self.version) == self.version


    def _read_config_settings(self):
        self._read_directory_settings()
        self._read_autocomplete_settings()
        self._read_other_settings()


    def _read_directory_settings(self):
        last_img_directory = self.config.get("Path", "last_img_directory", fallback=None)
        if not last_img_directory or not os.path.exists(last_img_directory) or not messagebox.askyesno("Confirmation", "Reload last directory?"):
            return
        self.external_image_editor_path = self.config.get("Path", "external_image_editor_path", fallback="mspaint")
        self.parent.load_order_var.set(value=self.config.get("Path", "load_order", fallback="Name (default)"))
        self.parent.reverse_load_order_var.set(value=self.config.getboolean("Path", "reverse_load_order", fallback=False))
        self.parent.image_dir.set(last_img_directory)
        self.parent.set_working_directory(silent=True)
        self.parent.set_text_file_path(str(self.config.get("Path", "last_txt_directory", fallback=last_img_directory)), silent=True)
        last_index = int(self.config.get("Path", "last_index", fallback=1))
        num_files = len([name for name in os.listdir(last_img_directory) if os.path.isfile(os.path.join(last_img_directory, name))])
        self.parent.jump_to_image(min(last_index, num_files))


    def _read_autocomplete_settings(self):
        self.parent.csv_danbooru.set(value=self.config.getboolean("Autocomplete", "csv_danbooru", fallback=False))
        self.parent.csv_danbooru_safe.set(value=self.config.getboolean("Autocomplete", "csv_danbooru_safe", fallback=False))
        self.parent.csv_derpibooru.set(value=self.config.getboolean("Autocomplete", "csv_derpibooru", fallback=False))
        self.parent.csv_e621.set(value=self.config.getboolean("Autocomplete", "csv_e621", fallback=False))
        self.parent.csv_english_dictionary.set(value=self.config.getboolean("Autocomplete", "csv_english_dictionary", fallback=False))
        self.parent.suggestion_quantity_var.set(value=self.config.getint("Autocomplete", "suggestion_quantity", fallback=4))
        self.parent.colored_suggestion_var.set(value=self.config.getboolean("Autocomplete", "use_colored_suggestions", fallback=True))
        self.parent.suggestion_threshold_var.set(value=self.config.get("Autocomplete", "suggestion_threshold", fallback="Normal"))
        self.parent.last_word_match_var.set(value=self.config.getboolean("Autocomplete", "last_word_match", fallback=False))
        self.parent.autocomplete.update_autocomplete_dictionary()


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
        self.parent.thumbnail_width.set(value=self.config.getint("Other", "thumbnail_width", fallback=50))
        self.parent.edit_panel_visible_var.set(value=self.config.getboolean("Other", "edit_panel_visible", fallback=False))
        self.parent.edit_panel.toggle_edit_panel()
        self.parent.image_quality_var.set(value=self.config.get("Other", "image_quality", fallback="Normal"))
        self.parent.set_image_quality()
        self.parent.font_var.set(value=self.config.get("Other", "font", fallback="Courier New"))
        self.parent.font_size_var.set(value=self.config.getint("Other", "font_size", fallback=10))
        if hasattr(self.parent, 'text_box'):
            self.parent.text_box.config(font=(self.parent.font_var.get(), self.parent.font_size_var.get()))
        self.parent.list_mode_var.set(value=self.config.getboolean("Other", "list_mode", fallback=False))


#endregion
################################################################################################################################################
#region Reset


    def reset_settings(self):
        """Resets all settings to their default values."""
        if not messagebox.askokcancel("Confirm Reset", "Reset all settings to their default parameters?"):
            return
        # Path
        self.parent.set_text_file_path(str(self.parent.image_dir.get()))
        self.parent.load_order_var.set(value="Name (default)")
        self.parent.reverse_load_order_var.set(value=False)
        # Autocomplete
        self.parent.csv_danbooru.set(value=False)
        self.parent.csv_danbooru_safe.set(value=False)
        self.parent.csv_derpibooru.set(value=False)
        self.parent.csv_e621.set(value=False)
        self.parent.csv_english_dictionary.set(value=False)
        self.parent.colored_suggestion_var.set(value=True)
        self.parent.suggestion_quantity_var.set(value=4)
        self.parent.suggestion_threshold_var.set(value="Normal")
        self.parent.last_word_match_var.set(value=False)
        # ONNX
        self.parent.text_controller.auto_insert_mode_var.set(value="disable")
        self.parent.text_controller.batch_interrogate_images_var.set(value=False)
        self.parent.text_controller.auto_tag_general_threshold_spinbox.set(value=0.35)
        self.parent.text_controller.auto_tag_character_threshold_spinbox.set(value=0.8)
        self.parent.text_controller.auto_tag_max_tags_spinbox.set(value=40)
        self.parent.onnx_tagger.keep_underscore.set(value=False)
        self.parent.onnx_tagger.keep_escape_character.set(value=True)
        self.parent.text_controller.excluded_tags_entry.delete(0, 'end')
        self.parent.text_controller.auto_exclude_tags_var.set(value=False)
        self.parent.text_controller.keep_tags_entry.delete(0, 'end')
        self.parent.text_controller.replace_tags_entry.delete(0, 'end')
        self.parent.text_controller.replace_with_tags_entry.delete(0, 'end')
        # Other
        self.parent.text_controller.clear_search_and_replace_tab()
        self.parent.text_controller.prefix_entry.delete(0, 'end')
        self.parent.text_controller.append_entry.delete(0, 'end')
        self.parent.text_controller.revert_text_image_filter(clear=True, silent=False)
        self.parent.text_controller.clear_highlight_tab()
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
        self.parent.big_save_button_var.set(value=True)
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
            self.parent.text_controller.size_scale.set(value=10)
            self.parent.text_controller.font_size_label.config(text=f"Size: 10")
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
        self.parent.thumbnail_width.set(value=50)
        self.parent.update_thumbnail_panel()
        self.parent.edit_panel_visible_var.set(value=False)
        self.parent.edit_panel.toggle_edit_panel()
        # Title
        self.parent.sync_title_with_content()
        # Guided setup
        self.prompt_first_time_setup()


#endregion
################################################################################################################################################
#region - Setup


    def prompt_first_time_setup(self):
        dictionary_vars = {
            "English Dictionary": BooleanVar(value=True),
            "Danbooru": BooleanVar(),
            "Danbooru (Safe)": BooleanVar(),
            "e621": BooleanVar(),
            "Derpibooru": BooleanVar()
        }
        last_word_match_var = StringVar(value="Match Last Word")
        match_modes = {"Match Whole String": False, "Match Last Word": True}

        def save_and_continue(close=False, back=False):
            self.parent.csv_english_dictionary.set(dictionary_vars["English Dictionary"].get())
            self.parent.csv_danbooru.set(dictionary_vars["Danbooru"].get())
            self.parent.csv_danbooru_safe.set(dictionary_vars["Danbooru (Safe)"].get())
            self.parent.csv_e621.set(dictionary_vars["e621"].get())
            self.parent.csv_derpibooru.set(dictionary_vars["Derpibooru"].get())
            self.parent.last_word_match_var.set(match_modes.get(last_word_match_var.get(), False))
            if close:
                save_and_close()
            elif back:
                clear_widgets()
                create_dictionary_selection_widgets()
                setup_window.geometry("400x250")
            else:
                self.save_settings()
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
            for header, description, value in options:
                ttk.Radiobutton(setup_window, text=header, variable=last_word_match_var, value=value).pack(pady=5)
                Label(setup_window, text=description).pack(pady=5)
            ttk.Separator(setup_window, orient="horizontal").pack(fill="x", padx=5, pady=5)
            ttk.Button(setup_window, text="Back", width=10, command=lambda: save_and_continue(back=True)).pack(side="left", anchor="w", pady=5, padx=10)
            ttk.Button(setup_window, text="Done", width=10, command=lambda: save_and_continue(close=True)).pack(side="right", anchor="e", pady=5, padx=10)

        def save_and_close():
            self.save_settings()
            setup_window.destroy()
            self.parent.autocomplete.update_autocomplete_dictionary()

        def create_setup_window():
            setup_window = Toplevel(self.parent.root)
            setup_window.title("Dictionary Setup")
            setup_window.iconphoto(False, self.parent.blank_image)
            window_width, window_height = 400, 250
            position_right = self.root.winfo_screenwidth() // 2 - window_width // 2
            position_top = self.root.winfo_screenheight() // 2 - window_height // 2
            setup_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
            setup_window.resizable(False, False)
            setup_window.grab_set()
            setup_window.protocol("WM_DELETE_WINDOW", save_and_close)
            return setup_window

        def create_dictionary_selection_widgets():
            def toggle_danbooru_safe(*args):
                if dictionary_vars["Danbooru"].get():
                    danbooru_safe_checkbutton.config(state="disabled")
                else:
                    danbooru_safe_checkbutton.config(state="normal")

            def toggle_danbooru(*args):
                if dictionary_vars["Danbooru (Safe)"].get():
                    danbooru_checkbutton.config(state="disabled")
                else:
                    danbooru_checkbutton.config(state="normal")

            # Widgets
            Label(setup_window, text="Please select your preferred autocomplete dictionaries").pack(pady=5)
            ttk.Separator(setup_window, orient="horizontal").pack(fill="x", padx=5, pady=5)
            # Centering frame vertically
            frame_container = Frame(setup_window)
            frame_container.pack(expand=True, fill="both")
            frame = Frame(frame_container)
            frame.pack(padx=5, pady=5, expand=True)
            frame.rowconfigure(0, weight=1)
            # First row (centered)
            frame_top = Frame(frame)
            frame_top.grid(row=0, column=0, columnspan=3)
            ttk.Checkbutton(frame_top, text="English Dictionary", variable=dictionary_vars["English Dictionary"]).pack(side="left", padx=5, pady=5)
            danbooru_safe_checkbutton = ttk.Checkbutton(frame_top, text="Danbooru (Safe)", variable=dictionary_vars["Danbooru (Safe)"])
            danbooru_safe_checkbutton.pack(side="left", padx=5, pady=5)
            dictionary_vars["Danbooru (Safe)"].trace_add("write", toggle_danbooru)
            # Second row (filled)
            danbooru_checkbutton = ttk.Checkbutton(frame, text="Danbooru", variable=dictionary_vars["Danbooru"])
            danbooru_checkbutton.grid(row=1, column=0, padx=5, pady=5)
            dictionary_vars["Danbooru"].trace_add("write", toggle_danbooru_safe)
            ttk.Checkbutton(frame, text="e621", variable=dictionary_vars["e621"]).grid(row=1, column=1, padx=5, pady=5)
            ttk.Checkbutton(frame, text="Derpibooru", variable=dictionary_vars["Derpibooru"]).grid(row=1, column=2, padx=5, pady=5)
            # Third row (centered)
            ttk.Separator(setup_window, orient="horizontal").pack(fill="x", padx=5, pady=5)
            Label(setup_window, text="The autocomplete dictionaries and settings can be changed at any time.").pack(pady=5)
            ttk.Button(setup_window, text="Next", width=10, command=save_and_continue).pack(side="bottom", anchor="e", pady=5, padx=10)
        setup_window = create_setup_window()
        create_dictionary_selection_widgets()


#endregion
