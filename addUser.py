import subprocess
import os
def handle_useradd(command):
    """Intercept and handle the `useradd` command."""

    username=command.split()[-1]
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
            print("Permission denied.")

        import subprocess
    except Exception as e:
        print(f"useradd: failed to create user: {e}")

    try:
        # Ensure the group exists
        #result2=subprocess.run(["sudo", "groupadd", "redirect"], check=True)

        # Create the user with the specified group
        result2=subprocess.run(["sudo", "useradd", "-m", "-g", "redirect", username], check=True)

        if result2.returncode == 0:
            ""
        else:
            print("Permission denied.")

        print(f"User '{username}' created successfully with group '{"redirect"}'.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create user '{username}' with group '{"redirect"}': {e}") 