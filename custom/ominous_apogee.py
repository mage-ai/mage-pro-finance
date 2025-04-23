import paramiko
import json
import os


@custom
def transform_custom(*args, **kwargs):
    hostname = "sftp"      # Use container name from docker-compose
    port = 22              # Default SFTP port inside the container
    username = os.getenv('SFTP_USER')
    password = os.getenv('SFTP_PASS')

    known_files = [
        'ba.csv',
        'baba.csv',
        'cost.csv',
        'lmt.csv',
        'meta.csv',
        'msft.csv',
        'nflx.csv',
        'nvda.csv',
        'pltr.csv',
        'uber.csv',
        'wmt.csv',
        'gme.csv',
    ]

    path = 'known_files.json'
    if os.path.exists(path):
        with open(path, 'r') as f:
            known_files.extend(json.load(f))

    known_files = set(known_files)

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

    with open(path, 'w') as f:
        f.write(json.dumps(list(set(list(known_files) + list(current_files)))))

    return new_files