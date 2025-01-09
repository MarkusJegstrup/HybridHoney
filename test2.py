

line = "user this is content "


parts = line.split(":::")
current_role = parts[0].strip()


print(current_role)
print(len(parts))

