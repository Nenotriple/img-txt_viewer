#region Imports


# Standard Library
import os
import time


# Standard Library - GUI
from tkinter import (
    ttk, Tk, Toplevel, messagebox,
    StringVar, BooleanVar,
    Frame, Menu, Scrollbar, PanedWindow,
    Label, Listbox,
    TclError
)


# Third-Party Libraries
from tkmarktext import TextWindow
from TkToolTip.TkToolTip import TkToolTip as Tip


# Custom Libraries
from main.scripts.OnnxTagger import OnnxTagger as OnnxTagger
import main.scripts.video_thumbnail_generator as vtg
import main.scripts.entry_helper as entry_helper
import main.scripts.HelpText as HelpText


# Type Hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region AutoTag


class AutoTag:
    def __init__(self, app: 'Main', root: 'Tk'):
        self.app = app
        self.root = root
        self.entry_helper = entry_helper

        # AutoTag
        self.onnx_model_dict = {}
        self.auto_insert_mode_var = StringVar(value="disable")
        self.batch_interrogate_images_var = BooleanVar(value=False)
        self.auto_exclude_tags_var = BooleanVar(value=False)
        self.filter_is_active = False
        self.use_viewport_as_image = BooleanVar(value=False)


    def create_auto_tag_widgets_tab4(self):
        def invert_selection():
            for i in range(self.autotag_listbox.size()):
                if self.autotag_listbox.selection_includes(i):
                    self.autotag_listbox.selection_clear(i)
                else:
                    self.autotag_listbox.select_set(i)
            self.update_auto_tag_stats_label()

        def clear_selection():
            self.autotag_listbox.selection_clear(0, 'end')
            self.update_auto_tag_stats_label()

        def all_selection():
            self.autotag_listbox.select_set(0, 'end')
            self.update_auto_tag_stats_label()

        def copy_selection():
            _, extracted_tags = self.get_auto_tag_selection()
            if extracted_tags:
                self.autotag_listbox.clipboard_clear()
                self.autotag_listbox.clipboard_append(', '.join(extracted_tags))

        # Top Frame for Buttons
        top_frame = Frame(self.app.tab4)
        top_frame.pack(fill='x')
        help_btn = ttk.Button(top_frame, text="?", takefocus=False, width=2, command=self.show_auto_tag_help)
        help_btn.pack(side='left')
        self.tag_list_stats_lbl = Label(top_frame, text="Total: 0  |  Selected: 0")
        self.tag_list_stats_lbl.pack(side='left')
        interrogate_btn = ttk.Button(top_frame, text="Interrogate", takefocus=False, command=self.interrogate_image_tags)
        interrogate_btn.pack(side='right')
        Tip.create(widget=interrogate_btn, text="Interrogate the current image using the selected settings.")
        ins_menubutton = ttk.Menubutton(top_frame, text="Auto-Insert", takefocus=False)
        ins_menubutton.pack(side='right')
        ins_menu = Menu(ins_menubutton, tearoff=0)
        ins_menu.add_radiobutton(label="Disable", variable=self.auto_insert_mode_var, value="disable")
        ins_menu.add_separator()
        ins_menu.add_radiobutton(label="Prefix", variable=self.auto_insert_mode_var, value="prefix")
        ins_menu.add_radiobutton(label="Append", variable=self.auto_insert_mode_var, value="append")
        ins_menu.add_radiobutton(label="Replace", variable=self.auto_insert_mode_var, value="replace")
        ins_menubutton.config(menu=ins_menu)
        batch_chk = ttk.Checkbutton(top_frame, text="Batch", takefocus=False, variable=self.batch_interrogate_images_var)
        batch_chk.pack(side='right')
        Tip.create(widget=batch_chk, text="Interrogate all images\nAn Auto-Insert mode must be selected")
        viewport_chk = ttk.Checkbutton(top_frame, text="Viewport", takefocus=False, variable=self.use_viewport_as_image)
        viewport_chk.pack(side='right')
        Tip.create(widget=viewport_chk, text="When enabled, the current image view will be used for interrogation instead of the original image file.\nUsed to interrogate only the visible portion.\nIgnored when using Batch Interrogate.")
        # Main Paned Window
        pane = PanedWindow(self.app.tab4, orient='horizontal', sashwidth=6, bg="#d0d0d0")
        pane.pack(fill='both', expand=True)
        # Listbox Frame
        listbox_frame = Frame(pane)
        pane.add(listbox_frame, stretch="never")
        pane.paneconfig(listbox_frame, width=200, minsize=40)
        scrollbar = Scrollbar(listbox_frame, orient="vertical")
        self.autotag_listbox = Listbox(listbox_frame, width=20, selectmode="extended", activestyle='none', exportselection=False, yscrollcommand=scrollbar.set)
        self.autotag_listbox.bind('<<ListboxSelect>>', lambda event: self.update_auto_tag_stats_label())
        self.autotag_listbox.bind("<Button-3>", lambda event: contextmenu.tk_popup(event.x_root, event.y_root))
        scrollbar.config(command=self.autotag_listbox.yview)
        self.autotag_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        # Listbox - Context Menu
        contextmenu = Menu(self.autotag_listbox, tearoff=0)
        contextmenu.add_command(label="Insert: Prefix", command=lambda: self.insert_listbox_selection(prefix=True))
        contextmenu.add_command(label="Insert: Append", command=lambda: self.insert_listbox_selection(append=True))
        contextmenu.add_command(label="Insert: Replace", command=lambda: self.insert_listbox_selection(replace=True))
        contextmenu.add_separator()
        contextmenu.add_command(label="Copy Selected Tags", command=copy_selection)
        contextmenu.add_command(label="Select All", command=all_selection)
        contextmenu.add_command(label="Invert Selection", command=invert_selection)
        contextmenu.add_command(label="Clear Selection", command=clear_selection)
        contextmenu.add_separator()
        contextmenu.add_command(label="Add to MyTags", command=lambda: self.app.text_controller.my_tags.add_to_custom_dictionary(origin="auto_tag"))
        contextmenu.add_separator()
        contextmenu.add_command(label="Add to Exclude", command=lambda: self.add_selected_tags_to_excluded_tags())
        contextmenu.add_command(label="Add to Keep", command=lambda: self.add_selected_tags_to_keep_tags())
        # Control Frame
        control_frame = Frame(pane)
        pane.add(control_frame, stretch="always")
        pane.paneconfig(control_frame, minsize=200)
        # Model Selection
        model_frame = Frame(control_frame)
        model_frame.pack(side='top', fill='x', padx=2, pady=2)
        model_label = Label(model_frame, text="Model:", width=16, anchor="w")
        model_label.pack(side='left')
        Tip.create(widget=model_label, text="Select the ONNX vision model to use for interrogation")
        self.get_onnx_model_list()
        self.autotag_model_combo = ttk.Combobox(model_frame, width=25, takefocus=False, state="readonly", values=list(self.onnx_model_dict.keys()))
        self.autotag_model_combo.pack(side='right')
        self.set_auto_tag_combo_box()
        # General Threshold
        gen_thr_frame = Frame(control_frame)
        gen_thr_frame.pack(side='top', fill='x', padx=2, pady=2)
        gen_thr_lbl = Label(gen_thr_frame, text="General Threshold:", width=16, anchor="w")
        gen_thr_lbl.pack(side='left')
        Tip.create(widget=gen_thr_lbl, text="The minimum confidence threshold for general tags")
        self.autotag_gen_threshold_spinbox = ttk.Spinbox(gen_thr_frame, takefocus=False, from_=0, to=1, increment=0.01, width=8)
        self.autotag_gen_threshold_spinbox.pack(side='right')
        self.autotag_gen_threshold_spinbox.set(self.app.onnx_tagger.general_threshold)
        # Character Threshold
        char_thr_frame = Frame(control_frame)
        char_thr_frame.pack(side='top', fill='x', padx=2, pady=2)
        char_thr_lbl = Label(char_thr_frame, text="Character Threshold:", width=16, anchor="w")
        char_thr_lbl.pack(side='left')
        Tip.create(widget=char_thr_lbl, text="The minimum confidence threshold for character tags")
        self.autotag_char_threshold_spinbox = ttk.Spinbox(char_thr_frame, takefocus=False, from_=0, to=1, increment=0.01, width=8)
        self.autotag_char_threshold_spinbox.pack(side='right')
        self.autotag_char_threshold_spinbox.set(self.app.onnx_tagger.character_threshold)
        # Max Tags
        max_tags_frame = Frame(control_frame)
        max_tags_frame.pack(side='top', fill='x', padx=2, pady=2)
        max_tags_lbl = Label(max_tags_frame, text="Max Tags:", width=16, anchor="w")
        max_tags_lbl.pack(side='left')
        Tip.create(widget=max_tags_lbl, text="The maximum number of tags that will be generated\nAdditional tags will be ignored")
        self.autotag_max_tags_spinbox = ttk.Spinbox(max_tags_frame, takefocus=False, from_=1, to=999, increment=1, width=8)
        self.autotag_max_tags_spinbox.pack(side='right')
        self.autotag_max_tags_spinbox.set(40)
        # Checkbutton Frame
        chk_frame = Frame(control_frame)
        chk_frame.pack(side='top', fill='x', padx=2, pady=2)
        # Keep (_)
        self.autotag_keep_underscore_chk = ttk.Checkbutton(chk_frame, text="Keep: _", takefocus=False, variable=self.app.onnx_tagger.keep_underscore)
        self.autotag_keep_underscore_chk.pack(side='left', anchor='w', padx=2, pady=2)
        Tip.create(widget=self.autotag_keep_underscore_chk, text="If enabled, Underscores will be kept in tags, otherwise they will be replaced with a space\n\nExample: Keep = simple_background, Replace = simple background")
        # Keep (\)
        self.autotag_keep_escape_chk = ttk.Checkbutton(chk_frame, text="Keep: \\", takefocus=False, variable=self.app.onnx_tagger.keep_escape_character)
        self.autotag_keep_escape_chk.pack(side='left', anchor='w', padx=2, pady=2)
        Tip.create(widget=self.autotag_keep_escape_chk, text="If enabled, the escape character will be kept in tags\n\nExample: Keep = \(cat\), Replace = (cat)")
        # Entry Frame
        entry_frame = Frame(control_frame)
        entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        excluded_entry_frame = Frame(entry_frame)
        excluded_entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        exclude_tags_lbl = Label(excluded_entry_frame, text="Exclude:", width=9, anchor="w")
        exclude_tags_lbl.pack(side='left')
        Tip.create(widget=exclude_tags_lbl, text="Enter tags that will be excluded from interrogation\nSeparate tags with commas")
        self.excluded_tags_entry = ttk.Entry(excluded_entry_frame, width=5)
        self.excluded_tags_entry.pack(side='left', fill='both', expand=True)
        self.entry_helper.bind_helpers(self.excluded_tags_entry)
        auto_exclude_tags_chk = ttk.Checkbutton(excluded_entry_frame, text="Auto", takefocus=False, variable=self.auto_exclude_tags_var)
        auto_exclude_tags_chk.pack(side='left', anchor='w', padx=2, pady=2)
        Tip.create(widget=auto_exclude_tags_chk, text="Automatically exclude tags that are already in the text box")
        keep_entry_frame = Frame(entry_frame)
        keep_entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        keep_tags_lbl = Label(keep_entry_frame, text="Keep:", width=9, anchor="w")
        keep_tags_lbl.pack(side='left')
        Tip.create(widget=keep_tags_lbl, text="Enter tags that will always be included in interrogation\nSeparate tags with commas")
        self.keep_tags_entry = ttk.Entry(keep_entry_frame, width=25)
        self.keep_tags_entry.pack(side='left', fill='both', expand=True)
        self.entry_helper.bind_helpers(self.keep_tags_entry)
        replace_entry_frame = Frame(entry_frame)
        replace_entry_frame.pack(side='top', fill='x', padx=2, pady=2)
        replace_tags_lbl = Label(replace_entry_frame, text="Replace:", width=9, anchor="w")
        replace_tags_lbl.pack(side='left')
        Tip.create(widget=replace_tags_lbl, text="Enter tags that will be replaced during interrogation\nSeparate tags with commas, the index of the tag in the 'Replace' entry will be used to replace the tag in the 'With' entry")
        self.replace_tags_entry = ttk.Entry(replace_entry_frame, width=1)
        self.replace_tags_entry.pack(side='left', fill='both', expand=True)
        self.entry_helper.bind_helpers(self.replace_tags_entry)
        replace_with_tags_lbl = Label(replace_entry_frame, text="With:", anchor="w")
        replace_with_tags_lbl.pack(side='left')
        Tip.create(widget=replace_with_tags_lbl, text="Enter tags that will replace the tags entered in the 'Replace' entry\nSeparate tags with commas, ensure tags match the index of the tags in the 'Replace' entry")
        self.replace_with_tags_entry = ttk.Entry(replace_entry_frame, width=1)
        self.replace_with_tags_entry.pack(side='left', fill='both', expand=True)
        self.entry_helper.bind_helpers(self.replace_with_tags_entry)
        # Selection Button Frame
        btn_frame = ttk.LabelFrame(control_frame, text="Selection")
        btn_frame.pack(side="bottom", fill='both', padx=2)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        # Selection Buttons
        ins_sel_prefix_btn = ttk.Button(btn_frame, text="Prefix", command=lambda: self.insert_listbox_selection(prefix=True))
        ins_sel_prefix_btn.grid(row=0, column=0, sticky='ew', pady=2)
        ins_sel_prefix_btn.bind("<Button-3>", lambda event: self.insert_listbox_selection(replace=True))
        Tip.create(widget=ins_sel_prefix_btn, text="Insert the selected tags at the START of the text box\nRight-click to replace the current tags")
        ins_sel_append_btn = ttk.Button(btn_frame, text="Append", command=lambda: self.insert_listbox_selection(append=True))
        ins_sel_append_btn.grid(row=0, column=1, sticky='ew', pady=2)
        ins_sel_append_btn.bind("<Button-3>", lambda event: self.insert_listbox_selection(replace=True))
        Tip.create(widget=ins_sel_append_btn, text="Insert the selected tags at the END of the text box\nRight-click to replace the current tags")
        copy_btn = ttk.Button(btn_frame, text="Copy", command=copy_selection)
        copy_btn.grid(row=0, column=2, sticky='ew', pady=2)
        Tip.create(widget=copy_btn, text="Copy the selected tags to the clipboard")
        all_btn = ttk.Button(btn_frame, text="All", command=all_selection)
        all_btn.grid(row=1, column=0, sticky='ew', pady=2)
        Tip.create(widget=all_btn, text="Select all tags")
        invert_btn = ttk.Button(btn_frame, text="Invert", command=invert_selection)
        invert_btn.grid(row=1, column=1, sticky='ew', pady=2)
        Tip.create(widget=invert_btn, text="Invert the current selection")
        clear_btn = ttk.Button(btn_frame, text="Clear", command=clear_selection)
        clear_btn.grid(row=1, column=2, sticky='ew', pady=2)
        Tip.create(widget=clear_btn, text="Clear the current selection")
        # Help Window
        self.help_window = TextWindow(master=self.root)


    def show_auto_tag_help(self):
        self.help_window.open_window(text=HelpText.AUTOTAG_HELP, title="Auto-Tag Help", geometry="600x500", icon=self.app.blank_image)


    def update_auto_tag_stats_label(self):
        total_tags = self.autotag_listbox.size()
        selected_tags = len(self.autotag_listbox.curselection())
        selected_tags_padded = str(selected_tags).zfill(len(str(total_tags)))
        self.tag_list_stats_lbl.config(text=f"Total: {total_tags}  |  Selected: {selected_tags_padded}")


    def insert_listbox_selection(self, prefix=False, append=False, replace=False):
        selected_items, extracted_tags = self.get_auto_tag_selection()
        if not selected_items:
            return
        current_text = self.app.text_box.get("1.0", "end-1c").strip(', ')
        if replace:
            new_text = ', '.join(extracted_tags)
        elif prefix:
            new_text = ', '.join(extracted_tags) + ', ' + current_text
        elif append:
            new_text = current_text + ', ' + ', '.join(extracted_tags)
        else:
            new_text = ', '.join(extracted_tags)
        new_text = new_text.strip(', ')
        self.app.text_box.delete("1.0", "end")
        self.app.text_box.insert("1.0", new_text)


    def get_auto_tag_selection(self):
        selected_items = [self.autotag_listbox.get(i) for i in self.autotag_listbox.curselection()]
        extracted_tags = [item.split(': ', 1)[-1] for item in selected_items]
        return selected_items, extracted_tags


    def update_tag_options(self, current_tags=None):
        self.app.onnx_tagger.exclude_tags.clear()
        self.app.onnx_tagger.keep_tags.clear()
        self.app.onnx_tagger.replace_tag_dict.clear()
        excluded_tags = [tag.strip().replace(' ', '_') for tag in self.excluded_tags_entry.get().strip().split(',')]
        if self.auto_exclude_tags_var.get():
            if current_tags is not None:
                source_tags = current_tags.strip()
            else:
                source_tags = self.app.text_box.get("1.0", "end-1c").strip()
            excluded_tags.extend(tag.strip().replace(' ', '_') for tag in source_tags.split(','))
        self.app.onnx_tagger.exclude_tags = [tag.strip() for tag in excluded_tags if tag.strip()]
        keep_tags = self.keep_tags_entry.get().strip().split(',')
        self.app.onnx_tagger.keep_tags = [tag.strip() for tag in keep_tags if tag.strip()]
        replace_tags = self.replace_tags_entry.get().strip().split(',')
        replace_with_tags = self.replace_with_tags_entry.get().strip().split(',')
        self.app.onnx_tagger.replace_tag_dict = {tag.strip(): replace_with_tags[i].strip() for i, tag in enumerate(replace_tags) if tag.strip() and i < len(replace_with_tags) and replace_with_tags[i].strip()}


    def update_tag_thresholds(self):
        def validate_spinbox_value(spinbox, default_value, from_, to):
            try:
                value = float(spinbox.get())
                if from_ <= value <= to:
                    return value
            except ValueError:
                pass
            spinbox.set(default_value)
            return default_value

        validate_spinbox_value(self.autotag_max_tags_spinbox, 40, 1, 999)
        self.app.onnx_tagger.general_threshold = validate_spinbox_value(self.autotag_gen_threshold_spinbox, 0.35, 0, 1)
        self.app.onnx_tagger.character_threshold = validate_spinbox_value(self.autotag_char_threshold_spinbox, 0.85, 0, 1)


    def interrogate_image_tags(self):
        self.app.text_notebook.select(self.app.tab4)
        if self.batch_interrogate_images_var.get():
            self.batch_interrogate_images()
            return
        if self.use_viewport_as_image.get():
            image_path = self.app.primary_display_image.get_visible_image()
        else:
            image_path = self.app.image_files[self.app.current_index]
        try:
            if image_path.lower().endswith('.mp4'):
                image_path = self.app.video_player.get_current_frame()
        except AttributeError:
            pass
        selected_model_path = self.onnx_model_dict.get(self.autotag_model_combo.get())
        if not selected_model_path or not os.path.exists(selected_model_path):
            if messagebox.askyesno("Error", f"Model file not found: {selected_model_path}\n\nWould you like to view the Auto-Tag Help?"):
                self.show_auto_tag_help()
            return
        self.update_tag_thresholds()
        self.update_tag_options()
        tag_list, tag_dict = self.app.onnx_tagger.tag_image(image_path, model_path=selected_model_path)
        max_tags = int(self.autotag_max_tags_spinbox.get())
        tag_list = tag_list[:max_tags]
        tag_dict = {k: v for k, v in list(tag_dict.items())[:max_tags]}
        self.populate_auto_tag_listbox(tag_dict)
        self.auto_insert_tags(tag_list)


    def populate_auto_tag_listbox(self, tag_dict):
        self.autotag_listbox.delete(0, "end")
        if not tag_dict:
            self.update_auto_tag_stats_label()
            return
        max_length = max(len(f"{float(confidence):.2f}") for confidence, _ in tag_dict.values())
        for tag, (confidence, category) in tag_dict.items():
            padded_score = f"{float(confidence):.2f}".ljust(max_length, '0')
            self.autotag_listbox.insert("end", f" {padded_score}: {tag}")
            if category == "character":
                self.autotag_listbox.itemconfig("end", {'fg': '#148632'})
            if category == "keep":
                self.autotag_listbox.itemconfig("end", {'fg': '#c00004'})
        self.update_auto_tag_stats_label()


    def auto_insert_tags(self, tags):
        mode = self.auto_insert_mode_var.get()
        if mode == "disable":
            return
        tags_str = ', '.join(tags)
        current_text = self.app.text_box.get("1.0", "end-1c")
        if mode == "prefix":
            new_text = tags_str + ', ' + current_text if current_text else tags_str
        elif mode == "append":
            new_text = current_text + ', ' + tags_str if current_text else tags_str
        elif mode == "replace":
            new_text = tags_str
        else:
            return
        self.app.text_box.delete("1.0", "end")
        self.app.text_box.insert("1.0", new_text)


    def get_onnx_model_list(self):
        model_dict = {}
        for onnx_model_path, dirs, files in os.walk(self.app.onnx_models_dir):
            if "model.onnx" in files and "selected_tags.csv" in files:
                folder_name = os.path.basename(onnx_model_path)
                model_file_path = os.path.join(onnx_model_path, "model.onnx")
                model_dict[folder_name] = model_file_path
        self.onnx_model_dict = model_dict


    def set_auto_tag_combo_box(self):
        try:
            first_model_key = next(iter(self.onnx_model_dict.keys()), None)
        except Exception:
            first_model_key = None
        if first_model_key:
            self.autotag_model_combo.set(first_model_key)


    def batch_interrogate_images(self):
        def stop_batch_process():
            self.stop_batch = True
            popup.destroy()
            messagebox.showinfo("Batch Interrogate", f"Batch interrogation stopped\n\n{index} out of {total_images} images were interrogated")
        popup = None
        if self.auto_insert_mode_var.get() == "disable":
            messagebox.showinfo("Batch Interrogate", "Auto-Insert must be enabled to use Batch Interrogate")
            return
        try:
            if not messagebox.askyesno("Batch Interrogate", "Interrogate all images in the current directory?"):
                return
            self.stop_batch = False
            popup = Toplevel(self.root)
            popup.iconbitmap(self.app.icon_path)
            popup.title("Batch Interrogate")
            popup.geometry("300x150")
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() - popup.winfo_reqwidth()) // 2
            y = (self.root.winfo_screenheight() - popup.winfo_reqheight()) // 2
            popup.geometry(f"+{x}+{y}")
            label = Label(popup, text="Starting...")
            label.pack(expand=True)
            progress = ttk.Progressbar(popup, orient="horizontal", length=200, mode="determinate")
            progress.pack(pady=10)
            stop_button = ttk.Button(popup, text="Stop", command=stop_batch_process)
            stop_button.pack(pady=10)
            popup.transient(self.root)
            popup.grab_set()
            self.root.update()
            popup.protocol("WM_DELETE_WINDOW", stop_batch_process)
            selected_model_path = self.onnx_model_dict.get(self.autotag_model_combo.get())
            if not selected_model_path or not os.path.exists(selected_model_path):
                if messagebox.askyesno("Error", f"Model file not found: {selected_model_path}\n\nWould you like to view the Auto-Tag Help?"):
                    self.show_auto_tag_help()
                popup.destroy()
                return
            self.update_tag_thresholds()
            max_tags = int(self.autotag_max_tags_spinbox.get())
            total_images = len(self.app.image_files)
            progress["maximum"] = total_images
            start_time = time.time()
            for index, (image_path, text_file_path) in enumerate(zip(self.app.image_files, self.app.text_files), start=1):
                if self.stop_batch:
                    break
                current_text = ""
                if os.path.exists(text_file_path):
                    with open(text_file_path, "r", encoding="utf-8") as f:
                        current_text = f.read().strip()
                if self.auto_exclude_tags_var.get() and self.batch_interrogate_images_var.get():
                    self.update_tag_options(current_tags=current_text)
                else:
                    self.update_tag_options()
                if image_path.lower().endswith('.mp4'):
                    video_frame = vtg.get_video_frame(image_path, timestamp_seconds=2.0)
                    if video_frame:
                        tag_list, tag_dict = self.app.onnx_tagger.tag_image(video_frame, model_path=selected_model_path)
                    else:
                        tag_list, tag_dict = [], {}  # Video frame could not be extracted
                        continue
                else:
                    tag_list, tag_dict = self.app.onnx_tagger.tag_image(image_path, model_path=selected_model_path)
                tag_list = tag_list[:max_tags]
                tag_dict = {k: v for k, v in list(tag_dict.items())[:max_tags]}
                self.auto_insert_batch_tags(tag_list, text_file_path)
                elapsed_time = time.time() - start_time
                avg_time_per_image = elapsed_time / index if index > 0 else 0
                remaining_images = total_images - index
                eta_seconds = avg_time_per_image * remaining_images
                eta_formatted = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
                label.config(text=f"Working... {index} out of {total_images}\nETA: {eta_formatted}")
                progress["value"] = index
                self.root.update()
            popup.destroy()
            if not self.stop_batch:
                messagebox.showinfo("Batch Interrogate", f"Batch interrogation complete\n\n{total_images} images were interrogated")
        except TclError:
            pass
        finally:
            self.app.refresh_text_box()
            if popup:
                popup.destroy()


    def auto_insert_batch_tags(self, tags, text_file_path):
        mode = self.auto_insert_mode_var.get()
        if mode == "disable":
            return
        tags_str = ', '.join(tags)
        current_text = ''
        if os.path.exists(text_file_path):
            with open(text_file_path, 'r', encoding='utf-8') as f:
                current_text = f.read().strip()
        else:
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write('')
        if mode == "prefix":
            new_text = tags_str + ', ' + current_text if current_text else tags_str
        elif mode == "append":
            new_text = current_text + ', ' + tags_str if current_text else tags_str
        elif mode == "replace":
            new_text = tags_str
        else:
            return
        new_text = new_text.strip(', ')
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write(new_text)


    def add_selected_tags_to_excluded_tags(self):
        selected_items, extracted_tags = self.get_auto_tag_selection()
        if not extracted_tags:
            return
        # Strip escape characters from extracted tags
        extracted_tags = [tag.replace('\\', '') for tag in extracted_tags]
        current_excluded = self.excluded_tags_entry.get().strip()
        excluded_list = [tag.strip() for tag in current_excluded.split(',') if tag.strip()] if current_excluded else []
        # Strip escape characters from existing excluded tags
        excluded_list = [tag.replace('\\', '') for tag in excluded_list]
        for tag in extracted_tags:
            if tag not in excluded_list:
                excluded_list.append(tag)
        self.excluded_tags_entry.delete(0, 'end')
        self.excluded_tags_entry.insert(0, ', '.join(excluded_list))


    def add_selected_tags_to_keep_tags(self):
        selected_items, extracted_tags = self.get_auto_tag_selection()
        if not extracted_tags:
            return
        # Strip escape characters from extracted tags
        extracted_tags = [tag.replace('\\', '') for tag in extracted_tags]
        current_keep = self.keep_tags_entry.get().strip()
        keep_list = [tag.strip() for tag in current_keep.split(',') if tag.strip()] if current_keep else []
        # Strip escape characters from existing keep tags
        keep_list = [tag.replace('\\', '') for tag in keep_list]
        for tag in extracted_tags:
            if tag not in keep_list:
                keep_list.append(tag)
        self.keep_tags_entry.delete(0, 'end')
        self.keep_tags_entry.insert(0, ', '.join(keep_list))


#endregion
