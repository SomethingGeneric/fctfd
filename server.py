from flask import Flask, render_template, request, redirect, url_for, make_response
import yaml

import urllib.parse
import os

app = Flask(__name__)
PASSWD = "chauncey12345"

teams = []
challenges = []


def reload_data():
    global teams
    global challenges

    if not os.path.exists("db"):
        os.mkdir("db")

    if os.path.exists("db/teams.yaml"):
        with open("db/teams.yaml", "r") as f:
            teams = yaml.safe_load(f)

    if os.path.exists("db/challenges.yaml"):
        with open("db/challenges.yaml", "r") as f:
            challenges = yaml.safe_load(f)


def save_data():
    if not os.path.exists("db"):
        os.mkdir("db")

    with open("db/teams.yaml", "w") as f:
        f.write(yaml.dump(teams))

    with open("db/challenges.yaml", "w") as f:
        f.write(yaml.dump(challenges))


reload_data()


@app.route("/")
def index():
    return render_template(
        "page.html",
        site_name="HP Scoreboard",
        page_name="Home",
        content="<p><a href='/scoreboard'>Scoreboard</a></p><p><a href='/admin'>Admin</a></p>",
    )


@app.route("/scoreboard")
def scoreboard():
    max_points = 0
    for challenge in challenges:
        max_points += challenge["points"]

    sb_html = ""

    for team in teams:
        sb_html += render_template(
            "team_prog.html",
            team_name=team["name"],
            points=team["score"],
            max_points=max_points,
        )

    return render_template(
        "page.html", site_name="HP Scoreboard", page_name="Scoreboard", content=sb_html
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template(
            "page.html",
            site_name="HP Scoreboard",
            page_name="Login",
            content=render_template("login.html"),
        )
    elif request.method == "POST":
        r = make_response(redirect(url_for("admin")))
        r.set_cookie("sk-lol", request.form["password"])
        return r
    else:
        return "use a normal request type please"


@app.route("/logout")
def do_logout():
    r = make_response(redirect(url_for("index")))
    r.set_cookie("sk-lol", "", expires=0)
    return r


@app.route("/list/<data>")
def dlist(data):
    if data == "teams":
        tn = []
        for team in teams:
            tn.append(team["name"])
        return tn
    elif data == "challenges":
        cn = []
        for challenge in challenges:
            cn.append(challenge["name"])
        return cn
    else:
        return "Invalid data type"


@app.route("/teams/<team_name>", methods=["GET", "POST"])
def team(team_name):
    if request.method == "GET":
        for team in teams:
            if team["name"] == team_name:
                return render_template(
                    "page.html",
                    site_name="HP Scoreboard",
                    page_name=f"Details - {team_name}",
                    content=render_template(
                        "admin_team.html",
                        team_name=team_name,
                        score=team["score"],
                        members=team["players"],
                        challenges_done=team["challenges-complete"],
                        challenges_working=team["challenges-working"],
                    ),
                )
        return "{}"
    else:
        return "WIP"


@app.route("/challenges/<challenge_name>", methods=["GET", "POST"])
def challenge(challenge_name):
    if request.method == "GET":
        for challenge in challenges:
            if challenge["name"] == challenge_name:
                return challenge
        return "{}"
    else:
        return "WIP"


@app.route("/admin")
def admin():
    if request.cookies.get("sk-lol") == PASSWD:
        teams = dlist("teams")
        t_html = "<h3>Teams:</h3><ul>"
        for team in teams:
            t_html += (
                f"<li><a href=/teams/{urllib.parse.quote(team)}>" + team + "</a></li>"
            )
        t_html += "</ul>"
        c_html = "<h3>Challenges:</h3><ul>"
        challenges = dlist("challenges")
        for challenge in challenges:
            c_html += (
                f"<li><a href=/challenges/{urllib.parse.quote(challenge)}>"
                + challenge
                + "</a></li>"
            )
        c_html += "</ul>"
        return render_template(
            "page.html",
            site_name="HP Scoreboard",
            page_name="Admin",
            content=render_template("admin.html", teams=t_html, challenges=c_html),
        )
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
