echo Install dependencies
sudo apt update
sudo apt install python3
sudo apt install python3-openai
sudo apt install python3-dotenv


echo Edit SSH configurations
sudo groupadd redirect
sudo chmod 644 /etc/ssh/sshd_config


sudo cat << EOF >> /etc/ssh/sshd_config
PermitEmptyPasswords yes
PasswordAuthentication yes
Match Group redirect
       ForceCommand /usr/local/bin/honeypot_shell
EOF

sudo systemctl restart ssh

>echo fix program permissions
sudo chmod 755 /home/$SUDO_USER
sudo chmod 755 /home/$SUDO_USER/HybridHoney
sudo chmod 666 logs.txt
sudo chmod 777 /home/$SUDO_USER/HybridHoney/logs
sudo chgrp -R redirect .
sudo chmod -R g+rwx .

echo Make shell for python program

chmod +x LinuxSSHbot.py
touch /usr/local/bin/honeypot_shell
sudo chmod 644 /usr/local/bin/honeypot_shell
sudo cat << EOF >> /usr/local/bin/honeypot_shell
#!/bin/bash
/usr/bin/python3 /home/$SUDO_USER/HybridHoney/LinuxSSHbot.py
EOF
sudo chmod +x /usr/local/bin/honeypot_shell
sudo chgrp redirect .
sudo chmod g+x .

sudo cat << EOF >> visudo
%redirect ALL=(ALL) NOPASSWD: /usr/sbin/useradd, /usr/bin/openssl
EOF

echo Add passwordless user and put them in the group redirect:
sudo useradd -m -g redirect userA
sudo passwd -d userA
