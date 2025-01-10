import subprocess

def handle_useradd(command):
    """Intercept and handle the `useradd` command."""
    try:
        # Ensure the command has required flags
        if "-m" not in command or "-p" not in command:
            print("useradd: invalid syntax")
            return

        # Extract the username from the command
        username = command.split()[-1]

        # Run the initial useradd command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"useradd: user '{username}' successfully created.")
        else:
            print(f"useradd: failed to create user. Error: {result.stderr.strip()}")
            return

        # Ensure the group 'redirect' exists
        group_result = subprocess.run(["sudo", "groupadd", "redirect"], capture_output=True, text=True)

        if group_result.returncode == 0:
            print("Group 'redirect' ensured.")
        elif "already exists" in group_result.stderr:
            print("Group 'redirect' already exists.")
        else:
            print(f"Failed to create group 'redirect': {group_result.stderr.strip()}")
            return

        # Add the user to the 'redirect' group
        user_group_result = subprocess.run(
            ["sudo", "usermod", "-g", "redirect", username],
            capture_output=True,
            text=True
        )
        if user_group_result.returncode == 0:
            print(f"User '{username}' added to group 'redirect' successfully.")
        else:
            print(f"Failed to add user '{username}' to group 'redirect': {user_group_result.stderr.strip()}")

    except Exception as e:
        print(f"An error occurred: {e}")
