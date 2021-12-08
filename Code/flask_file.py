
# THIS IS NOT READY YET, IT IS PART OF THE WORK SYSTEM



from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
import json
from threading import Thread

app = Flask(__name__)
app.secret_key = 'tempkey'

@app.route("/")
@app.route("/home")
def home():
	return render_template("index.html")

@app.route("/game/<messageid>")
def game(messageid):
	if not in_ids(messageid):
		abort(404)
	else:
		return render_template("game.html", messageid=messageid)


def in_ids(messageid):
	data = get_gamedata()
	if messageid in data:
		return True
	return False

def get_gamedata():
	with open("game_data.json", "r") as f:
		return json.load(f)

def dump_gamedata(data):
	with open("game_data.json") as f:
		json.dump(data, f)

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
