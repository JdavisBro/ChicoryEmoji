import json
from pathlib import Path

from sharedfunc import load_emoji

# Converts the second column of a CSV with emoji mapping

def main():
    emojimap = load_emoji()[0]

    text = ""
    with open("textin.csv", encoding="utf8") as f:
        line = f.readline() # skip first line
        text += line
        line = f.readline()
        while line:
            for char in line:
                if char in emojimap:
                    text += emojimap[char]
                else:
                    text += char
            line = f.readline()
    with open("text.csv", "w+", encoding="utf8") as f:
        f.write(text)

if __name__ == "__main__":
    main()
