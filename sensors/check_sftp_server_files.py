import paramiko
import os


@sensor
def check_condition(*args, **kwargs) -> bool:
    hostname = "sftp"      # Use container name from docker-compose
    port = 22              # Default SFTP port inside the container
    username = os.getenv('SFTP_USER')
    password = os.getenv('SFTP_PASS')

    known_files = set([
        'aapl.csv',
        'amzn.csv',
        'ba.csv',
        'baba.csv',
        'cost.csv',
        'lmt.csv',
        'meta.csv',
        'msft.csv',
        'nflx.csv',
        'nvda.csv',
        'pltr.csv',
        'tsla.csv',
        'uber.csv',
        'wmt.csv',
    ])

    transport = paramiko.Transport((hostname, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    current_files = set(sftp.listdir('/upload'))
    current_files = set([fn for fn in current_files if not fn.startswith('.')])
    new_files = current_files - known_files

    for fn in new_files:
        print(f'Here is a new file: {fn}')

    sftp.close()
    transport.close()

    return bool(new_files)