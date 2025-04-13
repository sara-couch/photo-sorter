import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import ffmpeg
import os
from pathlib import Path
import torch
from torchvision import transforms #models is ResNet, transforms is preprocessing
from torchvision.models import resnet50, ResNet50_Weights


# Load pre-trained ResNet50 model once globally. Remember, models comes from torchvision
weights = ResNet50_Weights.DEFAULT
resnet_model = resnet50(weights=weights)
resnet_model.eval()  # Set to evaluation mode rather than training mode

#why tf ResNet50 has such weird pretrained? Might consider a different model in the future
cat_labels = [
    "Egyptian cat", "cat", "tabby cat", "tiger cat", "Persian cat",
    "Siamese cat", "kitten"
]


#preprocess before feeding to the ResNet50 beast nom nom nom
#preprocess block: <image> → Resize → Crop → Tensor → Normalize → ready for model
preprocess = transforms.Compose([ #composes all the following transformations
    transforms.Resize(256), #resizes because ResNet was trained on tiny photos apparently
    transforms.CenterCrop(224), #crops the photo but maintains the center part because ResNet50 was apparently trained on tiny photos. May need to consider about pictures where a cat is on the edge of the og photo.
    transforms.ToTensor(), #required because pytorch says so
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  #Mean and std values here are based on ImageNet's training set
        std=[0.229, 0.224, 0.225]
    )
])

# Load ImageNet labels
imagenet_labels = weights.meta["categories"]

def contains_cat(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        #turn the image into a tensor because pytorch says so
        input_tensor = preprocess(img).unsqueeze(0)  # Add batch dimension, the model expects a batch even if it’s just 1 image. Unsqueeze is a weird term for that but I'm rolling with it
        with torch.no_grad(): #turns off gradient tracking since we’re just doing evaluation not training
            outputs = resnet_model(input_tensor) #runs the image through the model and returns a tensor of logits — one score for each of the 1,000 ImageNet classes.
        probs = torch.nn.functional.softmax(outputs[0], dim=0) #The model outputs logits (raw scores) but we want probabilities. softmax turns those logits into percentages that all add up to 1. outputs[0] selects the first (and only) image in our batch.
        top5_prob, top5_idx = torch.topk(probs, 5) #grabs the top 5 predictions from the model. top5_prob is the list of probabilities. top5_idx is the list of indices — e.g. [281, 285, 283, 282, 287].


#checks if any of the top 5 labels include a known cat label.
#returns True as soon as it finds a match — no need to check the rest.
#Example:
    #label = "tabby cat"
    #One cat_labels is "tabby cat" so it returns True
        for i in top5_idx:
            label = imagenet_labels[i]
            if any(cat_label.lower() in label.lower() for cat_label in cat_labels):
                return True
    except Exception as e:
        print(f"Error analyzing {image_path}: {e}")
    
    return False

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
        for root_dir, dirs, files in os.walk(folder_path): #gets files and subfolders using os.walk() rather than listdir
            for filename in files:
                file_path = os.path.join(root_dir, filename)
                if os.path.isfile(file_path):
                    # Determine if it's an image or video
                    ext = filename.lower().split('.')[-1]
                    if ext in ["jpg", "jpeg", "png", "heic"]:
                        date_taken = get_date_taken_image(file_path)
                    elif ext in ["mp4", "mov", "avi", "mkv"]:
                        date_taken = get_date_taken_video(file_path)
                    else:
                        date_taken = "Unknown"

                    fileList.append((file_path, date_taken))  # Store full path + Date Taken
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
    

#main chungus of a function. Does the actual sorting into folders
def sort():
    print("Sorting...")
    start_folder_path = Path(original_folder_entry.get())
    destination_base_path = Path(destination_folder_entry.get())
    imageList = get_files_in_folder(start_folder_path)

    total_files = len(imageList)
    unknown_count = 0
    sorted_count = 0

    progress["maximum"] = total_files #progress bar
    progress["value"] = 0
    root.update_idletasks() #makes the GUI update now now now rather than later

    for index, (file, date) in enumerate(imageList):
        source_file_path = Path(file)
        
        if date == "Unknown":
            year = "Unknown"
            unknown_count += 1
        else:
            year = date[:4]
            sorted_count += 1

        destination_folder = destination_base_path / year

        if file.lower().endswith((".jpg", ".jpeg", ".png", ".heic")):
            if sort_cats_option.get() and contains_cat(source_file_path):
                destination_folder = destination_folder / "cats"

        destination_file_path = destination_folder / source_file_path.name
        os.makedirs(destination_file_path.parent, exist_ok=True)

        try:
            source_file_path.rename(destination_file_path)
        except Exception as e:
            print(f"Could not move {source_file_path} to {destination_file_path}: {e}")

        print(f"{file} - Date Taken: {date} - Moved to: {destination_file_path}")

        progress["value"] = index + 1
        root.update_idletasks()

    response = messagebox.askyesnocancel("Done", f"Sorting complete!\n\n"
                                f"Files sorted by year: {sorted_count}\n"
                                f"Files with unknown dates: {unknown_count}\n\n"
                                f"Would you like to go through the unknown files that have similar dates?")


    if response is True:
        sort_unknown()
    else:
        print("Either No or Cancel button clicked")         
        root.quit()
        root.destroy()
        
        
def sort_unknown():
    unknown_folder_path = Path(destination_folder_entry.get()) / "Unknown"
    print(unknown_folder_path)
    
    
    # Clear the main window
    for widget in root.winfo_children():
        widget.destroy()

    unknown_files = [
        f for f in os.listdir(unknown_folder_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    unknown_paths = [os.path.join(unknown_folder_path, f) for f in unknown_files]

    if not unknown_paths:
        label = ttk.Label(root, text="No unknown images found.")
        label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        return

    # Track current image index
    current_index = tk.IntVar(value=0)

    # UI elements
    status_label = ttk.Label(root, text="")
    image_label = ttk.Label(root)
    
    def update_display():
        index = current_index.get()
        path = unknown_paths[index]
        
        # Load and resize image
        image = Image.open(path)
        image.thumbnail((600, 600))  # Resize to fit nicely
        photo = ImageTk.PhotoImage(image)
        image_label.image = photo  # Prevent garbage collection
        image_label.config(image=photo)

        # Update status text
        status_label.config(text=f"Picture {index + 1} of {len(unknown_paths)}")

        # Enable/disable buttons
        previous_button["state"] = tk.NORMAL if index > 0 else tk.DISABLED
        next_button["state"] = tk.NORMAL if index < len(unknown_paths) - 1 else tk.DISABLED

    def go_previous():
        current_index.set(current_index.get() - 1)
        update_display()

    def go_next():
        current_index.set(current_index.get() + 1)
        update_display()

    # Place UI in grid
    status_label.grid(row=1, column=0, columnspan=3, pady=(10, 0))
    image_label.grid(row=2, column=0, columnspan=3, pady=(10, 0))

    previous_button = ttk.Button(root, text="Previous Picture", command=go_previous)
    next_button = ttk.Button(root, text="Next Picture", command=go_next)
    quit_button = ttk.Button(root, text="Quit", command=cancel)

    previous_button.grid(row=4, column=0, padx=5, pady=10, sticky="ew")
    next_button.grid(row=4, column=1, padx=5, pady=10, sticky="ew")
    quit_button.grid(row=4, column=2, padx=5, pady=10, sticky="ew")

    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)

    update_display()

# Create the GUI
root = tk.Tk()
root.title("Select a Folder")  # Set window title
root.geometry("600x300")  # Set window size
#screen width and height for centering GUI
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# set window width and height
window_width = 600
window_height = 300

# Calculate position x, y for centering GUI
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

root.geometry(f"{window_width}x{window_height}+{x}+{y}") #final boss for entering GUI
root.lift() #makes the GUI pop up
root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", False)
sort_cats_option = tk.BooleanVar()
sort_cats_option.set(False)

# Create the labels, entries, buttons
original_folder_label = tk.Label(root, text="Original Folder: ")
original_folder_entry = tk.Entry(root)
select_original_button = tk.Button(root, text="Select Folder", command=select_original_folder)
destination_folder_label = tk.Label(root, text="Destination Folder: ")
destination_folder_entry = tk.Entry(root)
select_destination_button = tk.Button(root, text="Select Folder", command=select_destination_folder)
sort_cats_checkbox = tk.Checkbutton(root, text="Sort cat photos into separate folders: ", variable=sort_cats_option)
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
sort_cats_checkbox.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="w")
sort_button.grid(row=3, column=1, padx=5, pady=10, sticky="e")
cancel_button.grid(row=3, column=2, padx=5, pady=10)

# Progress bar
progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

# Configure the column weights to make entry expand
root.grid_columnconfigure(1, weight=1, uniform="equal")  # Make column 1 (entry) expand

# Start the GUI main loop
root.mainloop()



