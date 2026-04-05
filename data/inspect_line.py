# inspect_line.py
with open("data/chatbot_data.csv", "r", encoding="utf-8", errors="replace") as f:
    for i, line in enumerate(f, start=1):
        if 55 <= i <= 65:
            print(i, repr(line))
