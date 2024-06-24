import json

input_file = "osf.user.jsonl"
output_file = "athena-user_id-to-email.json"

data = {}

with open(input_file, "r") as file:
    for line in file:
        json_data = json.loads(line)
        employee_id = json_data["_id"]
        email = json_data["email"]
        data[employee_id] = email

with open(output_file, "w") as file:
    json.dump(data, file)
