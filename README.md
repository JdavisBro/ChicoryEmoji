# Chicory Emoji

Scripts used to generate files for making Chicory Emoji Mod

AddFont.py combines fonts exported by UndertaleModTool (`Export_Fonts/`) with a font specified in arguments. Comment line 32 to not replace other characters with emojis (only supports chars up to unicode 65535). Ignores most whitespace characters.

This does generate image files over 2048x2048 which gamemaker does not support (i think). Those will be ignored while importing the output (`Output_Fonts/`) with umt

TextCSV.py converts characters in textin.csv to the characters the emoji replaces (to support emojis over 65535).

# Credit

- [GitHub gemoji](https://github.com/github/gemoji/blob/master/db/emoji.json) for emoji json.
- [UndertaleModTool](https://github.com/krzys-h/UndertaleModTool)

