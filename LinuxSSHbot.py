#!/usr/bin/env python3
import openai
from dotenv import dotenv_values
import argparse
from datetime import datetime, timedelta
import yaml
from time import sleep
import random
import os
import sudoPass
from dotenv import load_dotenv
import sys
import re

##Global Fields
full_command = ""
main_command =""
args = []

host_alias_handle = ""

pre_handle = False
pre_handle_message = ""

commands = ["pwd", "whoami", "cat /etc/passwd", "uname -a", "id"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
username = ""
attacker_ip = ""
first_prompt = True

history = open(os.path.join(BASE_DIR, "history.txt"), "a+", encoding="utf-8")
history.truncate(0)


def log_to_files(history_content, logs_content):
    history = open(os.path.join(BASE_DIR, "history.txt"), "a+", encoding="utf-8")
    logs = open(os.path.join(BASE_DIR, "logs.txt"), "a+", encoding="utf-8")
    history.write(history_content)
    logs.write(logs_content)
    logs.close()
    history.close()

def readline_input(prompt):
    try:
        user_input = input(prompt)
        return user_input
    except EOFError:
        print("\nExiting terminal.")
        exit(0)
        
def get_last_content(messages, role):
    ##Returns the last message by the given role
    if messages[len(messages) - 1]["role"] == role:
        return messages[len(messages) - 1]["content"]
    else:
        return messages[len(messages) - 2]["content"]


def username_att_ip(ssh_connection):
    global attacker_ip
    global username
    if ssh_connection:
        # Extract the attacker's IP address (first field in SSH_CONNECTION)
        attacker_ip = ssh_connection.split()[0]
        username =  os.getlogin( )
        # print(f"Attacker IP Address: {attacker_ip}")
    else: 
        username = "matthew"
    
    


def handle_cmd(cmd):
    global full_command
    global main_command
    global args
    full_command = cmd
    if cmd == "": ### Cannot read parts[0] and args[1:] with empty cmd
        main_command = ""
        return
    parts = cmd.split()
    main_command = parts[0]
    args = parts[1:]



def plugin_pre_handler(cmd):
    global pre_handle
    global pre_handle_message
    match cmd:
        case "sudo":
            sudoPass.handle_fake_sudo_give_access()
        case "exit":
            sys.exit()
            # os.system("exit")
        case "whoami":
            pre_handle_message = host_alias_handle.split('@')[0] + "\n"+ host_alias_handle
            pre_handle = True
        case "":
            pre_handle_message = host_alias_handle
            pre_handle = True

def plugin_post_handler(message):
    #open(os.path.join(BASE_DIR, "plugin_post.txt"), 'r')
    ##Basic Checks
    if message.startswith("`"):
        message = message.replace('`', '')


    ##Command checks

    return message


def setup():
    # Load environment variables from the .env file
    load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

    # Set the OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY is not set or not loaded from the .env file.")
    
    # config = dotenv_values(".env")
    # openai.api_key = config["OPENAI_API_KEY"]


def last_login_random_ip():
    today = datetime.now()
    random_days = random.randint(0, 5)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    random_seconds = random.randint(0, 59)
    last_login = today - timedelta(days=random_days, hours=random_hours, minutes=random_minutes, seconds=random_seconds)
    random_ip = ".".join(map(str, (random.randint(0, 255) 
                            for _ in range(4))))
    return last_login, random_ip

def prompt_setup():
    prompt = ""
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
    return prompt

def llm_response(messages):
    res = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages = messages,
                temperature = 0.0,
                max_tokens = 800
            )

    return res.choices[0].message.content

def main():
    #### Variable setup
    global pre_handle
    global first_prompt
    global pre_handle_message
    global host_alias_handle
    ###Setup
    ssh_connection = os.getenv("SSH_CONNECTION", "")
    username_att_ip(ssh_connection)
    setup()
    last_login, random_ip = last_login_random_ip()
    
    prompt = prompt_setup()

    parser = argparse.ArgumentParser(description = "Simple command line with GPT-3.5-turbo")
    parser.add_argument("--personality", type=str, help="A brief summary of chatbot's personality", 
                        default= prompt + 
                        f"\nBased on these examples make something of your own (with username: {username} and different hostnames) to be a starting message. Always start the communication in this way and make sure your output ends with '$'\n" + 
                        "Ignore date-time in <> after user input. This is not your concern.\n"
                        )

    args = parser.parse_args()
    initial_prompt = args.personality
    messages = [{"role": "system", "content": initial_prompt}]
    #if os.stat(os.path.join(BASE_DIR, "history.txt")).st_size == 0:
    #    for msg in messages:
    #        print("hello")
    #       history.write(msg["content"])
    #else:
    #    history.write("The session continues in following lines.\n\n")
    
    history.close()
    connection_message = f"Welcome to Ubuntu 24.04.1 LTS\nLast login: {last_login} from {random_ip}"
    ## Starting message
    initial_message = llm_response(messages)
    pre_handle_message = ""+connection_message + plugin_post_handler(initial_message)
    pre_handle = True

    ##Extract the user, host handle
    host_alias_handle = pre_handle_message.splitlines()[-1]

    while True:


        
        try:
            if (pre_handle):
                msg = pre_handle_message
                pre_handle = False
            else:    
                msg = llm_response(messages)

            
            message = plugin_post_handler(msg)
            




            message = {"content": message, "role": 'assistant'}                        
            messages.append(message)
            
            ###Before session write attacker ip to logs
            if first_prompt:
                log_to_files(f"Attacker IP: {attacker_ip}\n",f"\nAttacker IP: {attacker_ip}\n")
                first_prompt = False

            #Logging content to history.txt and logs.txt
            content_input = "assistant:" + messages[len(messages) - 1]["content"] + "\n"
            log_to_files(content_input,content_input)

            user_input = readline_input(f'{message["content"]}'.strip() + " ")
            #user_input = readline_input(f'{messages[len(messages) - 1]["content"]}'.strip() + " ")
            

            handle_cmd(user_input)

            plugin_pre_handler(main_command)

            messages.append({"content": user_input, "role": 'user'}  )  

            # Log the IP address to history.txt and logs.txt
            content = "user:" + user_input + f"\t<{datetime.now()}>\n"
            log_to_files(content, content)


        except KeyboardInterrupt:
            messages.append({"role": "user", "content": "\n"})
            print("")
            break
        





if __name__ == "__main__":
    main()
