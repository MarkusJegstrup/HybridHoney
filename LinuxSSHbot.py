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
#username = ""
attacker_ip = ""
#machine_name = ""
# Get the SSH connection details from the environment
ssh_connection = os.getenv("SSH_CONNECTION", "")

if ssh_connection:
    attacker_ip = ssh_connection.split()[0]
else:
    print("IP address unreachable")

# Load environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

today = datetime.now()

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY is not set or not loaded from the .env file.")

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
    parser = argparse.ArgumentParser(description = "Simple command line with GPT-3.5-turbo")
    parser.add_argument("--personality", type=str, help="A brief summary of chatbot's personality", 
                        default= prompt + 
                        f"\nBased on these examples make something of your own (different username and hostname) to be a starting message. Always start the communication in this way and make sure your output ends with '$'. For the last login date use {today}\n" + 
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


    #readying log files and history and log the IP address in raw logs before prompting 
    session_logs = open(os.path.join(BASE_DIR, "history.txt"), "a+", encoding="utf-8")
    log_raw = open(os.path.join(BASE_DIR, "raw_logs.txt"), "a+", encoding="utf-8")
    log_cmd = open(os.path.join(BASE_DIR, "cmd_logs.txt"), "a+", encoding="utf-8")
    log_raw.write(f"Attacker IP: {attacker_ip} " + f"\t<{datetime.now()}>\n")
    session_logs.write(f"Attacker IP: {attacker_ip} " + f"\t<{datetime.now()}>\n")
    log_cmd.write(f"Attacker IP: {attacker_ip} " + f"\t<{datetime.now()}>\n")
    
    while True:

        try:
            res = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages = messages,
                temperature = 0.0,
                max_tokens = 800
            )

            msg = res.choices[0].message.content
            msg = msg.replace('`', '')
            message = {"content": msg, "role": 'assistant'}

            if "$cd" in message["content"] or "$ cd" in message["content"]:
                message["content"] = message["content"].split("\n")[1]

            lines = []

            messages.append(message)
            
            session_logs.write("assistant:"+messages[len(messages) - 1]["content"])

            if len(messages) > 1:
                log_cmd.write("assistant:"+messages[len(messages) - 1]["content"])
            
            if "will be reported" in messages[len(messages) - 1]["content"]:
                print(messages[len(messages) - 1]["content"])
                session_logs.write(" " + user_input + f"\t<{datetime.now()}>\n")
                log_cmd.write(" " + user_input + f"\t<{datetime.now()}>\n" + attacker_ip + "\n")
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
                log_cmd.write(messages[len(messages) - 1]["content"])
                messages.append({"role": "user", "content": user_input + f"\t<{datetime.now()}>\n" })

                session_logs.write(f"user {attacker_ip}:" + user_input + f"\t<{datetime.now()}>\n")
                log_cmd.write(f"user {attacker_ip}:" + user_input + f"\t<{datetime.now()}>\n")

            else:
                #print("\n", messages[len(messages) - 1]["content"], " ")
                user_input = input(f'\n{messages[len(messages) - 1]["content"]}'.strip() + " ")
                if user_input == "":
                    continue
                messages.append({"role": "user", "content": " " + user_input + f"\t<{datetime.now()}>\n"})
                session_logs.write(f"user {attacker_ip}:" + user_input + f"\t<{datetime.now()}>\n")
                log_cmd.write(f"user {attacker_ip}:" + user_input + f"\t<{datetime.now()}>\n")
            
        except KeyboardInterrupt:
            messages.append({"role": "user", "content": "\n"})
            print("")
            break
        
    session_logs.close()
    log_raw.close()
    log_cmd.close()
    # print(res)

if __name__ == "__main__":
    main()
