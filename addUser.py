import subprocess
import os
def handle_useradd(command):
    """Intercept and handle the `useradd` command."""

    print("Handling userAdd")
    os.system("sudo /usr/sbin/useradd --help")
    print("Done checking sudo access")
    try:
        # Parse the username and password from the command
        if "-m" not in command or "-p" not in command:
            print("useradd: invalid syntax")
            return

        parts = command.split()
        username_index = parts.index("-m") + 1
        password_index = parts.index("-p") + 1

        username = parts[username_index]
        password = parts[password_index]

        if "$(" in password:  # Handle password generation
            # Extract and execute the password generation command
            password_command = password[2:-1]
            password = subprocess.check_output(password_command, shell=True).decode().strip()

        # Add the user to the system
        create_system_user(username, password)

        print(f"useradd: user '{username}' successfully created.")
    except Exception as e:
        print(f"useradd: failed to create user: {e}")

def create_system_user(username, password):
    """Create a system user with the given username and password."""
    # Hash the password using openssl or Python's crypt library
    hashed_password = subprocess.check_output(
        ["openssl", "passwd", "-1", password]
    ).decode().strip()

    # Run the `useradd` command
    subprocess.run(
        ["sudo", "useradd", "-m", "-p", hashed_password, username],
        check=True
    )

    print(f"System user '{username}' created with the specified password.")        