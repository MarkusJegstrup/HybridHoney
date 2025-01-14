echo Install dependencies
sudo apt update
sudo apt install python3
sudo apt install python3-openai
sudo apt install python3-dotenv


echo Edit SSH configurations
sudo groupadd redirect
sudo chmod 666 /etc/ssh/sshd_config


sudo cat << EOF >> /etc/ssh/sshd_config
PermitEmptyPasswords yes
PasswordAuthentication yes
Match Group redirect
       ForceCommand /usr/local/bin/honeypot_shell
EOF

sudo systemctl restart ssh

echo Make shell for python program

chmod +x LinuxSSHbot.py
touch /usr/local/bin/honeypot_shell
sudo chmod 666 /usr/local/bin/honeypot_shell
sudo cat << EOF >> /usr/local/bin/honeypot_shell
#!/bin/bash
/usr/bin/python3 /home/$USER/LLMHoney/LinuxSSHbot.py
EOF
sudo chmod +x /usr/local/bin/honeypot_shell
sudo chgrp redirect .
sudo chmod g+x .

echo fix program permissions
sudo chmod 755 /home/$USER
sudo chmod 755 /home/$USER/LLMHoney
sudo chmod 666 logs.txt
sudo chmod 777 home/$USER/downloads
sudo chmod 766 home/$USER/downloads/dlog.txt

echo Add passwordless user admin and put them in the group redirect:
sudo useradd -m -g redirect admin
sudo passwd -d admin

