##################
#                #
# img-txt_viewer #
#                #
##################
# Requirements:  #
# pillow         # Included: Auto-install
################################################################################################################################################
################################################################################################################################################
#         #
# Imports #
#         #

import csv
import os
import re
import sys
import contextlib
import tkinter.font
import tkinter as tk
from tkinter import BooleanVar, Button, Checkbutton, Entry, Event, Frame, IntVar, Label, Menu, StringVar, Text, Tk, Toplevel, messagebox, ttk, TclError
from tkinter import RAISED, WORD, YES, NO, BOTH, END, TOP, BOTTOM, LEFT, RIGHT, X, W
from tkinter.filedialog import askdirectory

try:
    from PIL import ImageTk, Image
except ImportError:
    import subprocess, sys
    root = Tk()
    root.withdraw()
    install_pillow = messagebox.askyesno("Pillow not installed!", " Pillow (image viewer) not found. Would you like to install it? ~2.5MB \n\n It's required to display images.")
    if install_pillow:
        subprocess.check_call(["python", '-m', 'pip', 'install', 'pillow'])
        messagebox.showinfo("Pillow Installed", " Successfully installed Pillow. \n\n Please restart the program.")
    sys.exit()

################################################################################################################################################
################################################################################################################################################
#          #
# ToolTips #
#          #

class ToolTip:
    def __init__(self, widget, x_offset=0, y_offset=0):
        self.widget = widget
        self.tip_window = None
        self.x_offset = x_offset
        self.y_offset = y_offset

    def show_tip(self, tip_text):
        if self.tip_window or not tip_text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + self.x_offset
        y = y + self.widget.winfo_rooty() + self.y_offset
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=tip_text, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack()

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

    def create_tooltip(widget, text, delay=500, x_offset=0, y_offset=0):
        tool_tip = ToolTip(widget, x_offset, y_offset)
        id = None
        def enter(event):
            nonlocal id
            id = widget.after(delay, lambda: tool_tip.show_tip(text))
        def leave(event):
            nonlocal id
            widget.after_cancel(id)
            tool_tip.hide_tip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

################################################################################################################################################
################################################################################################################################################
#              #
# Autocomplete #
#              #

class Autocomplete:
    def __init__(self, data_file, max_suggestions=4):
        self.data = self.load_data(data_file)
        self.max_suggestions = max_suggestions

    def load_data(self, data_file):
        data = {}
        if not os.path.isfile(data_file):
            import requests
            download = messagebox.askyesno("File not found.", " 'danbooru.csv' is required for autocomplete suggestions.\n\n Do you want to download it from the repo? ~2MB \n\n Yes = Download \n No = Ignore")
            if download:
                url = "https://raw.githubusercontent.com/Nenotriple/img-txt_viewer/main/danbooru.csv"
                response = requests.get(url)
                with open(data_file, 'wb') as f:
                    f.write(response.content)
            else:
                return data
        with open(data_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                true_name = row[0]
                similar_names = row[3].split(',')
                data[true_name] = similar_names
        return data

    def autocomplete(self, text):
        suggestions = []
        text_with_underscores = text.replace(" ", "_")
        for true_name, similar_names in self.data.items():
            if true_name.startswith(text_with_underscores):
                suggestions.append((true_name, similar_names))
            else:
                for sim_name in similar_names:
                    if sim_name.startswith(text_with_underscores):
                        suggestions.append((true_name, similar_names))
                        break
        suggestions.sort(key=lambda x: self.get_score(x[0], text_with_underscores), reverse=True)
        return suggestions[:self.max_suggestions]

    def get_score(self, suggestion, text):
        score = 0
        if suggestion == text:
            score += len(text) * 2
        else:
            for i in range(len(text)):
                if suggestion[i] == text[i]:
                    score += 1
                else:
                    break
        return score

    def update_data(self, data_file):
        self.data = self.load_data(data_file)

################################################################################################################################################
################################################################################################################################################
#            #
# Main Class #
#            #

class imgtxt_viewer:
    def __init__(self, master):

        # Window settings
        master.minsize(905, 550)
        root.geometry("1050x680")

        # Variables
        self.master = master
        self.suggestion_quantity = IntVar()
        self.auto_save_var = BooleanVar()
        self.bold_commas = BooleanVar()
        self.button_label = StringVar()
        self.image_dir = StringVar()
        self.font_var = StringVar()
        self.max_width = IntVar()
        self.text_modified = False
        self.user_selected_no = False
        self.selected_suggestion_index = 0
        self.prev_num_files = 0
        self.current_index = 0
        self.image_files = []
        self.suggestions = []
        self.text_files = []

        # Settings
        self.max_width.set(650)
        self.bold_commas.set(False)
        self.auto_save_var.set(False)
        self.image_dir.set("Choose Directory")

        # Autocomplete settings
        self.autocomplete = Autocomplete("danbooru.csv")
        self.autocomplete.max_suggestions = 4
        self.suggestion_quantity.set(4)

        # Bindings
        master.bind("<Control-s>", lambda event: self.save_text_file())
        master.bind("<Alt-Right>", lambda event: self.next_pair())
        master.bind("<Alt-Left>", lambda event: self.prev_pair())

################################################################################################################################################
################################################################################################################################################
#         #
# Menubar #
#         #

        # Initilize Menu Bar
        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        optionsmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=optionsmenu)
        toolsmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=toolsmenu)

        # Suggestion Quantity Menu
        suggestion_quantity_menu = Menu(optionsmenu, tearoff=0)
        optionsmenu.add_cascade(label="Suggestion Quantity", menu=suggestion_quantity_menu)
        for i in range(1, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(i), variable=self.suggestion_quantity,
                                             value=i, command=lambda quantity=i: self.set_suggestion_quantity(quantity))

        # Size Menu
        sizemenu = Menu(optionsmenu, tearoff=0)
        optionsmenu.add_cascade(label="Image Size", menu=sizemenu)
        sizes = [("Smallest", 512, (1050, 540, 900, 550)),  # (MAX_img_W, set_W, set_H, min_W, min_H)
                 ("Small", 650, (1050, 680, 905, 550)),
                 ("Medium", 800, (1200, 830, 1200, 550)),
                 ("Large", 1000, (1400, 1030, 1400, 550)),
                 ("Largest", 1800, (1900, 1230, 1800, 550))]
        for size in sizes:
            sizemenu.add_radiobutton(label=size[0], variable=self.max_width,
                                     value=size[1], command=lambda s=size: self.adjust_window(*s[2]))

        # Font Menu and Big Comma Mode
        optionsmenu.add_separator()
        optionsmenu.add_command(label="Font Options", command=self.set_font)
        optionsmenu.add_checkbutton(label="Big Comma Mode", variable=self.bold_commas, command=self.toggle_big_comma)

        # Tools Menu
        toolsmenu.add_command(label="Search and Replace", command=self.search_and_replace)
        toolsmenu.add_command(label="Prefix Text Files", command=self.prefix_text_files)
        toolsmenu.add_command(label="Append Text Files", command=self.append_text_files)
        toolsmenu.add_separator()
        toolsmenu.add_command(label="Delete Current Pair", command=self.delete_pair); root.bind('<Delete>', lambda event: self.delete_pair())

################################################################################################################################################
################################################################################################################################################
#                           #
# Buttons, Labels, and more #
#                           #

        # Text Box and Suggestion Label
        self.text_box = Text(master, height=5, width=5, wrap=WORD, undo=True, maxundo=200)
        self.suggestion_label = Label(master, text="")

        # Image Label
        self.label_image = Label(master)
        self.label_image.pack(side=LEFT)
        self.label_image.bind('<Button-2>', self.open_directory); self.label_image.bind('<Button-3>', self.open_directory)
        ToolTip.create_tooltip(self.label_image, "Left click to open in system image viewer\n\nRight/Middle click to open in file explorer", 500, 0, 0)

        # Directory Button
        self.directory_button = Button(root, textvariable=self.image_dir, command=self.choose_directory)
        self.directory_button.bind('<Button-2>', self.open_directory); self.directory_button.bind('<Button-3>', self.copy_to_clipboard)
        ToolTip.create_tooltip(self.directory_button, "Right click to copy path\n\nMiddle click to open in file explorer", 500, 0, -48)
        self.directory_button.pack(side=TOP, fill=X)

        # Save Button
        self.save_button = Button(self.master, text="Save", command=self.save_text_file, fg="blue")
        self.save_button.pack(side=TOP, fill=X, pady=2)

        # Navigation Buttons
        button_frame = Frame(master)
        button_frame.pack()
        self.next_button = Button(button_frame, text="Next--->", command=self.next_pair, width=16)
        self.prev_button = Button(button_frame, text="<---Previous", command=self.prev_pair, width=16)
        self.next_button.pack(side=RIGHT, padx=2, pady=2)
        self.prev_button.pack(side=RIGHT, padx=2, pady=2)

        # Saved Label / Autosave
        saved_label_frame = Frame(master)
        saved_label_frame.pack(pady=2)
        self.auto_save_checkbutton = Checkbutton(saved_label_frame, text="Auto-save", variable=self.auto_save_var, command=self.change_label)
        self.auto_save_checkbutton.pack(side=RIGHT)
        self.saved_label(saved_label_frame)

        # Text Box bindings
        self.text_box.tag_configure("highlight", background="#5da9be")
        self.text_box.bind("<ButtonRelease-1>", self.highlight_duplicates); self.text_box.bind("<Shift-Left>", lambda event: self.highlight_duplicates(event, mouse=False)); self.text_box.bind("<Shift-Right>", lambda event: self.highlight_duplicates(event, mouse=False))
        self.text_box.bind("<Left>", lambda event: self.remove_highlight()); self.text_box.bind("<Right>", lambda event: self.remove_highlight()); self.text_box.bind("<Button-1>", lambda event: self.remove_highlight())
        self.text_box.bind("<KeyRelease>", lambda event: (self.update_suggestions(event), self.toggle_big_comma(event)))
        self.text_box.bind("<Key>", lambda event: self.change_label())
        self.text_box.bind("<Tab>", self.disable_tab)

################################################################################################################################################
################################################################################################################################################
#           #
# Info_Text #
#           #

        # Startup text
        self.info_label = Label(self.master, text=
            "Keyboard Shortcuts:\n"
            "  ▪️ ALT+Left/Right: Quickly move between img-txt pairs.\n"
            "  ▪️ Del: Send the current pair to a local trash folder.\n"
            "  ▪️ ALT: Cycle through auto-suggestions.\n"
            "  ▪️ TAB: Insert the highlighted suggestion.\n"
            "  ▪️ CTRL+S: Save the current text file.\n"
            "  ▪️ CTRL+Z / CTRL+Y: Undo/Redo.\n\n"


            "Tips:\n"
            "  ▪️ Highlight duplicates by selecting text.\n"
            "  ▪️ Right-click the directory button to copy the path.\n"
            "  ▪️ Middle-click the directory button to open the folder.\n"
            "  ▪️ Right-click or Middle-click the displayed image to open its folder.\n"
            "  ▪️ Get autocomplete suggestions while you type using Danbooru tags.\n"
            "  ▪️ Enable 'Big Comma' mode for more visual separation between captions.\n"
            "  ▪️ Blank text files can be created for images without any matching files when loading a directory.\n\n"


            "Text Tools:\n"
            "  ▪️ Search and Replace: Edit all text files at once.\n"
            "  ▪️ Prefix Text Files: Insert text at the START of all text files.\n"
            "  ▪️ Append Text Files: Insert text at the END of all text files.\n\n"



            "Auto-Save:\n"
            "  ▪️ Check the auto-save box to save text when navigating between img/txt pairs or closing the window.\n"
            "  ▪️ Text is cleaned up when saved, so you can ignore things like trailing comma/spaces, double comma/spaces, etc.\n\n",

            justify=LEFT, font=("Segoe UI", 10)); self.info_label.pack(anchor=W)

################################################################################################################################################
################################################################################################################################################
#                             #
# Autocomplete and Highlights #
#                             #

    def update_suggestions(self, event):
        if event.keysym == "Tab":
            if self.selected_suggestion_index < len(self.suggestions):
                completed_suggestion = self.suggestions[self.selected_suggestion_index]
                self.insert_completed_suggestion(completed_suggestion)
            self.clear_suggestions()
        elif event.keysym in ("Alt_L", "Alt_R"):
            if self.suggestions:
                if event.keysym == "Alt_R":
                    self.selected_suggestion_index = (self.selected_suggestion_index - 1) % len(self.suggestions)
                else:
                    self.selected_suggestion_index = (self.selected_suggestion_index + 1) % len(self.suggestions)
                self.highlight_selected_suggestion()
        elif event.keysym in ("Up", "Down"):
            self.clear_suggestions()
        elif event.char == ",":
            self.clear_suggestions()
        else:
            text = self.text_box.get("1.0", "insert")
            elements = [element.strip() for element in text.split(',')]
            current_word = elements[-1]
            current_word = current_word.strip()
            if current_word:
                suggestions = self.autocomplete.autocomplete(current_word)
                suggestions.sort(key=lambda x: self.autocomplete.get_score(x[0], current_word), reverse=True)
                self.suggestions = [suggestion[0].replace("_", " ") for suggestion in suggestions]
                if self.suggestions:
                    suggestion_text =", ".join(self.suggestions)
                    self.suggestion_label.config(text=suggestion_text)
                    self.selected_suggestion_index = 0
                    self.highlight_selected_suggestion()
                else:
                    self.clear_suggestions()
            else:
                self.clear_suggestions()

    def insert_completed_suggestion(self, completed_suggestion):
        text = self.text_box.get("1.0", "insert")
        elements = [element.strip() for element in text.split(',')]
        current_word = elements[-1]
        current_word = current_word.strip()
        remaining_text = self.text_box.get("insert", "end").rstrip('\n')
        if ',' in remaining_text or completed_suggestion.endswith(','):
            updated_text = text[:-len(current_word)] + completed_suggestion + ',' + remaining_text
        else:
            updated_text = text[:-len(current_word)] + completed_suggestion + ', ' + remaining_text
        updated_text = updated_text.replace(',,', ',')
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", updated_text)
        lines = updated_text.split('\n')
        line_number = len(lines)
        column_number = len(lines[-1]) - len(remaining_text) - len(completed_suggestion.split()) + 2
        cursor_position_after_inserted_comma = f"{line_number}.{column_number}"
        self.text_box.mark_set("insert", cursor_position_after_inserted_comma)

    def highlight_selected_suggestion(self):
        if self.suggestions:
            suggestion_text = ""
            for i, s in enumerate(self.suggestions):
                if i == self.selected_suggestion_index:
                    label_text = f"◾[{s}]"
                else:
                    label_text = s
                suggestion_text += label_text + ", "
            self.suggestion_label.config(text=suggestion_text[:-2])

    def highlight_duplicates(self, event, mouse=True):
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
        for word in selected_words:
            if len(word) < 3:
                continue
            pattern = re.escape(word)
            matches = re.finditer(pattern, self.text_box.get("1.0", "end"))
            for match in matches:
                start = match.start()
                end = match.end()
                self.text_box.tag_add("highlight", f"1.0 + {start} chars", f"1.0 + {end} chars")

    def remove_highlight(self):
        self.text_box.tag_remove("highlight", "1.0", "end")

    def clear_suggestions(self):
        self.suggestion_label.config(text="...")
        self.suggestions = []

################################################################################################################################################
################################################################################################################################################
#                   #
# Primary Functions #
#                   #

    def load_pairs(self):
        self.info_label.pack_forget()
        self.image_files = []
        self.text_files = []
        new_text_files = []
        files_in_dir = sorted(os.listdir(self.image_dir.get()), key=self.natural_sort)
        for filename in files_in_dir:
            if filename.lower().endswith("jpg_large"):
                new_filename = filename[:-9] + "jpg"
                os.rename(os.path.join(self.image_dir.get(), filename), os.path.join(self.image_dir.get(), new_filename))
                filename = new_filename
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp")):
                image_file_path = os.path.join(self.image_dir.get(), filename)
                self.image_files.append(image_file_path)
                text_filename = os.path.splitext(filename)[0] + ".txt"
                text_file_path = os.path.join(self.image_dir.get(), text_filename)
                if not os.path.exists(text_file_path):
                    new_text_files.append(filename)
                self.text_files.append(text_file_path)
        if new_text_files:
            self.create_blank_textfiles(new_text_files)
        self.show_pair()
        if hasattr(self, 'total_images_label'):
            self.total_images_label.config(text=f"/{len(self.image_files)}")
        self.prev_num_files = len(files_in_dir)

    def show_pair(self):
        if self.image_files:
            image_file = self.image_files[self.current_index]
            try:
                text_file = self.text_files[self.current_index]
            except IndexError:
                text_file = None
            image = Image.open(image_file)
            max_width = self.max_width.get()
            max_height = 2000
            image, aspect_ratio = self.resize_image(image, max_width, max_height)
            photo = ImageTk.PhotoImage(image)
            self.label_image.config(image=photo)
            self.label_image.image = photo
            self.label_image.config(width=max_width, height=max_height)
            self.label_image.bind("<Configure>", lambda event: self.scale_image(event, aspect_ratio, image))
            self.label_image.bind("<MouseWheel>", self.mouse_scroll)
            self.text_box.config(undo=False)
            self.text_box.delete("1.0", END)
            if text_file and os.path.isfile(text_file):
                with open(text_file, "r") as f:
                    self.text_box.insert(END, f.read())
            self.text_modified = False
            self.text_box.config(undo=True)
            if not self.text_modified and self.saved_label.cget("text") != "Saved":
                self.saved_label.config(text="No Changes", bg="#f0f0f0", fg="black")
            self.display_image_index()
            window_height = self.label_image.winfo_height()
            window_width = self.label_image.winfo_width()
            event = Event()
            event.height = window_height
            event.width = window_width
            self.scale_image(event, aspect_ratio, image)
        def open_image(event):
            os.startfile(image_file)
        self.label_image.bind("<Button-1>", open_image)

################################################################################################################################################
################################################################################################################################################
#            #
# Navigation #
#            #

    def display_image_index(self):
        if hasattr(self, 'image_index_entry'):
            self.image_index_entry.delete(0, END)
            self.image_index_entry.insert(0, f"{self.current_index + 1}")
        else:
            self.index_frame = Frame(self.master)
            self.index_frame.pack(side=TOP, expand=NO)
            self.image_index_entry = Entry(self.index_frame, width=5)
            self.image_index_entry.insert(0, f"{self.current_index + 1}")
            self.image_index_entry.bind("<Return>", self.jump_to_image)
            self.image_index_entry.pack(side=LEFT, expand=NO)
            self.total_images_label = Label(self.index_frame, text=f"/{len(self.image_files)}")
            self.total_images_label.pack(side=LEFT, expand=YES)

        self.text_box.pack(side=BOTTOM, expand=YES, fill=BOTH)
        self.suggestion_label.pack(side=BOTTOM, fill=X)

    def jump_to_image(self, event):
        try:
            index = int(self.image_index_entry.get()) - 1
            if index < 0:
                index = 0
            elif index >= len(self.image_files):
                index = len(self.image_files) - 1
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index = index
            self.show_pair()
            if not self.text_modified:
                self.saved_label.config(text="No Changes", fg="black")
        except ValueError:
            pass

    def next_pair(self):
        num_files_in_dir = len(os.listdir(self.image_dir.get()))
        if num_files_in_dir != self.prev_num_files:
            self.load_pairs()
        if not self.text_modified:
            self.saved_label.config(text="No Changes", fg="black")
        self.text_box.config(undo=False)
        self.text_box.edit_reset()
        if self.current_index < len(self.image_files) - 1:
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index += 1
        else:
            self.current_index = 0
        self.show_pair()
        self.toggle_big_comma()

    def prev_pair(self):
        num_files_in_dir = len(os.listdir(self.image_dir.get()))
        if num_files_in_dir != self.prev_num_files:
            self.load_pairs()
        if not self.text_modified:
            self.saved_label.config(text="No Changes", fg="black")
        self.text_box.config(undo=False)
        self.text_box.edit_reset()
        if self.current_index > 0:
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index -= 1
        else:
            self.current_index = len(self.image_files) - 1
        self.show_pair()
        self.toggle_big_comma()

    def mouse_scroll(self, event):
        if event.delta > 0:
            self.next_pair()
        else:
            self.prev_pair()

################################################################################################################################################
################################################################################################################################################
#              #
# Text Options #
#              #

    def set_suggestion_quantity(self, quantity):
        self.autocomplete.max_suggestions = quantity

    def set_font(self, event=None):
        current_font = self.text_box.cget("font")
        current_font_name = self.text_box.tk.call("font", "actual", current_font, "-family")
        current_font_size = self.text_box.tk.call("font", "actual", current_font, "-size")
        dialog = Toplevel(self.master)
        dialog.focus_force()
        dialog.geometry("220x100")
        dialog.title("Font and Size")
        dialog.attributes('-toolwindow', True)
        dialog.resizable(False, False)
        Label(dialog, text="Font:").pack()
        font_box = ttk.Combobox(dialog, textvariable=self.font_var, width=50)
        font_box['values'] = list(tkinter.font.families())
        font_box.set(current_font_name)
        font_box.bind("<<ComboboxSelected>>", lambda event: self.set_font_and_size(self.font_var.get(), size_var.get(), dialog))
        font_box.bind("<Button-1>", lambda event: font_box.event_generate('<Down>'))
        ToolTip.create_tooltip(font_box, "Recommended Fonts: Courier New, Ariel, Consolas, Segoe UI", 200, -10, -30)
        font_box.pack()
        Label(dialog, text="Font Size:").pack()
        size_var = StringVar()
        size_box = ttk.Combobox(dialog, textvariable=size_var, width=50)
        size_box['values'] = list(range(9, 19))
        size_box.set(current_font_size)
        size_box.bind("<<ComboboxSelected>>", lambda event: self.set_font_and_size(self.font_var.get(), size_var.get(), dialog))
        size_box.bind("<Button-1>", lambda event: size_box.event_generate('<Down>'))
        ToolTip.create_tooltip(size_box, "Default size = 10", 200, 0, -30)
        size_box.pack()

    def set_font_and_size(self, font, size, dialog):
        if font and size:
            self.text_box.config(font=(font, int(size)))

    def toggle_big_comma(self, event=None):
        if self.bold_commas.get():
            self.text_box.tag_remove("bold", "1.0", "end")
            index = "1.0"
            while True:
                index = self.text_box.search(",", index, stopindex="end")
                if not index:
                    break
                self.text_box.tag_add("bold", index, "{}+1c".format(index))
                index = "{}+1c".format(index)
            self.text_box.tag_configure("bold", font=(self.font_var.get(), 18, "bold"))
        else:
            self.text_box.tag_remove("bold", "1.0", "end")

################################################################################################################################################
################################################################################################################################################
#            #
# Text Tools #
#            #

    def search_and_replace(self):
        dialog = Toplevel(self.master)
        dialog.focus_force()
        dialog.geometry("345x145")
        dialog.title("Search and Replace")
        dialog.attributes('-toolwindow', True)
        dialog.resizable(False, False)
        Label(dialog, text="Search String:").pack()
        search_string_var = StringVar()
        search_string_entry = Entry(dialog, textvariable=search_string_var, width=55)
        default_text = "Enter EXACT search string here"
        search_string_entry.insert(0, default_text)
        search_string_entry.bind('<FocusIn>', lambda event: self.clear_entry(event, search_string_entry, default_text))
        search_string_entry.pack()
        Label(dialog, text="\nReplace String:\n(Leave empty to replace with nothing)").pack()
        replace_string_var = StringVar()
        replace_string_entry = Entry(dialog, textvariable=replace_string_var, width=55)
        default_replace_text = ""
        replace_string_entry.insert(0, default_replace_text)
        replace_string_entry.bind('<FocusIn>', lambda event: self.clear_entry(event, replace_string_entry, default_replace_text))
        replace_string_entry.pack()
        def perform_search_and_replace():
            search_string = search_string_var.get()
            replace_string = replace_string_var.get()
            total_count = 0
            for text_file in self.text_files:
                with open(text_file, 'r') as file:
                    filedata = file.read()
                count = filedata.count(search_string)
                total_count += count
            msg = f"The string: '{search_string}'\n\nWas found {total_count} times across all files.\n\nDo you want to replace it with:\n\n{replace_string}"
            if messagebox.askyesno("Confirmation", msg):
                for text_file in self.text_files:
                    with open(text_file, 'r') as file:
                        filedata = file.read()
                    filedata = filedata.replace(search_string, replace_string)
                    with open(text_file, 'w') as file:
                        file.write(filedata)
                close_dialog()
        def close_dialog():
            dialog.destroy()
            self.show_pair()
        button_frame = Frame(dialog)
        button_frame.pack()
        Button(button_frame, text="OK", command=perform_search_and_replace, width=15, relief=RAISED, borderwidth=3).pack(side=LEFT, pady=2, padx=2)
        Button(button_frame, text="Cancel", command=close_dialog, width=15).pack(side=LEFT, pady=2, padx=2)

    def prefix_text_files(self):
        dialog = Toplevel(self.master)
        dialog.focus_force()
        dialog.geometry("405x75")
        dialog.title("Prefix Text Files")
        dialog.attributes('-toolwindow', True)
        dialog.resizable(False, False)
        Label(dialog, text="Text to Prefix:").pack()
        prefix_text_var = StringVar()
        prefix_text_entry = Entry(dialog, textvariable=prefix_text_var, width=65)
        default_text = "Enter the text you want to prefix here"
        prefix_text_entry.insert(0, default_text)
        prefix_text_entry.bind('<FocusIn>', lambda event: self.clear_entry(event, prefix_text_entry, default_text))
        prefix_text_entry.pack()
        def perform_prefix_text():
            prefix_text = prefix_text_var.get()
            for text_file in self.text_files:
                try:
                    with open(text_file, 'r+') as file:
                        content = file.read()
                        file.seek(0, 0)
                        file.write(prefix_text + content)
                except Exception as e:
                    print(f"Error while processing file {text_file}: {e}")
            close_dialog()
        def close_dialog():
            dialog.destroy()
            self.show_pair()
        button_frame = Frame(dialog)
        button_frame.pack()
        Button(button_frame, text="OK", command=lambda: messagebox.askokcancel("Confirmation", f"Are you sure you want to prefix all files with:\n\n{prefix_text_var.get()}", parent=dialog) and perform_prefix_text(), width=15, relief=RAISED, borderwidth=3).pack(side=LEFT, pady=2, padx=2)
        Button(button_frame, text="Cancel", command=close_dialog, width=15).pack(side=LEFT, pady=2, padx=2)

    def append_text_files(self):
        dialog = Toplevel(self.master)
        dialog.focus_force()
        dialog.geometry("405x75")
        dialog.title("Append Text Files")
        dialog.attributes('-toolwindow', True)
        dialog.resizable(False, False)
        Label(dialog, text="Text to Append:").pack()
        append_text_var = StringVar()
        append_text_entry = Entry(dialog, textvariable=append_text_var, width=65)
        default_text = "Enter the text you want to append here"
        append_text_entry.insert(0, default_text)
        append_text_entry.bind('<FocusIn>', lambda event: self.clear_entry(event, append_text_entry, default_text))
        append_text_entry.pack()
        def perform_append_text():
            append_text = append_text_var.get()
            for text_file in self.text_files:
                try:
                    with open(text_file, 'a') as file:
                        file.write(append_text)
                except Exception as e:
                    print(f"Error while processing file {text_file}: {e}")
            close_dialog()
        def close_dialog():
            dialog.destroy()
            self.show_pair()
        button_frame = Frame(dialog)
        button_frame.pack()
        Button(button_frame, text="OK", command=lambda: messagebox.askokcancel("Confirmation", f"Are you sure you want to append all files with:\n\n{append_text_var.get()}", parent=dialog) and perform_append_text(), width=15, relief=RAISED, borderwidth=3).pack(side=LEFT, pady=2, padx=2)
        Button(button_frame, text="Cancel", command=close_dialog, width=15).pack(side=LEFT, pady=2, padx=2)

    def clear_entry(self, event, entry, default_text):
        if entry.get() == default_text:
            entry.delete(0, END)

################################################################################################################################################
################################################################################################################################################
#                        #
# Save/close and Cleanup #
#                        #

    def save_text_file(self):
        if self.text_files:
            text_file = self.text_files[self.current_index]
            with open(text_file, "w", encoding="utf-8") as f:
                text = self.text_box.get("1.0", END).strip()
                cleaned_text = self.cleanup_text(text)
                f.write(cleaned_text)

        self.saved_label.config(text="Saved", bg="#6ca079", fg="white")
        self.show_pair()

    def cleanup_text(self, text):
        text = re.sub(' +', ' ', text)
        text = re.sub(",+", ",", text)
        text = re.sub("(,)(?=[^\s])", ", ", text)
        text = re.sub(r'\((.*?)\)', r'\(\1\)', text)
        text = re.sub(r'\\\\+', r'\\', text)
        text = re.sub(",+$", "", text)
        text = re.sub(" +$", "", text)
        text = text.strip(",")
        text = text.strip(" ")
        return text

    def on_closing(self):
        if self.saved_label.cget("text") in ["No Changes", "Saved"]:
            root.destroy()
        elif self.auto_save_var.get():
            self.save_text_file()
            root.destroy()
        else:
            try:
                if messagebox.askokcancel("Quit", "Are you sure you want to quit without saving?"):
                    root.destroy()
            except:
                pass

################################################################################################################################################
################################################################################################################################################
#                #
# Misc Functions #
#                #

    def natural_sort(self, s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', s)]

    def open_directory(self, event):
        with contextlib.closing(os.startfile(self.image_dir.get())):
            pass

    def copy_to_clipboard(self, event):
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.image_dir.get())
        except:
            pass

    def disable_tab(self, event):
        return "break"

    def adjust_window(self, new_width, new_height, min_width=None, min_height=None):
        self.save_text_file()
        self.master.geometry(f"{new_width}x{new_height}")
        if min_width is not None and min_height is not None:
            self.master.minsize(min_width, min_height)

################################################################################################################################################
################################################################################################################################################
#               #
# Dynamic Label #
#               #

    def saved_label(self, saved_label_frame):
        self.saved_label = Label(saved_label_frame, text="No Changes", width=23)
        self.saved_label.pack()
        self.text_box.bind("<Key>", lambda event: self.text_modified())

    def change_label(self):
        if self.auto_save_var.get():
            self.saved_label.config(text="Changes are autosaved", bg="#5da9be", fg="white")
        else:
            self.saved_label.config(text="Changes not saved", bg="#FD8A8A", fg="white")

################################################################################################################################################
################################################################################################################################################
#               #
# Image Scaling #
#               #

    def resize_image(self, image, max_width, max_height):
        w, h = image.size
        aspect_ratio = w / h
        min_width = 512
        min_height = 512
        if w < min_width or h < min_height or w > max_width or h > max_height:
            if w > h:
                new_w = max(min_width, min(max_width, w))
                new_h = int(new_w / aspect_ratio)
            else:
                new_h = max(min_height, min(max_height, h))
                new_w = int(new_h * aspect_ratio)
            image = image.resize((new_w, new_h))
        return image, aspect_ratio

    def scale_image(self, event, aspect_ratio, image):
        window_height = event.height
        window_width = event.width
        new_height = window_height
        new_width = int(new_height * aspect_ratio)
        if new_width > window_width:
            new_width = window_width
            new_height = int(new_width / aspect_ratio)
        image = image.resize((new_width, new_height))
        photo = ImageTk.PhotoImage(image)
        self.label_image.config(image=photo)
        self.label_image.image = photo

################################################################################################################################################
################################################################################################################################################
#                 #
# File Management #
#                 #

    def choose_directory(self):
        self.user_selected_no = False
        try:
            directory = askdirectory()
            if directory:
                self.image_dir.set(directory)
                self.current_index = 0
                self.load_pairs()
                self.directory_button.config(anchor='w')
        except Exception as e:
            pass

    def create_blank_textfiles(self, new_text_files):
        if not self.user_selected_no:
            msg = f"Do you want to create {len(new_text_files)} new text file(s)?\n\nImages will still have a text box, even without a text pair."
            result = messagebox.askquestion("Create Blank Text File?", msg)
            if result == "yes":
                for filename in new_text_files:
                    text_filename = os.path.splitext(filename)[0] + ".txt"
                    text_file_path = os.path.join(self.image_dir.get(), text_filename)
                    with open(text_file_path, "w") as f:
                        f.write("")
            elif result == "no":
                self.user_selected_no = True

    def delete_pair(self):
        if messagebox.askokcancel("Warning", "This will move the img-txt pair to a local trash folder.\n\nThe trash folder will be created in the selected directory."):
            trash_dir = os.path.join(os.path.dirname(self.image_files[self.current_index]), "Trash")
            os.makedirs(trash_dir, exist_ok=True)
            os.rename(self.image_files[self.current_index], os.path.join(trash_dir, os.path.basename(self.image_files[self.current_index])))
            os.rename(self.text_files[self.current_index], os.path.join(trash_dir, os.path.basename(self.text_files[self.current_index])))
            del self.image_files[self.current_index]
            del self.text_files[self.current_index]
            self.total_images_label.config(text=f"/{len(self.image_files)}")
            self.show_pair()

################################################################################################################################################
################################################################################################################################################
#           #
# Framework #
#           #

root = Tk()
app = imgtxt_viewer(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.title("v1.74 - img-txt_viewer  ---  github.com/Nenotriple/img-txt_viewer")

if getattr(sys, 'frozen', False): # This is for including an icon with the --onefile excutable version.
    application_path = sys._MEIPASS
elif __file__:
    application_path = os.path.dirname(__file__)
icon_path = os.path.join(application_path, "icon.ico")
try:
    root.iconbitmap(icon_path)
except TclError:
    pass

root.mainloop()

################################################################################################################################################
################################################################################################################################################
#           #
# Changelog #
#           #

#- v1.74 changes:
#  - New:
#    - `Search and Replace`: Replace any text string across all text files in the loaded directory.
#    - `Prefix Text Files`: Insert text at the START of all text files.
#    - `Append Text Files`: Insert text at the END of all text files.
#    - Several UI tweaks and enhancements.

#  - Fixed:
#    - Resolved an issue where the app would repeatedly ask: `Do you want to create '...' new text files?` Even after selecting No.
#    - The 'Saved' label now updates correctly upon saving.
#    - The image index is now refreshed only when the folder quantity changes, resulting in faster navigation.
#    - Re-enabled the 'Undo' function.
#    - Extensive internal code refactoring for improved cleanliness and maintainability.
