import json

def main():
    out = "Category,Name/Aliases,Symbol,Name/Aliases,Symbol,Name/Aliases,Symbol,Name/Aliases,Symbol"
    with open("emoji.json", encoding="utf8") as f:
        emoji = json.load(f)

    row = [""] * 9
    col = 0
    lastcat = "N/A"
    for em in emoji:
        if len(em["emoji"]) > 2:
            continue
        if len(em["emoji"]) == 2:
            if ord(em["emoji"][-1]) not in range(65024, 65039+1):
                continue
        if em["category"] != lastcat:
            lastcat = em["category"]
            if row[1]:
                out += "\n"
                out += ",".join(row)
            out += "\n"
            out += em["category"] + (","*8)
            col = 0
            row = [""] * 9
        row[1+(col*2)] = " / ".join([i.replace("_", " ") for i in em["aliases"]])
        row[2+(col*2)] = em["emoji"]
        col += 1
        if col == 4:
            col = 0
            out += "\n"
            out += ",".join(row)
            row = [""] * 9
    out += "\n"
    out += ",".join(row)
    with open("emoji.csv", "w+", encoding="utf8") as f:
        f.write(out)

if __name__ == "__main__":
    main()
