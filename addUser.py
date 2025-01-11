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
        parts = command.split()
        username = parts[-1]

        # Insert '-g redirect' before the username
        updated_command = " ".join(parts[:-1]) + " -g redirect " + username
        # Run the initial useradd command
        result = subprocess.run(updated_command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"useradd: user '{username}' successfully created.")
        else:
            print(f"useradd: failed to create user. Error: {result.stderr.strip()}")
            return

    except Exception as e:
        print(f"An error occurred: {e}")
