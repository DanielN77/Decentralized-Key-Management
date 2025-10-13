import docker
import subprocess

# Run n number of node containers in the background
def create_node_containers(n):
    subprocess.run(["docker-compose", "up", "--scale", f"node={n}", "-d"])

# Get the ip addresses of node containers inside the docker network
def get_node_ips():
    containers = docker.from_env().containers.list()
    nodes = [ c for c in containers if "decentralized-key-management-node" in c.name ]
    node_ips = [ c.attrs['NetworkSettings']['Networks']['decentralized-key-management_keynet']['IPAddress'] for c in nodes ]
    return node_ips

if __name__ == "__main__":
    get_node_ips()
