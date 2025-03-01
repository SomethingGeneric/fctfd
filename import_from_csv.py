# import challenge data from a CSV and convert into YAML

import csv
import yaml

CHAL_DB_PATH = "db/challenges.yaml"

# Load existing data from YAML file
with open(CHAL_DB_PATH, 'r') as f:
    data = yaml.safe_load(f)

def update_csv_to_yaml(csv_file, chal_name_prefix):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row if present

        for row in reader:
            name = row[0].replace(" ", "_")
            description = row[1]
            flag = row[2]

            # Check if existing data exists
            for i, entry in enumerate(data):
                if entry['name'] == name and entry['flag'] == flag:
                    # Update the points of the corresponding entry
                    data[i]['points'] = 1
                    break
            else:
                # Add a new entry to the data list
                data.append({'name': chal_name_prefix + "_" + name, 'description': description, 'flag': flag, 'points': 1})

    # Write updated data back to YAML file
    with open(CHAL_DB_PATH, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


file_path = input("Enter the path of the CSV file: ")
chal_name_prefix = input("Enter the prefix for the challenge names: ")

# Call the function with your CSV file
update_csv_to_yaml(file_path, chal_name_prefix)