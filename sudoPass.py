import getpass
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Gives the 
def handle_fake_sudo_give_access():
    attempts = 0
    max_attempts = 3
    is_password = False

    # Load correct passwords from a file
    try:
        with open(os.path.join(BASE_DIR, "10kpasswords.txt"), "r", encoding="utf-8") as file:
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

    return is_password


