import getpass


def handle_fake_sudo_give_access():
    attempts = 0
    max_attempts = 3
    correct_passwords = ["", "password", "password123", "123456", "qwerty", "123123", "1234", "12345", "password1"]
    is_password = False

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


