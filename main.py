import os
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
        try:
            container = client.containers.get(container_name)
        except docker.errors.NotFound:
            container = client.containers.run('mrflyn:openvscodeserver', name=container_name, detach=True)
        else:
            if container.status != 'running':
                container.start()
        r.publish('docker-response-channel', f'Successfully started container {container_name}')
    elif command == 'stop':
        try:
            container = client.containers.get(container_name)
        except docker.errors.NotFound:
            pass
        else:
            container.stop()
        r.publish('docker-response-channel', f'Successfully stopped container {container_name}')