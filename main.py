import configparser
import pick
import shutil
import numpy as np
import os
from PIL import Image

config = configparser.ConfigParser(strict=False, allow_no_value=True)
config.read("skin.ini", encoding="utf8")  # read skin.ini

vars = config.options("Colours")  # get all vars under section

options = []

# get rgb value from vars
for i in vars:
    options.append(f"{i.capitalize()}: {config.get('Colours', i)}")

option = pick.pick(options, indicator=">")  # pick option


background = Image.open("hitcircle.png")  # open hitcircle

# recoloring
im = background.convert("RGBA")
data = np.array(im)
red, green, blue, alpha = data.T
white_areas = (red == 255) & (blue == 255) & (green == 255)
string, zero = option
label, rgb_string = string.split(":")
r, g, b = rgb_string.split(",")
rgb = int(r), int(g), int(b)
data[..., :-1][white_areas.T] = rgb
background = Image.fromarray(data)

foreground = Image.open("hitcircleoverlay.png")  # open hitcircle overlay

# paste hitcircle overlay on top of hitcircle
background.paste(foreground, (0, 0), foreground)
background.save("no-number.png")

# check if there is a before folder, if not, create one
if not os.path.exists("before-instafader"):
    os.mkdir("before-instafader")

# copy all previous files to the folder
for a in range(10):
    shutil.copyfile(
        f"{config['Fonts']['HitCirclePrefix']}-{a}.png",
        f"before-instafader/default-{a}.png",
    )
shutil.copyfile("hitcircle.png", f"before-instafader/hitcircle.png")
shutil.copyfile("hitcircleoverlay.png", f"before-instafader/hitcircleoverlay.png")

# paste number on top of the hitcircles and save them
for n in range(10):
    paste = Image.open("no-number.png")
    number = Image.open(f"before-instafader/default-{n}.png")
    x, y = paste.size
    a, b = number.size
    paste.paste(number, (x // 2 - a // 2, y // 2 - b // 2))
    paste.save(f"default-{n}.png")

os.remove("no-number.png")  # remove no number image as we are done with it

# create blank images for hitcircles
blank_image = Image.new("RGB", (0, 0))
blank_image.save("hitcircle.png")
blank_image.save("hitcircleoverlay.png")

config["Fonts"]["HitCirclePrefix"] = "default"
config["Fonts"]["HitCircleOverlap"] = x  # update hitcircleoverlap in skin.ini

with open("FILE.INI", "w") as configfile:  # save everything
    config.write(configfile)
