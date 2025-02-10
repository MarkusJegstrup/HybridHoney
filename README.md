# HybridHoney

The `HybridHoney` honeypot employs GPT-4o-mini to simulate an SSH honeypot. 
The tool was created as part of a master thesis, conducted by 3 students from DTU compute.

## Features

`HybridHoney` is developed in Python and employs GPT-4o-mini from Open AI. Its key features include:
1. Dynamic file system and file contents generated by LLM
2. Personality promt for LLM in-context-learning
3. Session logging and session history
4. File download for further inspection upon wget, curl and tftp
5. Emulated sudo access
6. Improved formatting and terminal interface actions

## Installation and usage
Can either be run locally or on a virtual machine, 
certain features that has to do with permissions, user creation only works by setting it with setup script.

With
Generally clone the project and run the commands in the HybridHoney directory      

For local deployment:
```bash
~$ # Install requirements
~$ pip install -r requirements.txt
~$
~$ # Create env file
~$ cp env_TEMPLATE .env
~$ # Edit the file to contain you API key: OPENAI_API_KEY=<your-key-here>
~$ vim .env
```
Run the program:
```
~$ python3 LinuxSSHbot.py 
```
For Virtual deployment:      
Make sure you are in HybridHoney directory      
Create .env file and add your API key.       
Make setup.sh an executable:    
"chmod+x setup.sh"          
run the setup.sh script with sudo privileges:     
"sudo ./setup.sh".      
Access the honeypot through SSH connection:        
ssh userA@`<your-IP-address>`      

