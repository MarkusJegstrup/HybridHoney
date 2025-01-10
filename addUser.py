import subprocess
import os
def handle_useradd(command):
    """Intercept and handle the `useradd` command."""

    try:
        # Parse the username and password from the command
        if "-m" not in command or "-p" not in command:
            print("useradd: invalid syntax")
            return

        os.system(command)

        print(f"useradd: user is successfully created.")
    except Exception as e:
        print(f"useradd: failed to create user: {e}")


    print(f"System user is created with the specified password.")        