from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter import messagebox, Tk, ttk
import csv, os, re

try:
    print("Pillow already installed... Skipping...")    
    from PIL import ImageTk, Image
except ImportError:
    print("Pillow not found...")    
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

class Autocomplete:
    def __init__(self, data_file, max_suggestions=4):
        self.data = self.load_data(data_file)
        self.max_suggestions = max_suggestions

    def load_data(self, data_file):
        data = {}
        if not os.path.isfile(data_file):
            import requests
            download = messagebox.askyesno("File not found.", " danbooru.csv is required for autocomplete suggestions.\n\n Do you want to download it from the repo? \n\n Yes = Download \n No = Ignore")
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
        suggestions.sort(key=lambda x: self.get_relevance_score(x[0], text_with_underscores), reverse=True)
        return suggestions[:self.max_suggestions]

    def get_relevance_score(self, suggestion, text):
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

class ImageTextViewer:
    def __init__(self, master):
        self.master = master        
        master.title("v1.7 - img-txt_viewer  ---  github.com/Nenotriple/img-txt_viewer")
        master.bind("<Control-s>", lambda event: self.save_text_file())
        master.bind("<Alt-Left>", lambda event: self.prev_pair())
        master.bind("<Alt-Right>", lambda event: self.next_pair())  
        self.autocomplete = Autocomplete("danbooru.csv")
        self.autocomplete.max_suggestions = 4
        self.master.minsize(905, 550)
        root.geometry("1050x680")
        self.max_width = IntVar()
        self.max_width.set(650)
        self.theme_var = StringVar()
        self.theme_var.set("Default")        

        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        sizemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Image Size", menu=sizemenu)
        sizemenu.add_radiobutton(label="Smallest", variable=self.max_width, value=512, command=lambda: self.adjust_window(1050, 540, 900, 550)) # (setW, setH, minW, minH)
        sizemenu.add_radiobutton(label="Small", variable=self.max_width, value=650, command=lambda: self.adjust_window(1050, 680, 905, 550))
        sizemenu.add_radiobutton(label="Medium", variable=self.max_width, value=800, command=lambda: self.adjust_window(1200, 830, 1200, 550))
        sizemenu.add_radiobutton(label="Large", variable=self.max_width, value=1000, command=lambda: self.adjust_window(1400, 1030, 1400, 550))
        sizemenu.add_radiobutton(label="Largest", variable=self.max_width, value=1800, command=lambda: self.adjust_window(1900, 1230, 1800, 550))
        textmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=textmenu)
        textmenu.add_command(label="Font Size", command=self.set_font_size)
        textmenu.add_command(label="Suggestion Quantity", command=self.set_suggestion_quantity)
        textmenu.add_command(label="Delete_Pair", command=self.delete_pair)
        
        self.image_dir = StringVar()
        self.button_label = StringVar()
        self.auto_save_var = BooleanVar()
        self.auto_save_var.set(False)
        self.text_modified = False
        self.current_index = 0
        self.selected_suggestion_index = 0
        self.image_files = []
        self.text_files = []
        self.suggestions = []
        self.image_dir.set("Choose Directory")
        self.label_image = Label(master)
        self.text_box = Text(master, height=5, width=5, wrap=WORD, undo=True, maxundo=200)
        self.suggestion_label = Label(master, text="")
        
        self.directory_button = Button(root, textvariable=self.image_dir, command=self.choose_directory)
        self.save_button = Button(self.master, text="Save", command=self.save_text_file, fg="blue")
        self.directory_button.pack(side=TOP, fill=X)
        self.label_image.pack(side=LEFT)
        separator_frame = Frame(root, height=8)
        separator_frame.pack()
        self.save_button.pack(side=TOP, fill=X, pady=3)

        button_frame = Frame(master)
        button_frame.pack()
        self.next_button = Button(button_frame, text="Next--->", command=self.next_pair, width=16)
        self.prev_button = Button(button_frame, text="<---Previous", command=self.prev_pair, width=16)
        self.next_button.pack(side=RIGHT, padx=2, pady=2)
        self.prev_button.pack(side=RIGHT, padx=2, pady=2)

        saved_label_frame = Frame(master)
        saved_label_frame.pack(pady=2)        
        self.auto_save_checkbutton = Checkbutton(saved_label_frame, text="Auto-save", variable=self.auto_save_var, command=self.change_label)
        self.auto_save_checkbutton.pack(side=RIGHT)
        self.saved_label(saved_label_frame)

        self.info_label = Label(self.master, text=
            "Keyboard Shortcuts:\n"
            "  ▪️ CTRL+Z / CTRL+Y: Undo/Redo.\n"
            "  ▪️ CTRL+S: Save the current text file.\n"
            "  ▪️ ALT+Left/Right arrow keys: Quickly move between img/txt pairs.\n\n"

            "Autocomplete Suggestions:\n"
            "  ▪️ Get autocomplete suggestions while you type using danbooru tags.\n"
            "  ▪️ Press TAB to insert the selected suggestion.\n"
            "  ▪️ Press ALT to cycle through suggestions.\n\n"

            "Text Selection:\n"
            "  ▪️ Select text to see duplicates.\n\n"

            "Auto-save Feature:\n"
            "  ▪️ If the auto-save box is checked, text will be saved when moving between img/txt pairs.\n\n"
            "File Creation:\n"
            "  ▪️ Blank text files can be created for images without any matching files when loading a directory.\n",
            justify=LEFT, font=("Segoe UI", 10))
        self.info_label.pack(anchor=W)

        self.text_box.tag_configure("highlight", background="#5da9be")
        self.text_box.bind("<Key>", lambda event: self.change_label())
        self.text_box.bind("<Left>", lambda event: self.remove_highlight())
        self.text_box.bind("<Right>", lambda event: self.remove_highlight())
        self.text_box.bind("<KeyRelease>", self.update_suggestions) 

################################################################################################################################################
################################################################################################################################################

    def update_suggestions(self, event):
        if event.keysym == "Tab":
            if self.selected_suggestion_index < len(self.suggestions):
                completed_suggestion = self.suggestions[self.selected_suggestion_index]
                self.insert_completed_suggestion(completed_suggestion)
            self.suggestion_label.config(text="...")
            self.suggestions = []
        elif event.keysym in ("Alt_L", "Alt_R"):
            if self.suggestions:
                if event.keysym == "Alt_R":
                    self.selected_suggestion_index = (self.selected_suggestion_index - 1) % len(self.suggestions)
                else:
                    self.selected_suggestion_index = (self.selected_suggestion_index + 1) % len(self.suggestions)
                self.highlight_selected_suggestion()
        elif event.keysym in ("Up", "Down"):
            self.suggestion_label.config(text="...")
            self.suggestions = []
        elif event.char == ",":
            self.suggestion_label.config(text="...")
            self.suggestions = []
        else:
            text = self.text_box.get("1.0", "insert")
            elements = [element.strip() for element in text.split(',')]
            current_word = elements[-1]
            current_word = current_word.strip()
            if current_word:
                suggestions = self.autocomplete.autocomplete(current_word)
                suggestions.sort(key=lambda x: self.autocomplete.get_relevance_score(x[0], current_word), reverse=True)
                self.suggestions = [suggestion[0].replace("_", " ") for suggestion in suggestions]
                if self.suggestions:
                    suggestion_text =", ".join(self.suggestions)
                    self.suggestion_label.config(text=suggestion_text)
                    self.selected_suggestion_index = 0
                    self.highlight_selected_suggestion()
                else:
                    self.suggestion_label.config(text="...")
            else:
                self.suggestion_label.config(text="...")

    def insert_completed_suggestion(self, completed_suggestion):
        text = self.text_box.get("1.0", "insert")
        elements = [element.strip() for element in text.split(',')]
        current_word = elements[-1]
        current_word = current_word.strip()
        remaining_text = self.text_box.get("insert", "end").rstrip('\n')
        if ',' in remaining_text:
            updated_text = text[:-len(current_word)] + completed_suggestion + remaining_text[remaining_text.index(','):]
        else:
            updated_text = text[:-len(current_word)] + completed_suggestion + ', ' + remaining_text
        cursor_position = self.text_box.index("insert")   
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", updated_text)
        self.text_box.mark_set("insert", cursor_position)
        num_words_in_suggestion = len(completed_suggestion.split())
        for _ in range(num_words_in_suggestion):
            self.text_box.event_generate("<Control-Right>")

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

################################################################################################################################################
################################################################################################################################################

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

    def natural_sort(self, s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', s)]

    def choose_directory(self):
        try:
            directory = askdirectory()
            if directory:
                self.image_dir.set(directory)
                self.current_index = 0
                self.load_pairs()
        except Exception as e:
            pass

    def load_pairs(self):
        self.info_label.pack_forget()
        self.image_files = []
        self.text_files = []
        new_text_files = []
        for filename in sorted(os.listdir(self.image_dir.get()), key=self.natural_sort):
            if filename.endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp")):
                self.image_files.append(os.path.join(self.image_dir.get(), filename))
                text_filename = os.path.splitext(filename)[0] + ".txt"
                text_file = os.path.join(self.image_dir.get(), text_filename)
                if not os.path.exists(text_file):
                    new_text_files.append(filename)
                self.text_files.append(text_file)
        if new_text_files:
            msg = f"Do you want to create {len(new_text_files)} new text files?"
            result = messagebox.askquestion("New Text Files", msg)
            if result == "yes":
                for filename in new_text_files:
                    text_filename = os.path.splitext(filename)[0] + ".txt"
                    text_file = os.path.join(self.image_dir.get(), text_filename)
                    with open(text_file, "w") as f:
                        f.write("")
        self.show_pair()

    def show_pair(self):
        if self.image_files:
            image_file = self.image_files[self.current_index]
            text_file = self.text_files[self.current_index]
            image = Image.open(image_file)
            w, h = image.size
            aspect_ratio = w / h
            max_width = self.max_width.get()
            max_height = 1200
            min_width = 512
            min_height = 512
            if w < min_width or h < min_height:
                if w > h:
                    new_w = min_width
                    new_h = int(new_w / aspect_ratio)
                else:
                    new_h = min_height
                    new_w = int(new_h * aspect_ratio)
                image = image.resize((new_w, new_h))
            elif w > max_width or h > max_height:
                if w > h:
                    new_w = max_width
                    new_h = int(new_w / aspect_ratio)
                else:
                    new_h = max_height
                    new_w = int(new_h * aspect_ratio)
                image = image.resize((new_w, new_h))
            photo = ImageTk.PhotoImage(image)
            self.label_image.config(image=photo)
            self.label_image.image = photo
            self.label_image.config(width=max_width, height=max_height)
            self.label_image.bind("<Configure>", lambda event: self.scale_image(event, aspect_ratio, image))
            self.text_box.config(undo=False)
            with open(text_file, "r") as f:
                self.text_box.delete("1.0", END)
                self.text_box.insert(END, f.read())
                self.text_modified = False
            if not self.text_modified:
                self.saved_label.config(text="No Changes", bg="#f0f0f0", fg="black")
            self.text_box.bind("<ButtonRelease-1>", self.highlight_duplicates)
            self.text_box.bind("<Shift-Left>", lambda event: self.highlight_duplicates(event, mouse=False))
            self.text_box.bind("<Shift-Right>", lambda event: self.highlight_duplicates(event, mouse=False))            
            self.text_box.bind("<Button-1>", lambda event: self.remove_highlight())
            self.text_box.bind("<Tab>", self.disable_tab)   
            self.display_image_index()
            self.text_box.config(undo=True)
            window_height = self.label_image.winfo_height()
            window_width = self.label_image.winfo_width()
            event = Event()
            event.height = window_height
            event.width = window_width
            self.scale_image(event, aspect_ratio, image)
            self.suggestion_label.config(text="...")

    def scale_image(self, event, aspect_ratio, image):
        window_height = event.height
        window_width = event.width
        new_height = int(window_height * 1)
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
        self.text_box.config(undo=False)
        self.text_box.edit_reset()
        if self.current_index < len(self.image_files) - 1:
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index += 1
        else:
            self.current_index = 0
        self.show_pair()
        if not self.text_modified:
            self.saved_label.config(text="No Changes", fg="black")

    def prev_pair(self):
        self.text_box.config(undo=False)
        self.text_box.edit_reset()
        if self.current_index > 0:
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index -= 1
        else:
            self.current_index = len(self.image_files) - 1
        self.show_pair()
        if not self.text_modified:
            self.saved_label.config(text="No Changes", fg="black")

################################################################################################################################################
################################################################################################################################################

    def save_text_file(self):
        if self.text_files:
            text_file = self.text_files[self.current_index]
            with open(text_file, "w", encoding="utf-8") as f:
                text = self.text_box.get("1.0", END).strip()
                text = ' '.join(text.split())
                text = re.sub(",+", ",", text)
                text = text.replace(" ,", ",")
                if text.endswith(","):
                    text = text[:-1]
                if text.startswith(","):
                    text = text[1:]
                f.write(text)
            self.saved_label.config(text="Saved", bg="#6ca079", fg="white")

    def on_closing(self):
        if self.saved_label.cget("text") == "No Changes":
            root.destroy()
        elif self.auto_save_var.get():
            self.save_text_file()
            root.destroy()
        else:
            if messagebox.askokcancel("Quit", "Are you sure you want to quit without saving?"):
                root.destroy()

    def delete_pair(self):
        if messagebox.askokcancel("Warning", "Are you sure you want to delete this img-txt pair?\n\nThis can't be undone!!"):
            os.remove(self.image_files[self.current_index])
            os.remove(self.text_files[self.current_index])
            del self.image_files[self.current_index]
            del self.text_files[self.current_index]
            self.total_images_label.config(text=f"/{len(self.image_files)}")
            self.show_pair()

    def disable_tab(self, event):
        return "break"

    def adjust_window(self, new_width, new_height, min_width=None, min_height=None):
        self.save_text_file()
        self.master.geometry(f"{new_width}x{new_height}")
        if min_width is not None and min_height is not None:
            self.master.minsize(min_width, min_height)  
        self.next_pair()
        self.prev_pair()

    def set_font_size(self, event=None):
        current_font = self.text_box.cget("font")
        current_size = self.text_box.tk.call("font", "actual", current_font, "-size")
        dialog = Toplevel(self.master)
        dialog.focus_force()
        dialog.geometry("180x50")
        dialog.title("Font Size")
        dialog.attributes('-toolwindow', True)
        Label(dialog, text="font size:").pack()
        size_var = StringVar()
        size_box = ttk.Combobox(dialog, textvariable=size_var)
        size_box['values'] = list(range(9, 19))
        size_box.set(current_size)
        size_box.bind("<<ComboboxSelected>>", lambda event: self.set_font_size_and_destroy(size_var.get(), dialog))
        size_box.bind("<Button-1>", lambda event: size_box.event_generate('<Down>'))
        size_box.pack()

    def set_font_size_and_destroy(self, size, dialog):
        if size:
            self.text_box.config(font=("monaco", int(size)))
            dialog.destroy()

    def set_suggestion_quantity(self):
        dialog = Toplevel(self.master)
        dialog.focus_force()
        dialog.geometry("200x50")
        dialog.title("Autocomplete")
        dialog.attributes('-toolwindow', True)
        Label(dialog, text="Suggestion Quantity:").pack()
        quantity_var = StringVar()
        quantity_box = ttk.Combobox(dialog, textvariable=quantity_var)
        quantity_box['values'] = list(range(0, 10))
        quantity_box.set(self.autocomplete.max_suggestions)
        quantity_box.bind("<<ComboboxSelected>>", lambda event: self.set_quantity_and_destroy(quantity_var.get(), dialog))
        quantity_box.bind("<Button-1>", lambda event: quantity_box.event_generate('<Down>'))
        quantity_box.pack()

    def set_quantity_and_destroy(self, quantity, dialog):
        if quantity:
            self.autocomplete.max_suggestions = int(quantity)
            dialog.destroy()

root = Tk()
app = ImageTextViewer(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()

# v1.7 changes:

# If auto-save is enabled, changes to the text file are now saved automatically when the window is closed.
# If auto-save isn’t enabled when closing, a warning is given. This allows the user to cancel and go back and save if needed.

# The insert_completed_suggestion function now mostly* positions the cursor at the end of multi-word suggestions.

# Autocomplete scorer now prioritizes whole word matches, addressing the bias towards longer tags.

# Pairs are now logically sorted during loading, fixing the issue where filenames like “10” or “100” loaded before “2” or “9”.

# The unused is_modified definition has been removed.

# The Pillow library and danbooru.csv file can now be installed and downloaded respectively, with an option to cancel/ignore.

# A new “Options” menu has been added:
# Adjust font size.
# Adjust suggestion quantity, allowing you to set a value between 0-10.
# Delete img-txt pairs. A warning popup will confirm the choice or give the user an option to cancel.

# UI enhancements include:
# Improved formatting and font size for info_label.
# Restructured layout for saved_label and auto-save checkbox.
# Color and width adjustments for saved_label.
# highlight_selected_suggestion now uses a “Black Medium-Small Square” as an additional visual indicator.
# An ellipsis has been added to the idle suggestion label.
