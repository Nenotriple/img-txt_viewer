#region Imports


# Standard Library
import os


# Standard Library - GUI
from tkinter import ttk, Tk, messagebox, Frame, Label, BooleanVar, TclError


# Third-Party Libraries
import numpy
from TkToolTip.TkToolTip import TkToolTip as Tip
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region EditPanel


class EditPanel:
    def __init__(self, parent: 'Main', root: 'Tk'):
        self.parent = parent
        self.root = root

        # Initialize Variables
        self.slider_value_dict = {"Brightness": 0, "Contrast": 0, "AutoContrast": 0, "Highlights": 0, "Shadows": 0, "Saturation": 0, "Sharpness": 0, "Hue": 0, "Color Temperature": 0}
        self.edit_last_slider_dict = {}
        self.edit_is_reverted_var = False
        self.edit_cumulative_var = BooleanVar(value=False)


#endregion
#region Create Widgets


    def toggle_edit_panel(self):
        if not self.parent.edit_panel_visible_var.get():
            if hasattr(self.parent, 'edit_image_panel') and self.parent.edit_image_panel.winfo_exists():
                self.parent.edit_image_panel.grid_remove()
            if hasattr(self, 'highlights_spinbox_frame') and self.highlights_spinbox_frame.winfo_exists():
                self.highlights_spinbox_frame.grid_remove()
            if hasattr(self, 'shadows_spinbox_frame') and self.shadows_spinbox_frame.winfo_exists():
                self.shadows_spinbox_frame.grid_remove()
            if hasattr(self, 'sharpness_spinbox_frame') and self.sharpness_spinbox_frame.winfo_exists():
                self.sharpness_spinbox_frame.grid_remove()
        else:
            self.parent.edit_image_panel.grid()
            self.create_edit_panel_widgets()
            if self.parent.image_file.lower().endswith('.gif'):
                self.toggle_edit_panel_widgets("disabled")
            else:
                self.toggle_edit_panel_widgets("normal")
        self.parent.refresh_image()


    def create_edit_panel_widgets(self):
        # Edit Mode Combobox
        self.edit_combobox = ttk.Combobox(self.parent.edit_image_panel, values=["Brightness", "Contrast", "AutoContrast", "Highlights", "Shadows", "Saturation", "Sharpness", "Hue", "Color Temperature"], width=18, state="readonly")
        self.edit_combobox.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.edit_combobox.set("Brightness")
        self.edit_combobox.bind("<<ComboboxSelected>>", self.update_slider_value)
        # Edit Slider
        self.edit_slider = ttk.Scale(self.parent.edit_image_panel, from_=-100, to=100, orient="horizontal", command=self.update_edit_value)
        self.edit_slider.grid(row=0, column=1, pady=5, sticky="ew")
        self.edit_slider.bind("<MouseWheel>", self.adjust_slider_with_mouse_wheel)
        self.parent.edit_image_panel.columnconfigure(1, weight=1)
        # Edit Value Label
        self.edit_value_label = Label(self.parent.edit_image_panel, text="0", width=3)
        self.edit_value_label.grid(row=0, column=2, pady=5, sticky="ew")
        # Cumulative Edit Checkbutton
        self.cumulative_edit_checkbutton = ttk.Checkbutton(self.parent.edit_image_panel, variable=self.edit_cumulative_var, command=self.apply_image_edit)
        self.cumulative_edit_checkbutton.grid(row=0, column=3, pady=5, sticky="ew")
        Tip.create(widget=self.cumulative_edit_checkbutton, text="If enabled, all edits will be done cumulatively; otherwise, only the selected option will be used.", show_delay=25, wraplength=200)
        # Revert Button
        self.edit_revert_image_button = ttk.Button(self.parent.edit_image_panel, text="Revert", width=7, command=self.revert_image_edit)
        self.edit_revert_image_button.grid(row=0, column=4, pady=5, sticky="ew")
        self.edit_revert_image_button.bind("<Button-3>", self._reset_edit)
        Tip.create(widget=self.edit_revert_image_button, text="Cancel changes and refresh the displayed image.\nRight-Click to reset the edit panel.")
        # Save Button
        self.edit_save_image_button = ttk.Button(self.parent.edit_image_panel, text="Save", width=7, command=self.save_image_edit)
        self.edit_save_image_button.grid(row=0, column=5, padx=(0,5), pady=5, sticky="ew")
        Tip.create(widget=self.edit_save_image_button, text="Save the current changes.\nOptionally overwrite the current image.")
        # Spinbox Frame - Highlights
        self.highlights_spinbox_frame = ttk.Frame(self.parent.edit_image_panel)
        self.highlights_spinbox_frame.grid(row=1, column=0, columnspan=2, pady=(0,5), sticky="ew")
        # Threshold
        self.highlights_threshold_label = ttk.Label(self.highlights_spinbox_frame, text="Threshold:")
        self.highlights_threshold_label.grid(row=0, column=0, padx=5, sticky="w")
        Tip.create(widget=self.highlights_threshold_label, text="From 1 to 256\nLower values affect more pixels", show_delay=25)
        self.highlights_threshold_spinbox = ttk.Spinbox(self.highlights_spinbox_frame, from_=1, to=256, increment=8, width=5, command=self.apply_image_edit)
        self.highlights_threshold_spinbox.grid(row=0, column=1, padx=5, sticky="ew")
        self.highlights_threshold_spinbox.set(128)
        self.highlights_threshold_spinbox.bind("<KeyRelease>", self.apply_image_edit)
        # Blur Radius
        self.highlights_blur_radius_label = ttk.Label(self.highlights_spinbox_frame, text="Blur Radius:")
        self.highlights_blur_radius_label.grid(row=0, column=2, padx=5, sticky="w")
        Tip.create(widget=self.highlights_blur_radius_label, text="From 0 to 10\nHigher values increase the blur effect", show_delay=25)
        self.highlights_blur_radius_spinbox = ttk.Spinbox(self.highlights_spinbox_frame, from_=0, to=10, width=5, command=self.apply_image_edit)
        self.highlights_blur_radius_spinbox.grid(row=0, column=3, padx=5, sticky="ew")
        self.highlights_blur_radius_spinbox.set(0)
        self.highlights_blur_radius_spinbox.bind("<KeyRelease>", self.apply_image_edit)
        # Spinbox Frame - Shadows
        self.shadows_spinbox_frame = ttk.Frame(self.parent.edit_image_panel)
        self.shadows_spinbox_frame.grid(row=1, column=0, columnspan=2, pady=(0,5), sticky="ew")
        # Threshold
        self.shadows_threshold_label = ttk.Label(self.shadows_spinbox_frame, text="Threshold:")
        self.shadows_threshold_label.grid(row=0, column=0, padx=5, sticky="w")
        Tip.create(widget=self.shadows_threshold_label, text="From 1 to 256\nHigher values affect more pixels", show_delay=25)
        self.shadows_threshold_spinbox = ttk.Spinbox(self.shadows_spinbox_frame, from_=1, to=256, increment=8, width=5, command=self.apply_image_edit)
        self.shadows_threshold_spinbox.grid(row=0, column=1, padx=5, sticky="ew")
        self.shadows_threshold_spinbox.set(128)
        self.shadows_threshold_spinbox.bind("<KeyRelease>", self.apply_image_edit)
        # Blur Radius
        self.shadows_blur_radius_label = ttk.Label(self.shadows_spinbox_frame, text="Blur Radius:")
        self.shadows_blur_radius_label.grid(row=0, column=2, padx=5, sticky="w")
        Tip.create(widget=self.shadows_blur_radius_label, text="From 0 to 10\nHigher values increase the blur effect", show_delay=25)
        self.shadows_blur_radius_spinbox = ttk.Spinbox(self.shadows_spinbox_frame, from_=0, to=10, width=5, command=self.apply_image_edit)
        self.shadows_blur_radius_spinbox.grid(row=0, column=3, padx=5, sticky="ew")
        self.shadows_blur_radius_spinbox.set(0)
        self.shadows_blur_radius_spinbox.bind("<KeyRelease>", self.apply_image_edit)
        # Spinbox Frame - Sharpness
        self.sharpness_spinbox_frame = ttk.Frame(self.parent.edit_image_panel)
        self.sharpness_spinbox_frame.grid(row=1, column=0, columnspan=2, pady=(0,5), sticky="ew")
        # Boost
        self.sharpness_boost_label = ttk.Label(self.sharpness_spinbox_frame, text="Boost:")
        self.sharpness_boost_label.grid(row=0, column=0, padx=5, sticky="w")
        Tip.create(widget=self.sharpness_boost_label, text="From 1 to 5\nHigher values add additional sharpening passes", show_delay=25)
        self.sharpness_boost_spinbox = ttk.Spinbox(self.sharpness_spinbox_frame, from_=1, to=5, width=5, command=self.apply_image_edit)
        self.sharpness_boost_spinbox.grid(row=0, column=1, padx=5, sticky="ew")
        self.sharpness_boost_spinbox.set(1)
        self.sharpness_boost_spinbox.bind("<KeyRelease>", self.apply_image_edit)
        # Hide the spinbox frame
        self.highlights_spinbox_frame.grid_remove()
        self.shadows_spinbox_frame.grid_remove()
        self.sharpness_spinbox_frame.grid_remove()


#endregion
#region UI Helpers


    def update_slider_value(self, event):
        current_option = self.edit_combobox.get()
        is_rgb = self.parent.current_image.mode == "RGB"
        rgb_required_options = ["AutoContrast", "Hue", "Color Temperature"]
        if current_option in rgb_required_options and not is_rgb:
            messagebox.showwarning("Unsupported Color Mode", f"{current_option} adjustment only supports images in RGB color mode!\n\nImage Color Mode: {self.parent.current_image.mode}\n\nAdjustments will be ignored.")
            return
        self.edit_slider.set(self.slider_value_dict[current_option])
        self.edit_value_label.config(text=str(self.slider_value_dict[current_option]))
        if current_option == "Highlights":
            self.shadows_spinbox_frame.grid_remove()
            self.sharpness_spinbox_frame.grid_remove()
            self.highlights_spinbox_frame.grid()
        elif current_option == "Shadows":
            self.highlights_spinbox_frame.grid_remove()
            self.sharpness_spinbox_frame.grid_remove()
            self.shadows_spinbox_frame.grid()
        elif current_option == "Sharpness":
            self.highlights_spinbox_frame.grid_remove()
            self.shadows_spinbox_frame.grid_remove()
            self.sharpness_spinbox_frame.grid()
        else:
            self.shadows_spinbox_frame.grid_remove()
            self.highlights_spinbox_frame.grid_remove()
            self.sharpness_spinbox_frame.grid_remove()


    def update_edit_value(self, value):
        value = int(float(value))
        self.edit_value_label.config(text=value)
        current_option = self.edit_combobox.get()
        self.slider_value_dict[current_option] = value
        self.apply_image_edit()


    def adjust_slider_with_mouse_wheel(self, event):
        current_value = self.edit_slider.get()
        new_value = current_value + (event.delta / 120) * (self.edit_slider.cget('to') - self.edit_slider.cget('from')) / 100
        self.edit_slider.set(new_value)
        self.update_edit_value(new_value)


    def toggle_edit_panel_widgets(self, state, event=None):
        def set_widget_state(frame, state):
            for widget in frame.winfo_children():
                try:
                    if isinstance(widget, ttk.Combobox) and state == "normal":
                        widget.config(state="readonly")
                    else:
                        widget.config(state=state)
                except TclError:
                    pass
                if isinstance(widget, Frame) or isinstance(widget, ttk.Frame):
                    set_widget_state(widget, state)

        set_widget_state(self.parent.edit_image_panel, state)


    def validate_spinbox_value(self, spinbox: 'ttk.Spinbox', min_value=0, max_value=1, integer=True, float=False):
        if integer and float:
            raise ValueError("validate_spinbox_value() - 'integer' and 'float' cannot be True at the same time!")
        try:
            value = spinbox.get() or min_value
            if integer:
                value = int(value)
            elif float:
                value = float(value)
            value = max(min_value, min(max_value, value))
        except ValueError:
            value = min_value
        spinbox.delete(0, "end")
        spinbox.insert(0, value)
        return value


    def _reset_edit(self, event=None):
        self.edit_is_reverted_var = False
        self.edit_revert_image_button.config(text="Revert")
        for option in self.slider_value_dict:
            self.slider_value_dict[option] = 0
        self.edit_last_slider_dict = self.slider_value_dict.copy()
        self.edit_slider.set(0)
        self.edit_value_label.config(text="0")
        self.highlights_threshold_spinbox.set(128)
        self.highlights_blur_radius_spinbox.set(0)
        self.shadows_threshold_spinbox.set(128)
        self.shadows_blur_radius_spinbox.set(0)
        self.sharpness_boost_spinbox.set(1)
        self.parent.refresh_image()


    def update_edited_image(self):
        display_width = self.parent.primary_display_image.winfo_width()
        display_height = self.parent.primary_display_image.winfo_height()
        self.parent.current_image, new_width, new_height = self.parent.resize_and_scale_image(self.parent.current_image, display_width, display_height, None)
        self.parent.current_image_tk = ImageTk.PhotoImage(self.parent.current_image)
        self.parent.primary_display_image.config(image=self.parent.current_image_tk)
        self.parent.primary_display_image.image = self.parent.current_image_tk


#endregion
#region Primary Functions


# --------------------------------------
# Edit
# --------------------------------------
    def apply_image_edit(self, event=None):
        if hasattr(self, 'apply_image_edit_id'):
            self.root.after_cancel(self.apply_image_edit_id)
        self.apply_image_edit_id = self.root.after(50, self._apply_image_edit)


    def _apply_image_edit(self):
        self.parent.current_image = self.parent.original_image.copy()
        is_rgb = self.parent.current_image.mode == "RGB"
        adjustment_methods = {
            "Brightness": self.adjust_brightness,
            "Contrast": self.adjust_contrast,
            "AutoContrast": self.adjust_autocontrast if is_rgb else None,
            "Highlights": self.adjust_highlights,
            "Shadows": self.adjust_shadows,
            "Saturation": self.adjust_saturation,
            "Sharpness": self.adjust_sharpness,
            "Hue": self.adjust_hue if is_rgb else None,
            "Color Temperature": self.adjust_color_temperature if is_rgb else None
        }
        if self.edit_cumulative_var.get():
            for option, value in self.slider_value_dict.items():
                if option in adjustment_methods and adjustment_methods[option] and value != 0:
                    adjustment_methods[option](value, image_type="display")
        else:
            option = self.edit_combobox.get()
            value = self.slider_value_dict.get(option)
            if option in adjustment_methods and adjustment_methods[option] and value != 0:
                adjustment_methods[option](value, image_type="display")
        self.update_edited_image()


    def edit_image(self, value, enhancer_class, image_type="display", image=None):
        factor = (value + 100) / 100.0
        if image_type == "display":
            enhancer_display = enhancer_class(self.parent.current_image)
            self.parent.current_image = enhancer_display.enhance(factor)
        elif image_type == "original" and image:
            enhancer_original = enhancer_class(image)
            return enhancer_original.enhance(factor)
        return image


# --------------------------------------
# Save
# --------------------------------------
    def save_image_edit(self):
        if all(value == 0 for value in self.slider_value_dict.values()):
            messagebox.showinfo("No Changes", "No changes to save.")
            return
        if not messagebox.askyesno("Save Image", "Do you want to save the edited image?"):
            return
        original_filepath = self.parent.image_files[self.parent.current_index]
        with Image.open(original_filepath) as original_image:
            is_rgb = original_image.mode == "RGB"
            adjustment_methods = {
                "Brightness": self.adjust_brightness,
                "Contrast": self.adjust_contrast,
                "AutoContrast": self.adjust_autocontrast if is_rgb else None,
                "Highlights": self.adjust_highlights,
                "Shadows": self.adjust_shadows,
                "Saturation": self.adjust_saturation,
                "Sharpness": self.adjust_sharpness,
                "Hue": self.adjust_hue if is_rgb else None,
                "Color Temperature": self.adjust_color_temperature if is_rgb else None
            }
            if self.edit_cumulative_var.get():
                for option, value in self.slider_value_dict.items():
                    if option in adjustment_methods and adjustment_methods[option]:
                        original_image = adjustment_methods[option](value, image_type="original", image=original_image)
            else:
                option = self.edit_combobox.get()
                value = self.slider_value_dict.get(option)
                if option in adjustment_methods and adjustment_methods[option]:
                    original_image = adjustment_methods[option](value, image_type="original", image=original_image)
            directory, filename = os.path.split(original_filepath)
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_edit{ext}"
            new_filepath = os.path.join(directory, new_filename)
            original_image.save(new_filepath)
        self.parent.refresh_file_lists()
        messagebox.showinfo("Image Saved", f"Image saved as {new_filename}")


# --------------------------------------
# Undo/Redo
# --------------------------------------
    def revert_image_edit(self):
        if self.edit_is_reverted_var:
            self.edit_revert_image_button.config(text="Revert")
            self.slider_value_dict.update(self.edit_last_slider_dict)
            for option, value in self.slider_value_dict.items():
                if value != 0:
                    self.edit_combobox.set(option)
                    self.edit_slider.set(value)
                    self.edit_value_label.config(text=str(value))
                    self.apply_image_edit()
            self.edit_is_reverted_var = False
        else:
            self.edit_revert_image_button.config(text="Restore")
            self.edit_last_slider_dict = {option: value for option, value in self.slider_value_dict.items() if value != 0}
            self.parent.refresh_image()
            for option in self.slider_value_dict:
                self.slider_value_dict[option] = 0
            self.edit_slider.set(0)
            self.edit_value_label.config(text="0")
            self.edit_is_reverted_var = True


#endregion
#region Image Functions


# --------------------------------------
# Brightness
# --------------------------------------
    def adjust_brightness(self, value, image_type="display", image=None):
        return self.edit_image(value, ImageEnhance.Brightness, image_type=image_type, image=image)


# --------------------------------------
# Contrast
# --------------------------------------
    def adjust_contrast(self, value, image_type="display", image=None):
        return self.edit_image(value, ImageEnhance.Contrast, image_type=image_type, image=image)


# --------------------------------------
# Saturation
# --------------------------------------
    def adjust_saturation(self, value, image_type="display", image=None):
        return self.edit_image(value, ImageEnhance.Color, image_type=image_type, image=image)


# --------------------------------------
# Sharpness
# --------------------------------------
    def adjust_sharpness(self, value, image_type="display", image=None, boost=None):
        if boost is None:
            boost = self.validate_spinbox_value(self.sharpness_boost_spinbox, min_value=1, max_value=5, integer=True)
        for _ in range(boost):
            image = self.edit_image(value, ImageEnhance.Sharpness, image_type=image_type, image=image)
        return image


# --------------------------------------
# AutoContrast
# --------------------------------------
    def adjust_autocontrast(self, value=None, image_type="display", image=None):
        if value is not None and value <= 0:
            return image
        iterations = max(1, (value - 1) // 20)
        if image_type == "display":
            for i in range(iterations):
                self.parent.current_image = ImageOps.autocontrast(self.parent.current_image)
                if value > 20:
                    enhancer = ImageEnhance.Contrast(self.parent.current_image)
                    self.parent.current_image = enhancer.enhance(1.025)
        elif image_type == "original" and image:
            for i in range(iterations):
                image = ImageOps.autocontrast(image)
                if value > 20:
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(1.025)
            return image
        return image


# --------------------------------------
# Highlights and Shadows
# --------------------------------------
    def adjust_highlights(self, value, image_type="display", image=None):
        old_min, old_max = -100, 100
        new_min, new_max = -30, 30
        value = ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
        factor = (value + 100) / 100.0
        threshold = self.validate_spinbox_value(self.highlights_threshold_spinbox, min_value=1, max_value=256, integer=True)
        blur_radius = self.validate_spinbox_value(self.highlights_blur_radius_spinbox, min_value=0, max_value=100, integer=True)
        if image_type == "display":
            mask = self.create_gradient_mask(self.parent.current_image, threshold, blur_radius, invert=True)
            self.parent.current_image = Image.composite(self.parent.current_image, ImageEnhance.Brightness(self.parent.current_image).enhance(factor), mask)
        elif image_type == "original" and image:
            mask = self.create_gradient_mask(image, threshold, blur_radius, invert=True)
            return Image.composite(image, ImageEnhance.Brightness(image).enhance(factor), mask)
        return image


    def adjust_shadows(self, value, image_type="display", image=None):
        factor = (value + 100) / 100.0
        threshold = self.validate_spinbox_value(self.shadows_threshold_spinbox, min_value=1, max_value=256, integer=True)
        blur_radius = self.validate_spinbox_value(self.shadows_blur_radius_spinbox, min_value=0, max_value=100, integer=True)
        if image_type == "display":
            mask = self.create_gradient_mask(self.parent.current_image, threshold, blur_radius)
            self.parent.current_image = Image.composite(self.parent.current_image, ImageEnhance.Brightness(self.parent.current_image).enhance(factor), mask)
        elif image_type == "original" and image:
            mask = self.create_gradient_mask(image, threshold, blur_radius)
            return Image.composite(image, ImageEnhance.Brightness(image).enhance(factor), mask)
        return image


    def create_gradient_mask(self, image, threshold, blur_radius, invert=False):
        def sigmoid(x):
            return 1 / (1 + numpy.exp(-x))
        grayscale = ImageOps.grayscale(image)
        gradient = numpy.array(grayscale).astype(numpy.float32)
        gradient = (gradient - threshold) / 256.0
        gradient = sigmoid(gradient * 10)
        gradient = (gradient * 256).astype(numpy.uint8)
        mask = Image.fromarray(gradient)
        if invert:
            mask = ImageOps.invert(mask)
        blurred_mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        return blurred_mask


# --------------------------------------
# Hue
# --------------------------------------
    def adjust_hue(self, value, image_type="display", image=None):
        factor = (value + 100) / 100.0
        if image_type == "display":
            hsv_image = self.parent.current_image.convert('HSV')
            channels = list(hsv_image.split())
            channels[0] = channels[0].point(lambda p: (p + factor * 256) % 256)
            self.parent.current_image = Image.merge('HSV', channels).convert('RGB')
        elif image_type == "original" and image:
            hsv_image = image.convert('HSV')
            channels = list(hsv_image.split())
            channels[0] = channels[0].point(lambda p: (p + factor * 256) % 256)
            return Image.merge('HSV', channels).convert('RGB')
        return image


# --------------------------------------
# Color Temperature
# --------------------------------------
    def adjust_color_temperature(self, value, image_type="display", image=None):
        factor = value / 100.0
        def _adjust_color_temperature(image, adjustment_factor):
            red_channel, green_channel, blue_channel = image.split()
            red_channel = red_channel.point(lambda intensity: intensity * (1 + 0.2 * adjustment_factor))
            blue_channel = blue_channel.point(lambda intensity: intensity * (1 - 0.2 * adjustment_factor))
            return Image.merge('RGB', (red_channel, green_channel, blue_channel))
        if image_type == "display":
            self.parent.current_image = _adjust_color_temperature(self.parent.current_image, factor)
        elif image_type == "original" and image:
            return _adjust_color_temperature(image, factor)
        return image
