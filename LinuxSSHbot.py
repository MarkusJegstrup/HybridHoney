import openai
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

def main():
    print("Running")
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": "Tell me an interesting fact about elephants",
            },
        ],
    )
    print(response["message"]["content"])

if __name__ == "__main__":
    main()    
