#region Imports


# Standard Library
import os
from io import BytesIO


# Standard Library - GUI
from tkinter import (
    ttk, Tk, Toplevel, messagebox,
    IntVar, StringVar, BooleanVar,
    Frame, Label, Button
)


# Third-Party Libraries
from PIL import Image, ImageSequence


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


# Custom Libraries
import main.scripts.entry_helper as EntryHelper

#endregion
#region ResizeTool


class ResizeTool:
    def __init__(self, master: 'Tk', app: 'Main', filepath, window_x, window_y, update_pair, jump_to_image):
        self.top = Toplevel(master, borderwidth=2, relief="groove")
        self.top.overrideredirect(True)
        self.top.geometry("+{}+{}".format(window_x, window_y))
        self.top.grab_set()
        self.top.focus_force()
        self.top.bind("<Escape>", self.close_window)

        self.filepath = os.path.abspath(filepath)
        self.load_image(self.filepath)

        self.supported_filetypes = (".png", ".webp", ".jpg", ".jpeg", ".jpg_large", ".jfif", ".tif", ".tiff", ".bmp", ".gif")

        self.app = app
        self.sort_key = self.app.get_file_sort_key()
        self.reverse_sort_direction_var = self.app.reverse_load_order_var.get()
        self.ImgTxt_update_pair = update_pair
        self.ImgTxt_jump_to_image = jump_to_image

        self.get_current_image_details()

        self.prev_width_percentage = None
        self.prev_height_percentage = None
        self.prev_width_pixels = None
        self.prev_height_pixels = None

        self.entry_width_var = StringVar(value=str(self.original_image_width))
        self.entry_height_var = StringVar(value=str(self.original_image_height))
        self.link_aspect_var = BooleanVar(value=True)
        self.overwrite_var = BooleanVar(value=False)
        self.scale_quality_var = IntVar(value=100)
        self.resize_condition = StringVar(value="pixels")
        self.previous_condition = "pixels"
        self.combobox_filetype_var = StringVar(value="JPG")
        self.combobox_filter_var = StringVar(value="Lanczos")

        self.entry_width_var.trace_add("write", lambda name, index, mode, string=self.entry_width_var: self.validate_entry(string))
        self.entry_height_var.trace_add("write", lambda name, index, mode, string=self.entry_height_var: self.validate_entry(string))

        self.create_interface()
        self.update_current_image_info()

        self.new_image_width = self.original_image_width
        self.new_image_height = self.original_image_height

        self.calculate_image_size()


#endregion
#region Interface Setup


    def create_interface(self):
        self.create_top_bar()
        self.create_unit_widgets()
        self.create_entry_widgets()
        self.create_quality_widgets()
        self.create_info_widgets()
        self.create_primary_buttons()


    def create_top_bar(self):
        frame_container = Frame(self.top)
        frame_container.pack(expand=True, fill="both")
        # Title Bar
        title = Label(frame_container, cursor="size", text="Resize Image", font=("", 16))
        title.pack(side="top", fill="x", padx=5, pady=5)
        title.bind("<ButtonPress-1>", self.start_drag)
        title.bind("<ButtonRelease-1>", self.stop_drag)
        title.bind("<B1-Motion>", self.dragging_window)
        # Close Button
        self.button_close = Button(frame_container, text="🞨", relief="flat", command=self.close_window)
        self.button_close.place(anchor="nw", relx=0.91, height=40, width=40)
        self.bind_widget_highlight(self.button_close, color="#C42B1C")
        separator = ttk.Separator(frame_container)
        separator.pack(side="top", fill="x")


    def create_unit_widgets(self):
        frame_radio_buttons = Frame(self.top)
        frame_radio_buttons.pack(side="top", fill="x", padx=10, pady=10)
        # Pixels
        radiobutton_pixels = ttk.Radiobutton(frame_radio_buttons, variable=self.resize_condition, value="pixels", text="Pixels", width=10, command=self.toggle_resize_condition)
        radiobutton_pixels.pack(anchor="center", side="left", expand=True, padx=5, pady=5)
        # Percentage
        radiobutton_percentage = ttk.Radiobutton(frame_radio_buttons, variable=self.resize_condition, value="percentage", text="Percentage", width=10, command=self.toggle_resize_condition)
        radiobutton_percentage.pack(anchor="center", side="left", expand=True, padx=5, pady=5)


    def create_entry_widgets(self):
        frame_width_height = Frame(self.top)
        frame_width_height.pack(side="top", fill="x", padx=10, pady=10)
        # Width
        frame_width = Frame(frame_width_height)
        frame_width.pack(side="left", fill="x", padx=10, pady=10)
        self.label_width = Label(frame_width, text="Width (px)")
        self.label_width.pack(anchor="w", side="top", padx=5, pady=5)
        self.entry_width = ttk.Entry(frame_width, textvariable=self.entry_width_var)
        self.entry_width.pack(side="top", padx=5, pady=5)
        self.entry_width.bind("<Button-1>", self.on_key_release)
        self.entry_width.bind("<KeyRelease>", self.on_key_release)
        self.entry_width.bind("<Button-3>", lambda event, entry="width": self.reset_entry(entry))
        self.entry_width.bind("<Up>", lambda event: self.adjust_entry_value(event, self.entry_width_var, True))
        self.entry_width.bind("<Down>", lambda event: self.adjust_entry_value(event, self.entry_width_var, False))
        EntryHelper.bind_helpers(self.entry_width)
        # Link Button
        frame_checkbutton = Frame(frame_width_height)
        frame_checkbutton.pack(side="left", fill="both", padx=10, pady=10)
        Label(frame_checkbutton, text="").pack(side="top")
        self.checkbutton_link_ratio = ttk.Checkbutton(frame_checkbutton, text="Locked", width=10, variable=self.link_aspect_var, command=self.on_link_button_toggle)
        self.checkbutton_link_ratio.pack(side="bottom", padx=5, pady=5)
        # Height
        frame_height = Frame(frame_width_height)
        frame_height.pack(side="left", fill="x", padx=10, pady=10)
        self.label_height = Label(frame_height, text="Height (px)")
        self.label_height.pack(anchor="w", side="top", padx=5, pady=5)
        self.entry_height = ttk.Entry(frame_height, textvariable=self.entry_height_var)
        self.entry_height.pack(side="top", padx=5, pady=5)
        self.entry_height.bind("<Button-1>", self.on_key_release)
        self.entry_height.bind("<KeyRelease>", self.on_key_release)
        self.entry_height.bind("<Button-3>", lambda event, entry="height": self.reset_entry(entry))
        self.entry_height.bind("<Up>", lambda event: self.adjust_entry_value(event, self.entry_height_var, True))
        self.entry_height.bind("<Down>", lambda event: self.adjust_entry_value(event, self.entry_height_var, False))
        EntryHelper.bind_helpers(self.entry_height)


    def create_quality_widgets(self):
        frame_quality_type = Frame(self.top)
        frame_quality_type.pack(side="top", fill="x", padx=10, pady=10)
        # Quality
        frame_quality = Frame(frame_quality_type)
        frame_quality.pack(side="left", expand=True, fill="x", padx=10, pady=10)
        frame_quality_labels = Frame(frame_quality)
        frame_quality_labels.pack(side="top", expand=True, fill="x", padx=10, pady=10)
        self.label_quality1 = Label(frame_quality_labels, text="Quality:")
        self.label_quality1.pack(side="left", pady=5)
        self.label_quality = Label(frame_quality_labels, text="100% (High)", width=12, anchor="w")
        self.label_quality.pack(side="left", pady=5)
        self.scale_quality = ttk.Scale(frame_quality, from_=10, to=100, value=100, variable=self.scale_quality_var, command=self.update_quality_label)
        self.scale_quality.pack(anchor="center", side="bottom", expand=True, fill="x", padx=5, pady=5)
        self.scale_quality.bind("<ButtonRelease-1>", self.calculate_image_size)
        # File Type
        frame_filetype = Frame(frame_quality_type)
        frame_filetype.pack(side="left", expand=True, fill="x", padx=10, pady=10)
        label_filetype = Label(frame_filetype, text="File Type", width=10)
        label_filetype.pack(side="top", padx=5, pady=5)
        self.combobox_filetype = ttk.Combobox(frame_filetype, state="readonly", width=10, textvariable=self.combobox_filetype_var, values=["JPG", "PNG", "WEBP"])
        self.combobox_filetype.pack(anchor="center", side="bottom", expand=True, padx=5, pady=5)
        self.combobox_filetype.bind("<<ComboboxSelected>>", self.update_new_filetype)
        # Filter
        frame_filter = Frame(frame_quality_type)
        frame_filter.pack(side="left", expand=True, fill="x", padx=10, pady=10)
        label_filter = Label(frame_filter, text="Method", width=10)
        label_filter.pack(side="top", padx=5, pady=5)
        combobox_filter = ttk.Combobox(frame_filter, state="readonly", width=10, textvariable=self.combobox_filter_var, values=["Lanczos", "Nearest", "Bicubic", "Hamming", "Bilinear", "Box"])
        combobox_filter.pack(anchor="center", side="bottom", expand=True, padx=5, pady=5)


    def create_info_widgets(self):
        frame_info = Frame(self.top)
        frame_info.pack(side="top", expand=True, fill="x", padx=10, pady=10)
        ttk.Separator(frame_info).pack(side="top", fill="x")
        frame_labels = Frame(frame_info)
        frame_labels.pack(side="left", expand=True, fill="x", padx=10, pady=10)
        # Current
        label_current = Label(frame_labels, text="Current:")
        label_current.pack(anchor="w", side="top", padx=5, pady=5)
        # New
        label_new = Label(frame_labels, text="New:")
        label_new.pack(anchor="w", side="top", padx=5, pady=5)
        # Dimensions
        frame_dimensions = Frame(frame_info)
        frame_dimensions.pack(side="left", expand=True, fill="x", padx=10, pady=10)
        # Current Dimensions
        self.label_current_dimensions = Label(frame_dimensions, text="0 x 0", width=20)
        self.label_current_dimensions.pack(anchor="w", side="top", padx=5, pady=5)
        # New Dimensions
        self.label_new_dimensions = Label(frame_dimensions, text=f"{self.original_image_width} x {self.original_image_height}", width=20)
        self.label_new_dimensions.pack(anchor="w", side="top", padx=5, pady=5)
        # Filesize
        frame_size = Frame(frame_info)
        frame_size.pack(side="left", expand=True, fill="x", padx=10, pady=10)
        # Current Filesize
        self.label_current_size = Label(frame_size, text="00.0 KB", width=9)
        self.label_current_size.pack(anchor="w", side="top", padx=5, pady=5)
        # New Filesize
        self.label_new_size = Label(frame_size, text="00.0 KB", width=9)
        self.label_new_size.pack(anchor="w", side="top", padx=5, pady=5)
        # Filetype
        frame_filetype = Frame(frame_info)
        frame_filetype.pack(side="left", expand=True, fill="x", padx=10, pady=10)
        # Current Filetype
        self.label_current_filetype = Label(frame_filetype, text="---", width=4)
        self.label_current_filetype.pack(anchor="w", side="top", padx=5, pady=5)
        # New Filetype
        self.label_new_filetype = Label(frame_filetype, text="JPG", width=4)
        self.label_new_filetype.pack(anchor="w", side="top", padx=5, pady=5)


    def create_primary_buttons(self):
        frame_primary_buttons = Frame(self.top)
        frame_primary_buttons.pack(side="top", fill="x")
        # Save
        button_save = ttk.Button(frame_primary_buttons, text="Resize", command=self.save_image)
        button_save.pack(side="left", expand=True, fill="x", padx=5, pady=5)
        # Cancel
        button_cancel = ttk.Button(frame_primary_buttons, text="Cancel", command=self.close_window)
        button_cancel.pack(side="left", expand=True, fill="x", padx=5, pady=5)


#endregion
#region Update interface


    def on_key_release(self, event):
        if event.widget == self.entry_width:
            self.update_aspect_ratio("width")
        elif event.widget == self.entry_height:
            self.update_aspect_ratio("height")
        self.update_new_resolution(event)
        self.calculate_image_size()


    def on_link_button_toggle(self):
        if self.link_aspect_var.get():
            self.checkbutton_link_ratio.config(text="Locked")
        else:
            self.checkbutton_link_ratio.config(text="Unlocked")
        self.update_aspect_ratio("both")
        self.update_new_resolution()


    def update_new_filetype(self, event):
        if self.combobox_filetype_var.get() in ["JPG", "WEBP"] :
            self.scale_quality.config(state="normal")
            self.label_quality1.config(state="normal")
            self.label_quality.config(state="normal")
        else:
            self.scale_quality.config(state="disabled")
            self.label_quality1.config(state="disabled")
            self.label_quality.config(state="disabled")
        self.label_new_filetype.config(text=self.combobox_filetype_var.get())
        self.calculate_image_size()


    def update_current_image_info(self):
        width = self.original_image_width
        height = self.original_image_height
        filesize = self.original_image_filesize
        filetype = self.original_image_filetype
        converted_filesize = self.convert_filesize(filesize)
        filetype = filetype.upper()[1:]
        self.label_current_dimensions.config(text=f"{width} x {height}")
        self.label_current_size.config(text=converted_filesize)
        self.label_current_filetype.config(text=filetype)
        if filetype == "GIF":
            self.combobox_filetype_var.set("GIF")
            self.combobox_filetype.config(state="disabled")
            self.scale_quality.config(state="disabled")
            self.label_quality1.config(state="disabled")
            self.label_quality.config(state="disabled")
            self.label_new_filetype.config(text="GIF")


    def update_quality_label(self, val):
        val = int(float(val))
        if val >= 80:
            val_rank = "High"
        elif val >= 50:
            val_rank = "Medium"
        else:
            val_rank = "Low"
        self.label_quality.config(text=f"{val}% ({val_rank})")


    def update_new_resolution(self, event=None):
        width = self.entry_width_var.get()
        height = self.entry_height_var.get()
        if not width.isdigit():
            width = "0"
        if not height.isdigit():
            height = "0"
        if self.resize_condition.get() == "pixels":
            self.new_image_width = int(width)
            self.new_image_height = int(height)
        elif self.resize_condition.get() == "percentage":
            self.new_image_width = round(self.original_image_width * int(width) / 100)
            self.new_image_height = round(self.original_image_height * int(height) / 100)
        self.label_new_dimensions.config(text=f"{self.new_image_width} x {self.new_image_height}")


    def toggle_resize_condition(self):
        if self.resize_condition.get() == "pixels":
            if self.previous_condition == "percentage":
                current_width = int(self.entry_width_var.get())
                current_height = int(self.entry_height_var.get())
                if self.prev_width_percentage == current_width and self.prev_height_percentage == current_height:
                    self.entry_width_var.set(self.prev_width_pixels)
                    self.entry_height_var.set(self.prev_height_pixels)
                else:
                    new_width = round((current_width / 100) * self.original_image_width)
                    new_height = round((current_height / 100) * self.original_image_height)
                    self.entry_width_var.set(str(new_width))
                    self.entry_height_var.set(str(new_height))
                    self.prev_width_pixels = str(new_width)
                    self.prev_height_pixels = str(new_height)
            self.label_width.config(text="Width (px)")
            self.label_height.config(text="Height (px)")
            self.previous_condition = "pixels"
        elif self.resize_condition.get() == "percentage":
            if self.previous_condition == "pixels":
                current_width = int(self.entry_width_var.get())
                current_height = int(self.entry_height_var.get())
                if self.prev_width_pixels == current_width and self.prev_height_pixels == current_height:
                    self.entry_width_var.set(self.prev_width_percentage)
                    self.entry_height_var.set(self.prev_height_percentage)
                else:
                    new_width = round((current_width / self.original_image_width) * 100)
                    new_height = round((current_height / self.original_image_height) * 100)
                    self.entry_width_var.set(str(new_width))
                    self.entry_height_var.set(str(new_height))
                    self.prev_width_percentage = str(new_width)
                    self.prev_height_percentage = str(new_height)
            self.label_width.config(text="Width (%)")
            self.label_height.config(text="Height (%)")
            self.previous_condition = "percentage"


    def update_aspect_ratio(self, last_edited):
        if self.link_aspect_var.get():
            width = self.entry_width_var.get()
            height = self.entry_height_var.get()
            if not width.isdigit():
                width = "0"
            if not height.isdigit():
                height = "0"
            width = int(width)
            height = int(height)
            if last_edited == "both":
                if self.resize_condition.get() == "pixels":
                    self.entry_height_var.set(str(round(width * (self.original_image_height / self.original_image_width))))
                    self.entry_width_var.set(str(width))
                elif self.resize_condition.get() == "percentage":
                    if width > height:
                        self.entry_height_var.set(str(width))
                        self.entry_width_var.set(str(width))
                    else:
                        self.entry_height_var.set(str(height))
                        self.entry_width_var.set(str(height))
            elif last_edited == "width" and width != 0:
                if self.resize_condition.get() == "pixels":
                    self.entry_height_var.set(str(round(width / (self.original_image_width / self.original_image_height))))
                elif self.resize_condition.get() == "percentage":
                    self.entry_height_var.set(str(width))
            elif last_edited == "height" and height != 0:
                if self.resize_condition.get() == "pixels":
                    self.entry_width_var.set(str(round(height * (self.original_image_width / self.original_image_height))))
                elif self.resize_condition.get() == "percentage":
                    self.entry_width_var.set(str(height))


#endregion
#region Misc


    def load_image(self, abs_filepath):
        with Image.open(abs_filepath) as img:
            self.image = img.copy()


    def get_image_index(self, directory, filename):
        filename = os.path.basename(filename)
        image_files = sorted(
            (file for file in os.listdir(directory) if file.lower().endswith(self.supported_filetypes)),
            key=self.sort_key,
            reverse=self.reverse_sort_direction_var
        )
        return image_files.index(filename) if filename in image_files else -1


    def get_current_image_details(self):
        self.original_image_width, self.original_image_height = self.image.size
        self.original_image_filesize = os.path.getsize(self.filepath)
        self.original_image_filetype = os.path.splitext(self.filepath)[1]


    def convert_filesize(self, filesize):
        if filesize < 1024:
            filesize = f"{filesize} B"
        elif filesize < 1024 * 1024:
            filesize = f"{filesize / 1024:.2f} KB"
        else:
            filesize = f"{filesize / 1024 / 1024:.2f} MB"
        return filesize


    def close_window(self, index=None, event=None):
        self.ImgTxt_update_pair()
        self.ImgTxt_jump_to_image(index)
        self.top.destroy()


#endregion
#region Entry field handling


    def validate_entry(self, string):
        value = string.get()
        if not value.isdigit() or len(value) > 5:
            string.set(''.join(filter(str.isdigit, value[:5])))


    def reset_entry(self, entry):
        if self.resize_condition.get() == "pixels":
            if entry == "width":
                self.entry_width_var.set(self.original_image_width)
                self.update_aspect_ratio("width")
            if entry == "height":
                self.entry_height_var.set(self.original_image_height)
                self.update_aspect_ratio("height")
        elif self.resize_condition.get() == "percentage":
            if entry == "width":
                self.entry_width_var.set(100)
                self.update_aspect_ratio("width")
            if entry == "height":
                self.entry_height_var.set(100)
                self.update_aspect_ratio("height")
        self.update_new_resolution()


    def adjust_entry_value(self, event, entry_var, increment):
        current_value = int(entry_var.get())
        if increment:
            entry_var.set(current_value + 1)
        elif current_value > 1:
            entry_var.set(current_value - 1)


#endregion
#region Window drag


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
#region Widget highlighting


    def bind_widget_highlight(self, widget, add=False, color=None):
        add = '+' if add else ''
        if color:
            widget.bind("<Enter>", lambda event: self.mouse_enter(event, color), add=add)
        else:
            widget.bind("<Enter>", self.mouse_enter, add=add)
        widget.bind("<Leave>", self.mouse_leave, add=add)

    def mouse_enter(self, event, color='#e5f3ff'):
        if event.widget['state'] == 'normal':
            event.widget.configure(background=color)
            event.widget.configure(foreground="white")
            event.widget.configure(text="🞫")

    def mouse_leave(self, event):
        event.widget.configure(background='SystemButtonFace')
        event.widget.configure(foreground="black")
        event.widget.configure(text="🞨")


#endregion
#region File Management


    def calculate_image_size(self, event=None):
        if self.new_image_width > 12000 or self.new_image_height > 12000:
            self.label_new_size.config(text="???")
            return
        try:
            file_type = self.combobox_filetype_var.get().lower()
            file_type = 'jpeg' if file_type == 'jpg' else file_type
            filter_method = str(self.combobox_filter_var.get()).upper()
            temp_file = BytesIO()
            if file_type == 'gif':
                frames = []
                durations = []
                for frame in ImageSequence.Iterator(self.image):
                    frame = frame.convert('RGBA').resize((self.new_image_width, self.new_image_height), getattr(Image, filter_method))
                    frames.append(frame)
                    durations.append(frame.info['duration'])
                frames[0].save(temp_file, format=file_type, save_all=True, append_images=frames[1:], duration=durations, loop=0)
            else:
                resized_image = self.image.resize((self.new_image_width, self.new_image_height), getattr(Image, filter_method))
                if file_type in ['jpeg', 'webp']:
                    resized_image.save(temp_file, format=file_type, quality=self.scale_quality_var.get())
                else:
                    resized_image.save(temp_file, format=file_type)
            image_size = temp_file.tell()
            temp_file.close()
            converted_size = self.convert_filesize(image_size)
            self.label_new_size.config(text=converted_size)
        except TypeError:
            messagebox.showerror("Error: resize_image.calculate_image_size()", "Something went wrong while processing this image.\n\nPlease try a different file type.")
        except (ValueError, PermissionError, IOError,):
            return


    def save_image(self):
        try:
            if self.new_image_width > 12000 or self.new_image_height > 12000:
                result = messagebox.askyesno("Large Output", "The selected output size is very large: > 12000.\n\nSaving the image may take longer than usual, continue?")
                if not result:
                    return
            file_type = self.combobox_filetype_var.get().lower()
            file_type = 'jpeg' if file_type == 'jpg' else file_type
            filter_method = str(self.combobox_filter_var.get()).upper()
            filename, extension = os.path.splitext(self.filepath)
            new_filepath = os.path.join(os.path.dirname(self.filepath), f"{os.path.basename(filename)}.{file_type}")
            if os.path.exists(new_filepath):
                result = messagebox.askyesno("File exists", "The file already exists.\n\nWould you like to overwrite it?")
                if not result:
                    return
            if file_type == 'gif':
                self._save_gif(filter_method, new_filepath)
            else:
                self._save_image(file_type, filter_method, new_filepath)
            index = self.get_image_index(os.path.dirname(new_filepath), new_filepath)
            self.close_window(index)
        except TypeError:
            messagebox.showerror("Error: resize_image.save_image()", "Something went wrong while processing this image.\n\nPlease try a different file type.")
        except ValueError:
            messagebox.showerror("Error: resize_image.save_image()", "Invalid values. Please enter valid digits.")
        except (PermissionError, IOError):
            messagebox.showerror("Error: resize_image.save_image()", "An error occurred while saving the image.")


    def _save_image(self, file_type, filter_method, new_filepath):
        resized_image = self.image.resize((self.new_image_width, self.new_image_height), getattr(Image, filter_method))
        if file_type in ['jpeg', 'webp']:
            resized_image.save(new_filepath, quality=self.scale_quality_var.get())
        else:
            resized_image.save(new_filepath)


    def _save_gif(self, filter_method, new_filepath):
        frames = []
        durations = []
        for frame in ImageSequence.Iterator(self.image):
            frame = frame.convert('RGBA').resize((self.new_image_width, self.new_image_height), getattr(Image, filter_method))
            frames.append(frame)
            durations.append(frame.info['duration'])
        frames[0].save(new_filepath, save_all=True, append_images=frames[1:], duration=durations, loop=0)
