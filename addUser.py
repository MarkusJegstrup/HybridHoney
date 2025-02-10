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
        if not re.match(r"^[a-zA-Z0-9_-]+$", parts[2:-1]):
            print(f"Error: Invalid password '{parts[2:-1]}'.")
            return
        if command.startswith("sudo"):
            updated_command = ["sudo"] + ["useradd"] + parts[2:-1] + [username] + ["-g", "redirect"]
        else:
            updated_command = ["sudo"] + ["useradd"] + parts[1:-1] + [username] + ["-g", "redirect"]

        updated_command=' '.join(updated_command)
        result = subprocess.run(updated_command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            ""
        else:
            ""
            return

    except Exception as e:
        print(f"An error occurred: {e}")
