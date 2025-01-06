import getpass


def handle_fake_sudo_give_access():
    attempts = 0
    max_attempts = 3
    is_password = False

    import getpass

def handle_fake_sudo_give_access():
    attempts = 0
    max_attempts = 3
    is_password = False

    # Load correct passwords from a file
    try:
        with open("10kpasswords.txt", "r") as file:
            correct_passwords = [line.strip() for line in file]  # Remove any leading/trailing whitespace
    except FileNotFoundError:
        print("Error: 10kpasswords.txt file not found.")
        return

    while attempts < max_attempts:
        try:
            # Display the fake sudo password prompt with hidden input
            password = getpass.getpass(prompt="[sudo] password for {}: ".format("user"))

            if password in correct_passwords:
                is_password = True
                break
            print("Sorry, try again.")
            attempts += 1
        except Exception as e:
            print("An error occurred while capturing password:", e)
    
    
    # After max attempts, show failure message
    if is_password == False:
        print("sudo: {} incorrect password attempts".format(max_attempts))

    # Write captured attempts to a log file for further analysis
    #with open("/tmp/honeypot_password_log.txt", "a") as log_file:
    #    for attempt_num, captured_password in enumerate(captured_passwords, 1):
    #        log_file.write(f"Attempt {attempt_num}: {captured_password}\n")

    return is_password


