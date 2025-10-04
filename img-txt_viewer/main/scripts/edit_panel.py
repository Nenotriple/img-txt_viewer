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
from typing import TYPE_CHECKING, Optional, Any, Dict, Union
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region EditPanel


class EditPanel:
    def __init__(self, app: 'Main', root: 'Tk') -> None:
        self.app = app
        self.root = root

        # Initialize Variables
        self.slider_value_dict: Dict[str, int] = {
            "Brightness": 0,
            "Contrast": 0,
            "AutoContrast": 0,
            "Highlights": 0,
            "Shadows": 0,
            "Saturation": 0,
            "Sharpness": 0,
            "Clarity": 0,
            "Hue": 0,
            "Color Temperature": 0,
        }
        self.edit_last_slider_dict: Dict[str, int] = {}
        self.edit_is_reverted_var: bool = False
        self.edit_cumulative_var: BooleanVar = BooleanVar(value=False)


#endregion
#region Create Widgets


    def toggle_edit_panel(self) -> None:
        if not self.app.edit_panel_visible_var.get():
            if hasattr(self.app, 'edit_image_panel') and self.app.edit_image_panel.winfo_exists():
                self.app.edit_image_panel.grid_remove()
            if hasattr(self, 'highlights_spinbox_frame') and self.highlights_spinbox_frame.winfo_exists():
                self.highlights_spinbox_frame.grid_remove()
            if hasattr(self, 'shadows_spinbox_frame') and self.shadows_spinbox_frame.winfo_exists():
                self.shadows_spinbox_frame.grid_remove()
            if hasattr(self, 'sharpness_spinbox_frame') and self.sharpness_spinbox_frame.winfo_exists():
                self.sharpness_spinbox_frame.grid_remove()
        else:
            self.app.edit_image_panel.grid()
            self.create_edit_panel_widgets()
            if self.app.image_file.lower().endswith('.gif'):
                self.toggle_edit_panel_widgets("disabled")
            else:
                self.toggle_edit_panel_widgets("normal")
        self.app.refresh_image()


    def create_edit_panel_widgets(self) -> None:
        # Edit Mode Combobox
        self.edit_combobox = ttk.Combobox(self.app.edit_image_panel, values=["Brightness", "Contrast", "AutoContrast", "Highlights", "Shadows", "Saturation", "Sharpness", "Clarity", "Hue", "Color Temperature"], width=18, state="readonly")
        self.edit_combobox.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.edit_combobox.set("Brightness")
        self.edit_combobox.bind("<<ComboboxSelected>>", self.update_slider_value)
        # Edit Slider
        self.edit_slider = ttk.Scale(self.app.edit_image_panel, from_=-100, to=100, orient="horizontal", command=self.update_edit_value)
        self.edit_slider.grid(row=0, column=1, pady=5, sticky="ew")
        self.edit_slider.bind("<MouseWheel>", self.adjust_slider_with_mouse_wheel)
        self.app.edit_image_panel.columnconfigure(1, weight=1)
        # Edit Value Label
        self.edit_value_label = Label(self.app.edit_image_panel, text="0", width=3)
        self.edit_value_label.grid(row=0, column=2, pady=5, sticky="ew")
        # Cumulative Edit Checkbutton
        self.cumulative_edit_checkbutton = ttk.Checkbutton(self.app.edit_image_panel, variable=self.edit_cumulative_var, command=self.apply_image_edit)
        self.cumulative_edit_checkbutton.grid(row=0, column=3, pady=5, sticky="ew")
        Tip.create(widget=self.cumulative_edit_checkbutton, text="If enabled, all edits will be done cumulatively; otherwise, only the selected option will be used.", show_delay=25, wraplength=200)
        # Revert Button
        self.edit_revert_image_button = ttk.Button(self.app.edit_image_panel, text="Revert", width=7, command=self.revert_image_edit)
        self.edit_revert_image_button.grid(row=0, column=4, pady=5, sticky="ew")
        self.edit_revert_image_button.bind("<Button-3>", self._reset_edit)
        Tip.create(widget=self.edit_revert_image_button, text="Cancel changes and refresh the displayed image.\nRight-Click to reset the edit panel.")
        # Save Button
        self.edit_save_image_button = ttk.Button(self.app.edit_image_panel, text="Save", width=7, command=self.save_image_edit)
        self.edit_save_image_button.grid(row=0, column=5, padx=(0,5), pady=5, sticky="ew")
        Tip.create(widget=self.edit_save_image_button, text="Save the current changes.\nOptionally overwrite the current image.")
        # Spinbox Frame - Highlights
        self.highlights_spinbox_frame = ttk.Frame(self.app.edit_image_panel)
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
        self.shadows_spinbox_frame = ttk.Frame(self.app.edit_image_panel)
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
        self.sharpness_spinbox_frame = ttk.Frame(self.app.edit_image_panel)
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


    def update_slider_value(self, event: Optional[Any]) -> None:
        current_option = self.edit_combobox.get()
        is_rgb = self.app.current_image.mode == "RGB"
        rgb_required_options = ["AutoContrast", "Hue", "Color Temperature"]
        if current_option in rgb_required_options and not is_rgb:
            messagebox.showwarning("Unsupported Color Mode", f"{current_option} adjustment only supports images in RGB color mode!\n\nImage Color Mode: {self.app.current_image.mode}\n\nAdjustments will be ignored.")
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


    def update_edit_value(self, value: Union[int, float, str]) -> None:
        value = int(float(value))
        self.edit_value_label.config(text=value)
        current_option = self.edit_combobox.get()
        self.slider_value_dict[current_option] = value
        self.apply_image_edit()


    def adjust_slider_with_mouse_wheel(self, event: Any) -> None:
        current_value = self.edit_slider.get()
        new_value = current_value + (event.delta / 120) * (self.edit_slider.cget('to') - self.edit_slider.cget('from')) / 100
        self.edit_slider.set(new_value)
        self.update_edit_value(new_value)


    def toggle_edit_panel_widgets(self, state: str, event: Optional[Any] = None) -> None:
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

        set_widget_state(self.app.edit_image_panel, state)


    def validate_spinbox_value(self, spinbox: 'ttk.Spinbox', min_value: int = 0, max_value: int = 1, integer: bool = True, float: bool = False) -> Union[int, float]:
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


    def _reset_edit(self, event: Optional[Any] = None) -> None:
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
        self.app.refresh_image()


    def update_edited_image(self) -> None:
        display_width = self.app.primary_display_image.winfo_width()
        display_height = self.app.primary_display_image.winfo_height()
        self.app.current_image, new_width, new_height = self.app.resize_and_scale_image(self.app.current_image, display_width, display_height, None)
        self.app.current_image_tk = ImageTk.PhotoImage(self.app.current_image)
        self.app.primary_display_image.config(image=self.app.current_image_tk)
        self.app.primary_display_image.image = self.app.current_image_tk


#endregion
#region Edit


    def apply_image_edit(self, event: Optional[Any] = None) -> None:
        if hasattr(self, 'apply_image_edit_id'):
            self.root.after_cancel(self.apply_image_edit_id)
        self.apply_image_edit_id = self.root.after(50, self._apply_image_edit)


    def _apply_image_edit(self) -> None:
        self.app.current_image = self.app.original_image.copy()
        is_rgb = self.app.current_image.mode == "RGB"
        adjustment_methods = {
            "Brightness": self.adjust_brightness,
            "Contrast": self.adjust_contrast,
            "AutoContrast": self.adjust_autocontrast if is_rgb else None,
            "Highlights": self.adjust_highlights,
            "Shadows": self.adjust_shadows,
            "Saturation": self.adjust_saturation,
            "Sharpness": self.adjust_sharpness,
            "Hue": self.adjust_hue if is_rgb else None,
            "Color Temperature": self.adjust_color_temperature if is_rgb else None,
            "Clarity": self.adjust_clarity  # register clarity for preview
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


    def edit_image(self, value: int, enhancer_class: Any, image_type: str = "display", image: Optional[Image.Image] = None) -> Optional[Image.Image]:
        factor = (value + 100) / 100.0
        if image_type == "display":
            enhancer_display = enhancer_class(self.app.current_image)
            self.app.current_image = enhancer_display.enhance(factor)
            return self.app.current_image
        elif image_type == "original" and image is not None:
            enhancer_original = enhancer_class(image)
            return enhancer_original.enhance(factor)
        return image


#endregion
#region Save


    def save_image_edit(self) -> None:
        if all(value == 0 for value in self.slider_value_dict.values()):
            messagebox.showinfo("No Changes", "No changes to save.")
            return
        if not messagebox.askyesno("Save Image", "Do you want to save the edited image?"):
            return
        original_filepath = self.app.image_files[self.app.current_index]
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
                "Color Temperature": self.adjust_color_temperature if is_rgb else None,
                "Clarity": self.adjust_clarity  # register clarity for saving
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
        self.app.refresh_file_lists()
        messagebox.showinfo("Image Saved", f"Image saved as {new_filename}")


#endregion
#region Revert


    def revert_image_edit(self) -> None:
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
            self.app.refresh_image()
            for option in self.slider_value_dict:
                self.slider_value_dict[option] = 0
            self.edit_slider.set(0)
            self.edit_value_label.config(text="0")
            self.edit_is_reverted_var = True


#endregion
#region Utility


    def _create_gradient_mask(self, image: Image.Image, threshold: int, blur_radius: int, invert: bool = False) -> Image.Image:
        def sigmoid(x):
            return 1 / (1 + numpy.exp(-x))
        grayscale = ImageOps.grayscale(image)
        gradient = numpy.asarray(grayscale, dtype=numpy.float32)
        gradient = (gradient - threshold) / 256.0
        gradient = sigmoid(gradient * 10)
        gradient = (gradient * 256).astype(numpy.uint8)
        if invert:
            gradient = 255 - gradient
        mask = Image.fromarray(gradient, mode='L')
        if blur_radius > 0:
            mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        return mask


#endregion
#region Image Functions


    def adjust_brightness(self, value: int, image_type: str = "display", image: Optional[Image.Image] = None) -> Optional[Image.Image]:
        return self.edit_image(value, ImageEnhance.Brightness, image_type=image_type, image=image)


    def adjust_contrast(self, value: int, image_type: str = "display", image: Optional[Image.Image] = None) -> Optional[Image.Image]:
        return self.edit_image(value, ImageEnhance.Contrast, image_type=image_type, image=image)


    def adjust_autocontrast(self, value: Optional[int] = None, image_type: str = "display", image: Optional[Image.Image] = None) -> Optional[Image.Image]:
        if value is None or value <= 0:
            return image
        strength = max(0.0, min(1.0, value / 100.0))
        contrast_boost = 1.0 + (0.1 * strength)
        if image_type == "display":
            img = ImageOps.autocontrast(self.app.current_image)
            enhancer = ImageEnhance.Contrast(img)
            self.app.current_image = enhancer.enhance(contrast_boost)
            return self.app.current_image
        elif image_type == "original" and image is not None:
            img = ImageOps.autocontrast(image)
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(contrast_boost)
        return image


    def adjust_highlights(self, value: int, image_type: str = "display", image: Optional[Image.Image] = None) -> Optional[Image.Image]:
        old_min, old_max = -100, 100
        new_min, new_max = -30, 30
        value = ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
        factor = (value + 100) / 100.0
        threshold = self.validate_spinbox_value(self.highlights_threshold_spinbox, min_value=1, max_value=256, integer=True)
        blur_radius = self.validate_spinbox_value(self.highlights_blur_radius_spinbox, min_value=0, max_value=100, integer=True)
        if image_type == "display":
            mask = self._create_gradient_mask(self.app.current_image, threshold, blur_radius, invert=True)
            self.app.current_image = Image.composite(self.app.current_image, ImageEnhance.Brightness(self.app.current_image).enhance(factor), mask)
        elif image_type == "original" and image:
            mask = self._create_gradient_mask(image, threshold, blur_radius, invert=True)
            return Image.composite(image, ImageEnhance.Brightness(image).enhance(factor), mask)
        return image


    def adjust_shadows(self, value: int, image_type: str = "display", image: Optional[Image.Image] = None) -> Optional[Image.Image]:
        factor = (value + 100) / 100.0
        threshold = self.validate_spinbox_value(self.shadows_threshold_spinbox, min_value=1, max_value=256, integer=True)
        blur_radius = self.validate_spinbox_value(self.shadows_blur_radius_spinbox, min_value=0, max_value=100, integer=True)
        if image_type == "display":
            mask = self._create_gradient_mask(self.app.current_image, threshold, blur_radius)
            self.app.current_image = Image.composite(self.app.current_image, ImageEnhance.Brightness(self.app.current_image).enhance(factor), mask)
        elif image_type == "original" and image:
            mask = self._create_gradient_mask(image, threshold, blur_radius)
            return Image.composite(image, ImageEnhance.Brightness(image).enhance(factor), mask)
        return image


    def adjust_saturation(self, value: int, image_type: str = "display", image: Optional[Image.Image] = None) -> Optional[Image.Image]:
        return self.edit_image(value, ImageEnhance.Color, image_type=image_type, image=image)


    def adjust_sharpness(self, value: int, image_type: str = "display", image: Optional[Image.Image] = None, boost: Optional[int] = None) -> Optional[Image.Image]:
        if boost is None:
            boost = self.validate_spinbox_value(self.sharpness_boost_spinbox, min_value=1, max_value=5, integer=True)
        if image_type == "display":
            result = self.app.current_image
        else:
            result = image
        for _ in range(boost):
            result = self.edit_image(value, ImageEnhance.Sharpness, image_type=image_type, image=result)
        if image_type == "display":
            return self.app.current_image
        return result


    def adjust_clarity(self, value: int, image_type: str = "display", image: Optional[Image.Image] = None) -> Optional[Image.Image]:
        """Local midtone contrast (clarity) implemented by adding a scaled high-pass (original - blurred)
        back to the image. value in [-100, 100], where positive increases clarity, negative softens.
        """
        if value == 0:
            return image
        amount = float(value) / 100.0  # scale factor: -1.0 .. 1.0
        # heuristic blur radius based on magnitude so larger clarity affects larger structures
        radius = max(1, int(1 + abs(value) * 0.05))

        def _apply(img: Image.Image) -> Image.Image:
            # preserve alpha if present
            has_alpha = img.mode == 'RGBA'
            alpha = None
            if has_alpha:
                *rgb_parts, alpha = img.split()
                img_rgb = Image.merge('RGB', rgb_parts)
            else:
                img_rgb = img.convert('RGB')

            blurred = img_rgb.filter(ImageFilter.GaussianBlur(radius=radius))
            arr = numpy.array(img_rgb).astype(numpy.float32)
            barr = numpy.array(blurred).astype(numpy.float32)
            # add scaled high-pass (original - blurred)
            result = arr + amount * (arr - barr)
            numpy.clip(result, 0, 255, out=result)
            out_img = Image.fromarray(result.astype(numpy.uint8), mode='RGB')
            if has_alpha and alpha is not None:
                out_img.putalpha(alpha)
            return out_img
        if image_type == "display":
            self.app.current_image = _apply(self.app.current_image)
            return self.app.current_image
        elif image_type == "original" and image is not None:
            return _apply(image)
        return image


    def adjust_hue(self, value: int, image_type: str = "display", image: Optional[Image.Image] = None) -> Optional[Image.Image]:
        shift = int(value * 255 / 200)
        def _shift_hue(img):
            hsv = img.convert('HSV')
            h, s, v = hsv.split()
            h = h.point(lambda p: (p + shift) % 256)
            return Image.merge('HSV', (h, s, v)).convert('RGB')
        if image_type == "display":
            self.app.current_image = _shift_hue(self.app.current_image)
            return self.app.current_image
        elif image_type == "original" and image is not None:
            return _shift_hue(image)
        return image


    def adjust_color_temperature(self, value: int, image_type: str = "display", image: Optional[Image.Image] = None) -> Optional[Image.Image]:
        factor = max(-1.0, min(1.0, value / 100.0))
        def _adjust_color_temperature_np(img):
            if img.mode != 'RGB':
                img = img.convert('RGB')
            arr = numpy.array(img).astype(numpy.float32)
            red_mult = 1.0 + 0.35 * factor
            blue_mult = 1.0 - 0.35 * factor
            arr[..., 0] *= red_mult
            arr[..., 2] *= blue_mult
            numpy.clip(arr, 0, 255, out=arr)
            return Image.fromarray(arr.astype(numpy.uint8), mode='RGB')
        if image_type == "display":
            self.app.current_image = _adjust_color_temperature_np(self.app.current_image)
            return self.app.current_image
        elif image_type == "original" and image is not None:
            return _adjust_color_temperature_np(image)
        return image


#endregion