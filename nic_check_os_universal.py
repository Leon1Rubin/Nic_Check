import paramiko # Import the paramiko module
import time  # Import the time module

# Function to check if the server is online
def check_ssh_connection(hostname, username, password):
    # Create an SSH client object
    ssh = paramiko.SSHClient()
    # Set the SSH client object to automatically add unrecognized SSH keys
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Attempt to connect to the SSH server with password authentication
    try:
        # Attempt to connect to the SSH server with password authentication
        ssh.connect(hostname, port=22, username=username, password=password, allow_agent=False, look_for_keys=False)
        # If the connection is successful, print a message indicating that the server is online
        print(f"Node {hostname} is online ✅")
    # If an error occurs during the connection attempt, print a message indicating that the server is offline
    except Exception as e:
        print(f"Node {hostname} is offline ❌ Error: {str(e)}")
    # Close the SSH connection
    finally:
        # Close the SSH connection
        ssh.close()

# Function to run a command on an SSH connection and return the output
def run_ssh_command(hostname, username, password, node, command, server_type):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the SSH server with password authentication
        ssh.connect(hostname, port=22, username=username, password=password, allow_agent=False, look_for_keys=False)

        # Extract the bus information from the command
        bus_info = command.split('-s')[-1].split()[0].strip()

        # Execute the command with grep -v to exclude the specific line
        command = f"{command} | grep -v 'TrErr- Train- SlotClk+ DLActive- BWMgmt- ABWMgmt-'"
        stdin, stdout, stderr = ssh.exec_command(command)
        # Read the output from the SSH connection
        output = stdout.read().decode('utf-8')

        # Print formatted output
        print(f"Output from {hostname} ({node}):")
        if "sudo mlxlink" in command:
            print(f"Bus {bus_info}")

            # Adjust the verification pattern based on the server type
            if server_type == "dell":
                verification_pattern = "Speed 16GT/s (ok), Width x16 (ok)"
            elif server_type == "hpe":
                verification_pattern = "Link Speed Active (Enabled)     : 16G-Gen 4 (16G-Gen 4)"
                verification_pattern_width = "Link Width Active (Enabled)     : 16X (16X)"
            else:
                verification_pattern = None

            if verification_pattern and verification_pattern in output and verification_pattern_width in output:
                print("Output verification: ✅ Passed ✅")
            else:
                print("Output verification: ❌ Failed ❌")
                print("Error: Output doesn't match the expected pattern.")
        elif "sudo lspci" in command:
            print(f"Bus {bus_info}")

            # Adjust the verification pattern based on the server type
            if server_type == "dell" and "Speed 16GT/s (ok), Width x16 (ok)" in output:
                print("Output verification: ✅ Passed ✅")
            elif server_type == "hpe" and "[SN] Serial number:" in output:
                print("Output verification: ✅ Passed ✅")
            else:
                print("Output verification: ❌ Failed ❌")
                print("Error: Output doesn't match the expected pattern.")
        print(output)
    except Exception as e:
        print(f"Error connecting to {hostname}: {str(e)}")
    finally:
        ssh.close()

# Function to run a command on an SSH connection and return the output
def what_server(hostname, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the SSH server with password authentication
        ssh.connect(hostname, port=22, username=username, password=password, allow_agent=False, look_for_keys=False)

        # Run dmidecode command to get system information
        stdin, stdout, stderr = ssh.exec_command("sudo dmidecode -t system")
        output = stdout.read().decode('utf-8').lower()

        if "dell" in output:
            return "dell"
        elif "hpe" in output:
            return "hpe"
        else:
            return "unknown"
    except Exception as e:
        print(f"Error ❌ checking server type for {hostname} : {str(e)}")
        return "unknown"
    finally:
        ssh.close()

def main():
    rack_cell_input = input("Enter rack-cell number (e.g.,8-1): ")

    # Split the input into rack and cell
    rack, cell = map(int, rack_cell_input.split('-'))

    username = "vastdata"
    password = "vastdata"

    nodes = {
        "node 1": 1,
        "node 2": 3,
        "node 3": 5,
        "node 4": 7,
    }

    for node, value in nodes.items():
        hostname = f"10.42.{rack}.{cell}{value}"
        print(f"\nChecking connection to {hostname} ({node}):")
        check_ssh_connection(hostname, username, password)

        server_type = what_server(hostname, username, password)
        print(f"The server type for {hostname} is: {server_type}")

        if server_type == "dell":
            commands = [
                rf"sudo lspci -s 31:00.0 -vv | grep -E 'LnkSta|\[SN\] Serial number' | grep -v 'LnkSta2'",
                rf"sudo lspci -s 31:00.1 -vv | grep -E 'LnkSta|\[SN\] Serial number' | grep -v 'LnkSta2'",
                rf"sudo lspci -s 17:00.0 -vv | grep -E 'LnkSta|\[SN\] Serial number' | grep -v 'LnkSta2'",
                rf"sudo lspci -s 17:00.1 -vv | grep -E 'LnkSta|\[SN\] Serial number' | grep -v 'LnkSta2'",
            ]
        elif server_type == "hpe":
            commands = [
                rf"sudo mlxlink -d 63:00.0 -e -c --port_type pcie | grep -E 'Link Speed|Link Width'",
                rf"sudo lspci -s 63:00.0 -vv | grep -E '\[SN\] Serial number'",
                rf"sudo mlxlink -d 63:00.1 -e -c --port_type pcie | grep -E 'Link Speed|Link Width'",
                rf"sudo lspci -s 63:00.1 -vv | grep -E '\[SN\] Serial number'",
                rf"sudo mlxlink -d 84:00.0 -e -c --port_type pcie | grep -E 'Link Speed|Link Width'",
                rf"sudo lspci -s 84:00.0 -vv | grep -E '\[SN\] Serial number'",
                rf"sudo mlxlink -d 84:00.1 -e -c --port_type pcie | grep -E 'Link Speed|Link Width'",
                rf"sudo lspci -s 84:00.1 -vv | grep -E '\[SN\] Serial number'",
            ]
        else:
            print(f"Unknown server type for {hostname}")
            continue

        print(f"\nRunning commands on ({server_type}) {hostname} ({node}):")
        for command in commands:
            run_ssh_command(hostname, username, password, node, command, server_type)

    # Print a message indicating that the checking is finished
    print("Successfully finished with the checking on NIC stats ✅")    

if __name__ == "__main__":
    main()
