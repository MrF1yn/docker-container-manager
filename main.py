import os
import shutil

import redis
import docker
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host='redis-13663.c264.ap-south-1-1.ec2.redns.redis-cloud.com',
    port=13663,
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True)

p = r.pubsub()
p.subscribe('docker-channel')

client = docker.from_env()

for message in p.listen():
    if message['type'] == 'subscribe':
        continue

    data = message['data']
    parsed_data = data.split(' ')
    if len(parsed_data) < 2:
        continue
    command, container_name = parsed_data
    print(f'Command: {command}, Container Name: {container_name}')
    if command == 'start':
        # Create a new directory for the container
        os.makedirs(f'containers/{container_name}/data', exist_ok=True)
        # Set the permission of the directory to 777
        os.chmod(f'containers/{container_name}', 0o777)
        try:
            container = client.containers.get(container_name)
        except docker.errors.NotFound:
            # Mount the data folder, expose port 4000, and add to network
            container = (client.containers
                         .run('mrflyn:openvscodeserver', name=container_name, detach=True,
                              volumes={f'containers/{container_name}/data': {'bind': '/home/workspace', 'mode': 'rw'}},
                              ports={'3000/tcp': 3000}, network='nginxproxymanager_default', command='--host 0.0.0.0'))
        else:
            if container.status != 'running':
                container.start()
        r.publish('docker-response-channel', f'Started:{container_name}')
        # Display the last container output
        print(container.logs())
    elif command == 'stop':
        try:
            container = client.containers.get(container_name)
        except docker.errors.NotFound:
            pass
        else:
            container.stop()
            # Delete the directory for the container
            shutil.rmtree(f'containers/{container_name}')
            # Display the last container output
            print(container.logs())
        r.publish('docker-response-channel', f'Stopped:{container_name}')