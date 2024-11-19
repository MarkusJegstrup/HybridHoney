import getpass

def plugin_pre_handler():
    print("Plugin-pre")

def handle_fake_sudo():
    attempts = 0
    max_attempts = 3
    captured_passwords = []

    while attempts < max_attempts:
        try:
            # Display the fake sudo password prompt with hidden input
            password = getpass.getpass(prompt="[sudo] password for {}: ".format("user"))

            captured_passwords.append(password)
            print("Sorry, try again.") 

            attempts += 1

        except Exception as e:
            print("An error occurred while capturing password:", e)

    # After max attempts, show failure message
    print("sudo: {} incorrect password attempts".format(max_attempts))

    # Write captured attempts to a log file for further analysis
    #with open("/tmp/honeypot_password_log.txt", "a") as log_file:
    #    for attempt_num, captured_password in enumerate(captured_passwords, 1):
    #        log_file.write(f"Attempt {attempt_num}: {captured_password}\n")

    return captured_passwords


def handle_fake_sudo_give_access():
    attempts = 0
    max_attempts = 2
    captured_passwords = []

    while attempts < max_attempts:
        try:
            # Display the fake sudo password prompt with hidden input
            password = getpass.getpass(prompt="[sudo] password for {}: ".format("user"))

            captured_passwords.append(password)
            print("Sorry, try again.") 

            attempts += 1

        except Exception as e:
            print("An error occurred while capturing password:", e)
    
    if attempts == 2:
        password = getpass.getpass(prompt="[sudo] password for {}: ".format("user"))
        captured_passwords.append(password)
        return captured_passwords
        

    # After max attempts, show failure message
    print("sudo: {} incorrect password attempts".format(max_attempts))

    # Write captured attempts to a log file for further analysis
    #with open("/tmp/honeypot_password_log.txt", "a") as log_file:
    #    for attempt_num, captured_password in enumerate(captured_passwords, 1):
    #        log_file.write(f"Attempt {attempt_num}: {captured_password}\n")

    return captured_passwords



def main() :
    
    passwords = handle_fake_sudo()

    message =""
    for password in passwords:
        newMessage = "[sudo] password for user: " + password + "\n"
        message = message + newMessage
    message = message
    print(message)

if __name__ == "__main__":
     main()
