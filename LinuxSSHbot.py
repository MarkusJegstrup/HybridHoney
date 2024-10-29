#import openai
from dotenv import dotenv_values
import argparse
from datetime import datetime
import yaml
from time import sleep
import random
import os
import ollama

# Hello
main_command =""
args = []

def handle_cmd(cmd):
    parts = cmd.split()
    global main_command
    main_command = parts[0]
    global args
    args = parts[1:]

def plugin_pre_handler():
    print("Plugin-pre")

def plugin_post_handler(message):
    print("Plugin_post")
    return message 

config = dotenv_values(".env")
# openai.api_key = config["OPENAI_API_KEY"]
today = datetime.now()

history = open("history.txt", "a+", encoding="utf-8")
history.truncate(0)


if os.stat('history.txt').st_size == 0:
    with open('personalitySSH.yml', 'r', encoding="utf-8") as file:
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
   # initial_prompt = f"You are Linux OS terminal. Your personality is to answer the commands the user inputs, thus imitating a Linux OS terminal."
    messages = [{"role": "system", "content": initial_prompt}]
    if os.stat('history.txt').st_size == 0:
        for msg in messages:
                    history.write(msg["content"])
    else:
        history.write("The session continues in following lines.\n\n")
    
    history.close()

    while True:
        logs = open("history.txt", "a+", encoding="utf-8")
        try:
            print("ollamaStart")
            res = ollama.chat(
                model="llama3.2",
                messages=messages
            )
            print("ollamaDone")
            #msg = res.choices[0].message.content
            msg = res["message"]["content"]
            message = {"content": msg, "role": 'assistant'}

            lines = []

            if "$cd" in message["content"] or "$ cd" in message["content"]:
                message["content"] = message["content"].split("\n")[1]
            
            with open("plugin_post.txt", 'r') as file:
                    content = file.read()
                    if not(main_command=="") & (main_command in content):
                        message = plugin_post_handler(message)            
            messages.append(message)

            logs.write(messages[len(messages) - 1]["content"])
            logs.close()
            logs = open("history.txt", "a+", encoding="utf-8")
            
            if "will be reported" in messages[len(messages) - 1]["content"]:
                print(messages[len(messages) - 1]["content"])
                raise KeyboardInterrupt 

            if "PING" in message["content"]:
                lines = message["content"].split("\n")
                print(lines[0])

                for i in range(1, len(lines)-5):
                    print(lines[i])
                    sleep(random.uniform(0.1, 0.5))
                
                for i in range(len(lines)-4, len(lines)-1):
                    print(lines[i])
                messages[len(messages) - 1]
                user_input = input(f'{lines[len(lines)-1]}'.strip() + " ")
                messages.append({"role": "user", "content": user_input + f"\t<{datetime.now()}>\n" })
                logs.write(" " + user_input + f"\t<{datetime.now()}>\n")

            else:
                print("else")
                #print("\n", messages[len(messages) - 1]["content"], " ")
                user_input = input(f'\n{messages[len(messages) - 1]["content"]}'.strip() + " ")
                
                handle_cmd(user_input)
                with open("plugin_pre.txt", 'r') as file:
                    content = file.read()
                    if main_command in content:
                        plugin_pre_handler()
                    
                messages.append({"role": "user", "content": " " + user_input + f"\t<{datetime.now()}>\n"})
                logs.write(" " + user_input + f"\t<{datetime.now()}>\n")
            
        except KeyboardInterrupt:
            messages.append({"role": "user", "content": "\n"})
            print("")
            break
        
        logs.close()
    # print(res)




if __name__ == "__main__":
     main()