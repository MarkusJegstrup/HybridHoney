import subprocess
import os
def handle_useradd(command):
    """Intercept and handle the `useradd` command."""
    try:
        # Parse the username and password from the command
        if "-m" not in command or "-p" not in command:
            print("useradd: invalid syntax")
            return

        # Execute the useradd command securely
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"useradd: user successfully created.")
        else:
            print(f"useradd: failed to create user. Error: {result.stderr.strip()}")

    except Exception as e:
        print(f"useradd: failed to create user: {e}")

    print(f"System user creation process complete.")    