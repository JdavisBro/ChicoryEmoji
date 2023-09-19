import json

__all__ = (
    "load_emoji"
)

def load_emoji():
    emoji_replacement = 1120
    with open("emoji.json", encoding="utf8") as f:
        emoji = json.load(f)
    emojimap = {} # char: char
    varsel = {} # char: varselchar
    for em in emoji:
        if len(em["emoji"]) == 1:
            emojimap[em["emoji"]] = chr(emoji_replacement)
            emoji_replacement += 1
        elif len(em["emoji"]) == 2:
            # check for variation selector
            if ord(em["emoji"][-1]) in range(65024, 65039+1):
                emojimap[em["emoji"][0]] = chr(emoji_replacement)
                varsel[em["emoji"][0]] = em["emoji"]
                emoji_replacement += 1
    print(emojimap)
    return emojimap, varsel