Executing the create_symlinks script, with the modified .bashrc file in place,
will create symbolic links to scripts we wish to regularly use from anywhere.

This allows us to run commands without referencing the path to the script.
- e.g. instead of /home/fairbanks/fairbanks/scripts/aws/syncaws
- we can use: syncaws

To make symlinks work, from fairbanks user account:
1. Edit ~/.bashrc file
 - nano ~/.bashrc
 - Add the following to the bottom of the file:
  # >>> fairbanks A-TLS initialize >>>
  export PATH=$PATH:~/fairbanks/symlinks
  # <<< fairbanks A-TLS initialize <<<
2. cd /home/fairbanks/fairbanks/symlinks
3. ./create_symlinks
4. exit and restart terminal, to add symlinks to pathing.

To add sudo permissions to these files, modify the sudoers.tmp file by:
1. sudo su -l root
2. sudo visudo
3. Change: Defaults        secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/s"
 - TO: Defaults        secure_path="/home/fairbanks/fairbanks/symlinks:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/s"

To make symlinks work, from root user account:
1. sudo su -l root
2. Edit ~/.bashrc file
 - nano ~/.bashrc
 - Add the following to the bottom of the file:
   # >>> fairbanks A-TLS initialize >>>
   export PATH=$PATH:~/../home/fairbanks/fairbanks/symlinks
   # <<< fairbanks A-TLS initialize <<<
