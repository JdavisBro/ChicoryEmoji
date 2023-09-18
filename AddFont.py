import sys
import copy
import os
import subprocess
import shutil
import re
import json
from pathlib import Path

import numpy
import rectpack
from fontTools import ttLib
from PIL import Image, ImageDraw, ImageFont

imagemagick = os.environ.get("IMAGEMAGICK")
if imagemagick:
    imagemagick = Path(imagemagick) / "convert.exe"
else:
    shutil.which("magick") or shutil.which("convert")

def main(args):
    font = Path(" ".join(args))
    if not font.is_file():
        return print(f"Font {font} not found.")

    export = Path("Export_Fonts/")
    if not export.is_dir():
        return print("Export not found, place an 'Export_Fonts' in this dir")
    
    print("Loading Emojis")
    emojimap = {}
    emojimap = load_emoji() # Enables emoji replacement

    # get glyphs from in font
    print("Loading font glyphs")
    fontglyphs = get_font_glyphs(font, emojimap)
    print(get_glyphs_area(fontglyphs, 1))
    outdir = Path("Output_Fonts/")
    outdir.mkdir(exist_ok=True)
    for fp in export.glob("*.png"):
        fontpath = fp.stem
        print(f"Opening gmfont {fontpath}")
        fontinfo, glyphs = open_export(fp)
        print("Adding font glyphs")
        glyphs = add_font_glpyhs(fontglyphs, glyphs, emojimap)
        print("Packing Glyphs")
        packedbin, charorder = pack_glyphs(glyphs)
        glyphs = update_glyphs_position(glyphs, packedbin, charorder)
        print("Making Image")
        im = make_glyphs_image((packedbin.width, packedbin.height), glyphs)
        im.save(outdir / f"{fontpath}.png")
        with open(outdir / f"glyphs_{fontpath}.csv", "w+") as f:
            f.write(f"\"{fontinfo['displayName']}\";{fontinfo['emSize']};{fontinfo['bold']};{fontinfo['italic']};{fontinfo['charset']};{fontinfo['antiAliasing']};{fontinfo['scaleX']};{fontinfo['scaleY']}\n")
            make_glyphs_csv(f, glyphs)

def load_emoji():
    emoji_replacement = 1120
    with open("emoji.json", encoding="utf8") as f:
        emoji = json.load(f)
    emojimap = {} # char: char
    for em in emoji:
        if len(em["emoji"]) == 1:
            emojimap[em["emoji"]] = chr(emoji_replacement)
            emoji_replacement += 1
    print(emojimap)
    return emojimap

def get_font_glyphs(font, emojimap):
    glyphs = {}
    chars = []
    with ttLib.TTFont(font) as ttfontf:
        for x in ttfontf["cmap"].tables:
            for code, _ in x.cmap.items():
                chars.append(chr(code))
    font = ImageFont.truetype(str(font), 48, layout_engine=ImageFont.Layout.RAQM)
    for char in chars:
        if char not in emojimap:
            if ord(char) > 65535:
                continue
            elif re.match(r"\s", char): # Whitespace characters
                continue
            elif ord(char) in [173, 8205]: # Soft hyphen / Zero width joiner
                continue
            elif char in emojimap.values():
                continue

        im = Image.new("RGBA", (100, 100), (0,0,0,0))
        draw = ImageDraw.Draw(im)
        draw.text((0, 30), char, (0,0,0,255), font=font, embedded_color=True)

        imnp = numpy.array(im)
        imnp = numpy.where(imnp[:, :, 3] > 0) # Non transparent pixels
        try:
            crop  = [imnp[1].min(), max(0, imnp[0].min()-1), imnp[1].max(), imnp[0].max()+1] # crop to content +2 pixels on each side vertically
        except ValueError: # 0 width / height
            pass
        else:
            im = im.crop(crop)

        if char in emojimap:
            char = emojimap[char]

        glyphs[char] = {}
        glyphs[char]["im"] = im
        glyphs[char]["sourceX"] = 0
        glyphs[char]["sourceY"] = 0
        glyphs[char]["sourceWidth"] = im.width
        glyphs[char]["sourceHeight"] = im.height 
        glyphs[char]["shift"] = im.width
        glyphs[char]["offset"] = 2
    return glyphs

def parse_fontinfo(fontinfotext):
    fontinfo = {}
    fontinfoorder = ["displayName","emSize","bold","italic","charset","antiAliasing","scaleX","scaleY"]
    for i, value in enumerate(fontinfotext.split(";")):
        if i == 0:
            fontinfo[fontinfoorder[i]] = value[1:-1]
        else:
            fontinfo[fontinfoorder[i]] = value
    return fontinfo

def parse_glyph(glyphtext):
    glyph = {}
    glyphlist = glyphtext.split(";")
    char = chr(int(glyphlist[0]))
    glyph["sourceX"], glyph["sourceY"] = int(glyphlist[1]), int(glyphlist[2])
    glyph["sourceWidth"], glyph["sourceHeight"] = int(glyphlist[3]), int(glyphlist[4])
    glyph["shift"] = int(glyphlist[5])
    glyph["offset"] = int(glyphlist[6])
    if char == " ":
        print(glyph)
    return char, glyph

def open_export(impath):
    fontpath = impath.stem
    csvpath = impath.parent / f"glyphs_{fontpath}.csv"
    fontinfo = {}
    glyphs = {}
    im = Image.open(impath)
    with csvpath.open() as f:
        fontinfo = parse_fontinfo(f.readline().strip())
        line = f.readline()
        while line:
            char, glyph = parse_glyph(line.strip())
            glyph["im"] = im.crop(
                (
                    glyph["sourceX"],
                    glyph["sourceY"],
                    glyph["sourceX"] + glyph["sourceWidth"],
                    glyph["sourceY"] + glyph["sourceHeight"]
                )
            )
            glyphs[char] = glyph
            line = f.readline()
    return fontinfo, glyphs

def add_font_glpyhs(fontglyphs, glyphs, emojimap):
    fontglyphs = copy.deepcopy(fontglyphs)
    for i in list(glyphs.keys()):
        if i in emojimap.values() and i in fontglyphs:
            glyphs.pop(i)
    fontglyphs.update(glyphs)
    return fontglyphs

def get_glyphs_area(glyphs, div=16):
    area = 0
    for glyph in glyphs.values():
        area += glyph["sourceWidth"] * glyph["sourceHeight"]
    area += area // div
    return area

def pack_glyphs(glyphs):
    packer = rectpack.newPacker(bin_algo=rectpack.PackingBin.BNF, pack_algo=rectpack.GuillotineBssfSas, rotation=False)
    area = get_glyphs_area(glyphs)
    charorder = []
    binsize = 256
    while binsize*binsize < area: # 256 x 256 to 2048 x 2048
        binsize *= 2
    packer.add_bin(binsize, binsize)
    i = 0
    for char, glyph in glyphs.items():
        if glyph["sourceWidth"] == 0 or glyph["sourceHeight"] == 0:
            continue
        charorder.append(char)
        packer.add_rect(glyph["sourceWidth"]+1, glyph["sourceHeight"]+1, i)
        i += 1
    packer.pack()
    return packer[0], charorder

def update_glyphs_position(glyphs, packedbin, charorder):
    for rect in packedbin:
        glyphs[charorder[rect.rid]]["sourceX"] = rect.x
        glyphs[charorder[rect.rid]]["sourceY"] = rect.y
    return glyphs

def make_glyphs_image(size, glyphs):
    im = Image.new("RGBA", size, (0,0,0,0))
    for glyph in glyphs.values():
        im.paste(glyph["im"], (glyph["sourceX"], glyph["sourceY"]))
    return im

def make_glyphs_csv(f, glyphs):
    glyphssorted = sorted(list(glyphs), key=lambda a: ord(a)) # needs to be sorted for umt to import correctly
    for char in glyphssorted:
        glyph = glyphs[char] 
        f.write(f"{ord(char)};{glyph['sourceX']};{glyph['sourceY']};{glyph['sourceWidth']};{glyph['sourceHeight']};{glyph['shift']};{glyph['offset']}\n")

if __name__ == "__main__":
    main(sys.argv[1:])