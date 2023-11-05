import os
import subprocess
import paramiko
from datetime import datetime

current_folder = os.path.abspath(os.path.dirname(__file__))
timestamp = datetime.timestamp(datetime.now())
zip_filename = f"archive_{timestamp}.zip"
remote_server = "35.239.41.43"
remote_username = "ducrouxolivier"

git_archive_command = ["git", "archive", "--format=zip", "-o", zip_filename, "HEAD"]
subprocess.run(git_archive_command, cwd=current_folder)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(remote_server, username=remote_username)

scp = ssh.open_sftp()
scp.put(zip_filename, zip_filename)
scp.close()

folder_name = zip_filename.split('.')[0]
ssh.exec_command(f"unzip {zip_filename} -d {folder_name} && rm {zip_filename}")
ssh.exec_command(f"cd {folder_name} && pip3 install .")

os.remove(zip_filename)
ssh.close()
