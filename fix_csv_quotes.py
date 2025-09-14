import csv

input_file = "data/chatbot_data.csv"
output_file = "data/chatbot_data_clean.csv"

with open(input_file, "r", encoding="utf-8") as infile, \
     open(output_file, "w", encoding="utf-8", newline='') as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)

    for row in reader:
        if len(row) > 2:
            # Merge all columns after first into one string
            row = [row[0], ",".join(row[1:]).strip()]
        writer.writerow(row)

print("✅ Fixed CSV saved as:", output_file)
