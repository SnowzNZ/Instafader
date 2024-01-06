import os
import datetime
from tkinter import filedialog
import configparser
import sys
import shutil
from PIL import Image, ImageChops
import pick
import re

# Ask for skin folder
skin_folder = filedialog.askdirectory(title="Select Skin Folder")

# Change directory to skin folder
os.chdir(skin_folder)

# Create backup folder
backup_folder = (
    f"Instafader-Backup-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
)
os.mkdir(backup_folder)

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
    shutil.copy2("skin.ini", os.path.join(backup_folder, "skin.ini"))

    # Remove indentation
    with open("skin.ini", encoding="utf-8") as f:
        lines = [line.lstrip(" \t") for line in f]

    # Join all lines and read into configparser
    config.read_string("\n".join(lines))

except FileNotFoundError:
    print("No skin.ini found!")
    sys.exit(1)

# Ask if user wants to use hitcircle or sliderstartcircle
...

# Ask if user wants to use hitcircleoverlay or sliderstartcircleoverlay
...

try:
    hitcircle = Image.open("hitcircle@2x.png")
    shutil.copy2("hitcircle@2x.png", os.path.join(backup_folder, "hitcircle@2x.png"))
    hitcircle_hd = True
except FileNotFoundError:
    try:
        hitcircle = Image.open("hitcircle.png")
        shutil.copy2("hitcircle.png", os.path.join(backup_folder, "hitcircle.png"))
        hitcircle_hd = False
    except FileNotFoundError:
        print("No hitcircle could be found!")
        sys.exit(1)

try:
    hitcircleoverlay = Image.open("hitcircleoverlay@2x.png")
    shutil.copy2(
        "hitcircleoverlay@2x.png",
        os.path.join(backup_folder, "hitcircleoverlay@2x.png"),
    )
    hitcircleoverlay_hd = True
except FileNotFoundError:
    try:
        hitcircleoverlay = Image.open("hitcircleoverlay.png")
        shutil.copy2(
            "hitcircleoverlay.png",
            os.path.join(backup_folder, "hitcircleoverlay.png"),
        )
        hitcircleoverlay_hd = False
    except FileNotFoundError:
        print("No hitcircleoverlay could be found!")
        sys.exit(1)

options = []

for option in config["Colours"]:
    if option.startswith("combo"):
        options.append((str(option).capitalize(), config["Colours"][option]))
options.append(("Custom Colour", ""))

option, _ = pick.pick(options=options, title="Choose color", indicator=">")  # type: ignore

if option[0] == "Custom Colour":
    custom_color = input("RGB Color (e.g. 255, 149, 182): ")
    r, g, b = tuple(map(int, custom_color.split(",")))
else:
    r, g, b = tuple(map(int, option[1].split(",")))

if not (r == 255 and g == 255 and b == 255):
    # Create image of solid color
    solid_color = Image.new("RGBA", (hitcircle.width, hitcircle.height), (r, g, b))

    hitcircle = ImageChops.multiply(
        hitcircle.convert("RGBA"), solid_color.convert("RGBA")
    )

# Resize by 1.25x
hitcircle = hitcircle.resize(
    (
        int(
            hitcircle.width
            * (2.5 if not hitcircle_hd and hitcircleoverlay_hd else 1.25)
        ),
        int(
            hitcircle.height
            * (2.5 if not hitcircle_hd and hitcircleoverlay_hd else 1.25)
        ),
    ),
    resample=Image.Resampling.LANCZOS,
)

hitcircleoverlay = hitcircleoverlay.resize(
    (
        int(
            hitcircleoverlay.width
            * (2.5 if not hitcircleoverlay_hd and hitcircle_hd else 1.25)
        ),
        int(
            hitcircleoverlay.height
            * (2.5 if not hitcircleoverlay_hd and hitcircle_hd else 1.25)
        ),
    ),
    resample=Image.Resampling.LANCZOS,
)

circle_hd = False
if hitcircle_hd or hitcircleoverlay_hd:
    circle_hd = True

if hitcircleoverlay.size > hitcircle.size:
    circle = Image.new("RGBA", hitcircleoverlay.size, (255, 255, 255, 0))

    paste_position = (
        (hitcircleoverlay.width - hitcircle.width) // 2,
        (hitcircleoverlay.height - hitcircle.height) // 2,
    )

    circle.paste(hitcircle, paste_position, hitcircle)
    circle.paste(hitcircleoverlay, (0, 0))
    circle.save("circle.png")

elif hitcircle.size > hitcircleoverlay.size:
    circle = Image.new("RGBA", hitcircle.size, (255, 255, 255, 0))

    paste_position = (
        (hitcircle.width - hitcircleoverlay.width) // 2,
        (hitcircle.height - hitcircleoverlay.height) // 2,
    )

    circle.paste(hitcircle, (0, 0))
    circle.paste(hitcircleoverlay, paste_position, hitcircleoverlay)
    circle.save("circle.png")

elif hitcircle.size == hitcircleoverlay.size:
    hitcircle.paste(hitcircleoverlay, (0, 0), hitcircleoverlay)
    hitcircle.save("circle.png")


# Get the prefix of the hitcircle number
try:
    hitcircle_prefix = config["Fonts"]["HitCirclePrefix"]
except KeyError:
    hitcircle_prefix = "default"

for i in range(1, 10):
    try:
        number = Image.open(f"{hitcircle_prefix}-{i}@2x.png")
        hd = True
        shutil.copy2(
            f"{hitcircle_prefix}-{i}@2x.png",
            f"{backup_folder}/{hitcircle_prefix}-{i}@2x.png",
        )
    except FileNotFoundError:
        try:
            number = Image.open(f"{hitcircle_prefix}-{i}.png")
            hd = False
            shutil.copy2(
                f"{hitcircle_prefix}-{i}.png",
                f"{backup_folder}/{hitcircle_prefix}-{i}.png",
            )
        except FileNotFoundError:
            print(f"No {hitcircle_prefix}-{i} could be found in the provided skin!")
            sys.exit(1)

    circle = Image.open("circle.png")

    if number.size > circle.size:
        no_number = Image.new("RGBA", number.size, (255, 255, 255, 0))

        # Calculate the position to paste the original image centered on the new canvas
        paste_position = (
            (number.width - circle.width) // 2,
            (number.height - circle.height) // 2,
        )

        # Paste the original image onto the new canvas
        no_number.paste(circle, paste_position, circle)
        no_number.paste(number, (0, 0))
    else:
        no_number = circle

    # Paste the hitcircle number on top of the circle image
    w, h = number.size
    # if number isnt hd
    if not hd:
        # if circle is hd
        if circle_hd:
            number = number.resize((w * 2, h * 2), resample=Image.Resampling.LANCZOS)

    x, y = no_number.size
    no_number.paste(number, ((x - w) // 2, (y - h) // 2), number)
    no_number.save(f"{hitcircle_prefix}-{i}{'@2x' if hd else ''}.png")

default_0 = Image.new("RGBA", (no_number.size), (255, 255, 255, 0))
default_0.save(f"{hitcircle_prefix}-0{'@2x' if hd else ''}.png")

# create blank images for hitcircles
blank_image = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
blank_image.save(f"hitcircle{'@2x' if hitcircle_hd else ''}.png")
blank_image.save(f"hitcircleoverlay{'@2x' if hitcircleoverlay_hd else ''}.png")

# try:
#     os.remove("circle.png")
# except FileNotFoundError:
#     pass

try:
    os.remove("sliderstartcircle.png")
    os.remove("sliderstartcircle@2x.png")

    os.remove("sliderstartcircleoverlay.png")
    os.remove("sliderstartcircleoverlay@2x.png")
except FileNotFoundError:
    pass


with open("skin.ini", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "HitCircleOverlap" in line and "//" not in line:
        lines[i] = f"HitCircleOverlap: {str(x // 2 if hd else x)}\n"
    if "Combo1" in line and "//" not in line:
        lines[i] = f"Combo1: {r}, {g}, {b}\n"
    if re.search(r"Combo\d+", line) and "Combo1" not in line and "//" not in line:
        lines[i] = ""

with open("skin.ini", "w") as f:
    f.writelines(lines)

# Todo:
# - Ask if user wants to use sliderendcircle/overlay instead if it exists
# - Account for transparency
# - Account for HitCirclePrefixes with a path
# - Account for HitCircleOverlayAboveNum(b)er
# - Account for SD circle (and HD/SD mismatch of hitcircle(overlay)) (# - Do checks for HD assets and account for that)
# - Alternating/multiple colors
