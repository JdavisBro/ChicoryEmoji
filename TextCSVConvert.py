import json
from pathlib import Path

# Converts the second column of a CSV with emoji mapping

def main():
    emojimap = load_emoji()

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

if __name__ == "__main__":
    main()
