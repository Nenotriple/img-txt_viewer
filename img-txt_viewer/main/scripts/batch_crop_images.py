#region Imports


# Standard Library
import os
import shutil
import threading


# Standard Library - GUI
from tkinter import (
    ttk, Toplevel, messagebox,
    StringVar,
    Frame, Label, Button,
)


# Third-Party Libraries
from PIL import Image


# Custom Libraries
import main.scripts.entry_helper as EntryHelper
from main.scripts import custom_simpledialog


#endregion
#region BatchCrop


class BatchCrop:
    def __init__(self, master, filepath, total_images, window_x, window_y):
        self.filepath = filepath
        self.total_images = total_images
        self.supported_formats = {".jpg", ".jpeg", ".png", ".jfif", ".jpg_large", ".bmp", ".webp"}
        self.top = Toplevel(master, borderwidth=2, relief="groove")
        self.top.overrideredirect("true")
        self.top.geometry("+{}+{}".format(window_x, window_y))
        self.top.bind("<Escape>", self.close_window)
        self.top.grab_set()
        self.top.focus_force()

        self.style = ttk.Style()
        self.style.configure("Anchor.TButton", padding=5)
        self.style.configure("Selected.Anchor.TButton", padding=5, background="#0078D4")
        self.selected_anchor = "Center"

        self.create_interface()


#endregion
#region Create Interface


    def create_interface(self):
        self._create_title()
        self._create_dimension_input()
        self._create_anchor_buttons()
        self._create_primary_buttons()
        self._create_progress_bar()


    def _create_title(self):
        self.frame_container = Frame(self.top)
        self.frame_container.pack(expand=True, fill="both")
        title = Label(self.frame_container, cursor="size", text="Batch Crop", font=("", 16))
        title.pack(fill="x", padx=5)
        title.bind("<ButtonPress-1>", self.start_drag)
        title.bind("<ButtonRelease-1>", self.stop_drag)
        title.bind("<B1-Motion>", self.dragging_window)
        self.button_close = Button(self.frame_container, text="🞨", relief="flat", command=self.close_window)
        self.button_close.place(anchor="nw", relx=0.92, height=38, width=38, x=-15, y=-5)
        self.bind_widget_highlight(self.button_close, color="#C42B1C")
        separator = ttk.Separator(self.frame_container)
        separator.pack(fill="x")


    def _create_dimension_input(self):
        self.frame_width_height = Frame(self.top)
        self.frame_width_height.pack(fill="x")
        # Width Entry
        self.frame_width = Frame(self.frame_width_height)
        self.frame_width.pack(side="left", fill="x", padx=10, pady=10)
        self.label_width = Label(self.frame_width, text="Width (px)")
        self.label_width.pack(fill="x", side="top", padx=5)
        self.entry_width_var = StringVar(value="1024")
        self.entry_width = ttk.Spinbox(self.frame_width, from_=1, to=20000, textvariable=self.entry_width_var, width=16)
        self.entry_width.pack(padx=5)
        self.entry_width.bind("<Return>", self.process_images)
        EntryHelper.bind_helpers(self.entry_width)
        # Height Entry
        self.frame_height = Frame(self.frame_width_height)
        self.frame_height.pack(side="left", fill="x", padx=10, pady=10)
        self.label_height = Label(self.frame_height, text="Height (px)")
        self.label_height.pack(fill="x", side="top", padx=5)
        self.entry_height_var = StringVar(value="1024")
        self.entry_height = ttk.Spinbox(self.frame_height, from_=1, to=20000, textvariable=self.entry_height_var, width=16)
        self.entry_height.pack(padx=5)
        self.entry_height.bind("<Return>", self.process_images)
        EntryHelper.bind_helpers(self.entry_height)


    def _create_anchor_buttons(self):
        self.frame_anchor = Frame(self.top)
        self.frame_anchor.pack(pady=10)
        self.label_anchor = Label(self.frame_anchor, text="Crop Anchor")
        self.label_anchor.pack(fill="x", padx=5, pady=(0, 5))
        self.anchor_buttons = {}
        self.anchor_grid = Frame(self.frame_anchor)
        self.anchor_grid.pack()
        anchor_config = [
            ("North-West", "↖", 0, 0),
            ("North", "↑", 0, 1),
            ("North-East", "↗", 0, 2),
            ("West", "←", 1, 0),
            ("Center", "•", 1, 1),
            ("East", "→", 1, 2),
            ("South-West", "↙", 2, 0),
            ("South", "↓", 2, 1),
            ("South-East", "↘", 2, 2)
        ]
        for anchor_name, symbol, row, col in anchor_config:
            btn = ttk.Button(
                self.anchor_grid,
                text=symbol,
                style="Anchor.TButton" if anchor_name != "Center" else "Selected.Anchor.TButton",
                width=3,
                command=lambda a=anchor_name: self.select_anchor(a)
            )
            btn.grid(row=row, column=col, padx=1, pady=1)
            self.anchor_buttons[anchor_name] = btn


    def _create_primary_buttons(self):
        self.frame_primary_buttons = Frame(self.top)
        self.frame_primary_buttons.pack(fill="x", pady=10)
        # Crop Button
        self.button_crop = ttk.Button(self.frame_primary_buttons, text="Crop", command=self.process_images)
        self.button_crop.pack(side="left", expand=True, fill="x", padx=5)
        # Cancel Button
        self.button_cancel = ttk.Button(self.frame_primary_buttons, text="Cancel", command=self.close_window)
        self.button_cancel.pack(side="left", expand=True, fill="x", padx=5)


    def _create_progress_bar(self):
        ttk.Separator(self.top).pack(fill="x")
        self.frame_progress = Frame(self.top)
        self.frame_progress.pack(fill="x", padx=5, pady=5)
        self.progress_var = StringVar(value=f"0/{self.total_images}")
        self.progress_label = Label(self.frame_progress, textvariable=self.progress_var)
        self.progress_label.pack(side="right")
        self.progressbar = ttk.Progressbar(self.frame_progress, orient="horizontal", mode="determinate")
        self.progressbar.pack(side="left", fill="x", expand=True)


#endregion
#region Primary Functions


    def resize_image(self, image, resolution):
        width, height = image.size
        new_width, new_height = resolution
        if width < new_width or height < new_height:
            aspect_ratio = width / height
            if aspect_ratio > (new_width / new_height):
                new_width = int(new_height * aspect_ratio)
            else:
                new_height = int(new_width / aspect_ratio)
            image = image.resize((new_width, new_height), Image.LANCZOS)
        return image


    def crop_image(self, image, resolution, anchor='Center'):
        width, height = image.size
        new_width, new_height = resolution
        if anchor == 'Center':
            left = (width - new_width) / 2
            top = (height - new_height) / 2
        elif anchor == 'North':
            left = (width - new_width) / 2
            top = 0
        elif anchor == 'South':
            left = (width - new_width) / 2
            top = height - new_height
        elif anchor == 'West':
            left = 0
            top = (height - new_height) / 2
        elif anchor == 'East':
            left = width - new_width
            top = (height - new_height) / 2
        elif anchor == 'North-West':
            left = 0
            top = 0
        elif anchor == 'North-East':
            left = width - new_width
            top = 0
        elif anchor == 'South-West':
            left = 0
            top = height - new_height
        elif anchor == 'South-East':
            left = width - new_width
            top = height - new_height
        else:
            raise ValueError(f"Invalid anchor point: {anchor}")
        right = left + new_width
        bottom = top + new_height
        return image.crop((left, top, right, bottom))


    def copy_related_text_files(self):
        new_directory = os.path.join(self.filepath, 'cropped_images')
        for filename in os.listdir(self.filepath):
            if filename.endswith(".txt"):
                basename = os.path.splitext(filename)[0]
                for image_filename in os.listdir(new_directory):
                    if image_filename.startswith(basename):
                        new_basename = os.path.splitext(image_filename)[0]
                        new_txt_filename = f"{new_basename}.txt"
                        shutil.copy(os.path.join(self.filepath, filename), os.path.join(new_directory, new_txt_filename))


    def process_images(self, event=None):
        try:
            width_str = self.entry_width_var.get().strip()
            height_str = self.entry_height_var.get().strip()
            if not width_str.isdigit() or not height_str.isdigit():
                raise ValueError
            width = int(width_str)
            height = int(height_str)
            if width <= 0 or height <= 0:
                raise ValueError
            resolution = (width, height)
        except ValueError:
            messagebox.showerror("Error: batch_crop_images.process_images()", "Invalid values. Please enter positive integer digits for width and height.")
            return
        files_to_process = []
        for filename in os.listdir(self.filepath):
            fullpath = os.path.join(self.filepath, filename)
            if not os.path.isfile(fullpath):
                continue
            lower_name = filename.lower()
            if any(lower_name.endswith(fmt) for fmt in self.supported_formats):
                files_to_process.append(filename)
        if not files_to_process:
            messagebox.showinfo("No Images", "No supported image files were found to process.")
            return
        if not messagebox.askyesno("Confirm Batch Crop", f"This will crop {len(files_to_process)} image(s) to {resolution[0]}x{resolution[1]}.\n\nContinue?"):
            return
        new_directory = os.path.join(self.filepath, 'cropped_images')
        os.makedirs(new_directory, exist_ok=True)
        total = len(files_to_process)
        self.progressbar['maximum'] = total
        self.progressbar['value'] = 0
        self.progress_var.set(f"0/{total}")
        self._set_ui_state("disabled")
        thread = threading.Thread(target=self._process_images_worker, args=(files_to_process, resolution, new_directory), daemon=True)
        thread.start()


    def _process_images_worker(self, files_to_process, resolution, new_directory):
        processed = 0
        errors = []
        for filename in files_to_process:
            fullpath = os.path.join(self.filepath, filename)
            try:
                with Image.open(fullpath) as image:
                    resized_image = self.resize_image(image, resolution)
                    cropped_image = self.crop_image(resized_image, resolution, self.selected_anchor)
                    if cropped_image.mode != 'RGB':
                        cropped_image = cropped_image.convert('RGB')
                    out_name = f'{os.path.splitext(filename)[0]}_{resolution[0]}x{resolution[1]}.jpg'
                    out_path = os.path.join(new_directory, out_name)
                    if os.path.exists(out_path):
                        os.remove(out_path)
                    cropped_image.save(out_path, format='JPEG', quality=100)
                    processed += 1
            except Exception as e:
                errors.append(f"{filename}: {e}")
            self.top.after(0, self._update_progress, processed, len(files_to_process))
        # Copy related txt files and finalize on main thread to avoid race conditions
        self.top.after(0, self.copy_related_text_files)
        self.top.after(0, self._on_processing_finished, processed, errors, new_directory)


    def _update_progress(self, processed, total):
        self.progressbar['value'] = processed
        self.progress_var.set(f"{processed}/{total}")


    def _on_processing_finished(self, processed, errors, new_directory):
        if processed == 0:
            messagebox.showinfo("No Images", "No supported image files were found to process.")
            self._set_ui_state("normal")
            return
        result = messagebox.askyesno("Crop Successful", f"Cropped {processed} image(s).\n\nOutput path:\n{new_directory}\n\nOpen output path?")
        if result:
            try:
                os.startfile(new_directory)
            except Exception:
                pass
        if errors:
            messagebox.showwarning("Some files skipped", f"{len(errors)} file(s) were skipped due to errors.")
        self._set_ui_state("normal")
        self.close_window()


    def _set_ui_state(self, state):
        # state: "disabled" or "normal"
        widgets = [self.entry_width, self.entry_height, self.button_crop, self.button_cancel, self.button_close]
        for w in widgets:
            try:
                w['state'] = state
            except Exception:
                pass
        # Also update anchor buttons
        for btn in self.anchor_buttons.values():
            try:
                btn['state'] = state
            except Exception:
                pass


#endregion
#region Window drag bar setup


    def start_drag(self, event):
        self.x = event.x
        self.y = event.y


    def stop_drag(self, event):
        self.x = None
        self.y = None


    def dragging_window(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        x = self.top.winfo_x() + dx
        y = self.top.winfo_y() + dy
        self.top.geometry(f"+{x}+{y}")


#endregion
#region Widget highlight setup


    def bind_widget_highlight(self, widget, add=False, color=None):
        add = '+' if add else ''
        if color:
            widget.bind("<Enter>", lambda event: self.mouse_enter(event, color), add=add)
        else:
            widget.bind("<Enter>", self.mouse_enter, add=add)
        widget.bind("<Leave>", self.mouse_leave, add=add)


    def mouse_enter(self, event, color="#e5f3ff"):
        if event.widget['state'] == 'normal':
            event.widget.configure(background=color)
            event.widget.configure(foreground="white")
            event.widget.configure(text="🞫")


    def mouse_leave(self, event):
        event.widget.configure(background='SystemButtonFace')
        event.widget.configure(foreground="black")
        event.widget.configure(text="🞨")


    def select_anchor(self, anchor_name):
        self.anchor_buttons[self.selected_anchor].configure(style="Anchor.TButton")
        self.selected_anchor = anchor_name
        self.anchor_buttons[anchor_name].configure(style="Selected.Anchor.TButton")


#endregion
#region Misc


    def close_window(self, event=None):
        self.top.destroy()
