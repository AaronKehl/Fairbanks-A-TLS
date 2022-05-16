Logs Scripts

logs_split:
 - Copies the mail files generated via cronjobs and then clears the original.
 - This splits mail log files by months.
 - Root user mail logs are copied to /home/fairbanks/fairbanks/Logs/root/
 - fairbanks user mail logs are copied to /home/fairbanks/fairbanks/Logs/fairbanks/
 - The copied file has the YYYY_MM prefix appended to its name.

 **** NOTE:
    The root mail file requires sudo permissions or a root user to access.
