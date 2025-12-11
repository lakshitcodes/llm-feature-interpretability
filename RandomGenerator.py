import csv
import random

# Input and output file names
input_file = "AmesHousing.csv"
output_file = "random_sample.txt"

# Read the CSV file
with open(input_file, "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Pick a random row
sample_row = random.choice(rows)

# Write formatted output to a text file
with open(output_file, "w", encoding="utf-8") as out:
    for col_name, value in sample_row.items():
        out.write(f"{col_name} : {value}\n")

print("Random sample saved to random_sample.txt")
