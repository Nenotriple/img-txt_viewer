################## github.com/Nenotriple
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

import os
import re
import csv
import sys
import requests
import subprocess
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

    def download_data(self, data_file):
        download = messagebox.askyesno("File not found.", "'danbooru.csv' is required for autocomplete suggestions.\n\nDo you want to download it from the repo? ~2MB\n\nYes = Download\nNo = Ignore")
        if download:
            url = "https://raw.githubusercontent.com/Nenotriple/img-txt_viewer/main/danbooru.csv"
            response = requests.get(url)
            with open(data_file, 'wb') as f:
                f.write(response.content)

    def load_data(self, data_file):
        data = {}
        if not os.path.isfile(data_file):
            self.download_data(data_file)
        if not os.path.isfile(data_file):
            return None
        with open(data_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                true_name = row[0]
                similar_names = row[3].split(',')
                data[true_name] = similar_names
        return data

    def autocomplete(self, text):
        if not hasattr(self, 'data') or not self.data:
            return None
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

################################################################################################################################################
################################################################################################################################################
#            #
# Main Class #
#            #

class imgtxt_viewer:
    def __init__(self, master):

        # Window settings
        master.minsize(905, 516)
        root.geometry("1050x655")

        # Variables
        self.master = master
        self.suggestion_quantity = IntVar()
        self.auto_save_var = BooleanVar()
        self.bold_commas = BooleanVar()
        self.button_label = StringVar()
        self.image_dir = StringVar()
        self.font_var = StringVar()
        self.max_width = IntVar()
        self.suggestion_alignment = StringVar()
        self.suggestion_style = StringVar()
        self.text_modified = False
        self.user_selected_no = False
        self.is_alt_arrow_pressed = False
        self.selected_suggestion_index = 0
        self.prev_num_files = 0
        self.current_index = 0
        self.image_files = []
        self.suggestions = []
        self.text_files = []
        self.new_text_files = []

        # Settings
        self.max_width.set(650)
        self.suggestion_style.set("Style 1: ⚫")
        self.suggestion_alignment.set("Left Aligned")
        self.bold_commas.set(False)
        self.auto_save_var.set(False)
        self.image_dir.set("Choose Directory")

        # Autocomplete settings
        self.autocomplete = Autocomplete("danbooru.csv")
        self.autocomplete.max_suggestions = 4
        self.suggestion_quantity.set(4)

        # Bindings
        master.bind("<Control-s>", lambda event: self.save_text_file())
        master.bind("<Alt-Right>", lambda event: self.next_pair(event))
        master.bind("<Alt-Left>", lambda event: self.prev_pair(event))

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

        # Size Menu
        sizemenu = Menu(optionsmenu, tearoff=0)
        optionsmenu.add_cascade(label="Image Size", menu=sizemenu)
        sizes = [("Smallest", 512, (1050, 516, 900, 516)),  # (MAX_img_W, set_W, set_H, min_W, min_H)
                 ("Small", 650, (1050, 655, 905, 516)),
                 ("Medium", 800, (1200, 805, 1200, 516)),
                 ("Large", 1000, (1400, 1005, 1400, 516)),
                 ("Largest", 1200, (1300, 1205, 1800, 516))]
        for size in sizes:
            sizemenu.add_radiobutton(label=size[0], variable=self.max_width, value=size[1], command=lambda s=size: self.adjust_window(*s[2]))

        # Suggestion Quantity Menu
        optionsmenu.add_separator()
        suggestion_quantity_menu = Menu(optionsmenu, tearoff=0)
        optionsmenu.add_cascade(label="Suggestion Quantity", menu=suggestion_quantity_menu)
        for i in range(1, 10):
            suggestion_quantity_menu.add_radiobutton(label=str(i), variable=self.suggestion_quantity, value=i, command=lambda suggestion_quantity=i: self.set_suggestion_quantity(suggestion_quantity))

        # Suggestion Alignment Menu
        suggestion_style_menu = Menu(optionsmenu, tearoff=0)
        suggestion_alignment_menu = Menu(suggestion_style_menu, tearoff=0)
        suggestion_style_menu.add_cascade(label="Alignment", menu=suggestion_alignment_menu)
        for suggestion_alignment in ["Left Aligned", "Centered"]:
            suggestion_alignment_menu.add_radiobutton(label=suggestion_alignment, variable=self.suggestion_alignment, value=suggestion_alignment, command=lambda suggestion_alignment=suggestion_alignment: self.set_suggestion_alignment(suggestion_alignment))

        # Suggestion Style Menu
        suggestion_style_menu.add_separator()
        optionsmenu.add_cascade(label="Suggestion Style", menu=suggestion_style_menu)
        for style in ["Style 1: ⚫", "Style 2: ⬛", "Style 3: ◾", "Style 4: ◾[]"]:
            suggestion_style_menu.add_radiobutton(label=style, variable=self.suggestion_style, value=style, command=lambda style=style: self.set_suggestion_style(style))

        # Font Menu and Big Comma Mode
        optionsmenu.add_separator()
        optionsmenu.add_command(label="Font Options", command=self.set_font)
        optionsmenu.add_checkbutton(label="Big Comma Mode", variable=self.bold_commas, command=self.toggle_big_comma)

        # Tools Menu
        toolsmenu.add_command(label="Cleanup Text", command=self.cleanup_all_text_files)
        toolsmenu.add_separator()
        toolsmenu.add_command(label="Batch Token Delete", command=self.batch_token_delete)
        toolsmenu.add_separator()
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
        self.text_box.tag_configure("highlight", background="#5da9be")
        self.suggestion_label = Label(master, text="", anchor='w')

        # Image Label
        self.label_image = Label(master)
        self.label_image.pack(side=LEFT)
        self.label_image.bind('<Button-2>', self.open_directory)
        self.label_image.bind('<Button-3>', self.open_directory)
        self.label_image.bind("<MouseWheel>", self.mouse_scroll)
        ToolTip.create_tooltip(self.label_image, "Left click to open in system image viewer\n\nRight/Middle click to open in file explorer\n\nMouse-Wheel to scroll through images", 1000, 1, -80)

        # Directory Button
        self.directory_button = Button(root, textvariable=self.image_dir, command=self.choose_directory)
        self.directory_button.pack(side=TOP, fill=X)
        self.directory_button.bind('<Button-2>', self.open_directory)
        self.directory_button.bind('<Button-3>', self.copy_to_clipboard)
        ToolTip.create_tooltip(self.directory_button, "Right click to copy path\n\nMiddle click to open in file explorer", 1000, 50, 30)

        # Save Button
        self.save_button = Button(self.master, text="Save", command=self.save_text_file, fg="blue")
        self.save_button.pack(side=TOP, fill=X, pady=2)
        ToolTip.create_tooltip(self.save_button, "CTRL+S", 1000, 1, 1)

        # Navigation Buttons
        button_frame = Frame(master)
        button_frame.pack()
        self.next_button = Button(button_frame, text="Next--->", command=lambda event=None: self.next_pair(event), width=16)
        self.prev_button = Button(button_frame, text="<---Previous", command=lambda event=None: self.prev_pair(event), width=16)
        self.next_button.pack(side=RIGHT, padx=2, pady=2)
        self.prev_button.pack(side=RIGHT, padx=2, pady=2)
        ToolTip.create_tooltip(self.next_button, "ALT+Right", 1000, -65, 1)
        ToolTip.create_tooltip(self.prev_button, "ALT+Left", 1000, -50, 1)

        # Saved Label / Autosave
        saved_label_frame = Frame(master)
        saved_label_frame.pack(pady=2)
        self.auto_save_checkbutton = Checkbutton(saved_label_frame, text="Auto-save", variable=self.auto_save_var, command=self.change_label)
        self.auto_save_checkbutton.pack(side=RIGHT)
        self.saved_label(saved_label_frame)

        # Text Box bindings
        self.text_box.bind("<KeyRelease>", lambda event: (self.update_suggestions(event), self.toggle_big_comma(event)))
        self.text_box.bind("<Shift-Right>", lambda event: self.highlight_duplicates(event, mouse=False))
        self.text_box.bind("<Shift-Left>", lambda event: self.highlight_duplicates(event, mouse=False))
        self.text_box.bind("<ButtonRelease-1>", self.highlight_duplicates)
        self.text_box.bind("<Left>", lambda event: self.remove_highlight())
        self.text_box.bind("<Right>", lambda event: self.remove_highlight())
        self.text_box.bind("<Button-1>", lambda event: self.remove_highlight())
        self.text_box.bind("<Tab>", self.disable_button)
        self.text_box.bind("<Alt_L>", self.disable_button)
        self.text_box.bind("<Alt_R>", self.disable_button)
        self.text_box.bind("<Key>", lambda event: self.change_label())

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
            "  ▪️ Enable 'Big Comma' mode for more visual separation between captions.\n"
            "  ▪️ Blank text files can be created for images without any matching pair when loading a directory.\n\n"

            "Text Tools:\n"
            "  ▪️ These are destructive tools, the process cannot be undone! Test before using.\n"
            "         ▪️ Search and Replace: Edit all text files at once.\n"
            "         ▪️ Prefix Text Files: Insert text at the START of all text files.\n"
            "         ▪️ Append Text Files: Insert text at the END of all text files.\n"
            "         ▪️ Batch Token Delete: View all tokens in a directory, and quickly delete them.\n"
            "         ▪️ Cleanup Text: This tool fixes simple typos in text files in the selected folder, such as multiple spaces or commas, and missing spaces after commas.\n\n"

            "Auto-Save:\n"
            "  ▪️ Check the auto-save box to save text when navigating between img/txt pairs or closing the window.\n"
            "  ▪️ Text is cleaned up when saved, so you can ignore things like trailing comma/spaces, double comma/spaces, etc.\n\n",

            justify=LEFT, font=("Segoe UI", 10)); self.info_label.pack(anchor=W)

################################################################################################################################################
################################################################################################################################################
    #                             #
    # Autocomplete and Highlights #
    #                             #

    def update_suggestions(self, event=None):
        if event is None:
            event = type('', (), {})()
            event.keysym = ''
            event.char = ''
        if event.keysym == "Tab":
            if self.selected_suggestion_index < len(self.suggestions):
                completed_suggestion = self.suggestions[self.selected_suggestion_index]
                self.insert_completed_suggestion(completed_suggestion)
            self.clear_suggestions()
        elif event.keysym in ("Alt_L", "Alt_R"):
            if self.suggestions and not self.is_alt_arrow_pressed:
                if event.keysym == "Alt_R":
                    self.selected_suggestion_index = (self.selected_suggestion_index - 1) % len(self.suggestions)
                else:
                    self.selected_suggestion_index = (self.selected_suggestion_index + 1) % len(self.suggestions)
                self.highlight_selected_suggestion(self.suggestion_style.get())
            self.is_alt_arrow_pressed = False
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
                    self.highlight_selected_suggestion(self.suggestion_style.get())
                else:
                    self.clear_suggestions()
            else:
                self.clear_suggestions()

    def insert_completed_suggestion(self, completed_suggestion):
        completed_suggestion = completed_suggestion.strip()
        current_position = self.text_box.index("insert")
        text = self.text_box.get("1.0", "insert")
        elements = [element.strip() for element in text.split(',')]
        current_word = elements[-1]
        current_word = current_word.strip()
        remaining_text = self.text_box.get("insert", "end").rstrip('\n')
        space_after_comma = ' ' if not remaining_text.startswith(' ') and remaining_text else ''
        space_before_comma = ' ' if len(current_word) < len(text) and text[-len(current_word)-1] != ' ' else ''
        updated_text = text[:-len(current_word)] + space_before_comma + completed_suggestion + ',' + space_after_comma + remaining_text
        cleaned_text = self.cleanup_text(updated_text)
        if not cleaned_text.endswith(", ") and remaining_text == '':
            cleaned_text += ", "
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", cleaned_text)
        current_position_split = current_position.split('.')
        current_position_split[1] = str(int(current_position_split[1]) + len(completed_suggestion) - len(current_word) + 2)
        new_position = '.'.join(current_position_split)
        while self.text_box.get(new_position) == ' ':
            new_position_split = new_position.split('.')
            new_position_split[1] = str(int(new_position_split[1]) + 1)
            new_position = '.'.join(new_position_split)
        self.text_box.mark_set("insert", new_position)

    def highlight_selected_suggestion(self, suggestion_style):
        if self.suggestions:
            if suggestion_style == "Style 1: ⚫":
                suggestion_text = ",   ".join(
                    f"⚫{s}" if i == self.selected_suggestion_index else f"⚪{s}"
                    for i, s in enumerate(self.suggestions)
                )
            elif suggestion_style == "Style 2: ⬛":
                suggestion_text = ",   ".join(
                    f"⬛{s}" if i == self.selected_suggestion_index else f"⬜{s}"
                    for i, s in enumerate(self.suggestions)
                )
            elif suggestion_style == "Style 3: ◾":
                suggestion_text = ",   ".join(
                    f"◾{s}" if i == self.selected_suggestion_index else f"◽{s}"
                    for i, s in enumerate(self.suggestions)
                )
            elif suggestion_style == "Style 4: ◾[]":
                suggestion_text = ", ".join(
                    f"◾[{s}]" if i == self.selected_suggestion_index else f"{s}"
                    for i, s in enumerate(self.suggestions)
                )
            self.suggestion_label.config(text=suggestion_text)

    def set_suggestion_quantity(self, suggestion_quantity):
        self.autocomplete.max_suggestions = suggestion_quantity
        self.update_suggestions(event=None)

    def set_suggestion_style(self, suggestion_style):
        self.suggestion_style.set(suggestion_style)
        self.highlight_selected_suggestion(suggestion_style)

    def set_suggestion_alignment(self, suggestion_alignment):
        if suggestion_alignment == "Centered":
            self.suggestion_label.config(anchor='center')
        elif suggestion_alignment == "Left Aligned":
            self.suggestion_label.config(anchor='w')

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
        self.suggestions = []
        self.suggestion_label.config(text="...")

################################################################################################################################################
################################################################################################################################################
    #                   #
    # Primary Functions #
    #                   #

    def load_pairs(self):
        self.info_label.pack_forget()
        self.image_files = []
        self.text_files = []
        self.new_text_files = []
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
                    self.new_text_files.append(filename)
                self.text_files.append(text_file_path)
        if self.new_text_files:
            self.create_blank_textfiles(self.new_text_files)
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
            self.label_image.config(width=max_width, height=max_height)
            self.label_image.bind("<Configure>", lambda event: self.scale_image(event, aspect_ratio, image))
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
        self.toggle_big_comma()
        self.clear_suggestions()

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
        ToolTip.create_tooltip(self.suggestion_label, "TAB: insert highlighted suggestion\nALT: Cycle suggestions", 1000, 10, -35)

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

    def next_pair(self, event):
        self.is_alt_arrow_pressed = True
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

    def prev_pair(self, event):
        self.is_alt_arrow_pressed = True
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

    def mouse_scroll(self, event):
        if event.delta > 0:
            self.next_pair(event)
        else:
            self.prev_pair(event)

################################################################################################################################################
################################################################################################################################################
    #              #
    # Text Options #
    #              #

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

    def batch_token_delete(self):
        try:
            self.check_directory()
        except ValueError:
            return
        process = subprocess.Popen(["pythonw", "v1.0_batch_token_delete.py", self.image_dir.get()])
        process.communicate()
        self.cleanup_all_text_files(show_confirmation=False)
        self.show_pair()

    def search_and_replace(self):
        try:
            self.check_directory()
        except ValueError:
            return
        dialog = Toplevel(self.master)
        dialog.focus_force()
        dialog.geometry("345x145")
        dialog.title("Search and Replace")
        dialog.attributes('-toolwindow', True)
        dialog.resizable(False, False)
        Label(dialog, text="Search For:").pack()
        search_string_var = StringVar()
        search_string_entry = Entry(dialog, textvariable=search_string_var, width=55)
        default_text = "Enter EXACT search string here"
        search_string_entry.insert(0, default_text)
        search_string_entry.bind('<FocusIn>', lambda event: self.clear_entry_field(event, search_string_entry, default_text))
        search_string_entry.pack()
        Label(dialog, text="\nReplace With:\n(Leave empty to replace with nothing)").pack()
        replace_string_var = StringVar()
        replace_string_entry = Entry(dialog, textvariable=replace_string_var, width=55)
        default_replace_text = ""
        replace_string_entry.insert(0, default_replace_text)
        replace_string_entry.bind('<FocusIn>', lambda event: self.clear_entry_field(event, replace_string_entry, default_replace_text))
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
        try:
            self.check_directory()
        except ValueError:
            return
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
        prefix_text_entry.bind('<FocusIn>', lambda event: self.clear_entry_field(event, prefix_text_entry, default_text))
        prefix_text_entry.pack()
        def perform_prefix_text():
            prefix_text = prefix_text_var.get()
            if not prefix_text.endswith(', '):
                prefix_text += ', '
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
        Button(button_frame, text="OK", command=lambda: messagebox.askokcancel("Confirmation", f"Are you sure you want to prefix all files with:\n\n'{prefix_text_var.get()}, '", parent=dialog) and perform_prefix_text(), width=15, relief=RAISED, borderwidth=3).pack(side=LEFT, pady=2, padx=2)
        Button(button_frame, text="Cancel", command=close_dialog, width=15).pack(side=LEFT, pady=2, padx=2)

    def append_text_files(self):
        try:
            self.check_directory()
        except ValueError:
            return
        self.check_directory()
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
        append_text_entry.bind('<FocusIn>', lambda event: self.clear_entry_field(event, append_text_entry, default_text))
        append_text_entry.pack()
        def perform_append_text():
            append_text = append_text_var.get()
            if not append_text.startswith(', '):
                append_text = ', ' + append_text
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
        Button(button_frame, text="OK", command=lambda: messagebox.askokcancel("Confirmation", f"Are you sure you want to append all files with:\n\n', {append_text_var.get()}'", parent=dialog) and perform_append_text(), width=15, relief=RAISED, borderwidth=3).pack(side=LEFT, pady=2, padx=2)
        Button(button_frame, text="Cancel", command=close_dialog, width=15).pack(side=LEFT, pady=2, padx=2)

    def clear_entry_field(self, event, entry, default_text):
        if entry.get() == default_text:
            entry.delete(0, END)

################################################################################################################################################
################################################################################################################################################
    #                        #
    # Save/close and Cleanup #
    #                        #

    def save_text_file(self):
        try:
            self.check_directory()
        except ValueError:
            return
        if self.text_files:
            text_file = self.text_files[self.current_index]
            with open(text_file, "w", encoding="utf-8") as f:
                text = self.text_box.get("1.0", END).strip()
                cleaned_text = self.cleanup_text(text)
                f.write(cleaned_text)
        self.saved_label.config(text="Saved", bg="#6ca079", fg="white")
        self.show_pair()

    def cleanup_text(self, text):
        text = re.sub(' *, *', ',', text)  # replace one or more spaces surrounded by optional commas with a single comma
        text = re.sub(' +', ' ', text)  # replace multiple spaces with a single space
        text = re.sub(",+", ",", text)  # replace multiple commas with a single comma
        text = re.sub(",(?=[^\s])", ", ", text)  # add a space after a comma if it's not already there
        text = re.sub(r'\\\\+', r'\\', text)  # replace multiple backslashes with a single backslash
        text = re.sub(",+$", "", text)  # remove trailing commas
        text = re.sub(" +$", "", text)  # remove trailing spaces
        text = text.strip(",")  # remove leading and trailing commas
        text = text.strip()  # remove leading and trailing spaces
        return text

    def cleanup_all_text_files(self, show_confirmation=True):
        try:
            self.check_directory()
        except ValueError:
            return
        if show_confirmation:
            user_confirmation = messagebox.askokcancel("Confirmation", "This operation will clean all text files from typos like:\nExtra commas, Extra spaces, trailing commas/spaces, commas without spaces, and more.\n\nExample Cleanup:\n  From: dog,solo,  ,happy  ,,\n       To: dog, solo, happy")
            self.saved_label.config(text="Text Files Cleaned Up!", bg="#6ca079", fg="white")
            if not user_confirmation:
                return
        for text_file in self.text_files:
            with open(text_file, "r+", encoding="utf-8") as f:
                text = f.read().strip()
                cleaned_text = self.cleanup_text(text)
                f.seek(0)
                f.write(cleaned_text)
                f.truncate()
        self.show_pair()

    def on_closing(self):
        if self.saved_label.cget("text") in ["No Changes", "Saved", "Text Files Cleaned up!"]:
            root.destroy()
        elif self.auto_save_var.get():
            self.cleanup_all_text_files(show_confirmation=False)
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

    def open_directory(self, event=None):
        try:
            os.startfile(self.image_dir.get())
        except:
            pass

    def check_directory(self):
        if not os.path.isdir(self.image_dir.get()):
            tk.messagebox.showerror("Error!", "Invalid or No directory selected.\n\n Select a directory before using this tool.")
            raise ValueError("Invalid directory")

    def copy_to_clipboard(self, event):
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.image_dir.get())
        except:
            pass

    def disable_button(self, event):
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

    def resize_image(self, image, max_width, max_height): # Resizes an image to fit within the specified maximum and minimum limits, while maintaining its aspect ratio.
      w, h = image.size
      aspect_ratio = w / h
      min_width = 512
      min_height = 512
      if w < min_width or h < min_height or w > max_width or h > max_height: # Check if the image's dimensions are outside the acceptable range.
        if w > h:
          new_width = max(min_width, min(max_width, w))
          new_height = int(new_width / aspect_ratio)
        else:
          new_height = max(min_height, min(max_height, h))
          new_width = int(new_height * aspect_ratio)
        image = image.resize((new_width, new_height))
      return image, aspect_ratio

    def scale_image(self, event, aspect_ratio, image): # Scales an image to fit within a window while maintaining its aspect ratio.
      window_height = event.height
      window_width = event.width
      new_height = window_height
      new_width = int(new_height * aspect_ratio)
      if new_width > window_width: # If the calculated width is greater than the window width, recalculate both width and height based on the window width.
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
        try:
            self.check_directory()
        except ValueError:
            return
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
root.title("v1.75 - img-txt_viewer  ---  github.com/Nenotriple/img-txt_viewer")

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

'''

- [v1.75 changes:](https://github.com/Nenotriple/img-txt_viewer/releases/tag/v1.75)
  - New:
    - New tool: `Batch Token Delete` This tool allows you to see a list of all tokens in the selected folder and delete them easily.
      - This tool can be used "standalone" without img-txt_viewer. Simply double-click the .py file and select a directory.
      - Note: v1.0 of Batch Token Delete currently relies on a cleanup function within img-txt_viewer to properly clean text files.
    - New tool: `Cleanup Text` This fixes common typos in all text files within a chosen folder, such as double commas or spaces and missing spaces after commas.
    - New option: `Suggestion Style` Here, you can select from four options. The old style is still there, plus a new default style.
    - New option: `Suggestion Alignment` Here you can select between "Left Aligned", and "Centered". The default is now: Left Aligned.
    - Changes: `Prefix` and `Append`: These tools now insert commas and spaces where appropriate. Prefix=`token, ` Append=`, token`
    - UI Tweaks.

<br>

  - Fixed:
    - `cleanup_text` now handles situations like `, ,` *(and repeating)*
    - Further improvements for suggested text insertion and cursor positioning. *(This is a tricky one to nail down)*
    - Pressing “Alt” to cycle a suggestion, then typing, unintentionally cycles the suggestion again.
    - When moving to the next/prev pair using the alt+Arrow hotkeys: The suggestion index would progress by +/-1.
    - The suggestion label now updates after setting the suggestion quantity.
    - Issue where `Big Comma Mode` wouldn't enable when using some features.
    - Error handling is added to check for a directory before running certain tools.

'''

################################################################################################################################################
################################################################################################################################################
#      #
# todo #
#      #

'''

- Todo
  -

- Tofix
  - When inserting a suggestion: If the cursor position isn't at the very end of the currently typed word when the suggestion is inserted, the inserted word is split.
       This also happens when moving the cursor over a previously typed word and inserting a suggestion.
       (Asterisk = Cursor)
       Example Input: ", dog*g"
       Example Output: ", doggystyle, *g"

'''
