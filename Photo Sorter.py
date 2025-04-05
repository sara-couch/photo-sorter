
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from PIL.ExifTags import TAGS
import ffmpeg
import os
from pathlib import Path
import torch
from torchvision import models, transforms
from PIL import Image
import urllib.request

imageList = []

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
    
#Retrieves files and their Date Taken property
def get_files_in_folder(folder_path):
    fileList = []
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                # Determine if it's an image or video
                ext = filename.lower().split('.')[-1]
                if ext in ["jpg", "jpeg", "png", "heic"]:
                    date_taken = get_date_taken_image(file_path)
                elif ext in ["mp4", "mov", "avi", "mkv"]:
                    date_taken = get_date_taken_video(file_path)
                else:
                    date_taken = "Unknown"

                fileList.append((filename, date_taken))  # Store filename and Date Taken
    else:
        print(f"Folder '{folder_path}' not found.")
    return fileList

#Extracts the Date Taken from image metadata
def get_date_taken_image(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()  # Get EXIF metadata
        if exif_data:
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "DateTimeOriginal":
                    return value  # Format: "YYYY:MM:DD HH:MM:SS"
    except Exception as e:
        print(f"Could not read Date Taken for image {image_path}: {e}")
    return "Unknown"

#Extracts the Date Taken from video metadata using ffprobe
def get_date_taken_video(video_path):
    try:
        probe = ffmpeg.probe(video_path)
        metadata = probe.get("format", {}).get("tags", {})
        date_taken = metadata.get("creation_time", "Unknown")  # Format: "YYYY-MM-DDTHH:MM:SS"
        return date_taken.replace("T", " ")  # Convert to readable format
    except Exception as e:
        print(f"Could not read Date Taken for video {video_path}: {e}")
    return "Unknown"
    
    
#retrieves filenames and Date Taken properties
def sort():
    print("Sorting...")
    start_folder_path = Path(original_folder_entry.get())  # Get path from Entry widget
    destination_base_path = Path(destination_folder_entry.get())
    imageList = get_files_in_folder(start_folder_path)  # Get list of files with Date Taken
    for file, date in imageList:
        if date == "Unknown":
            year = "Unknown"
            source_file_path = start_folder_path / file
            destination_file_path = destination_base_path / year / file
            os.makedirs(destination_file_path.parent, exist_ok=True)
            source_file_path.rename(destination_file_path)
        else:
            year = date[:4]
            source_file_path = start_folder_path / file
            destination_file_path = destination_base_path / year / file
            os.makedirs(destination_file_path.parent, exist_ok=True)
            source_file_path.rename(destination_file_path)
        
        print(f"{file} - Date Taken: {date} - Start path: {source_file_path} Dest File path: {destination_file_path}\n")

    root.quit()
    root.destroy()

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



