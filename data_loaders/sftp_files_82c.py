import polars as pl

import paramiko
import os
import sys
from stat import S_ISDIR


@data_loader
def load_data(*args, **kwargs):
    # Connection details
    hostname = "sftp"      # Use container name from docker-compose
    port = 22              # Default SFTP port inside the container
    username = os.getenv('SFTP_USER')
    password = os.getenv('SFTP_PASS')
    
    # Try to list files in the user's home directory
    print("\nListing files in home directory:")
    home_files = list_sftp_files(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        remote_dir="/"  # Root of the user's directory in SFTP
    )
    
    if home_files:
        print("Files available in home directory:")
        for file_path in home_files:
            print(f"  {file_path}")
    
    # Try to list files in the upload directory
    print("\nListing files in upload directory:")
    upload_files = list_sftp_files(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        remote_dir="/upload"  # The mounted directory in your docker-compose
    )
    
    if not upload_files:
        return
    
    arr = []

    print("Files available in upload directory:")
    for file_path in upload_files:
        print(f"  {file_path}")
    
    # Fetch contents of all files
    regular_files = [f for f in upload_files if not f.endswith('(directory)')]
    if regular_files:
        for sample_file in regular_files:
            print(f"\nFetching contents of {sample_file}")
            
            contents = fetch_sftp_file_contents(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                remote_path=sample_file
            )
            
            if contents:
                arr.append(contents)
                # Print first 100 bytes as a preview (if it's a text file)
                try:
                    preview = contents[:100].decode('utf-8')
                    print(f"\nPreview of {sample_file}:\n{preview}...")
                except UnicodeDecodeError:
                    print(f"\n{sample_file} is a binary file with {len(contents)} bytes")
    else:
        print("No files found in upload directory. You may need to add some files first.")

    if not arr:
        return

    return pl.DataFrame([dict(content=content) for content in arr]).to_pandas()


def fetch_sftp_file_contents(hostname, port, username, password, remote_path):
    """
    Fetch the contents of a file from an SFTP server
    
    Args:
        hostname (str): SFTP server hostname or IP
        port (int): SFTP server port
        username (str): SFTP username
        password (str): SFTP password
        remote_path (str): Path to the file on the SFTP server
    
    Returns:
        bytes: The contents of the file as bytes
    """
    # Create SSH client
    ssh = paramiko.SSHClient()
    # Automatically add the server's host key (not recommended for production)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to SFTP server {hostname}:{port} with user {username}")
        # Connect to the server
        ssh.connect(hostname, port, username, password)
        
        # Create SFTP client
        sftp = ssh.open_sftp()
        
        # Check if the path exists
        try:
            attrs = sftp.stat(remote_path)
        except FileNotFoundError:
            print(f"Error: Remote file {remote_path} does not exist")
            return None
        
        # Check if it's a directory
        if S_ISDIR(attrs.st_mode):
            print(f"Error: {remote_path} is a directory, not a file")
            return None
        
        # Read the file contents
        print(f"Fetching contents of {remote_path}")
        with sftp.open(remote_path, 'rb') as remote_file:
            file_contents = remote_file.read()
        
        print(f"Successfully fetched {len(file_contents)} bytes")
        return file_contents
    
    except Exception as e:
        print(f"Error fetching file from SFTP: {str(e)}")
        return None
    
    finally:
        # Close connections
        if 'sftp' in locals():
            sftp.close()
        if 'ssh' in locals():
            ssh.close()


def list_sftp_files(hostname, port, username, password, remote_dir):
    """
    List all files in an SFTP directory
    
    Args:
        hostname (str): SFTP server hostname or IP
        port (int): SFTP server port
        username (str): SFTP username
        password (str): SFTP password
        remote_dir (str): Remote directory to list
    
    Returns:
        list: List of file paths in the directory (non-recursive)
    """
    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to SFTP server {hostname}:{port} with user {username}")
        # Connect to the server
        ssh.connect(hostname, port, username, password)
        
        # Create SFTP client
        sftp = ssh.open_sftp()
        
        # List files in the directory (non-recursive for simplicity)
        file_list = []
        for item in sftp.listdir_attr(remote_dir):
            item_path = f"{remote_dir}/{item.filename}" if remote_dir.endswith('/') else f"{remote_dir}/{item.filename}"
            if not S_ISDIR(item.st_mode):
                file_list.append(item_path)
            else:
                file_list.append(f"{item_path}/ (directory)")
        
        return file_list
    
    except Exception as e:
        print(f"Error listing files from SFTP: {str(e)}")
        return []
    
    finally:
        # Close connections
        if 'sftp' in locals():
            sftp.close()
        if 'ssh' in locals():
            ssh.close()