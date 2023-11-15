"""
########################################
#                                      #
#          batch_token_delete          #
#                                      #
#   Version : v1.02                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
 This script reads the contents of all text files in a selected directory, creating a list of tokens, and their occurence.
 Tokens are each listed on a separate button beside their occurence, allowing you to easily click a token and delete it from all text files. Or batch delete using a "less than or equal to" threshold.
 This script is dependent on the function "cleanup_all_text_files" found in img-txt_viewer.pyw to fix some minor text errors.

 Expected text format: "token, token 2, another token here, ..."

"""

################################################################################################################################################
################################################################################################################################################
#         #
# Imports #
#         #

import os
import sys
import tkinter as tk
from collections import Counter
from tkinter import messagebox, simpledialog, filedialog

################################################################################################################################################
################################################################################################################################################
#           #
# Variables #
#           #

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
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(pair_frame, variable=var)
        checkbox.var = var
        checkbox.pack(side=tk.RIGHT)
        checkbox.bind('<Button-3>', lambda event: toggle_all_checkboxes(event, scrollable_frame))
        pair_frame.pack(side=tk.TOP, pady=2)

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
                    file.write(new_line)
    parent.destroy()

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

################################################################################################################################################
################################################################################################################################################
#              #
# Batch Delete #
#              #

def batch_delete(directory, count_threshold, scrollable_frame):
    token_dict = count_tokens(directory)
    tokens_to_delete = [token for token, count in token_dict.items() if count <= count_threshold]
    if not tokens_to_delete:
      messagebox.showinfo("No Tokens Found", "No tokens found that meet the given criteria.")
      return
    confirm = messagebox.askyesno("Delete Tokens?", f"Found {len(tokens_to_delete)} tokens. Are you sure you want to delete them?")
    if confirm:
      for token in tokens_to_delete:
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
    root.geometry("490x800")
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

#- v1.02 changes:
#  - New:
#    - You can now select multiple tokens then delete them all at once.

#  - Fixed:
#    - Newlines should be properly handled/deleted now.

################################################################################################################################################
################################################################################################################################################
#      #
# todo #
#      #

#- Todo
#  -

#- Tofix
#  -
#
