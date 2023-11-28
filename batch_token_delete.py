"""
########################################
#                                      #
#          batch_token_delete          #
#                                      #
#   Version : v1.04                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
 This script reads the contents of all text files in a selected directory, creating a list of tokens, and their occurence.

 Tokens are each listed on a separate button beside their occurence, allowing you to easily click a token and delete it from all text files.
 Or batch delete using a "less than or equal to" threshold.

 Expected text format: "token, token 2, another token here, ..."

"""

################################################################################################################################################
################################################################################################################################################
#         #
# Imports #
#         #

import os
import sys
import ctypes
import tkinter as tk
from collections import Counter
from tkinter import messagebox, simpledialog, filedialog

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

def display_tokens(token_dict, directory, scrollable_frame, filter_text=''):
    if sort_order == 'alpha':
        sorted_token_items = sorted(token_dict.items(), key=lambda item: item[0])
    else:
        sorted_token_items = sorted(token_dict.items(), key=lambda item: item[1], reverse=True)
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    scrollable_frame.canvas.configure(scrollregion=scrollable_frame.canvas.bbox("all"))
    scrollable_frame.canvas.yview_moveto(0)
    for token, count in sorted_token_items:
        if filter_text and not fuzzy_search(filter_text.lower(), token.lower()):
            continue
        pair_frame = tk.Frame(scrollable_frame)
        label = tk.Label(pair_frame, text=f" x{count} ---------------", width=6, anchor="w")
        label.pack(side=tk.LEFT)
        button = tk.Button(pair_frame, text=f"{token}", width=55, anchor="w", command=lambda t=token: (delete_token(directory, t, filter_text), display_tokens(count_tokens(directory), directory, scrollable_frame, filter_text)))
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

def count_tokens(directory):
    token_dict = Counter()
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as file:
                lines = file.readlines()
                for line in lines:
                    tokens = line.strip().split(',')
                    for token in tokens:
                        token_dict[token.strip()] += 1
    return token_dict

def delete_token(directory, token, filter_text='', confirm_prompt=True):
    parent = tk.Toplevel()
    parent.withdraw()
    if confirm_prompt:
        message = "Are you sure you want to delete the token\n\n'%s'" % (token)
        result = tk.messagebox.askquestion("Delete Token", message, parent=parent)
        if result != "yes":
            return
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as file:
                lines = file.read().replace('\n', '')
            with open(os.path.join(directory, filename), 'w') as file:
                tokens = lines.strip().split(',')
                tokens = [t for t in tokens if t.strip() != token]
                new_line = ','.join(tokens)
                if filter_text and not fuzzy_search(filter_text.lower(), lines.lower()):
                    file.write(lines)
                else:
                    new_line = cleanup_text(new_line)  # Call cleanup_text here
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

def batch_delete(directory, count_threshold, scrollable_frame, max_display_tokens=150):
    token_dict = count_tokens(directory)
    tokens_to_delete = [token for token, count in token_dict.items() if count <= count_threshold]
    sorted_tokens_to_delete = sorted(tokens_to_delete)
    limited_tokens_to_display = sorted_tokens_to_delete[:max_display_tokens]
    tokens_message = ', '.join(limited_tokens_to_display)
    message = f"Found {len(sorted_tokens_to_delete)} tokens:\n\n{tokens_message}\n\n"
    if len(sorted_tokens_to_delete) > max_display_tokens:
        message += f"... and {len(sorted_tokens_to_delete) - max_display_tokens} more tokens.\n\n"
    message += "Are you sure you want to delete them?"
    if not sorted_tokens_to_delete:
        messagebox.showinfo("No Tokens Found", "No tokens found that meet the given criteria.")
        return
    confirm = messagebox.askyesno("Delete Tokens?", message)
    if confirm:
        for token in sorted_tokens_to_delete:
            delete_token(directory, token, confirm_prompt=False)
        display_tokens(count_tokens(directory), directory, scrollable_frame)

def ask_count_threshold(directory, scrollable_frame, root):
    count_threshold = simpledialog.askinteger("Delete all less than or equal to", "\tEnter the count threshold\t\t", parent=root)
    if count_threshold is not None:
        batch_delete(directory, count_threshold, scrollable_frame)

def delete_selected_tokens(directory, scrollable_frame, filter_text=''):
    parent = tk.Toplevel()
    parent.withdraw()
    token_count = 0
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, tk.Frame):
            checkbox = widget.winfo_children()[-1]
            if checkbox.var.get():
                token_count += 1
    if messagebox.askokcancel("Confirmation", f"Are you sure you want to delete {token_count} tokens?"):
        for widget in scrollable_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                checkbox = widget.winfo_children()[-1]
                if checkbox.var.get():
                    token = widget.winfo_children()[1].cget("text")
                    delete_token(directory, token, filter_text, confirm_prompt=False)
    parent.destroy()
    display_tokens(count_tokens(directory), directory, scrollable_frame, filter_text)

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

def toggle_token_order(token_dict, directory, scrollable_frame, filter_text=''):
    global sort_order
    if sort_order == 'count':
        sort_order = 'alpha'
    else:
        sort_order = 'count'
    display_tokens(token_dict, directory, scrollable_frame, filter_text)

def filter_tokens(event, directory, scrollable_frame):
    filter_text = event.widget.get()
    token_dict = count_tokens(directory)
    filtered_dict = {k: v for k, v in token_dict.items() if fuzzy_search(filter_text.lower(), k.lower())}
    display_tokens(filtered_dict, directory, scrollable_frame, filter_text)

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
#      #
# Main #
#      #

def main(directory=None):

    # Get directory
    if not directory or not os.path.isdir(directory):
        root = tk.Tk()
        root.withdraw()
        directory = filedialog.askdirectory()
        root.destroy()
        if not directory:
            return

    # Initialize the root window
    root = tk.Tk()
    root.title(f"Token List: {directory}")
    window_width = 490
    window_height = 800
    position_right = root.winfo_screenwidth()//2 - window_width//2
    position_top = root.winfo_screenheight()//2 - window_height//2
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    root.minsize(400, 100)
    root.maxsize(490, 2000)

    # Count tokens in the directory
    token_dict = count_tokens(directory)

    # Create the menubar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Add options to the menubar
    menubar.add_command(label="Change Sort", command=lambda: toggle_token_order(token_dict, directory, scrollable_frame))
    menubar.add_separator()
    menubar.add_command(label="Delete ≤", command=lambda: ask_count_threshold(directory, scrollable_frame, root))
    menubar.add_separator()
    menubar.add_command(label="Delete Selected", command=lambda: delete_selected_tokens(directory, scrollable_frame))

    # Create the filter entry
    filter_entry = tk.Entry(root)
    filter_entry.insert(0, "Filter tokens here (fuzzy search)")
    filter_entry.bind("<FocusIn>", lambda args: filter_entry.delete('0', 'end') if filter_entry.get() == "Filter tokens here (fuzzy search)" else None)
    filter_entry.pack(side="top", fill="x", ipady=1)
    filter_entry.bind("<KeyRelease>", lambda event: filter_tokens(event, directory, scrollable_frame))

    # Create the frame and canvas for displaying tokens
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)
    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.canvas = canvas
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Display tokens and Start main loop
    display_tokens(token_dict, directory, scrollable_frame)
    root.mainloop()

# This starts the main function. If a command-line argument is provided, it uses that. If "None", it opens a file dialog.
if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

################################################################################################################################################
################################################################################################################################################
#           #
# Changelog #
#           #

'''

v1.04 changes:

  - New:
    - The window now opens in the center of the screen.

<br>

  - Fixed:
    -

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
