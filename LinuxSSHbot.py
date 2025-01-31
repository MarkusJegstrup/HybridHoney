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
#Input
full_command = ""
main_command = ""
messages = ""
args = []
#Flags
is_sudo = False
is_pre_handle = False
is_multi_cmd = False
#prehandle output
pre_handle_message = ""
#File path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = ""
#user handle
host_alias_handle = ""
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

#Takes the user input and updates global variables that holds full command, main command and arguments.
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

#Seperates command, where seperator is: ';' '||' '&&'
def split_commands(command):
    pattern = r"(.*?)(;|&&|\|\||$)"
    matches = re.findall(pattern,command)
    return [(cmd.strip(), op.strip()) for cmd, op in matches if cmd.strip() or op.strip()]
#Removes the last line of a string
def remove_last_line(input_string):
    lines = input_string.split('\n')
    if len(lines) > 0:
        lines = lines[:-1] 
    return '\n'.join(lines)
#Check if there is multiple commands
def checkMultiCmd(user_input):
    multi_cmds = split_commands(user_input)
    global is_multi_cmd
    if len(multi_cmds) > 1:
        exist_pre_handle = False
        is_multi_cmd = True
        for cmd,op in multi_cmds:
            handle_cmd(cmd)
            plugin_pre_handler(main_command)
            if is_pre_handle:
                exist_pre_handle = True
        is_multi_cmd = False
        if exist_pre_handle:
            return True
    return False
# Handle multicommands, by either prehandling them or let the llm handle it.
def multiCommandExecution(command_with_operators):
    global messages
    global is_pre_handle
    global pre_handle_message
    final_output = ""
    # Operator is if we want to add the operator logic into it.
    for command,operator in command_with_operators:
        handle_cmd(command)
        is_pre_handle = False
        plugin_pre_handler(main_command)
        if is_pre_handle:
            pre_handle_output = plugin_post_handler(pre_handle_message)
            final_output += remove_last_line(pre_handle_output)
        else:
            messages.append({"content": command, "role":'user'})
            llm_output = plugin_post_handler(llm_response(messages))
            final_output += remove_last_line(llm_output)
            messages.pop()
        if not operator == "":
            final_output += "\n"

    final_output += "\n" + host_alias_handle
    return final_output

#Prehandle, check if there is specific command handling needed. Otherwise if no specific handling needed the LLM handles it.
def plugin_pre_handler(cmd):
    global is_pre_handle
    global pre_handle_message
    global messages
    global is_sudo
    #Max length of user input, 
    if len(full_command) > 800:
            pre_handle_message = "Permission denied\n" + host_alias_handle
            session_logs.log_to_files("system:User tried to execute command with length more than 800\n",file_path)
            is_pre_handle = True
            return
    #Match the main command, the first input token
    match cmd:
        case _ if bool(re.match(r'\w*[A-Z]\w*', main_command)): #
            if '||' in full_command or '&&' in full_command or ';' in full_command:
                return
            pre_handle_message = ""+main_command + ": command not found\n" + host_alias_handle
            is_pre_handle = True
            time.sleep(0.2)
        case "sudo" if is_sudo == False:
            if len(args) == 0:
                time.sleep(0.2)
                with open(os.path.join(BASE_DIR, "sudomessage.txt"), 'r', encoding="utf-8") as message_file:
                    sudo_message = message_file.read()
                pre_handle_message = ""+sudo_message +host_alias_handle
                is_pre_handle = True
                return
            #If check for multi cmd executions
            if is_multi_cmd:
                is_pre_handle = True
                return
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
            if len(args) == 0:
                time.sleep(0.2)
                with open(os.path.join(BASE_DIR, "sudomessage.txt"), 'r', encoding="utf-8") as message_file:
                    sudo_message = message_file.read()
                pre_handle_message = ""+sudo_message +host_alias_handle
                is_pre_handle = True
                return
            ##Remove sudo prefix and then check if there is any matches on the main command
            plugin_pre_handler(args[0])
        case "exit":
            session_logs.log_to_files("system::: Logout:" + f"{datetime.now(timezone.utc).strftime("%a %b %d %H:%M:%S %Y")}" + " from " + attacker_ip + ":::\n", file_path)
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
        case "date": # Give correct date and time
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
        case "": #No command, immediately go to next line.
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
        case "wget" | "curl" | "tftp":
            wget.fake_wget(args)
        case "useradd":
            addUser.handle_useradd(full_command)
            is_pre_handle = True
            pre_handle_message=""

                
def plugin_post_handler(message):
    global host_alias_handle
    #Occassionally llm will start and end with ''', removing those
    if message.startswith("`"):
        message = message.replace('`', '')
    #Ensuring there is no double line skip when ls, occassional error
    if '\n\n' in message and "ls" in main_command:
        message = message.replace('\n\n','\n')
    #update host_alias handle, if location string has changed
    if f"@{hostname}:" in message:
        host_alias_handle = message.splitlines()[-1]
    #Check to ensure that the end of the message always has host_alias_handle
    if f"@{hostname}:" not in message:
        message = message + "\n" + host_alias_handle
    return message

#Communicate with LLM
def llm_response(messages):
    res = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages = messages,
                temperature = 0.0,
                max_tokens = 800
            )
    return res.choices[0].message.content

def main():
    #### Variable setup, global variables that are gonna change values
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
    
    # Load environment variables from the .env file
    load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))
    # Set the OpenAI API key, from .env file. 
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # Check if it is API key
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY is not set or not loaded from the .env file.")
    
    #Personality input to LLM
    with open(os.path.join(BASE_DIR, "personalitySSH.yml"), 'r', encoding="utf-8") as file:
        personality = yaml.safe_load(file)
    prompt = personality['personality']['prompt']

    parser = argparse.ArgumentParser(description = "Simple command line with GPT-3.5-turbo")
    parser.add_argument("--personality", type=str, help="A brief summary of chatbot's personality", 
                        default= prompt + 
                        f"\nBased on these examples make something of your own (with username: {username} and hostname: {hostname}) to be a starting message. Always start the communication in this way and make sure your output ends with '$'\n" + 
                        "Ignore date-time in <> after user input. This is not your concern.\n"
                        )
    initial_prompt = parser.parse_args().personality
    messages = [{"role": "system", "content": initial_prompt}]


    history, history_hostname = session_logs.create_history(file_path)
    messages.extend(history)
    #Time, a last login time that is a bit off the current time and create a random ip.
    time_now = datetime.now(timezone.utc)
    adjusted_time = time_now - timedelta(hours=1, minutes=-random.randint(10, 59))
    last_login = adjusted_time.strftime("%a %b %d %H:%M:%S %Y")
    random_ip = ".".join(map(str, (random.randint(0, 255) 
                            for _ in range(4))))
    #Add ubuntu banner as the connection message
    with open(os.path.join(BASE_DIR, "connection_message.txt"), 'r', encoding="utf-8") as message_file:
        banner_file = message_file.read()
    corrected_banner = banner_file.replace('timedate',time_now.strftime("%a %b %d %H:%M:%S UTC %Y"))
    connection_message = corrected_banner + f"\nLast login: {last_login} from {random_ip}"
    
    ## set hostname to the hostname in history if there was one.
    if len(history_hostname) > 0:
        hostname = history_hostname
    
    #Use the users last login instead of a random one.
    if len(history) > 0:
        if "Logout" in messages[-1]["content"]:
            connection_message = f"{corrected_banner}\nLast login: " + messages[-1]["content"].split("Logout:")[1]

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
                pre_handle_message=""
            else:    
                msg = llm_response(messages)
            
            #Check for any mistakes in the generated response
            message_content = plugin_post_handler(msg)
            
            #Update LLM input
            message = {"content": message_content, "role": 'assistant'}                        
            messages.append(message)

            #Logging content to logs.txt
            content_input = "assistant:::" + message_content + ":::" + "\n"
            #content_input = "assistant:::" + messages[len(messages) - 1]["content"]+ ":::" + "\n"
            session_logs.log_to_files(content_input,file_path)

            # This is where the message is outputted to the user as well as waiting for the user response.
            user_input = readline_input(f'{message["content"]}'.strip() + " ")

            #Check for multiple cmd executions
            if checkMultiCmd(user_input):
                pre_handle_message = multiCommandExecution(multiCmds)
                is_pre_handle = True
            else:
                #Split the user commands into main_command, args
                handle_cmd(user_input)
                #Prehandle any specific main command, that we want to handle ourselves
                plugin_pre_handler(main_command)

            #Update LLM input
            messages.append({"content": user_input, "role": 'user'}  )  

            # Log the IP address to logs.txt
            content = f"user:::" + user_input + ":::" + f"\t<{datetime.now()}>\n"
            session_logs.log_to_files(content,file_path)


        except KeyboardInterrupt:
            #messages.append({"role": "user", "content": "\n"})
            print("^C")
            pre_handle_message = "" + host_alias_handle
            is_pre_handle = True
            continue
        


if __name__ == "__main__":
    main()
