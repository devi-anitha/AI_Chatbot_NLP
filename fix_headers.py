# fix_headers.py
input_file = "data/chatbot_data_clean.csv"  # Update with your actual file
output_file = "data/chatbot_data_fixed.csv"

with open(input_file, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

# Check and add header
if not lines[0].strip().lower().startswith("patterns"):
    lines.insert(0, "patterns,responses\n")

with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.writelines(lines)

print("✅ Header fixed and saved to:", output_file)
