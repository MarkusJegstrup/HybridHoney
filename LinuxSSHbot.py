#!/usr/bin/env python3
import openai
from dotenv import dotenv_values
import argparse
from datetime import datetime, timedelta,timezone
import yaml
import time
import random
import os
import sudoPass
import wget
from dotenv import load_dotenv
import sys
import re
import readline

##Global Fields
full_command = ""
main_command = ""
messages = ""
args = []

host_alias_handle = ""

is_sudo = False
is_pre_handle = False
pre_handle_message = ""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
username = ""
hostname = ""
attacker_ip = ""


def log_to_files(logs_content):
    logs = open(os.path.join(BASE_DIR, "logs.txt"), "a+", encoding="utf-8")
    logs.write(logs_content)
    logs.close()

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
    global hostname
    if ssh_connection:
        # Extract the attacker's IP address (first field in SSH_CONNECTION)
        attacker_ip = ssh_connection.split()[0]
        username =  os.getlogin( )
        hostname = random.choice(["devbox", "workstation","testbench", "dbnode", "buildhost", "vmlab", "backend", "gateway", "docker", "webnode", "webserver", "webhost"])
        # print(f"Attacker IP Address: {attacker_ip}")
    else: 
        username = "dev"
        hostname = random.choice(["devbox", "workstation","testbench", "dbnode", "buildhost", "vmlab", "backend", "gateway", "docker", "webnode", "webserver", "webhost"])
    
    


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
    global is_pre_handle
    global pre_handle_message
    global messages
    match cmd:
        case _ if bool(re.match(r'\w*[A-Z]\w*', main_command)):
            pre_handle_message = ""+main_command + ": command not found\n" + host_alias_handle
            is_pre_handle = True
            time.sleep(0.2)
        case "sudo":
            ### First go through sudo to gain privilege
            if is_sudo == False:
                is_sudo = sudoPass.handle_fake_sudo_give_access()
            
            ### After the first privilege access, we then check if the user got sudo privilege
            if is_sudo == True:
                message = {"content": "USER HAS SUDO PRIVILEGE, PROCEED WITH THE USER COMMAND", "role": 'assistant'}                        
                messages.append(message)
            else: 
                pre_handle_message = "\n"+ host_alias_handle
                is_pre_handle = True
            
        case "exit":
            sys.exit()
            # os.system("exit")
        case "whoami":
            pre_handle_message = host_alias_handle.split('@')[0] + "\n"+ host_alias_handle
            is_pre_handle = True
            time.sleep(0.2)
        case "hostname":
            pre_handle_message = host_alias_handle.split('@')[1].split(':')[0] + "\n"+ host_alias_handle
            is_pre_handle = True
            time.sleep(0.2)
        case "date":
            now_utc = datetime.now(timezone.utc)
            formatted_time = now_utc.strftime("%a %b %d %H:%M:%S UTC %Y")
            pre_handle_message = ""+ formatted_time + "\n" + host_alias_handle
            is_pre_handle = True
            time.sleep(0.2)
        case "ping":
            if len(args)==1:
                os.system(f"ping {args[0]}")
                pre_handle_message = host_alias_handle
                is_pre_handle = True
                log_to_files(f"Ping {args[0]} success")
                message = {"content": f"Ping {args[0]} success", "role": 'assistant'}                        
                messages.append(message)
        case "":
            pre_handle_message = host_alias_handle
            is_pre_handle = True
            time.sleep(0.1)
        case "apt":
            s1="Reading package lists..."
            s2="Building dependency tree..."
            s3="Reading state information..."
            done=" Done"
            if args[0]=="update":
                is_pre_handle = True
                h1="Hit:1 http://azure.archive.ubuntu.com/ubuntu noble InRelease"
                h2="Hit:2 http://azure.archive.ubuntu.com/ubuntu noble-updates InRelease"
                h3="Hit:3 http://azure.archive.ubuntu.com/ubuntu noble-backports InRelease"
                h4="Hit:4 http://azure.archive.ubuntu.com/ubuntu noble-security InRelease"
                end="All packages are up to date."
                print(h1 + "\n" + h2 + "\n" + h3 + "\n" + h4 + "\n")
                print(s1)
                time.sleep(0.5)
                print(done)
                print(s2)
                time.sleep(0.7)
                print(done)
                print(s3)
                time.sleep(0.4)
                print(done)
                print(end)
                concat=h1 + "\n" + h2 + "\n" + h3 + "\n" + h4 + "\n" + s1 + done + "\n" + s2 + done + "\n" + s3 + done + "\n" + end
                messages.append(concat)   
                
            elif args[0]=="upgrade":
                is_pre_handle = True
                s4="Calculating upgrade..."
                end="0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded."
                print(s1)
                time.sleep(0.5)
                print(done)
                print("\n")
                print(s2)
                time.sleep(0.7)
                print(done)
                print("\n")
                print(s3)
                time.sleep(0.4)
                print(done)
                print("\n")
                print(s4)
                time.sleep(0.9)
                print(end)
                concat=s1 + done + "\n" + s2 + done + "\n" + s3 + done + "\n" + s4 + done + "\n" + end
                messages.append(concat)  
        case "wget":
            url=args[0]
            wget.fake_wget(url)

def plugin_post_handler(message):
    ##Basic Checks
    if message.startswith("`"):
        message = message.replace('`', '')
    if '\n\n' in message:
        message = message.replace('\n\n','\n')

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
    with open(os.path.join(BASE_DIR, "personalitySSH.yml"), 'r', encoding="utf-8") as file:
        identity = yaml.safe_load(file)

    personality = identity['personality']

    prompt = personality['prompt']

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
    global is_pre_handle
    global pre_handle_message
    global host_alias_handle
    global messages
    ###Setup
    ssh_connection = os.getenv("SSH_CONNECTION", "")
    username_att_ip(ssh_connection)
    setup()
    last_login, random_ip = last_login_random_ip()
    
    prompt = prompt_setup()

    parser = argparse.ArgumentParser(description = "Simple command line with GPT-3.5-turbo")
    parser.add_argument("--personality", type=str, help="A brief summary of chatbot's personality", 
                        default= prompt + 
                        f"\nBased on these examples make something of your own (with username: {username} and hostname: {hostname}) to be a starting message. Always start the communication in this way and make sure your output ends with '$'\n" + 
                        "Ignore date-time in <> after user input. This is not your concern.\n"
                        )

    args = parser.parse_args()
    initial_prompt = args.personality
    messages = [{"role": "system", "content": initial_prompt}]

    ###Before session write attacker ip to logs
    log_to_files(f"\nAttacker IP: {attacker_ip}\n")

    connection_message = f"Welcome to Ubuntu 24.04.1 LTS\nLast login: {last_login} from {random_ip}"
    ## Starting message
    pre_handle_message = ""+connection_message + f"\n{username}@{hostname}:~$ "
    is_pre_handle = True

    ##Extract the user, host handle
    host_alias_handle = pre_handle_message.splitlines()[-1]

    while True:


        
        try:
            if (is_pre_handle):
                msg = pre_handle_message
                is_pre_handle = False
            else:    
                msg = llm_response(messages)
            
            #Check for any mistakes in the generated response
            message = plugin_post_handler(msg)
            

            message = {"content": message, "role": 'assistant'}                        
            messages.append(message)
            

            #Logging content to and logs.txt
            content_input = "assistant:" + messages[len(messages) - 1]["content"] + "\n"
            log_to_files(content_input)

            # This i where the message is outputted to the user as well as waiting for the user response.
            user_input = readline_input(f'{message["content"]}'.strip() + " ")

            #Split the user commands into main_command, args
            handle_cmd(user_input)

            #Prehandle any specific main command, that we want to handle ourselves
            plugin_pre_handler(main_command)

            messages.append({"content": user_input, "role": 'user'}  )  

            # Log the IP address to logs.txt
            content = "user:" + user_input + f"\t<{datetime.now()}>\n"
            log_to_files(content)


        except KeyboardInterrupt:
            messages.append({"role": "user", "content": "\n"})
            print("")
            break
        





if __name__ == "__main__":
    main()
