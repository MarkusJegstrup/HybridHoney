import re
def split_commands(command):
    pattern = r"(.*?)([;&|]{1,2}|$)"
    matches = re.findall(pattern,command)
    return [(cmd.strip(), op.strip()) for cmd, op in matches if cmd.strip() or op.strip()]



splitting = []

splitting = split_commands(" echo ; cd Projects && mkdir no || ping google.com | gg")

print(splitting)