
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tkinter as tk
from tkinter import filedialog

# Function to open folder dialog and print selected folder
def select_original_folder():
    folder_selected = filedialog.askdirectory()  # Opens a dialog to select folder
    if folder_selected:  # If the user selects a folder
        original_folder_entry.delete(0, tk.END)  # Clear the entry field
        original_folder_entry.insert(0, folder_selected)  # Insert the selected folder into the entry field
        
def select_destination_folder():
    folder_selected = filedialog.askdirectory()  # Opens a dialog to select folder
    if folder_selected:  # If the user selects a folder
        destination_folder_entry.delete(0, tk.END)  # Clear the entry field
        destination_folder_entry.insert(0, folder_selected)  # Insert the selected folder into the entry field

#Close the app
def cancel():
    root.quit()
    root.destroy()
    
    
def sort():
    print("Sorting...")

# Create the main window (GUI)
root = tk.Tk()
root.title("Select a Folder")  # Set window title
root.geometry("600x300")  # Set window size

# Create the labels, entries, buttons
original_folder_label = tk.Label(root, text="Original Folder: ")
original_folder_entry = tk.Entry(root)
select_original_button = tk.Button(root, text="Select Folder", command=select_original_folder)
destination_folder_label = tk.Label(root, text="Destination Folder: ")
destination_folder_entry = tk.Entry(root)
select_destination_button = tk.Button(root, text="Select Folder", command=select_destination_folder)
sort_cats_label = tk.Label(root, text="Sort cats:")
sort_button = tk.Button(root, text="Sort!", command=sort)
cancel_button = tk.Button(root, text="Cancel", command=cancel)

#Row1
original_folder_label.grid(row=0, column=0, padx=5, pady=10, sticky="e")  # "e" for east (right-aligned)
original_folder_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")  # "ew" for expand horizontally
select_original_button.grid(row=0, column=2, padx=5, pady=10)

#Row 2
destination_folder_label.grid(row=1, column=0, padx=5, pady=10, sticky="e")  # "e" for east (right-aligned)
destination_folder_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")  # "ew" for expand horizontally
select_destination_button.grid(row=1, column=2, padx=5, pady=10)

#Row 3
sort_cats_label.grid(row=3, column=0, padx=5, pady=10)
sort_button.grid(row=3, column=1, padx=5, pady=10, sticky="e")
cancel_button.grid(row=3, column=2, padx=5, pady=10)


# Configure the column weights to make entry expand
root.grid_columnconfigure(1, weight=1, uniform="equal")  # Make column 1 (entry) expand

# Start the GUI main loop
root.mainloop()
