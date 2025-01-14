
import os


def create_logfile(filename):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if filename == "":
        filename = "local_number1"
    file_path = os.path.join(BASE_DIR,"logs", filename+".txt")

    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("")
    return file_path
    

def create_history(file_path):
    messages = []
    hostname = ""

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return messages

    # Read and parse the file
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    current_role = ""
    current_content = ""
    start_message = False

    for line in lines:

        parts = line.split(":::")
        #Start of a message
        if "user:::" in line or "assistant:::" in line:
            current_role = parts[0].strip()
            # There are two ::: seperators, the content is between the two seperators
            if len(parts) == 3:
                current_message = {"content": parts[1], "role": current_role}
                messages.append(current_message)
            # There is one ::: seperator, meaning the content continues on the next lines
            elif len(parts) == 2:
                current_content = current_content + parts[1]
                start_message = True

        #If no user or assistant, then it is multiple lines of content
        elif start_message:
            #There is no ::: in this line 
            if len(parts) == 1:
                current_content = current_content + parts[0]
            #There is one :::, meaning it is the end of the content
            elif len(parts) == 2:
                current_content = current_content + parts[0]
                if current_role == "assistant" and hostname == "" and '@' in parts[0]:
                    hostname = parts[0].split('@')[1].split(':')[0]
                current_message = {"content": current_content, "role": current_role}
                messages.append(current_message)
                current_content = ""
                start_message = False
        elif "system:::" in line:
            if len(parts) >= 2:
                current_message = {"content": line.split(":::")[1], "role":"system"}
                messages.append(current_message)

    return messages, hostname

def log_to_files(logs_content,file_path):
    logs = open(file_path, "a+", encoding="utf-8")
    logs.write(logs_content)
    logs.close()
