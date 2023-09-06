from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from PIL import ImageTk, Image
from difflib import get_close_matches
import csv
import os
import re

class Autocomplete:
    def __init__(self, data_file, autocomplete_delay=75, max_suggestions=3):
        self.data = self.load_data(data_file)
        self.autocomplete_delay = autocomplete_delay
        self.max_suggestions = max_suggestions

    def load_data(self, data_file):
        data = {}
        with open(data_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                true_name = row[0]
                similar_names = row[3].split(',')
                data[true_name] = similar_names
        return data

    def autocomplete(self, text):
        suggestions = []
        text_without_spaces = text.replace(" ", "_")
        for true_name, similar_names in self.data.items():
            if true_name.startswith(text_without_spaces):
                suggestions.append((true_name, similar_names))
            else:
                for sim_name in similar_names:
                    if sim_name.startswith(text_without_spaces):
                        suggestions.append((true_name, similar_names))
                        break
        return suggestions[:self.max_suggestions]

class ImageTextViewer:
    def __init__(self, master):
        self.master = master
        master.title("v1.6 - img-txt_Viewer: (CTRL + S Quicksaves) (ALT + Left/Right Moves between img/txt pairs) (TAB inserts selected suggestion, TAB+Left/Right Selects suggestion)")
        master.bind("<Control-s>", lambda event: self.save_text_file())
        master.bind("<Alt-Left>", lambda event: self.prev_pair())
        master.bind("<Alt-Right>", lambda event: self.next_pair())
        self.master.minsize(1025, 600)
        self.image_dir = StringVar()
        self.current_index = 0
        self.image_files = []
        self.text_files = []
        self.suggestions = []
        self.label_image = Label(master)
        self.text_box = Text(master, height=20, width=50, wrap=WORD, undo=True, maxundo=100)
        self.suggestion_label = Label(master, text="")
        self.next_button = Button(master, text="Next", command=self.next_pair)
        self.prev_button = Button(master, text="Previous", command=self.prev_pair)
        self.directory_button = Button(master, text="Choose Directory", command=self.choose_directory)
        self.directory_entry = Entry(master, textvariable=self.image_dir)
        self.save_button = Button(self.master, text="Save", command=self.save_text_file, fg="blue")
        self.auto_save_var = BooleanVar()
        self.auto_save_var.set(False)
        self.text_modified = False
        self.directory_entry.pack(side=TOP, fill=X)               
        self.directory_button.pack(side=TOP, fill=X)
        self.label_image.pack(side=LEFT)
        self.next_button.pack(anchor=N, fill=X, ipadx=120, pady=3)
        self.prev_button.pack(anchor=N, fill=X, ipadx=120, pady=3)
        self.save_button.pack(side=TOP, fill=X, ipadx=120, pady=3)
        self.auto_save_checkbutton = Checkbutton(master, text="Auto-save", variable=self.auto_save_var)
        self.auto_save_checkbutton.pack(side=TOP)
        self.create_saved_label()
        self.image_index_label = Label(self.master, text="Load a directory with image and text pairs.")
        self.image_index_label.pack(anchor=N)
        self.suggestion_label.pack(side=TOP, fill=X)
        self.text_box.bind("<Key>", lambda event: self.change_label())
        self.text_box.tag_configure("highlight", background="lightblue")
        self.text_box.bind("<ButtonRelease-1>", lambda event: self.highlight_duplicates(event, mouse=True))
        self.text_box.bind("<KeyRelease>", lambda event: self.highlight_duplicates(event, mouse=False))
        self.text_box.bind("<Left>", lambda event: self.remove_highlight())
        self.text_box.bind("<Right>", lambda event: self.remove_highlight())
        self.autocomplete = Autocomplete("danbooru.csv")
        self.text_box.bind("<KeyRelease>", self.update_suggestions) 
        self.selected_suggestion_index = 0
        
    def update_suggestions(self, event):
        if event.keysym == "Tab":
            if self.selected_suggestion_index < len(self.suggestions):
                completed_suggestion = self.suggestions[self.selected_suggestion_index]
                self.insert_completed_suggestion(completed_suggestion)
            self.suggestion_label.config(text="")
            self.suggestions = []
        elif event.keysym in ("Left", "Right"):
            if self.suggestions:
                if event.keysym == "Left":
                    self.selected_suggestion_index = (self.selected_suggestion_index - 1) % len(self.suggestions)
                else:
                    self.selected_suggestion_index = (self.selected_suggestion_index + 1) % len(self.suggestions)
                self.highlight_selected_suggestion()
        elif event.keysym in ("Up", "Down"):
            self.suggestion_label.config(text="")
            self.suggestions = []
        elif event.char == ",":
            self.suggestion_label.config(text="")
            self.suggestions = []
        else:
            if event.char and event.char.isalnum():
                text = self.text_box.get("1.0", "insert")
                elements = [element.strip() for element in text.split(',')]
                current_word = elements[-1]
                current_word = current_word.strip()
                if current_word:
                    self.suggestions = [suggestion[0].replace("_", " ") for suggestion in self.autocomplete.autocomplete(current_word)]
                    if self.suggestions:
                        suggestion_text = "Suggestions: " + ", ".join(self.suggestions)
                        self.suggestion_label.config(text=suggestion_text)
                        self.selected_suggestion_index = 0
                        self.highlight_selected_suggestion()
                    else:
                        self.suggestion_label.config(text="")
                else:
                    self.suggestion_label.config(text="")

    def insert_completed_suggestion(self, completed_suggestion):
        text = self.text_box.get("1.0", "insert")
        elements = [element.strip() for element in text.split(',')]
        current_word = elements[-1]
        current_word = current_word.strip()
        updated_text = text.rsplit(',', 1)[0] + ', ' + completed_suggestion + ', '
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", updated_text)
    
    def highlight_selected_suggestion(self):
        if self.suggestions:
            suggestion_text = "Suggestions: "
            for i, s in enumerate(self.suggestions):
                if i == self.selected_suggestion_index:
                    label_text = f"[{s}]"
                else:
                    label_text = s
                suggestion_text += label_text + ", "
            self.suggestion_label.config(text=suggestion_text[:-2])
    
    def create_saved_label(self):
        self.saved_label = Label(self.master, text="No Changes")
        self.saved_label.pack(anchor=N)
        self.text_box.bind("<Key>", lambda event: self.text_modified())

    def change_label(self):
        if self.auto_save_var.get():
            self.saved_label.config(text="Changes Being autosaved", bg="#4DB6D2", fg="white")
        else:
            self.saved_label.config(text="Changes Are Not Saved", bg="red", fg="white")

    def choose_directory(self):
        self.image_dir.set(askdirectory())
        self.current_index = 0
        self.load_pairs()

    def load_pairs(self):
        self.image_files = []
        self.text_files = []
        new_text_files = []
        for filename in sorted(os.listdir(self.image_dir.get())):
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
            max_width = 650
            max_height = 550
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
            self.text_box.config(undo=False)
            with open(text_file, "r") as f:
                self.text_box.delete("1.0", END)
                self.text_box.insert(END, f.read())
                self.text_modified = False
            if not self.text_modified:
                self.saved_label.config(text="No Changes", bg="white", fg="black")
            self.text_box.bind("<ButtonRelease-1>", self.highlight_duplicates)
            self.text_box.bind("<Button-1>", lambda event: self.remove_highlight())
            self.text_box.bind("<Tab>", self.disable_tab)   
            self.display_image_index()
            self.text_box.config(undo=True)
            

    def highlight_duplicates(self, event, mouse=True):
        if not self.text_box.tag_ranges("sel"):
            return
        selected_text = self.text_box.selection_get().strip()
        if len(selected_text) < 3:
            return
        self.text_box.tag_remove("highlight", "1.0", "end")
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
    
    def display_image_index(self):
        if hasattr(self, 'image_index_label'):
            self.image_index_label.config(text=f"Image {self.current_index + 1}/{len(self.image_files)}")
        else:
            self.image_index_label = Label(self.master, text=f"Image {self.current_index + 1}/{len(self.image_files)}")
            self.image_index_label.pack(side=TOP, expand=YES)
        self.text_box.pack(side=BOTTOM, expand=YES, fill=BOTH)

    def next_pair(self):
        if self.current_index < len(self.image_files) - 1:
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index += 1
            self.show_pair()
            if not self.text_modified:
                self.saved_label.config(text="No Changes", fg="black")

    def prev_pair(self):
        if self.current_index > 0:
            if self.auto_save_var.get():
                self.save_text_file()
            self.current_index -= 1
            self.show_pair()
            if not self.text_modified:
                self.saved_label.config(text="No Changes", fg="black")

    def is_modified(self, *args):
        if self.text_files:
            text_file = self.text_files[self.current_index]
            with open(text_file, "r") as f:
                file_content = f.read()
                text_content = self.text_box.get("1.0", END)
                self.text_modified = file_content != text_content
                if self.text_modified:
                    self.saved_label.config(text="Changes Not Saved", fg="red")
                else:
                    self.saved_label.config(text="No Changes", fg="black")

    def save_text_file(self):
        if self.text_files:
            text_file = self.text_files[self.current_index]
            with open(text_file, "w", encoding="utf-8") as f:
                text = self.text_box.get("1.0", END).strip()
                text = text.replace(",,,", ",")
                text = text.replace(",,", ",")
                text = ' '.join(text.split())
                if text.endswith(","):
                    text = text[:-1]
                if text.startswith(","):
                    text = text[1:]
                f.write(text)
            self.saved_label.config(text="Saved", bg="green", fg="white")       

    def disable_tab(self, event):
        return "break"            

root = Tk()
app = ImageTextViewer(root)
root.mainloop()
