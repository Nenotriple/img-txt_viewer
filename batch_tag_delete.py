"""
########################################
#                                      #
#          batch_tag_delete            #
#                                      #
#   Version : v1.05                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
 This script reads the contents of all text files in a selected directory, creating a list of tags, and their occurence.

 tags are each listed on a separate button beside their occurence, allowing you to easily click a tag and delete it from all text files.
 Or batch delete using a "less than or equal to" threshold.

 Expected text format: "tag, tag 2, another tag here, ..."

"""

################################################################################################################################################
################################################################################################################################################
#         #
# Imports #
#         #

import os
import sys
import ctypes
import shutil
import tkinter as tk
from collections import Counter
from tkinter import messagebox, simpledialog, filedialog, TclError

################################################################################################################################################
################################################################################################################################################
#           #
# Variables #
#           #

# Used to create a group ID so app shares the parent icon, and groups with the main window in the taskbar.
myappid = 'ImgTxtViewer.Nenotriple'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

sort_order = 'count'

################################################################################################################################################
################################################################################################################################################
#                   #
# Primary Functions #
#                   #

def display_tags(tag_dict, directory, scrollable_frame, filter_text=''):
    if sort_order == 'alpha':
        sorted_tag_items = sorted(tag_dict.items(), key=lambda item: item[0])
    else:
        sorted_tag_items = sorted(tag_dict.items(), key=lambda item: item[1], reverse=True)
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    scrollable_frame.canvas.configure(scrollregion=scrollable_frame.canvas.bbox("all"))
    scrollable_frame.canvas.yview_moveto(0)
    for tag, count in sorted_tag_items:
        if filter_text and not fuzzy_search(filter_text.lower(), tag.lower()):
            continue
        pair_frame = tk.Frame(scrollable_frame)
        label = tk.Label(pair_frame, text=f" x{count} ---------------", width=6, anchor="w")
        label.pack(side=tk.LEFT)
        button = tk.Button(pair_frame, text=f"{tag}", width=55, anchor="w", command=lambda t=tag: (delete_tag(directory, t, filter_text), display_tags(count_tags(directory), directory, scrollable_frame, filter_text)))
        button.pack(side=tk.LEFT)
        enter, leave = create_hover_effect(button, "#ffcac9")
        button.bind("<Enter>", enter)
        button.bind("<Leave>", leave)
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(pair_frame, variable=var)
        checkbox.var = var
        checkbox.pack(side=tk.RIGHT)
        enter, leave = create_hover_effect(checkbox, "#e5f3ff")
        checkbox.bind("<Enter>", enter)
        checkbox.bind("<Leave>", leave)
        checkbox.bind('<Button-3>', lambda event: toggle_all_checkboxes(event, scrollable_frame))
        pair_frame.pack(side=tk.TOP, pady=2)

def count_tags(directory):
    tag_dict = Counter()
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as file:
                lines = file.readlines()
                for line in lines:
                    tags = line.strip().split(',')
                    for tag in tags:
                        tag_dict[tag.strip()] += 1
    return tag_dict

def delete_tag(directory, tag, filter_text='', confirm_prompt=True):
    parent = tk.Toplevel()
    parent.withdraw()
    if confirm_prompt:
        message = "Are you sure you want to delete the tag\n\n'%s'" % (tag)
        result = tk.messagebox.askquestion("Delete tag", message, parent=parent)
        if result != "yes":
            return
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as file:
                lines = file.read().replace('\n', '')
            with open(os.path.join(directory, filename), 'w') as file:
                tags = lines.strip().split(',')
                tags = [t for t in tags if t.strip() != tag]
                new_line = ','.join(tags)
                if filter_text and not fuzzy_search(filter_text.lower(), lines.lower()):
                    file.write(lines)
                else:
                    new_line = cleanup_text(new_line)
                    file.write(new_line)
    parent.destroy()

def cleanup_text(text):
        import re
        text = remove_duplicates(text)
        text = re.sub(r'\.\s', ', ', text)  # replace period and space with comma and space
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

def remove_duplicates(text):
    text = text.lower().split(',')
    text = [item.strip() for item in text]
    text = list(dict.fromkeys(text))
    text = ','.join(text)
    return text

def create_hover_effect(widget, hover_color):
    return (lambda event: widget.config(bg=hover_color), lambda event: widget.config(bg="SystemButtonFace"))

################################################################################################################################################
################################################################################################################################################
#              #
# Batch Delete #
#              #

def batch_delete(directory, count_threshold, scrollable_frame, max_display_tags=150):
    tag_dict = count_tags(directory)
    tags_to_delete = [tag for tag, count in tag_dict.items() if count <= count_threshold]
    sorted_tags_to_delete = sorted(tags_to_delete)
    limited_tags_to_display = sorted_tags_to_delete[:max_display_tags]
    tags_message = ', '.join(limited_tags_to_display)
    message = f"Found {len(sorted_tags_to_delete)} tags:\n\n{tags_message}\n\n"
    if len(sorted_tags_to_delete) > max_display_tags:
        message += f"... and {len(sorted_tags_to_delete) - max_display_tags} more tags.\n\n"
    message += "Are you sure you want to delete them?"
    if not sorted_tags_to_delete:
        messagebox.showinfo("No tags Found", "No tags found that meet the given criteria.")
        return
    confirm = messagebox.askyesno("Delete tags?", message)
    if confirm:
        for tag in sorted_tags_to_delete:
            delete_tag(directory, tag, confirm_prompt=False)
        display_tags(count_tags(directory), directory, scrollable_frame)

def ask_count_threshold(directory, scrollable_frame, root):
    count_threshold = simpledialog.askinteger("Delete all less than or equal to", "\tEnter the count threshold\t\t", parent=root)
    if count_threshold is not None:
        batch_delete(directory, count_threshold, scrollable_frame)

def delete_selected_tags(directory, scrollable_frame, filter_text=''):
    parent = tk.Toplevel()
    parent.withdraw()
    tag_count = 0
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, tk.Frame):
            checkbox = widget.winfo_children()[-1]
            if checkbox.var.get():
                tag_count += 1
    if messagebox.askokcancel("Confirmation", f"Are you sure you want to delete {tag_count} tags?"):
        for widget in scrollable_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                checkbox = widget.winfo_children()[-1]
                if checkbox.var.get():
                    tag = widget.winfo_children()[1].cget("text")
                    delete_tag(directory, tag, filter_text, confirm_prompt=False)
    parent.destroy()
    display_tags(count_tags(directory), directory, scrollable_frame, filter_text)

def toggle_all_checkboxes(event, scrollable_frame):
    clicked_checkbox_state = event.widget.var.get()
    new_state = not clicked_checkbox_state
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, tk.Frame):
            for sub_widget in widget.winfo_children():
                if isinstance(sub_widget, tk.Checkbutton):
                    sub_widget.var.set(new_state)

################################################################################################################################################
################################################################################################################################################
#         #
# Sorting #
#         #

def toggle_tag_order(tag_dict, directory, scrollable_frame, filter_text=''):
    global sort_order
    if sort_order == 'count':
        sort_order = 'alpha'
    else:
        sort_order = 'count'
    display_tags(tag_dict, directory, scrollable_frame, filter_text)

def filter_tags(event, directory, scrollable_frame):
    filter_text = event.widget.get()
    tag_dict = count_tags(directory)
    filtered_dict = {k: v for k, v in tag_dict.items() if fuzzy_search(filter_text.lower(), k.lower())}
    display_tags(filtered_dict, directory, scrollable_frame, filter_text)

def fuzzy_search(str1, str2):
    m = len(str1)
    n = len(str2)
    j = 0
    i = 0
    while j < m and i < n:
      if str1[j] == str2[i]:
        j = j+1
      i = i + 1
    return j == m

################################################################################################################################################
################################################################################################################################################
#                #
# Manage Backups #
#                #

def backup_files(directory):
    backup_directory = os.path.join(directory, "text_backup")
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            shutil.copy2(os.path.join(directory, filename), os.path.join(backup_directory, filename))

def restore_backup(directory, scrollable_frame):
    backup_directory = os.path.join(directory, "text_backup")
    for filename in os.listdir(backup_directory):
        if filename.endswith(".txt"):
            shutil.copy(os.path.join(backup_directory, filename), os.path.join(directory, filename))
    display_tags(count_tags(directory), directory, scrollable_frame)

def on_closing(directory, root):
    backup_directory = os.path.join(directory, "text_backup")
    if os.path.exists(backup_directory):
        shutil.rmtree(backup_directory)
    root.destroy()

################################################################################################################################################
################################################################################################################################################
#      #
# Main #
#      #

def main(directory=None):
    # If directory is not provided or is not valid, ask user to select a directory
    if not directory or not os.path.isdir(directory):
        root = tk.Tk()
        root.withdraw()
        directory = filedialog.askdirectory()
        root.destroy()
        if not directory:
            return

    # Initialize root window
    root = tk.Tk()
    root.title(f"tag List: {directory}")
    window_width = 490
    window_height = 800
    position_right = root.winfo_screenwidth() // 2 - window_width // 2
    position_top = root.winfo_screenheight() // 2 - window_height // 2
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    root.minsize(400, 100)
    root.maxsize(490, 2000)
    root.focus_force()

    # Count tags in the directory
    tag_dict = count_tags(directory)

    # Initialize last modification times
    last_modification_times = {}

    # Function to refresh the display
    def refresh():
        nonlocal last_modification_times
        txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
        modified = False
        for file in txt_files:
            path = os.path.join(directory, file)
            mod_time = os.path.getmtime(path)
            if file not in last_modification_times or mod_time > last_modification_times[file]:
                last_modification_times[file] = mod_time
                modified = True
        if modified:
            display_tags(count_tags(directory), directory, scrollable_frame)
        root.after(1000, refresh)

    # Function to set the icon
    def set_icon():
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(__file__)
        icon_path = os.path.join(application_path, "icon.ico")
        try:
            root.iconbitmap(icon_path)
        except TclError:
            pass

    # Initialize menubar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Add commands to the menubar
    menubar.add_command(label="Change Sort", command=lambda: toggle_tag_order(tag_dict, directory, scrollable_frame))
    menubar.add_separator()
    menubar.add_command(label="Delete ≤", command=lambda: ask_count_threshold(directory, scrollable_frame, root))
    menubar.add_separator()
    menubar.add_command(label="Delete Selected", command=lambda: delete_selected_tags(directory, scrollable_frame))
    menubar.add_separator()
    menubar.add_command(label="Undo All", command=lambda: restore_backup(directory, scrollable_frame))

    # Initialize filter entry
    filter_entry = tk.Entry(root)
    filter_entry.insert(0, "Filter tags here (fuzzy search)")
    filter_entry.bind("<FocusIn>", lambda args: filter_entry.delete('0', 'end') if filter_entry.get() == "Filter tags here (fuzzy search)" else None)
    filter_entry.pack(side="top", fill="x", ipady=1)
    filter_entry.bind("<KeyRelease>", lambda event: filter_tags(event, directory, scrollable_frame))

    # Initialize frame, canvas, scrollbar, and scrollable frame
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)
    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.canvas = canvas
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Display tags, backup files, and set closing protocol
    display_tags(tag_dict, directory, scrollable_frame)
    backup_files(directory)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(directory, root))

    # Refresh display and set icon
    refresh()
    set_icon()

    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    # If a command line argument is provided, it is used as the directory. Otherwise, None is passed to the main function.
    main(sys.argv[1] if len(sys.argv) > 1 else None)

################################################################################################################################################
################################################################################################################################################
#           #
# Changelog #
#           #

'''

v1.05 changes:

  - New:
    - `Undo All` You can now restore the text files to their original state from when Batch Tag Delete was launched. [#7d574a8][7d574a8]
    - Implement Auto-Refresh Feature. [#4f78be5][4f78be5]
    - Renamed to: Batch Tag Delete [#f7e9389][f7e9389]

<br>

  - Fixed:
    - Properly set app icon. [#358ee1d][358ee1d]

  - Other:

[7d574a8]: https://github.com/Nenotriple/img-txt_viewer/commit/7d574a85b300f60bd01015aeadfca4e3d38cdf71
[4f78be5]: https://github.com/Nenotriple/img-txt_viewer/commit/4f78be5df917f6af19796591fbbff05e64f8e944
[f7e9389]: https://github.com/Nenotriple/img-txt_viewer/commit/f7e9389d77ed86508ccb4f9705c3d709eb00ab0e

[358ee1d]: https://github.com/Nenotriple/img-txt_viewer/commit/358ee1d93636d0001a3e9b96d72ba3230697fcdd

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
  -

'''
