from flask import Flask, render_template, request, redirect, url_for, make_response
import yaml

import os

app = Flask(__name__)

teams = []
challenges = []

if not os.path.exists("db"):
    os.mkdir("db")

if os.path.exists("db/teams.yaml"):
    with open("db/teams.yaml", "r") as f:
        teams = yaml.safe_load(f)

if os.path.exists("db/challenges.yaml"):
    with open("db/challenges.yaml", "r") as f:
        challenges = yaml.safe_load(f)

@app.route("/")
def index():
    return render_template("page.html", site_name="HP Scoreboard", page_name="Home", content="<p><a href='/scoreboard'>Scoreboard</a></p><p><a href='/login'>Admin</a></p>")


@app.route("/scoreboard")
def scoreboard():

    max_points = 0
    for challenge in challenges:
        max_points += challenge["points"]

    sb_html = ""

    for team in teams:
        sb_html += render_template("team_prog.html", team_name=team["name"], points=team["score"], max_points=max_points)

    return render_template("page.html", site_name="HP Scoreboard", page_name="Scoreboard", content=sb_html)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("page.html", site_name="HP Scoreboard", page_name="Login", content=render_template("login.html"))
    elif request.method == "POST":
        r = make_response(redirect(url_for("admin")))
        r.set_cookie("sk-lol", request.form["password"])
        return r
    else:
        return "use a normal request type please"

@app.route("/admin")
def admin():
    if request.cookies.get("sk-lol") == "chauncey12345":
        return "haha you're a gamer"
    else:
        return "nope"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
