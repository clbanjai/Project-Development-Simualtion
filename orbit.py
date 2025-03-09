import yaml
import csv

# Load YAML file
with open("ORBIT/examples/configs/Kratos.yaml", "r") as yaml_file:
    data = yaml.safe_load(yaml_file)

print(data)
# Define CSV file
csv_file = "output.csv"

# Extract keys (assuming the YAML file has a list of dictionaries)

# Write to CSV
with open(csv_file, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=data)
    writer.writeheader()
    writer.writerows(data)

print(f"Converted YAML to {csv_file}")
