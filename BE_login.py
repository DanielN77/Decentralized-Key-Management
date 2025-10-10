from flask import Flask, request, render_template
import docker
import json
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
