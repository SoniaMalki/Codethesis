import json
import subprocess

def run_configurations(config_file_path):
    with open(config_file_path, 'r') as f:
        configurations = json.load(f)

    for config_key, config_data in configurations.items():
        print(f"Running configuration: {config_key}")
        command = ["python3", "main.py", config_key]  # Assuming your main script is named main.py
        subprocess.run(command)  # This will run the command and wait for it to finish

# Run configurations in order: tasksets, assignments, schedulings
run_configurations("./config_files/tasksets.json")
run_configurations("./config_files/assignments.json")
run_configurations("./config_files/schedulings.json") 