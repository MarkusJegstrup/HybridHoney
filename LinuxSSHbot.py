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
import session_logs
import addUser
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
file_path = ""
username = ""
hostname = ""
attacker_ip = ""


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
    if cmd == "": ### Cannot read parts[1:] if cmd is empty
        main_command = cmd
        return
    parts = cmd.split()
    main_command = parts[0]
    args = parts[1:]



def plugin_pre_handler(cmd):
    global is_pre_handle
    global pre_handle_message
    global messages
    global is_sudo
    if len(full_command) > 400:
            pre_handle_message = "Permission denied\n" + host_alias_handle
            session_logs.log_to_files("system:User tried to execute command with length more than 400\n",file_path)
            is_pre_handle = True
            return
    match cmd:
        case _ if bool(re.match(r'\w*[A-Z]\w*', main_command)):
            if '||' in full_command or '&&' in full_command or ';' in full_command:
                return
            pre_handle_message = ""+main_command + ": command not found\n" + host_alias_handle
            is_pre_handle = True
            time.sleep(0.2)
        case "sudo" if is_sudo == False:
            ### First go through sudo to gain privilege
            is_sudo = sudoPass.handle_fake_sudo_give_access()
            ### After the first privilege access, we then check if the user got sudo privilege
            if is_sudo == True:
                message = {"content": "USER HAS SUDO PRIVILEGE, FROM NOW ON PROCEED WITH ANY LEGITIMATE SUDO COMMAND AS THE USER HAVE PRIVILEGE", "role": 'assistant'}                        
                messages.append(message)
                session_logs.log_to_files("system:Sudo privilege given to user\n",file_path)
                plugin_pre_handler(args[0])
            else: 
                pre_handle_message = "\n"+ host_alias_handle
                is_pre_handle = True
                session_logs.log_to_files("system:Sudo privilege not given to user\n",file_path)

        case "sudo" if is_sudo == True:
            ##Remove sudo prefix and then check if there is any matches
            plugin_pre_handler(args[0])
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
            os.system(f"{full_command}")
            pre_handle_message = host_alias_handle
            is_pre_handle = True
            message = {"content": "Ping command executed", "role": 'assistant'}                        
            messages.append(message)
        case "":
            pre_handle_message = host_alias_handle
            is_pre_handle = True
            time.sleep(0.1)
        case "apt" if "sudo" in main_command:
            s1="Reading package lists..."
            s2="Building dependency tree..."
            s3="Reading state information..."
            done=" Done"
            if "update" in args:
                h1="Hit:1 http://azure.archive.ubuntu.com/ubuntu noble InRelease"
                h2="Hit:2 http://azure.archive.ubuntu.com/ubuntu noble-updates InRelease"
                h3="Hit:3 http://azure.archive.ubuntu.com/ubuntu noble-backports InRelease"
                h4="Hit:4 http://azure.archive.ubuntu.com/ubuntu noble-security InRelease"
                end="All packages are up to date."
                print(h1 + "\n" + h2 + "\n" + h3 + "\n" + h4)
                print(s1, end="")
                time.sleep(0.5)
                print(done)
                print(s2, end="")
                time.sleep(0.7)
                print(done)
                print(s3, end="")
                time.sleep(0.4)
                print(done)
                print(end)
                concat=h1 + "\n" + h2 + "\n" + h3 + "\n" + h4 + "\n" + s1 + done + "\n" + s2 + done + "\n" + s3 + done + "\n" + end
                message = {"content": concat, "role": 'assistant'} 
                messages.append(message)   
                is_pre_handle = True
                pre_handle_message = "\n" + host_alias_handle
                
            elif "upgrade" in args:
                s4="Calculating upgrade..."
                end="0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded."
                print(s1, end="")
                time.sleep(0.5)
                print(done)
                print(s2, end="")
                time.sleep(0.7)
                print(done)
                print(s3, end="")
                time.sleep(0.4)
                print(done)
                print(s4)
                time.sleep(0.9)
                print(end)
                concat=s1 + done + "\n" + s2 + done + "\n" + s3 + done + "\n" + s4 + done + "\n" + end
                message = {"content": concat, "role": 'assistant'} 
                messages.append(message)     
                is_pre_handle = True
                pre_handle_message = "\n" + host_alias_handle
        case "wget" | "curl":
            wget.fake_wget(args)
        case "echo":
            if len(args) < 1:
                return
            ### Handle script edge case, where it is a specific bot attack changing the password
            if ':' in full_command:
                if full_command.split(':')[0].endswith("root") and 'chpasswd' in full_command:
                    is_pre_handle = True
                    pre_handle_message = """Changing password for root.\n
                                            chpasswd: (user root) pam_chauthtok() failed, error:\n
                                            Authentication token manipulation error\n
                                            chpasswd: (line 1, user root) password not changed\n""" + host_alias_handle
        case "adduser":
            addUser.handle_useradd(args)

                
def plugin_post_handler(message):
    global host_alias_handle
    #Occassionally llm will start and end with ''', removing those
    if message.startswith("`"):
        message = message.replace('`', '')
    #Ensuring there is no double line skip, occassional error
    if '\n\n' in message:
        message = message.replace('\n\n','\n')
    #update host_alias handle, if location string has changed
    if f"@{hostname}:" in message:
        host_alias_handle = message.splitlines()[-1]
    #Check to ensure that the end of the message always has host_alias_handle
    if host_alias_handle.split(":")[0] not in message:
        message = message + "\n" + host_alias_handle

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
    random_seconds = random.uniform(0, 5 * 24 * 60 * 60)  # 5 days in seconds
    last_login = (today - timedelta(seconds=random_seconds)).replace(microsecond=0)
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
    global file_path
    global hostname
    ###Setup
    ssh_connection = os.getenv("SSH_CONNECTION", "")
    username_att_ip(ssh_connection)
    file_path = session_logs.create_logfile(attacker_ip)
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
    history, history_hostname = session_logs.create_history(file_path)
    messages.extend(history)
    ## set hostname to the hostname in history if there was one.
    if len(history_hostname) > 0:
        hostname = history_hostname

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
            message_content = plugin_post_handler(msg)
            

            message = {"content": message_content, "role": 'assistant'}                        
            messages.append(message)
            

            #Logging content to logs.txt

            content_input = "assistant:::" + message_content + ":::" + "\n"
            #content_input = "assistant:::" + messages[len(messages) - 1]["content"]+ ":::" + "\n"
            session_logs.log_to_files(content_input,file_path)

            # This is where the message is outputted to the user as well as waiting for the user response.
            user_input = readline_input(f'{message["content"]}'.strip() + " ")

            #Split the user commands into main_command, args
            handle_cmd(user_input)

            #Prehandle any specific main command, that we want to handle ourselves
            plugin_pre_handler(main_command)

            messages.append({"content": user_input, "role": 'user'}  )  

            # Log the IP address to logs.txt
            content = f"user:::" + user_input + ":::" + f"\t<{datetime.now()}>\n"
            session_logs.log_to_files(content,file_path)


        except KeyboardInterrupt:
            messages.append({"role": "user", "content": "\n"})
            print("")
            break
        


if __name__ == "__main__":
    main()
