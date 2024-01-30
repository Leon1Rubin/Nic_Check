### README for SSH Network Checker

#### Overview

This script, `SSH Network Checker`, is designed to automate the process of checking the network interface card (NIC) stats of servers in a specific rack-cell. It uses SSH (Secure Shell) to connect to servers, determine their type (Dell or HPE), and execute specific commands to gather NIC statistics. The script is built in Python and utilizes the `paramiko` library for handling SSH connections.

#### Requirements

-   Python 3.x
-   `paramiko` library (can be installed via `pip install paramiko`)

#### Usage

To use the script, you need to provide three command-line arguments:

1.  `rack-cell`: The rack-cell number in the format `rack-cell` (e.g., `8-1`).
2.  `user`: The SSH username for the server.
3.  `password`: The SSH password for the server.

Run the script from the command line as follows:

`python script.py <rack-cell> <user> <password>` 

#### Functionality

1.  **Check SSH Connection (`check_ssh_connection`)**: Verifies if the server is online by attempting an SSH connection.
2.  **Run SSH Command (`run_ssh_command`)**: Executes commands on the server to gather NIC stats and validates the output based on server type.
3.  **Determine Server Type (`what_server`)**: Identifies the server type (Dell or HPE) using system information.
4.  **Main Function (`main`)**: Orchestrates the overall process, including parsing command-line arguments and iterating through nodes in the specified rack-cell.

#### Nodes Configuration

The script is currently configured to check the following nodes in a rack-cell:

-   node 1
-   node 2
-   node 3
-   node 4

This configuration can be adjusted in the `nodes` dictionary within the `main` function.

#### Output

The script outputs the connection status of each node, its server type, and the results of the executed commands, including a verification check against expected patterns.

#### Limitations

-   The script is specifically tailored for Dell and HPE servers.
-   It requires valid SSH credentials and network access to the specified servers.
-   The server must allow the execution of the required commands via SSH.

#### Customization

The script can be modified to include different commands or to accommodate additional server types. Adjustments can be made in the `run_ssh_command` function and the command lists in the `main` function.
