import os
import datetime
from tkinter import filedialog
import configparser
import sys
import shutil
from PIL import Image, ImageChops
import pick

# Ask for skin folder
skin_folder = filedialog.askdirectory(title="Select Skin Folder")

# Change directory to skin folder
os.chdir(skin_folder)

# Create backup folder
backup_folder = (
    f"Instafader-Backup-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
)
os.mkdir(backup_folder)
print("Creating backup folder")

# Initialize configparser
config = configparser.ConfigParser(
    allow_no_value=True,
    comment_prefixes="//",
    delimiters=":",
    inline_comment_prefixes="//",
    strict=False,
)

try:
    # Create backup of skin.ini
    shutil.copy2("skin.ini", f"{backup_folder}/skin.ini")

    # lstrip(" \t") each line
    with open("skin.ini", encoding="utf-8") as f:
        lines = [line.lstrip(" \t") for line in f]

    # Join all lines and read into configparser
    config.read_string("\n".join(lines))

except FileNotFoundError:
    print("No skin.ini found!")
    sys.exit()

# Try to open the @2x hitcircle, if it cant be found then try to open the SD hitcircle
try:
    hitcircle = Image.open("hitcircle@2x.png")
    shutil.copy2("hitcircle@2x.png", f"{backup_folder}/hitcircle@2x.png")
except FileNotFoundError:
    try:
        hitcircle = Image.open("hitcircle.png")
        shutil.copy2("hitcircle.png", f"{backup_folder}/hitcircle.png")
    except FileNotFoundError:
        # Alert the user if no hitcircle image could be found
        print("No hitcircle could be found in the provided skin!")
        sys.exit()

# Try to open the @2x hitcircleoverlay, if it cant be found then try to open the SD hitcircleoverlay
try:
    hitcircleoverlay = Image.open("hitcircleoverlay@2x.png")
    shutil.copy2("hitcircleoverlay@2x.png", f"{backup_folder}/hitcircleoverlay@2x.png")
except FileNotFoundError:
    try:
        hitcircleoverlay = Image.open("hitcircleoverlay.png")
        shutil.copy2("hitcircleoverlay.png", f"{backup_folder}/hitcircleoverlay.png")
    except FileNotFoundError:
        # Alert the user if no hitcircle image could not be found
        print("No hitcircleoverlay could be found in the provided skin!")
        sys.exit()

options = []

for option in config["Colours"]:
    if option.startswith("combo"):
        options.append((option, config["Colours"][option]))

option, _ = pick.pick(options=options, title="Choose color")

r, g, b = tuple(map(int, option[1].split(",")))

solid_color = Image.new("RGBA", (hitcircle.width, hitcircle.height), (r, g, b))

hitcircle = ImageChops.multiply(hitcircle.convert("RGBA"), solid_color.convert("RGBA"))
hitcircle = hitcircle.resize(
    (int(hitcircle.width * 1.25), int(hitcircle.height * 1.25)), resample=Image.LANCZOS
)

hitcircleoverlay = hitcircleoverlay.resize(
    (int(hitcircleoverlay.width * 1.25), int(hitcircleoverlay.height * 1.25)),
    resample=Image.LANCZOS,
)


if hitcircle.size < hitcircleoverlay.size:
    # Create a new image with the desired canvas size
    no_number = Image.new(
        "RGBA", hitcircleoverlay.size, (255, 255, 255, 0)
    )  # Use a white background

    # Calculate the position to paste the original image centered on the new canvas
    paste_position = (
        (hitcircleoverlay.width - hitcircle.width) // 2,
        (hitcircleoverlay.height - hitcircle.height) // 2,
    )

    # Paste the original image onto the new canvas
    no_number.paste(hitcircle, paste_position)
    no_number.paste(hitcircleoverlay, (0, 0), hitcircleoverlay)

elif hitcircle.size > hitcircleoverlay.size:
    no_number = Image.new("RGBA", hitcircle.size, (255, 255, 255, 0))

    paste_position = (
        (hitcircle.width - hitcircleoverlay.width) // 2,
        (hitcircle.height - hitcircleoverlay.height) // 2,
    )

    no_number.paste(hitcircleoverlay, paste_position)
    no_number.paste(hitcircle, (0, 0), hitcircle)
else:
    no_number = hitcircle.paste(hitcircleoverlay, (0, 0), hitcircleoverlay)

no_number.save("no-number.png")


# Get the prefix of the hitcircle number
hitcircle_prefix = config["Fonts"]["HitCirclePrefix"]

# Check if all the hitcircle numbers exist
for i in range(10):
    try:
        # Try to open the @2x hitcircle number
        number = Image.open(f"{hitcircle_prefix}-{i}@2x.png")
        hd = True
        # Copy the file into the backup folder
        shutil.copy2(
            f"{hitcircle_prefix}-{i}@2x.png",
            f"{backup_folder}/{hitcircle_prefix}-{i}@2x.png",
        )
    except FileNotFoundError:
        try:
            # Try to open the SD hitcircle number
            number = Image.open(f"{hitcircle_prefix}-{i}.png")
            # Copy the file into the backup folder
            shutil.copy2(
                f"{hitcircle_prefix}-{i}.png",
                f"{backup_folder}/{hitcircle_prefix}-{i}.png",
            )
        except FileNotFoundError:
            # Alert the user if the hitcircle number could not be found
            print(f"No default-{i}(@2x) could be found in the provided skin!")
            sys.exit()  # Move this line inside the inner except block

    # Paste the hitcircle number on top of the no-number image
    no_number = Image.open("no-number.png")
    x, y = no_number.size
    a, b = number.size
    no_number.paste(number, ((x - a) // 2, (y - b) // 2), number)
    no_number.save(f"default-{i}{'@2x' if hd else ''}.png")


config["Fonts"]["HitCircleOverlap"] = str(x // 2 if hd else x)

for option in config["Colours"]:
    if option.startswith("combo"):
        if not option.startswith("combo1"):
            del config["Colours"][option]

config["Colours"]["Combo1"] = option[1]

# Write all changes
...


# Todo:
# - Ask if user wants to use sliderendcircle/overlay if it exists
# - Do checks for HD assets and account for that
