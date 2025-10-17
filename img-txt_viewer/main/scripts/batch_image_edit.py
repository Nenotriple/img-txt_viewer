#region Imports

import os
import time

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from PIL import Image

from main.scripts import HelpText
from main.scripts.help_window import HelpWindow
import main.scripts.entry_helper as entry_helper
from main.scripts.scrollable_frame import ScrollableFrame
from main.scripts.image_zoom import ImageZoomWidget

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main

#endregion
#region BatchImgEdit

class BatchImgEdit:
    def __init__(self):
        self.app: 'Main' = None
        self.root: 'tk.Tk' = None
        self.working_dir = None
        self.help_window = None
        self.entry_helper = entry_helper

        self.supported_filetypes = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".jfif")
        self.previous_adjustments = {}
        self._var_to_option = {}
        self._advanced_vars = {}
        self._advanced_defaults = {}
        self.original_selected_image = None
        self._original_selected_filename = None
        self._image_preview_update_id = None
        self.image_filelist = []
        self.is_batch_running = False
        self._edited_selected_image = None
        self._active_value_entry = None

#endregion
#region Initialization & Setup

    def setup_window(self, app, root):
        self.app = app
        self.root = root
        self.working_dir = self.app.image_dir.get()
        self.help_window = HelpWindow(self.root)
        self.setup_ui()
        self.set_working_directory(self.working_dir)

    def setup_ui(self):
        self.create_primary_frame()
        self.create_directory_row()
        self.create_content_frames()
        self.create_list_frame()
        self.create_image_frame()
        self.create_options_frame()
        self.create_bottom_row()

#endregion
#region UI Creation

    def create_primary_frame(self):
        self.app.batch_img_edit_tab.grid_rowconfigure(0, weight=1)
        self.app.batch_img_edit_tab.grid_columnconfigure(0, weight=1)
        self.batch_img_edit_frame = tk.Frame(self.app.batch_img_edit_tab)
        self.batch_img_edit_frame.grid(row=0, column=0, sticky="nsew")
        self.batch_img_edit_frame.grid_rowconfigure(1, weight=1)
        self.batch_img_edit_frame.grid_columnconfigure(0, weight=1)

    def create_directory_row(self):
        top_frame = tk.Frame(self.batch_img_edit_frame)
        top_frame.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        top_frame.grid_columnconfigure(0, weight=1)

        self.entry_directory = ttk.Entry(top_frame)
        self.entry_directory.insert(0, os.path.normpath(self.working_dir) if self.working_dir else "...")
        self.entry_directory.grid(row=0, column=0, sticky="ew", padx=2)
        self.entry_directory.bind("<Return>", lambda event: self.set_working_directory(self.entry_directory.get()))
        self.entry_directory.bind("<Button-1>", lambda event: self.entry_directory.delete(0, "end") if self.entry_directory.get() == "..." else None)
        self.entry_helper.bind_helpers(self.entry_directory)

        self.browse_button = ttk.Button(top_frame, width=8, text="Browse...", command=self.set_working_directory)
        self.browse_button.grid(row=0, column=1, padx=2)

        self.open_button = ttk.Button(top_frame, width=8, text="Open", command=self.open_folder)
        self.open_button.grid(row=0, column=2, padx=2)

        self.refresh_button = ttk.Button(top_frame, width=8, text="Refresh", command=self.refresh_files)
        self.refresh_button.grid(row=0, column=3, padx=2)

        self.help_button = ttk.Button(top_frame, text="?", width=2, command=self.open_help_window)
        self.help_button.grid(row=0, column=4, padx=2)

    def create_content_frames(self):
        self.content_frame = tk.Frame(self.batch_img_edit_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1, minsize=200)
        self.content_frame.grid_columnconfigure(0, weight=0, minsize=120)
        self.content_frame.grid_columnconfigure(1, weight=999, minsize=240)
        self.content_frame.grid_columnconfigure(2, weight=1, minsize=100)

        self.left_content_frame = tk.Frame(self.content_frame)
        self.left_content_frame.grid(row=0, column=0, sticky="nsew", padx=4)

        self.middle_content_frame = tk.Frame(self.content_frame)
        self.middle_content_frame.grid(row=0, column=1, sticky="nsew")

        self.right_content_frame = tk.Frame(self.content_frame)
        self.right_content_frame.grid(row=0, column=2, sticky="nsew", padx=4)
        self.right_content_frame.configure(width=250)
        self.right_content_frame.grid_propagate(False)

    def create_list_frame(self):
        self.left_content_frame.grid_rowconfigure(1, weight=1)
        self.left_content_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(self.left_content_frame, text="Images", anchor="center").grid(row=0, column=0, columnspan=2, sticky="ew")

        self.image_listbox = tk.Listbox(self.left_content_frame, exportselection=False, selectmode="extended", width=30)
        self.image_listbox.grid(row=1, column=0, sticky="nsew")
        self.image_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        list_scroll = ttk.Scrollbar(self.left_content_frame, orient="vertical", command=self.image_listbox.yview)
        list_scroll.grid(row=1, column=1, sticky="ns")
        self.image_listbox.config(yscrollcommand=list_scroll.set)

    def create_image_frame(self):
        self.middle_content_frame.grid_rowconfigure(0, weight=1)
        self.middle_content_frame.grid_columnconfigure(0, weight=1)

        self.preview_image = ImageZoomWidget(self.middle_content_frame)
        self.preview_image.grid(row=0, column=0, sticky="nsew")
        self.preview_image.canvas.bind("<ButtonPress-3>", self.on_preview_right_press)
        self.preview_image.canvas.bind("<ButtonRelease-3>", self.on_preview_right_release)

    def create_options_frame(self):
        self.right_content_frame.grid_rowconfigure(0, weight=1)
        self.right_content_frame.grid_columnconfigure(0, weight=1)

        self.scrollable = ScrollableFrame(self.right_content_frame, layout="vertical", label="Options")
        self.scrollable.grid(row=0, column=0, sticky="nsew")
        self.scrollable.frame.configure(width=100)
        self._advanced_frames = {}

        groups = [
            ("Light", [
                ("Brightness", "brightness_var", "brightness_scale", -100, 100, 10, None),
                ("Contrast", "contrast_var", "contrast_scale", -100, 100, 10, None),
                ("AutoContrast", "autocontrast_var", "autocontrast_scale", -100, 100, 10, None),
                ("Highlights", "highlights_var", "highlights_scale", -200, 200, 10, self._create_highlights_advanced),
                ("Shadows", "shadows_var", "shadows_scale", -200, 200, 10, self._create_shadows_advanced),
            ]),
            ("Color", [
                ("Saturation", "saturation_var", "saturation_scale", -100, 100, 10, None),
                ("Vibrance", "vibrance_var", "vibrance_scale", -100, 100, 10, None),
                ("Hue", "hue_var", "hue_scale", -100, 100, 10, None),
                ("Color Temp", "color_temp_var", "color_temp_scale", -100, 100, 10, None),
            ]),
            ("Detail", [
                ("Sharpness", "sharpness_var", "sharpness_scale", -100, 100, 10, self._create_sharpness_advanced),
                ("Clarity", "clarity_var", "clarity_scale", -100, 100, 10, self._create_clarity_advanced),
            ]),
        ]

        def add_advanced_option(parent_frame, option_name, param_name, default_value, from_val, to_val, label_text=None):
            if label_text is None:
                label_text = param_name.replace("_", " ").title() + ":"

            var = tk.IntVar(value=default_value)

            if option_name not in self._advanced_vars:
                self._advanced_vars[option_name] = {}
            self._advanced_vars[option_name][param_name] = var

            if option_name not in self._advanced_defaults:
                self._advanced_defaults[option_name] = {}
            self._advanced_defaults[option_name][param_name] = default_value

            value_frame = ttk.Frame(parent_frame)
            value_frame.pack(fill="x", padx=16)
            ttk.Label(value_frame, text=label_text, font=("", 8), foreground="gray").pack(side="left", anchor="w", padx=(0, 8))

            if option_name == "Clarity" and param_name == "radius":
                radius_label_var = tk.StringVar()

                def update_radius_label(*_):
                    val = var.get()
                    radius_label_var.set("Auto" if val == 0 else str(val))

                var.trace_add("write", update_radius_label)
                update_radius_label()
                value_label = ttk.Label(value_frame, textvariable=radius_label_var, width=5, anchor="e", foreground="gray")
                value_label.pack(side="right", padx=(4, 0))
                self._make_label_clickable(value_label, var, from_val, to_val, is_special_radius=True)
            else:
                value_label = ttk.Label(value_frame, textvariable=var, width=5, anchor="e", foreground="gray")
                value_label.pack(side="right", padx=(4, 0))
                self._make_label_clickable(value_label, var, from_val, to_val)

            scale_frame = ttk.Frame(parent_frame)
            scale_frame.pack(fill="x", padx=16)

            def _advanced_scale_cmd(v):
                var.set(int(float(v)))
                var_attr = f"{option_name.lower().replace(' ', '_')}_var"
                primary_var = getattr(self, var_attr, None)
                if var.get() != 0 or (primary_var and primary_var.get() != 0):
                    self.on_option_change()

            def _reset_advanced_scale(event):
                var.set(default_value)
                var_attr = f"{option_name.lower().replace(' ', '_')}_var"
                primary_var = getattr(self, var_attr, None)
                if primary_var and primary_var.get() != 0:
                    self.on_option_change()

            adv_scale = ttk.Scale(scale_frame, from_=from_val, to_=to_val, variable=var, command=_advanced_scale_cmd)
            adv_scale.pack(fill="x", expand=True)
            adv_scale.bind("<Button-3>", _reset_advanced_scale)

        def add_scale(parent, name, var_attr, scale_attr, from_=-100, to_=100, pady=10, advanced_options=None):
            frame = ttk.Frame(parent)
            frame.pack(fill="x", pady=pady)

            top_row = ttk.Frame(frame)
            top_row.pack(fill="x", padx=4)

            ttk.Label(top_row, text=f"{name}").pack(side="left", anchor="w", padx=4)

            if advanced_options:
                toggle_btn = ttk.Button(top_row, text="+", width=1, command=lambda: self._toggle_advanced_options(name), takefocus=False)
                toggle_btn.pack(side="right", padx=2)

            var = getattr(self, var_attr)
            self._var_to_option[var_attr] = name
            value_label = ttk.Label(top_row, text="0", textvariable=var)
            value_label.pack(side="right", anchor="e", padx=4)
            self._make_label_clickable(value_label, var, from_, to_)

            def _scale_cmd(v, var=var):
                var.set(self.float_to_int(v))
                self.on_option_change()

            scale = ttk.Scale(frame, from_=from_, to_=to_, variable=var, command=_scale_cmd)
            setattr(self, scale_attr, scale)
            scale.pack(fill="x", padx=4)
            scale.bind("<Button-3>", lambda event, scale_name=name: self.reset_scale(scale_name))

            if advanced_options:
                adv_frame = ttk.Frame(frame, borderwidth=1)
                self._advanced_frames[name] = {
                    "frame": adv_frame,
                    "visible": False,
                    "toggle_btn": toggle_btn,
                }
                advanced_options(adv_frame, add_advanced_option)

        self._var_names = []
        for group_name, option_defs in groups:
            group_frame = ttk.Labelframe(self.scrollable.frame, text=group_name)
            group_frame.pack(fill="x", padx=4, pady=6)

            for item in option_defs:
                display_name, var_attr, scale_attr = item[0], item[1], item[2]
                from_, to_, pady = item[3], item[4], item[5]
                advanced_options = item[6] if len(item) > 6 else None

                setattr(self, var_attr, tk.IntVar(value=0))
                self._var_names.append(var_attr)
                add_scale(group_frame, display_name, var_attr, scale_attr, from_, to_, pady, advanced_options)

    def _toggle_advanced_options(self, option_name):
        if option_name not in self._advanced_frames:
            return

        info = self._advanced_frames[option_name]
        frame = info["frame"]
        toggle_btn = info["toggle_btn"]

        if info["visible"]:
            frame.pack_forget()
            toggle_btn.configure(text="+")
            info["visible"] = False
        else:
            frame.pack(fill="x", padx=8, pady=4)
            toggle_btn.configure(text="-")
            info["visible"] = True

    def _create_highlights_advanced(self, parent_frame, add_option):
        add_option(parent_frame, "Highlights", "threshold", 190, 1, 256)

    def _create_shadows_advanced(self, parent_frame, add_option):
        add_option(parent_frame, "Shadows", "threshold", 64, 1, 256)

    def _create_sharpness_advanced(self, parent_frame, add_option):
        add_option(parent_frame, "Sharpness", "boost", 1, 1, 4)

    def _create_clarity_advanced(self, parent_frame, add_option):
        add_option(parent_frame, "Clarity", "radius", 0, 0, 100)

    def create_bottom_row(self):
        bottom_row = ttk.Frame(self.batch_img_edit_frame)
        bottom_row.grid(row=2, column=0, sticky="ew", padx=2, pady=2)

        btn_frame = ttk.Frame(bottom_row)
        btn_frame.pack(fill="x")

        self.create_options_menu(btn_frame)

        self.button_action = ttk.Button(btn_frame, text="Apply!", command=self.process_all_images)
        self.button_action.pack(side="left", fill="x", expand=True, padx=2, pady=2)

        self.button_reset = ttk.Button(btn_frame, text="Reset", command=lambda: self.reset_scale("all"))
        self.button_reset.pack(side="left", fill="x", padx=2, pady=2)

        self.button_cancel = ttk.Button(btn_frame, width=8, state="disabled", text="Cancel", command=self.stop_batch_process)
        self.button_cancel.pack(side="left", fill="x", padx=2, pady=2)

        self.info_frame = tk.Frame(bottom_row)
        self.info_frame.pack(fill="x")

        self.total_var = tk.StringVar(value="Total: 0")
        tk.Label(self.info_frame, anchor="w", textvariable=self.total_var, relief="groove", width=15).pack(side="left", fill="both", padx=2)

        self.processed_var = tk.StringVar(value="Processed: 0")
        tk.Label(self.info_frame, anchor="w", textvariable=self.processed_var, relief="groove", width=15).pack(side="left", fill="both", padx=2)

        self.elapsed_var = tk.StringVar(value="Elapsed: ..")
        tk.Label(self.info_frame, anchor="w", textvariable=self.elapsed_var, relief="groove", width=15).pack(side="left", fill="both", padx=2)

        self.eta_var = tk.StringVar(value="ETA: ...")
        tk.Label(self.info_frame, anchor="w", textvariable=self.eta_var, relief="groove", width=15).pack(side="left", fill="both", padx=2)

        self.progress_var = tk.StringVar()
        ttk.Progressbar(self.info_frame, value=0, length=100, variable=self.progress_var).pack(side="left", fill="both", expand=True, padx=2)

    def create_options_menu(self, btn_frame):
        m_btn = ttk.Menubutton(btn_frame, text="Options")
        menu = tk.Menu(m_btn, tearoff=0)

        self.save_path_var = tk.IntVar(value=1)
        menu.add_command(label="Save To", state="disabled")
        menu.add_radiobutton(label="Subfolder", variable=self.save_path_var, value=1)
        menu.add_radiobutton(label="Same Folder", variable=self.save_path_var, value=2)
        menu.add_separator()

        self.save_format_var = tk.IntVar(value=1)
        menu.add_command(label="Save As", state="disabled")
        menu.add_radiobutton(label="Same Format", variable=self.save_format_var, value=1)
        menu.add_radiobutton(label="JPEG", variable=self.save_format_var, value=2)
        menu.add_radiobutton(label="PNG", variable=self.save_format_var, value=3)
        menu.add_separator()

        self.overwrite_mode_var = tk.IntVar(value=2)
        menu.add_command(label="Overwrite", state="disabled")
        menu.add_radiobutton(label="Always", variable=self.overwrite_mode_var, value=1)
        menu.add_radiobutton(label="On Conflict", variable=self.overwrite_mode_var, value=2)
        menu.add_radiobutton(label="Never", variable=self.overwrite_mode_var, value=3)

        m_btn.configure(menu=menu)
        m_btn.pack(side="left", padx=2, pady=2)

    def _make_label_clickable(self, label, var, from_val, to_val, is_special_radius=False):
        """Make a value label clickable to allow direct value entry."""
        def on_label_click(event):
            if self._active_value_entry is not None:
                return
            parent = label.master
            pack_info = label.pack_info()
            entry = ttk.Entry(parent, width=4, justify="right")
            self._active_value_entry = entry
            if is_special_radius:
                current = var.get()
                entry.insert(0, "0" if current == 0 else str(current))
            else:
                entry.insert(0, str(var.get()))
            label.pack_forget()
            entry.pack(**pack_info)
            entry.focus_set()
            entry.select_range(0, "end")

            def on_any_click(event):
                widget = event.widget
                if widget is not entry:
                    restore_label()

            def remove_bindings():
                try:
                    parent.unbind("<Button-1>", parent_bind_id)
                except Exception:
                    pass
                try:
                    self.root.unbind("<Button-1>", root_bind_id)
                except Exception:
                    pass

            def restore_label():
                if self._active_value_entry is None:
                    return
                remove_bindings()
                entry.pack_forget()
                label.pack(**pack_info)
                self._active_value_entry = None

            parent_bind_id = parent.bind("<Button-1>", on_any_click, add="+")
            root_bind_id = self.root.bind("<Button-1>", on_any_click, add="+")

            def on_entry_return(event):
                try:
                    value_text = entry.get().strip()
                    if is_special_radius and value_text.lower() in ("auto", "a", "0"):
                        new_value = 0
                    else:
                        new_value = self.float_to_int(value_text)
                        new_value = max(from_val, min(to_val, new_value))
                    var.set(new_value)
                    self.on_option_change()
                except ValueError:
                    pass
                restore_label()

            def on_entry_escape(event):
                restore_label()

            def on_focus_out(event):
                self.root.after(50, lambda: restore_label() if self._active_value_entry == entry else None)

            entry.bind("<Return>", on_entry_return)
            entry.bind("<KP_Enter>", on_entry_return)
            entry.bind("<Escape>", on_entry_escape)
            entry.bind("<FocusOut>", on_focus_out)

        label.bind("<Button-1>", on_label_click)
        label.configure(cursor="hand2")

#endregion
#region Event Handlers

    def on_listbox_select(self, event):
        selection = self.get_listbox_selection_idx()
        if not selection:
            return
        return self.display_selected_image(selection)

    def on_option_change(self, *args):
        self.previous_adjustments = self.get_adjustment_methods()
        if self._show_original_if_no_adjustments():
            return
        self._schedule_preview_update()
        self.processed_var.set(f"Processed: 0")
        self.elapsed_var.set("Elapsed: ..")
        self.eta_var.set("ETA: ...")
        self.set_progress(0)

    def on_preview_right_press(self, event):
        if self.original_selected_image is not None:
            self.preview_image.set_image(self.original_selected_image, keep_view=True)

    def on_preview_right_release(self, event):
        if self._show_original_if_no_adjustments():
            return
        if self._edited_selected_image is not None:
            self.preview_image.set_image(self._edited_selected_image, keep_view=True)
        elif self.original_selected_image is not None:
            adjustment_methods = self.get_adjustment_methods()
            if adjustment_methods:
                self._apply_adjustments_to_preview(adjustment_methods, self.original_selected_image)

#endregion
#region Directory & File Management

    def set_working_directory(self, path=None):
        if path is None:
            path = filedialog.askdirectory(initialdir=self.working_dir)
            if not os.path.isdir(path):
                return
            self.working_dir = path
        else:
            self.working_dir = path
        self.entry_directory.delete(0, "end")
        self.entry_directory.insert(0, os.path.normpath(self.working_dir))
        self.update_image_filelist()
        self.populate_listbox()
        self.set_listbox_selection(index=0)
        self.update_total_count()
        self.set_progress(0)

    def refresh_files(self):
        path = self.working_dir
        self.set_working_directory(path=path)
        self.set_listbox_selection(index=0)

    def open_folder(self):
        path = self.working_dir
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error: batch_image_edit.open_folder()", f"Failed to open folder: {e}")

    def update_image_filelist(self):
        self.image_filelist = []
        if not self.working_dir or not os.path.isdir(self.working_dir):
            return
        if self.working_dir == self.app.image_dir.get():
            self.image_filelist = list(self.app.image_files)
            return
        else:
            for fname in os.listdir(self.working_dir):
                fpath = os.path.join(self.working_dir, fname)
                if os.path.isfile(fpath) and fname.lower().endswith(self.supported_filetypes):
                    self.image_filelist.append(fname)
        self.populate_listbox()

    def populate_listbox(self):
        self.image_listbox.delete(0, "end")
        for file in self.image_filelist:
            file = os.path.basename(file)
            if file.lower().endswith(self.supported_filetypes):
                self.image_listbox.insert("end", file)

    def set_listbox_selection(self, index=0):
        if self.image_listbox.size() > 0:
            self.image_listbox.selection_set(index)
            self.display_selected_image()

    def get_listbox_selection_idx(self):
        return [int(i) for i in self.image_listbox.curselection()]

#endregion
#region Image Display & Preview

    def display_selected_image(self, selection=None):
        if not selection:
            selection = self.get_listbox_selection_idx()
        try:
            idx = selection[0]
            filename = self.image_listbox.get(idx)
            return self._update_original_image(filename)
        except Exception as e:
            messagebox.showerror("Error: batch_image_edit.display_selected_image()", f"Unexpected error loading image: {e}")

    def get_pil_image(self, filepath):
        if not filepath:
            return None
        if not os.path.isabs(filepath) and self.working_dir:
            candidate = os.path.join(self.working_dir, filepath)
            if os.path.isfile(candidate):
                filepath = candidate
        if not os.path.isfile(filepath):
            return None
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in self.supported_filetypes:
            return None
        try:
            img = Image.open(filepath)
            img = img.convert("RGBA")
            return img
        except Exception as e:
            messagebox.showerror("Error: batch_image_edit.get_pil_image()", f"Failed to open image: {e}")
            return None

    def _update_original_image(self, filename):
        if os.path.isabs(filename):
            fullpath = filename
        else:
            fullpath = os.path.join(self.working_dir, filename) if self.working_dir else filename
        img = self.get_pil_image(filename)
        if img is None:
            return
        self.preview_image.set_image(img)
        if fullpath != self._original_selected_filename:
            self.original_selected_image = img.copy()
            self._original_selected_filename = fullpath
            self._schedule_preview_update()

    def _schedule_preview_update(self, delay=150):
        self._cancel_scheduled_preview()
        try:
            self._image_preview_update_id = self.root.after(delay, self._perform_scheduled_preview)
        except Exception:
            self._image_preview_update_id = None

    def _perform_scheduled_preview(self):
        self._image_preview_update_id = None
        adjustment_methods = self.get_adjustment_methods()
        if self._show_original_if_no_adjustments():
            return
        if not adjustment_methods:
            return
        image = self.original_selected_image
        if image is None:
            return
        self._apply_adjustments_to_preview(adjustment_methods, image)

    def _apply_adjustments_to_preview(self, adjustment_methods, image):
        try:
            edited_image = self.app.edit_panel.public_image_edit(image, adjustment_methods)
            self.preview_image.set_image(edited_image, keep_view=True)
            self._edited_selected_image = edited_image.copy()
        except Exception as e:
            messagebox.showerror("Error: batch_image_edit._apply_adjustments_to_preview()", f"Failed to update preview: {e}")

    def _cancel_scheduled_preview(self):
        if getattr(self, "_image_preview_update_id", None):
            try:
                self.root.after_cancel(self._image_preview_update_id)
            except Exception:
                pass
            self._image_preview_update_id = None

    def _show_original_if_no_adjustments(self):
        if all(getattr(self, var_attr).get() == 0 for var_attr in self._var_to_option):
            if self.original_selected_image is not None:
                self.preview_image.set_image(self.original_selected_image, keep_view=True)
            return True
        return False

#endregion
#region Adjustment Controls

    def get_adjustment_methods(self):
        adjustments = {}
        mapping = self._get_option_mapping()
        for var_attr, option_name in mapping.items():
            var = getattr(self, var_attr, None)
            if var is None:
                continue
            try:
                value = self.float_to_int(var.get())
            except Exception:
                continue
            if value != 0:
                adjustments[option_name] = {"value": value}
                if option_name in self._advanced_vars:
                    for param_name, param_var in self._advanced_vars[option_name].items():
                        try:
                            param_value = self.float_to_int(param_var.get())
                            adjustments[option_name][param_name] = param_value
                        except Exception:
                            pass
        return adjustments

    def set_adjustment_methods(self, adjustments):
        mapping = self._get_option_mapping()
        option_to_var = {v: k for k, v in mapping.items()}
        for option_name, params in adjustments.items():
            var_attr = option_to_var.get(option_name)
            if var_attr:
                self._set_option_var(var_attr, params.get("value", 0))
        self.on_option_change()

    def reset_scale(self, scale_name):
        if scale_name == "all":
            var_names = getattr(self, "_var_names", None)
            if var_names:
                for var_attr in var_names:
                    self._set_option_var(var_attr, 0)
            for option_name, params in self._advanced_vars.items():
                for param_name, param_var in params.items():
                    default_val = self._advanced_defaults.get(option_name, {}).get(param_name, 0)
                    param_var.set(default_val)
            self._edited_selected_image = None
            self.on_option_change()
            return
        var_attr = f"{scale_name.lower().replace(' ', '_')}_var"
        if hasattr(self, var_attr):
            self._set_option_var(var_attr, 0)
            if scale_name in self._advanced_vars:
                for param_name, param_var in self._advanced_vars[scale_name].items():
                    default_val = self._advanced_defaults.get(scale_name, {}).get(param_name, 0)
                    param_var.set(default_val)
            self._edited_selected_image = None
            self.on_option_change()

    def _get_option_mapping(self):
        if getattr(self, "_var_to_option", None):
            return self._var_to_option
        return {attr: attr[:-4].replace("_", " ").title() for attr in dir(self) if attr.endswith("_var")}

    def _set_option_var(self, var_attr, value):
        var = getattr(self, var_attr, None)
        if var is not None:
            try:
                var.set(self.float_to_int(value))
            except Exception:
                pass

#endregion
#region Batch Processing

    def process_all_images(self):
        self.set_progress(0)
        adjustments = self.get_adjustment_methods()
        if not adjustments:
            messagebox.showinfo("Info", "No adjustments selected.\n\nAt least one adjustment must be set.")
            return
        result = self._validate_dir_and_confirm()
        if not result:
            return
        _, files, output_dir = result
        files_to_process = []
        for fname in files:
            src = self._resolve_full_src(fname)
            if not self._should_skip_file(src):
                files_to_process.append(fname)
        if not files_to_process:
            messagebox.showinfo("Info", "No valid images to process (all files missing or unsupported).")
            return
        self.set_progress(10)
        self.button_cancel.config(state="normal")
        exclude = [self.button_cancel, self.info_frame]
        self.set_widget_states(self.app.batch_img_edit_tab, enabled=False, exclude=exclude)
        saved = 0
        errors = []
        processed = 0
        total_files = len(files_to_process)
        self.is_batch_running = True
        self._start_timer()
        self._initialize_timer_display()
        try:
            for fname in files_to_process:
                if not self.is_batch_running:
                    break
                src = self._resolve_full_src(fname)
                ok, err = self._process_and_save(src, output_dir, adjustments)
                if ok:
                    saved += 1
                elif err:
                    errors.append(err)
                processed += 1
                self.processed_var.set(f"Processed: {processed}")
                self._update_timer_display(processed, total_files)
                progress_val = int((processed / total_files) * 100) if total_files else 100
                self.set_progress(progress_val)
        finally:
            self._finalize_timer_display(processed, total_files)
            self.set_widget_states(self.app.batch_img_edit_tab, enabled=True)
            self.button_cancel.config(state="disabled")
            self.is_batch_running = False
        summary = f"Saved: {saved}\nErrors: {len(errors)}"
        messagebox.showinfo("Batch Image Edit - Complete", summary)

    def _validate_dir_and_confirm(self):
        if not self.working_dir or not os.path.isdir(self.working_dir):
            messagebox.showinfo("Info", "Working directory is not set or does not exist.")
            return False
        save_path_mode = self.save_path_var.get()
        overwrite_mode = self.overwrite_mode_var.get()
        if save_path_mode == 1:
            output_dir = os.path.join(self.working_dir, "Edited Images")
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                messagebox.showinfo("Info", f"Failed to create output folder: {e}")
                return False
        else:
            output_dir = self.working_dir
        files = list(self.image_filelist) or []
        if not files:
            messagebox.showinfo("Info", "No images to process.")
            return False
        overwrite_labels = {1: "Always", 2: "On Conflict", 3: "Never"}
        overwrite_text = overwrite_labels.get(overwrite_mode, "Unknown")
        if save_path_mode == 1:
            msg = f"Apply adjustments to {len(files)} images and save to:\n\n{output_dir}\n\nOverwrite mode: {overwrite_text}"
        else:
            if overwrite_mode == 1:
                msg = f"WARNING: This will REMOVE {len(files)} original files and save edited versions!\n\nOverwrite mode: {overwrite_text}\n\nAre you sure?"
            else:
                msg = f"Apply adjustments to {len(files)} images in the same folder.\n\nOverwrite mode: {overwrite_text}"
        if not messagebox.askyesno("Confirm Batch Edit", msg):
            return False
        return True, files, output_dir

    def _process_and_save(self, src, output_dir, adjustments):
        try:
            img = self.get_pil_image(src)
            if img is None:
                return False, f"{src}: failed to open"
            self.set_progress(50)
            edited = self.app.edit_panel.public_image_edit(img, adjustments)
            self.set_progress(75)
            base = os.path.basename(src)
            save_path = os.path.join(output_dir, base)
            ext = os.path.splitext(src)[1].lower()
            save_format = self.save_format_var.get()
            if save_format == 2:
                new_ext = ".jpg"
            elif save_format == 3:
                new_ext = ".png"
            else:
                new_ext = ext
            if new_ext != ext:
                save_path = os.path.splitext(save_path)[0] + new_ext
            overwrite_mode = self.overwrite_mode_var.get()
            save_path_var = self.save_path_var.get()
            if overwrite_mode == 1:
                if save_path_var == 1 and os.path.exists(src):
                    os.remove(src)
            elif overwrite_mode == 3:
                save_path = self._get_unique_filename(save_path)
            if new_ext in (".jpg", ".jpeg", ".jfif"):
                prepared = self.app.edit_panel._prepare_image_for_save(edited, new_ext)
                prepared.save(save_path, format="JPEG", quality=100)
            elif new_ext == ".png":
                prepared = self.app.edit_panel._prepare_image_for_save(edited, new_ext)
                prepared.save(save_path, format="PNG")
            else:
                prepared = self.app.edit_panel._prepare_image_for_save(edited, new_ext)
                prepared.save(save_path)
            self.set_progress(90)
            return True, None
        except Exception as e:
            return False, f"{src}: {e}"

    def _resolve_full_src(self, fname):
        if os.path.isabs(fname):
            return fname
        if self.working_dir:
            return os.path.join(self.working_dir, fname)
        return fname

    def _should_skip_file(self, src):
        if not os.path.isfile(src):
            return True
        ext = os.path.splitext(src)[1].lower()
        return ext not in self.supported_filetypes

    def _get_unique_filename(self, filepath):
        if not os.path.exists(filepath):
            return filepath
        directory = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)
        counter = 1
        while True:
            new_name = f"{name}_{counter}{ext}"
            new_path = os.path.join(directory, new_name)
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def stop_batch_process(self):
        if self.is_batch_running:
            self.is_batch_running = False
            self.button_cancel.config(state="disabled")

#endregion
#region Widget State Management

    def set_widget_states(self, container, enabled=True, exclude=None):
        exclude_list = self._normalize_exclude_list(exclude)
        children = container.winfo_children()
        for child in children:
            if self._should_exclude_widget(child, exclude_list):
                continue
            self._set_widget_state(child, enabled)
            self.set_widget_states(child, enabled=enabled, exclude=exclude_list)

    def _set_widget_state(self, widget, enabled):
        try:
            state_val = "normal" if enabled else "disabled"
            widget.configure(state=state_val)
        except Exception:
            pass

    def _normalize_exclude_list(self, exclude):
        if exclude is None:
            exclude_list = []
        elif isinstance(exclude, (list, tuple, set)):
            exclude_list = list(exclude)
        else:
            exclude_list = [exclude]
        return self._expand_exclude_list(exclude_list)

    def _expand_exclude_list(self, exclude_list):
        expanded = []
        for item in exclude_list:
            if isinstance(item, str):
                expanded.append(item)
                continue
            try:
                children = getattr(item, "winfo_children", None)
                if callable(children):
                    expanded.extend(self._collect_widget_and_children(item))
                else:
                    expanded.append(item)
            except Exception:
                expanded.append(item)
        return expanded

    def _collect_widget_and_children(self, widget):
        collected = [widget]
        try:
            for child in widget.winfo_children():
                collected.extend(self._collect_widget_and_children(child))
        except Exception:
            pass
        return collected

    def _widget_matches_exclude(self, widget, exclude_item):
        if widget is exclude_item:
            return True
        if isinstance(exclude_item, str):
            try:
                if str(widget) == exclude_item or widget.winfo_name() == exclude_item:
                    return True
            except Exception:
                pass
        return False

    def _should_exclude_widget(self, widget, exclude_list):
        if not exclude_list:
            return False
        for it in exclude_list:
            if self._widget_matches_exclude(widget, it):
                return True
        return False

#endregion
#region Timing & Progress

    def _start_timer(self):
        self._start_time = time.time()

    def _elapsed_seconds(self):
        return int(time.time() - getattr(self, "_start_time", time.time()))

    def _compute_eta_seconds(self, processed, total):
        if processed <= 0:
            return 0
        elapsed = self._elapsed_seconds()
        avg_per = elapsed / processed
        remaining = max(0, total - processed)
        return int(avg_per * remaining)

    def _format_hhmmss(self, seconds):
        return time.strftime("%H:%M:%S", time.gmtime(max(0, int(seconds))))

    def _initialize_timer_display(self):
        self.elapsed_var.set("Elapsed: 00:00:00")
        self.eta_var.set("ETA: 00:00:00")

    def _update_timer_display(self, processed, total):
        elapsed = self._elapsed_seconds()
        eta = self._compute_eta_seconds(processed, total)
        self.elapsed_var.set(f"Elapsed: {self._format_hhmmss(elapsed)}")
        self.eta_var.set(f"ETA: {self._format_hhmmss(eta)}")

    def _finalize_timer_display(self, processed, total):
        elapsed = self._elapsed_seconds()
        self.elapsed_var.set(f"Elapsed: {self._format_hhmmss(elapsed)}")
        if processed >= total:
            self.eta_var.set("ETA: 00:00:00")

    def set_progress(self, value=0):
        self.progress_var.set(value)
        self.root.update()

    def update_total_count(self):
        total = len(self.image_filelist) if self.image_filelist else 0
        self.total_var.set(f"Total: {total}")

#endregion
#region Utility Methods

    def float_to_int(self, value):
        try:
            return int(float(value))
        except ValueError:
            return 0

    def open_help_window(self):
        help_text = HelpText.BATCH_IMAGE_EDIT_HELP
        self.help_window.open_window(geometry="450x700", help_text=help_text)

#endregion
