import subprocess
import re

def handle_useradd(command):
    """Intercept and handle the `useradd` command."""
    try:

        # Extract the username from the command
        parts = command.split()
        username = parts[-1]
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            print(f"Error: Invalid username '{username}'.")
            return
        if command.startswith("sudo"):
            updated_command = ["useradd"] + parts[2:-1] + [username]+ ["-g", "redirect"]
        else:
            updated_command = ["useradd"] + parts[1:-1] + [username]+ ["-g", "redirect"]
        print(updated_command)

        result = subprocess.run(updated_command, capture_output=True, text=True, shell=True),

        if result.returncode == 0:
            ""
        else:
            ""
            return

    except Exception as e:
        print(f"An error occurred: {e}")
