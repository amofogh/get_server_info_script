import pandas as pd
import paramiko


class SSHOperation:

    def __init__(self, username, password, hostname, port):
        self.hostname = hostname
        # Set up SSH client
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to the server with password-based authentication
            self.ssh.connect(hostname, port=port, username=username, password=password)
        except paramiko.AuthenticationException:
            print("Authentication failed. Please check your credentials.")
        except Exception as e:
            print(f"Error: {e}")

    def close_connection(self):
        self.ssh.close()

    def root_login(self, close_connection=False):
        # Check if root user can SSH directly
        root_login_command = "cat /etc/ssh/sshd_config | grep '^PermitRootLogin'"
        stdin, stdout, stderr = self.ssh.exec_command(root_login_command)
        permit_root_login = stdout.read().decode().strip()

        if permit_root_login == "PermitRootLogin no":
            print("Root can login: ", False)
        else:
            print("Root can login: ", True)
        if close_connection:
            self.close_connection()

    def ufw_status(self, close_connection=False):
        # Check if UFW is enabled
        ufw_status_command = "sudo ufw status"
        stdin, stdout, stderr = self.ssh.exec_command(ufw_status_command)
        ufw_status = stdout.read().decode().strip()

        if "Status: active" in ufw_status:
            print("UFW: ", True)
        else:
            print("UFW: ", False)
        if close_connection:
            self.close_connection()

    def open_ports(self, close_connection=False):
        # Show open ports with 0.0.0.0 using netstat
        open_ports_command = "netstat -ltnp | grep '0.0.0.0'"
        stdin, stdout, stderr = self.ssh.exec_command(open_ports_command)
        open_ports_output = stdout.read().decode().strip()
        print("Open Ports (0.0.0.0):\n", open_ports_output)

        if close_connection:
            self.close_connection()

    def server_info(self, close_connection=False):
        # Run commands to get RAM and CPU information
        commands = [
            "free -h | awk '/^Mem/ {print $2}'",
            "nproc --all"
        ]
        print('server_info: ')
        for command in commands:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            print(stdout.read().decode().strip())

        if close_connection:
            self.close_connection()
            
    def get_hard_drive_info(self, close_connection=False):
        # Get hard drive information using lsblk command
        lsblk_command = "lsblk"
        stdin, stdout, stderr = self.ssh.exec_command(lsblk_command)
        hard_drive_info = stdout.read().decode().strip()
        print("Hard Drive Information:\n", hard_drive_info)

        if close_connection:
            self.close_connection()
            
    def show_all(self):
        print('\n' + self.hostname)
        print('-' * 30)
        self.root_login()
        self.ufw_status()
        self.open_ports()
        self.server_info()
        self.get_hard_drive_info()


# Example usage:
# Replace 'your_username', 'your_password', 'your_server_ip', and 'your_port' with your actual SSH credentials
# ssh_op = SSHOperation(username='your_username', password='your_password', hostname='your_server_ip', port=your_port)
# ssh_op.root_login(close_connection=True)
# ssh_op.ufw_status(close_connection=True)
# ssh_op.open_ports(close_connection=True)
# ssh_op.server_info(close_connection=True)


def extract_credentials_from_excel(file_path):
    # Read data from Excel file using pandas
    df = pd.read_excel(file_path)

    # Iterate over rows and create SSHOperation instances
    for index, row in df.iterrows():
        ssh_op = SSHOperation(
            username=row['username'],
            password=row['password'],
            hostname=row['ip'],
            port=row['port']
        )
        ssh_op.show_all()  # Modify as needed based on your requirements


extract_credentials_from_excel('d:\\servers.xlsx')
