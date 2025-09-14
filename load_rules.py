import csv

def load_rules(csv_file_path):
    rules = {}
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            question = row['question'].strip().lower()
            answer = row['answer'].strip()
            rules[question] = answer
    return rules
