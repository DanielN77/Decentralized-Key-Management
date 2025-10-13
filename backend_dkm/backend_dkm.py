import subprocess
from flask import Flask, request, render_template
import docker
import json

import requests

from deconstruct import deconstruct
from node_container import create_node_containers, get_node_ips
from reconstruct import reconstruct
# måste importera recoonstruct

app = Flask(__name__)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        shards = get_Shards(username)
        reconstructed_pass = reconstruct(shards)

        if username and password == reconstructed_pass:
            message = "Welcome " + username
            return message
        else:
            message = "Wrong username or password."
            return message
    
    else: # Om det är GET så går vi till login formuläret och visar den
        return render_template("login.html")


def get_Shards(user):

    """
        Returnerar en lista av tuples [(x,y), ...] för användaren 'user' genom att läsa in varje shard från våra containers.
    """

    shards = []
    client = docker.from_env() #Skapar en doker client som pratar med doker demonen
    containers = client.containers.list(filters= {"label": "shard-node=true"}) # Hämtar listan av alla körande containers
    shard_path = f"/var/lib/shards/{user}.json"

    if not containers:
        return shards # listan är tom

    for c in containers:
        res = c.exec_run(["cat", shard_path], demux = True) # demux för att få standard output och standard error separat
        exit_code = res.exit_code # returnerar 0 om det funka (filen finns i docker) och inte 0 om det inte funka
        stdout, stderr = res.output # stdout får outputen av filen (alltså våra koordinater men den kan vara i bytes)

        if exit_code != 0 or not stdout: # Om filen inte finns i denna nod så går vi till nästa
             continue
        
        try:
            text = stdout.decode("utf-8", errors = "strict") # för att upptäcka fel tidigt
            koord = json.loads(text)

            x, y = koord

            x = float(x)
            y = float(y)

            shards.append((x, y))


        except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError): # Om ogiltigt innehål gå vidare till nästa nod
             continue
             

    return shards

# Log in to user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return {"message": "Username and password are required."}, 400

    # Simulate shard creation and storage logic here
    # For example, you might split the password into shards and store them in Docker containers
    # This is a placeholder for actual shard generation and distribution
    try:
        store_shards(username, password)
        return {"message": f"User '{username}' registered successfully."}, 200
    except Exception as e:
        return {"message": f"Registration failed: {str(e)}"}, 500


def store_shards(username, password, n=5, t=3):
    """
    Deconstructs the password and stores each shard in a node via HTTP POST with URL parameters.
    """
    print("inside")
    
    pwd_bytes = password.encode("utf-8")
    
    # Get shards
    #shards = list(deconstruct(pwd_bytes, n, t))
    shards = [
    (1, 842394),
    (2, 1293847),
    (3, 1938475),
    (4, 2493847),
    (5, 3129384)
    ]
    
    # Generate node containers
    create_node_containers(n)
    print("last working")
    # Get node containers ip addresses
    node_ips = get_node_ips()
    
    print("done with that")
    
    if len(node_ips) < n:
        raise RuntimeError(f"Not enough nodes available: need {n}, found {len(node_ips)}")
    
    print("gonna test nodes")
    
    # Sends shard to each node
    for i in range(n):
       
        x, y = shards[i]
        ip = node_ips[i]
        print(ip)
        curl_cmd = [
            "curl", "-X", "POST",
            f"http://{ip}:6000/store?username={username}&x={x}&y={y}"
        ]
        print("hellooooo")
        try:
            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            print("wokred executing")
            if result.status_code != 200:
                print(f"Node {ip} failed to store shard: {result.text}")
        except Exception as e:
            print(f"Error contacting node {ip}: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)