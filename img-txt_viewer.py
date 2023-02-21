from tkinter import *
from tkinter.filedialog import askdirectory
from PIL import ImageTk, Image
import os

class ImageTextViewer:
    def __init__(self, master):
        self.master = master
        master.title("Image Text Viewer - ctrl+s Saves - alt+arrow Next/Previous Pair")
        master.bind("<Control-s>", lambda event: self.save_text_file())
        master.bind("<Alt-Left>", lambda event: self.prev_pair())
        master.bind("<Alt-Right>", lambda event: self.next_pair())

        self.image_dir = StringVar()
        self.current_index = 0
        self.image_files = []
        self.text_files = []

        self.label_image = Label(master)
        self.text_box = Text(master, height=20, width=50, wrap=WORD, undo=TRUE)
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

        self.image_index_label = Label(self.master, text="Load a directory with image and text pairs.")
        self.image_index_label.pack(anchor=N)

        self.create_saved_label()
        self.text_box.bind("<Key>", lambda event: self.change_label())

    def create_saved_label(self):
        self.saved_label = Label(self.master, text="No Changes")
        self.saved_label.pack(anchor=N)
        self.text_box.bind("<Key>", lambda event: self.text_modified())

    def change_label(self):
        self.saved_label.config(text="Changes Are Not Saved", bg="red", fg="white")

    def choose_directory(self):
        self.image_dir.set(askdirectory())
        self.current_index = 0
        self.load_pairs()

    def load_pairs(self):
        self.image_files = []
        self.text_files = []
        for filename in sorted(os.listdir(self.image_dir.get())):
            if filename.endswith((".jpg", ".png")):
                self.image_files.append(os.path.join(self.image_dir.get(), filename))
                text_filename = os.path.splitext(filename)[0] + ".txt"
                self.text_files.append(os.path.join(self.image_dir.get(), text_filename))
        self.show_pair()

    def show_pair(self):
        if self.image_files:
            image_file = self.image_files[self.current_index]
            text_file = self.text_files[self.current_index]
            image = Image.open(image_file)
            w, h = image.size
            aspect_ratio = w / h
            label_w = self.label_image.winfo_width()
            label_h = self.label_image.winfo_height()
            min_size = 512
            max_size = min(label_w, label_h) - 20
            new_w = max(min_size, min(max_size, label_w))
            new_h = max(min_size, min(max_size, int(new_w / aspect_ratio)))
            image = image.resize((new_w, new_h))
            photo = ImageTk.PhotoImage(image)
            self.label_image.config(image=photo)
            self.label_image.image = photo
            with open(text_file, "r") as f:
                self.text_box.delete("1.0", END)
                self.text_box.insert(END, f.read())
                self.text_modified = False
            if not self.text_modified:
                self.saved_label.config(text="No Changes", bg="white", fg="black")
            self.display_image_index()
    
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
            with open(text_file, "w") as f:
                f.write(self.text_box.get("1.0", END))
            self.saved_label.config(text="Saved", bg="green", fg="white")

root = Tk()
app = ImageTextViewer(root)
root.mainloop()
