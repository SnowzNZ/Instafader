"""
Makes osu! skins instafade.
"""
import configparser
import os
import shutil
import sys

import numpy as np
import pick
from PIL import Image, ImageDraw

config = configparser.ConfigParser()

backup_folder = "instafader-backup"

# Check if a backup folder doesnt exist
if not os.path.exists(backup_folder):
    os.mkdir(backup_folder)  # Create backup folder

# Read the skin.ini file
try:
    config.read("skin.ini")
    shutil.copy2("skin.ini", f"{backup_folder}/skin.ini")
except:
    print("No skin.ini found!")
    sys.exit()

options = []

# Get all colors in the section
try:
    # Get all colors
    section_keys = config.options("Colours")

    # Filter out all colors that arent Combo colors and add them to the options that the user can choose from
    options = [
        f"{i.capitalize()}: {config.get('Colours', i)}"
        for i in (key for key in section_keys if "combo" in key.lower())
    ]

    # Ask the user to pick a Combo color
    option = pick.pick(options, indicator=">")

except configparser.NoSectionError:
    print(
        "The skin.ini provided does not contain a Colours section, the hitcircle will NOT be colored."
    )

# Try to open the @2x hitcircle, if it cant be found then try to open the SD hitcircle
try:
    hitcircle = Image.open("hitcircle@2x.png")
    shutil.copy2(f"hitcircle@2x.png", f"{backup_folder}/hitcircle@2x.png")
except FileNotFoundError:
    try:
        hitcircle = Image.open("hitcircle.png")
        shutil.copy2(f"hitcircle.png", f"{backup_folder}/hitcircle.png")
    except FileNotFoundError:
        # Alert the user if no hitcircle image could be found
        print("No hitcircle could be found in the provided skin!")
        sys.exit()

# Try to open the @2x hitcircleoverlay, if it cant be found then try to open the SD hitcircleoverlay
try:
    hitcircleoverlay = Image.open("hitcircleoverlay@2x.png")
    shutil.copy2(
        f"hitcircleoverlay@2x.png", f"{backup_folder}/hitcircleoverlay@2x.png"
    )
except FileNotFoundError:
    try:
        hitcircleoverlay = Image.open("hitcircleoverlay.png")
        shutil.copy2(
            f"hitcircleoverlay.png", f"{backup_folder}/hitcircleoverlay.png"
        )
    except FileNotFoundError:
        # Alert the user if no hitcircle image could not be found
        print("No hitcircleoverlay could be found in the provided skin!")
        sys.exit()

# Color the hitcircle
try:
    string, zero = option
    label, rgb_string = string.split(":")
    rgb_list = rgb_string.split(",")
    r, g, b = (int(rgb_list[0]), int(rgb_list[1]), int(rgb_list[2]))
except:
    r, g, b = (255, 255, 255)


solid_color = Image.new("RGB", hitcircle.size, color=(r, g, b))
solid_color = solid_color.convert(hitcircle.mode)
result = Image.blend(hitcircle, solid_color, 1.0)
result.save("b.png")

# hitcircle = hitcircle.point(lambda x: (x, x, x, 255))
# hitcircle.save("overlayed.png")

# # recoloring
# im = hitcircle.convert("RGBA")
# data = np.array(im)
# red, green, blue, alpha = data.T
# white_areas = (red == 255) & (blue == 255) & (green == 255)
# string, zero = option
# label, rgb_string = string.split(":")
# r, g, b = rgb_string.split(",")
# rgb = int(r), int(g), int(b)
# data[..., :-1][white_areas.T] = rgb
# background = Image.fromarray(data)

# Paste the hitcircleoverlay on top of the hitcircle
hitcircle.paste(hitcircleoverlay, (0, 0), hitcircleoverlay)

# Get the prefix of the hitcircle number
hitcircle_prefix = config.get("Fonts", "HitCirclePrefix")

# Check if all the hitcircle numbers exist
for i in range(10):
    try:
        # Try to open the @2x hitcircle number
        number = Image.open(f"{hitcircle_prefix}-{i}@2x.png")
        # Copy the file into the backup folder
        shutil.copy2(f"{hitcircle_prefix}-{i}@2x.png", {backup_folder})

    except FileNotFoundError:
        try:
            # Try to open the SD hitcircle number
            number = Image.open(f"{hitcircle_prefix}-{i}.png")
            # Copy the file into the backup folder
            shutil.copy2(f"{hitcircle_prefix}-{i}.png", {backup_folder})
        except FileNotFoundError:
            # Alert the user if the hitcircle number could not be found
            print(f"No default-{i}(@2x) could be found in the provided skin!")
            sys.exit()

for n in range(10):
    paste = Image.open("no-number.png")
    number = Image.open(f"before-instafader/default-{n}.png")
    x, y = paste.size
    a, b = number.size
    paste.paste(number, (x // 2 - a // 2, y // 2 - b // 2))
    # paste.resize(160, 160, Image.Resampling.LANCZOS)
    paste.save(f"default-{n}.png")

os.remove("no-number.png")  # remove no number image as we are done with it

# create blank images for hitcircles
blank_image = Image.new("RGB", (0, 0))
blank_image.save("hitcircle.png")
blank_image.save("hitcircleoverlay.png")

config["Fonts"]["HitCirclePrefix"] = "default"
config["Fonts"]["HitCircleOverlap"] = str(
    x
)  # update hitcircleoverlap in skin.ini

with open("skin.ini", "w", encoding="utf-8") as f:  # save everything
    config.write(f)
