"""
########################################
#                                      #
#          Batch Resize Images         #
#                                      #
#   Version : v1.02                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
This GUI script allows you to select a directory and resize all images in the selected directory.
Resize operations: Resize to Resolution, Percentage, Resize to Width, Resize to Height, Resize to Shorter Side, Resize to Longer Side
Resize conditions: Upscale and Downscale, Upscale Only, Downscale Only


"""


################################################################################################################################################
#region -  Imports


import os
import sys
import ctypes
import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, TclError
from tkinter.scrolledtext import ScrolledText
from PIL import Image

myappid = 'ImgTxtViewer.Nenotriple'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

#endregion
################################################################################################################################################
#region -  Main


class Resize_Images(tk.Frame):
    def __init__(self, master=None, folder_path=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)
        self.folder_path = folder_path
        self.create_widgets()


#endregion
################################################################################################################################################
#region -  Interface


    def create_widgets(self):
        widget_frame = tk.Frame(self)
        widget_frame.pack(fill="both", padx=2, pady=2)


        # Directory Frame
        directory_frame = tk.Frame(widget_frame)
        directory_frame.pack(fill="both")

        self.directory_label = tk.Label(directory_frame, relief="groove", text="", anchor="w", background="white")
        if self.folder_path is None:
            self.directory_label.config(text="Select a directory containing images to begin!")
        else:
            self.directory_label.config(text=f"{self.folder_path}")
        self.directory_label.pack(side="left", fill="x", expand=True)

        self.select_button = tk.Button(directory_frame, width=8, overrelief="groove")
        self.select_button["text"] = "Browse..."
        self.select_button["command"] = self.select_folder
        self.select_button.pack(side="left", padx=2, pady=2)

        self.open_button = tk.Button(directory_frame, width=8, overrelief="groove")
        self.open_button["text"] = "Open"
        self.open_button["command"] = self.open_folder
        self.open_button.pack(side="left", padx=2, pady=2)


        # Resize Mode Frame
        resize_mode_frame = tk.Frame(widget_frame)
        resize_mode_frame.pack(fill="x")

        self.resize_mode_label = tk.Label(resize_mode_frame, text="Resize To:")
        self.resize_mode_label.pack(side="left", anchor="w", padx=2, pady=2)

        self.resize_mode_var = tk.StringVar()
        self.resize_mode = ttk.Combobox(resize_mode_frame, width=11, textvariable=self.resize_mode_var, values=["Resolution", "Percentage", "Width", "Height", "Shorter Side", "Longer Side"], state="readonly")
        self.resize_mode.set("Resolution")
        self.resize_mode.pack(side="left", fill="x", padx=2, pady=2)


        self.resize_condition_label = tk.Label(resize_mode_frame, text="Condition:")
        self.resize_condition_label.pack(side="left", anchor="w", padx=2, pady=2)

        self.resize_condition_var = tk.StringVar()
        self.resize_condition = ttk.Combobox(resize_mode_frame, width=21, textvariable=self.resize_condition_var, values=["Upscale and Downscale", "Upscale Only", "Downscale Only"], state="readonly")
        self.resize_condition.set("Upscale and Downscale")
        self.resize_condition.pack(side="left", fill="x", padx=2, pady=2)


        self.filetype_label = tk.Label(resize_mode_frame, text="Filetype:")
        self.filetype_label.pack(side="left", anchor="w", padx=2, pady=2)

        self.filetype_var = tk.StringVar()
        self.filetype = ttk.Combobox(resize_mode_frame, width=4, textvariable=self.filetype_var, values=["JPEG", "PNG", "WEBP"], state="readonly")
        self.filetype.set("JPEG")
        self.filetype.pack(side="left", fill="x", padx=2, pady=2)

        self.use_output_folder_var = tk.IntVar(value=1)
        self.use_output_folder_checkbutton = tk.Checkbutton(resize_mode_frame, overrelief="groove", text="Use Output Folder", variable=self.use_output_folder_var)
        self.use_output_folder_checkbutton.pack(side="left", fill="x")


        # Width Frame
        width_frame = tk.Frame(widget_frame)
        width_frame.pack(fill="x", anchor="w")
        self.width_label = tk.Label(width_frame, text="Width:", width=5)
        self.width_label.pack(side="left", anchor="w", padx=2, pady=2)
        self.width_entry = tk.Entry(width_frame, width=10)
        self.width_entry.pack(side="right", fill="x", expand=True, padx=2, pady=2)


        # Height Frame
        height_frame = tk.Frame(widget_frame)
        height_frame.pack(fill="x", anchor="w")
        self.height_label = tk.Label(height_frame, text="Height:", width=5)
        self.height_label.pack(side="left", anchor="w", padx=2, pady=2)
        self.height_entry = tk.Entry(height_frame, width=10)
        self.height_entry.pack(side="right", fill="x", expand=True, padx=2, pady=2)


        # Resize Button
        self.resize_button = tk.Button(widget_frame, overrelief="groove")
        self.resize_button["text"] = "Resize!\t   "
        self.resize_button["command"] = self.resize
        self.resize_button.pack(fill="x", padx=2, pady=2)


        # Percent Bar
        self.percent_complete = tk.StringVar()
        self.percent_bar = ttk.Progressbar(widget_frame, value=0)
        self.percent_bar.pack(fill="x", padx=2, pady=2)


        # Text Box
        self.text_box = ScrolledText(widget_frame)
        self.text_box.pack(fill="both", expand=True, padx=2, pady=2)
        descriptions = ["Resize to Resolution: Resize to specific width and height\n\n"
                        "Preserves aspect ratio:\n\n"
                        "Resize to Percentage: Resize the image by a percent scale\n\n"
                        "Resize to Width: Resize the image width\n\n"
                        "Resize to Height: Resize the image height\n\n"
                        "Resize to Shorter side: Resize the shorter side of the image\n\n"
                        "Resize to Longer side: Resize the longer side of the image\n\n"
                        "Resize Condition:\n"
                        "Upscale and Downscale: Resize the image to the new dimensions regardless of whether they are larger or smaller than the original dimensions.\n\n"
                        "Upscale Only: Resize the image if the new dimensions are larger than the original dimensions.\n\n"
                        "Downscale Only: Resize the image if the new dimensions are smaller than the original dimensions."]

        for description in descriptions:
            self.text_box.insert("end", description + "\n")
        self.text_box.config(state="disabled")


        self.resize_mode_var.trace_add('write', self.update_entries)


#endregion
################################################################################################################################################
#region -  Misc


    def update_entries(self, *args):
        mode = self.resize_mode_var.get()
        if mode == "Resolution":
            self.width_entry.config(state="normal")
            self.width_label.config(state="normal")
            self.height_entry.config(state="normal")
            self.height_label.config(state="normal")
            self.resize_condition_label.config(state="normal")
            self.resize_condition.config(state="readonly")
            self.width_label.config(text="Width:")
            self.height_label.config(text="Heigth:")

        elif mode == "Percentage":
            self.width_entry.config(state="normal")
            self.width_label.config(state="normal")
            self.height_entry.delete(0, 'end')
            self.height_entry.config(state="disabled")
            self.height_label.config(state="disabled")
            self.resize_condition_label.config(state="normal")
            self.resize_condition.config(state="disabled")
            self.width_label.config(text="%")
            self.height_label.config(text="-")

        elif mode in ["Width", "Shorter Side", "Longer Side"]:
            self.width_entry.config(state="normal")
            self.width_label.config(state="normal")
            self.height_entry.delete(0, 'end')
            self.height_entry.config(state="disabled")
            self.height_label.config(state="disabled")
            self.resize_condition_label.config(state="normal")
            self.resize_condition.config(state="readonly")
            if mode == "Width":
                self.width_label.config(text="Width:")
            else:
                self.width_label.config(text="Size")
            self.height_label.config(text="-")

        elif mode in ["Height"]:
            self.width_entry.delete(0, 'end')
            self.width_entry.config(state="disabled")
            self.width_label.config(state="disabled")
            self.height_entry.config(state="normal")
            self.height_label.config(state="normal")
            self.resize_condition_label.config(state="normal")
            self.resize_condition.config(state="readonly")
            self.width_label.config(text="-")
            self.height_label.config(text="Height:")

    def select_folder(self):
        new_folder_path = filedialog.askdirectory()
        if new_folder_path:
            self.folder_path = new_folder_path
            self.directory_label.config(text=f"{self.folder_path}")


    def open_folder(self):
        try:
            os.startfile(self.folder_path)
        except Exception: pass


    def get_output_folder_path(self):
        if self.use_output_folder_var.get() == 1:
            output_folder_path = os.path.join(self.folder_path, "Resize Output")
            if not os.path.exists(output_folder_path):
                os.makedirs(output_folder_path)
        else:
            output_folder_path = self.folder_path
        return output_folder_path


#endregion
################################################################################################################################################
#region -  Resize


    def resize_to_resolution(self, img, width, height):
        if width is None or height is None:
            messagebox.showinfo("Error", "Please enter a valid width and height.")
            return
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError("Width and height must be integers.")
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be greater than 0.")
        img = img.resize((width, height), Image.LANCZOS)
        return img


    def resize_to_percentage(self, img, percentage):
        if percentage is None:
            messagebox.showinfo("Error", "Please enter a valid percentage")
            return
        if not isinstance(percentage, (int, float)):
            raise TypeError("Percentage must be a number.")
        if percentage <= 0:
            raise ValueError("Percentage must be greater than 0.")
        width = int(img.size[0] * percentage)
        height = int(img.size[1] * percentage)
        img = img.resize((width, height), Image.LANCZOS)
        return img


    def resize_to_width(self, img, width):
        if width is None:
            messagebox.showinfo("Error", "Please enter a valid width")
            return
        if not isinstance(width, int):
            raise TypeError("Width must be an integer.")
        if width <= 0:
            raise ValueError("Width must be greater than 0.")
        wpercent = (width/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((width, hsize), Image.LANCZOS)
        return img


    def resize_to_height(self, img, height):
        if height is None:
            messagebox.showinfo("Error", "Please enter a valid height")
            return
        if not isinstance(height, int):
            raise TypeError("Height must be an integer.")
        if height <= 0:
            raise ValueError("Height must be greater than 0.")
        hpercent = (height/float(img.size[1]))
        wsize = int((float(img.size[0])*float(hpercent)))
        img = img.resize((wsize, height), Image.LANCZOS)
        return img


    def resize_to_shorter_side(self, img, width):
        if width is None:
            messagebox.showinfo("Error", "Please enter a valid size")
            return
        if not isinstance(width, int):
            raise TypeError("Size must be an integer.")
        if width <= 0:
            raise ValueError("Size must be greater than 0.")
        if img.size[0] < img.size[1]:
            wpercent = (width/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((width, hsize), Image.LANCZOS)
        else:
            hpercent = (width/float(img.size[1]))
            wsize = int((float(img.size[0])*float(hpercent)))
            img = img.resize((wsize, width), Image.LANCZOS)
        return img


    def resize_to_longer_side(self, img, width):
        if width is None:
            messagebox.showinfo("Error", "Please enter a valid size")
            return
        if not isinstance(width, int):
            raise TypeError("Size must be an integer.")
        if width <= 0:
            raise ValueError("Size must be greater than 0.")
        if img.size[0] > img.size[1]:
            wpercent = (width/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((width, hsize), Image.LANCZOS)
        else:
            hpercent = (width/float(img.size[1]))
            wsize = int((float(img.size[0])*float(hpercent)))
            img = img.resize((wsize, width), Image.LANCZOS)
        return img


    def should_resize(self, original_size, new_size):
        resize_condition = self.resize_condition_var.get()
        if resize_condition == "Upscale Only":
            return new_size > original_size
        elif resize_condition == "Downscale Only":
            return new_size < original_size
        elif resize_condition == "Percentage":
            return True
        else:  # "Upscale and Downscale"
            return True


    def calculate_resize_mode(self, img, resize_mode, width, height):
        original_size = img.size
        if resize_mode == "Resolution":
            new_size = (width, height)
            if self.should_resize(original_size, new_size):
                img = self.resize_to_resolution(img, width, height)
        elif resize_mode == "Percentage":
            percentage = width / 100
            new_size = (int(original_size[0] * percentage), int(original_size[1] * percentage))
            if self.should_resize(original_size, new_size):
                img = self.resize_to_percentage(img, percentage)
        elif resize_mode == "Width":
            new_size = (width, original_size[1])
            if self.should_resize(original_size, new_size):
                img = self.resize_to_width(img, width)
        elif resize_mode == "Height":
            new_size = (original_size[0], height)
            if self.should_resize(original_size, new_size):
                img = self.resize_to_height(img, height)
        elif resize_mode == "Shorter Side":
            new_size = (width, width)
            if self.should_resize(original_size, new_size):
                img = self.resize_to_shorter_side(img, width)
        elif resize_mode == "Longer Side":
            new_size = (height, height)
            if self.should_resize(original_size, new_size):
                img = self.resize_to_longer_side(img, width)
        return img


    def resize(self):
        self.percent_complete.set(0)
        if self.folder_path is not None:
            try:
                resize_mode = self.resize_mode_var.get()
                width_entry = self.width_entry.get()
                height_entry = self.height_entry.get()
                width = int(width_entry) if width_entry else None
                height = int(height_entry) if height_entry else None
                image_files = [f for f in os.listdir(self.folder_path) if f.endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp"))]
                total_images = len(image_files)
                output_folder_path = self.get_output_folder_path()
                if self.use_output_folder_var.get() == 1:
                    confirm_message = f"Images will be saved to\n{os.path.normpath(output_folder_path)}"
                else:
                    confirm_message = "Images will be overwritten, continue?"
                if messagebox.askokcancel("Confirmation", confirm_message):
                    self.master.focus_force()
                    for i, filename in enumerate(image_files):
                        try:
                            img = Image.open(os.path.join(self.folder_path, filename))
                            if img is None:
                                return
                            img = img.convert('RGB')
                            img = self.calculate_resize_mode(img, resize_mode, width, height)
                            if img is None:
                                return
                            if 'icc_profile' in img.info:
                                del img.info['icc_profile']
                            filetype = self.filetype_var.get().lower()
                            base_filename, _ = os.path.splitext(filename)
                            filename_with_new_extension = f"{base_filename}.{filetype}"
                            img.save(os.path.join(output_folder_path, filename_with_new_extension), filetype, quality=100, optimize=True)
                            self.percent_complete.set((i+1)/total_images*100)
                            self.percent_bar['value'] = self.percent_complete.get()
                            self.percent_bar.update()
                        except Exception as e:
                            print(f"Error processing file {filename}: {str(e)}")
                    messagebox.showinfo("Done!", "Resizing finished.")
                    self.master.focus_force()
            except Exception as e:
                print(f"Error in resize function: {str(e)}")
        else:
            return


#endregion
################################################################################################################################################
#region -  Framework


def parse_arguments():
    parser = argparse.ArgumentParser(description='Resize Images Resize_Image')
    parser.add_argument('--folder_path', type=str, help='Path to the folder')
    args = parser.parse_args()
    return args


def setup_root():
    root = tk.Tk()
    root.title("Resize Images")
    root.geometry("650x425")
    root.minsize(610,165)
    root.maxsize(2000,500)
    root.update_idletasks()
    set_icon(root)
    return root


def set_icon(root):
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    elif __file__:
        application_path = os.path.dirname(__file__)
    icon_path = os.path.join(application_path, "icon.ico")
    try:
        root.iconbitmap(icon_path)
    except TclError:
        pass


def center_window(root):
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")


def create_app(root, folder_path):
    app = Resize_Images(master=root, folder_path=folder_path)


if __name__ == "__main__":
    args = parse_arguments()
    root = setup_root()
    center_window(root)
    create_app(root, args.folder_path)
    root.mainloop()


#endregion

'''

v1.02 changes:

  - New:
    - New resize mode: Resize to: `Percentage`. Use this to resize images by a percent scaling percentage.
    - The input labels now change depending on the resize mode.


<br>

  - Fixed:
    -

<br>

  - Other changes:
    - Renamed to `batch_resize_images`.

<br>

  - To fix:
    - Files with the same basename but different extension may be overwritten when being resized.

'''
