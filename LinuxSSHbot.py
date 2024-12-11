#!/usr/bin/env python3
import openai
from dotenv import dotenv_values
import argparse
from datetime import datetime, timedelta
import yaml
from time import sleep
import random
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
username = ""
attacker_ip = ""

# Get the SSH connection details from the environment
ssh_connection = os.getenv("SSH_CONNECTION", "")

if ssh_connection:
    # Extract the attacker's IP address (first field in SSH_CONNECTION)
    attacker_ip = ssh_connection.split()[0]
    username =  os.getlogin( )

    # Log the IP address
    #with open(os.path.join(BASE_DIR, "logs.txt"), "a+", encoding="utf-8") as log_file:
        #log_file.write(f"Attacker IP: {attacker_ip}\n")
else:
    print("IP address unreachable")

# Load environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY is not set or not loaded from the .env file.")

today = datetime.now()
random_days = random.randint(0, 5)
random_hours = random.randint(0, 23)
random_minutes = random.randint(0, 59)
random_seconds = random.randint(0, 59)
last_login = today - timedelta(days=random_days, hours=random_hours, minutes=random_minutes, seconds=random_seconds)
random_ip = ".".join(map(str, (random.randint(0, 255)
                        for _ in range(4))))

history = open(os.path.join(BASE_DIR, "history.txt"), "a+", encoding="utf-8")
history.truncate(0)

if os.stat(os.path.join(BASE_DIR, "history.txt")).st_size == 0:
    with open(os.path.join(BASE_DIR, "personalitySSH.yml"), 'r', encoding="utf-8") as file:
        identity = yaml.safe_load(file)

    identity = identity['personality']

    prompt = identity['prompt']

else:
    history.write("\nHere the session stopped. Now you will start it again from the beginning with the same user. You must respond just with starting message and nothing more. " +
                              "Make sure you use same file and folder names. Ignore date-time in <>. This is not your concern.\n")
    history.seek(0)
    prompt = history.read()


def main():
    first_prompt = True
    parser = argparse.ArgumentParser(description = "Simple command line with GPT-3.5-turbo")
    parser.add_argument("--personality", type=str, help="A brief summary of chatbot's personality", 
                        default= prompt + 
                        f"\nBased on these examples make something of your own (with username: {username} and different hostnames) to be a starting message. Always start the communication in this way and make sure your output ends with '$'\n" + 
                        "Ignore date-time in <> after user input. This is not your concern.\n")

    args = parser.parse_args()

    initial_prompt = f"You are Linux OS terminal. Your personality is: {args.personality}"
    messages = [{"role": "system", "content": initial_prompt}]
    if os.stat(os.path.join(BASE_DIR, "history.txt")).st_size == 0:
        for msg in messages:
                    history.write(msg["content"])
    else:
        history.write("The session continues in following lines.\n\n")
    
    history.close()
    connection_message = f"Welcome to Ubuntu 24.04.1 LTS\nLast login: {last_login} from {random_ip}\n"
    print(connection_message)

    while True:

        logs = open(os.path.join(BASE_DIR, "history.txt"), "a+", encoding="utf-8")
        logcmd = open(os.path.join(BASE_DIR, "logs.txt"), "a+", encoding="utf-8")
        try:
            res = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages = messages,
                temperature = 0.0,
                max_tokens = 800
            )

            msg = res.choices[0].message.content
            message = {"content": msg, "role": 'assistant'}

            if "$cd" in message["content"] or "$ cd" in message["content"]:
                message["content"] = message["content"].split("\n")[1]

            lines = []

            messages.append(message)
            
            # Log the IP address
            if first_prompt:
                    logcmd.write(f"Attacker IP: {attacker_ip}\n")
                    first_prompt = False
            
            logs.write(messages[len(messages) - 1]["content"])
            logcmd.write(messages[len(messages) - 1]["content"])
            logs.close()
            logcmd.close()

            logs = open(os.path.join(BASE_DIR, "history.txt"), "a+", encoding="utf-8")
            logcmd = open(os.path.join(BASE_DIR, "logs.txt"), "a+", encoding="utf-8")
            
            if "will be reported" in messages[len(messages) - 1]["content"]:
                print(messages[len(messages) - 1]["content"])
                logs.write(" " + user_input + f"\t<{datetime.now()}>\n")
                logcmd.write(" " + user_input + f"\t<{datetime.now()}>\n")
                raise KeyboardInterrupt 

            if "PING" in message["content"]:
                lines = message["content"].split("\n")
                print(lines[0])

                for i in range(1, len(lines)-5):
                    print(lines[i])
                    sleep(random.uniform(0.1, 0.5))
                
                for i in range(len(lines)-4, len(lines)-1):
                    print(lines[i])
                
                user_input = input(f'{lines[len(lines)-1]}'.strip() + " ")
                messages.append({"role": "user", "content": user_input + f"\t<{datetime.now()}>\n" })

                logs.write(" " + user_input + f"\t<{datetime.now()}>\n")
                logcmd.write(" " + user_input + f"\t<{datetime.now()}>\n")

            else:
                #print("\n", messages[len(messages) - 1]["content"], " ")
                user_input = input(f'\n{messages[len(messages) - 1]["content"]}'.strip() + " ")
                messages.append({"role": "user", "content": " " + user_input + f"\t<{datetime.now()}>\n"})
                logs.write(" " + user_input + f"\t<{datetime.now()}>\n")
                logcmd.write(" " + user_input + f"\t<{datetime.now()}>\n")
            
        except KeyboardInterrupt:
            messages.append({"role": "user", "content": "\n"})
            print("")
            break
        
        logs.close()
        logcmd.close()
    # print(res)

if __name__ == "__main__":
    main()
