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


def get_attrib(name, key):
    for team in teams:
        if team["name"] == name:
            return team[key]
    return None


def get_chall(name):
    for chal in challenges:
        if chal["name"] == name:
            return chal
    return None


def has_team(fteam):
    for team in teams:
        if team["name"] == fteam:
            return True
    return False


def edit_team(name, key, value):
    global teams

    for team in teams:
        if team["name"] == name:
            team[key] = value
            return True

    return False


def has_challenge(name):
    for challenge in challenges:
        if challenge["name"] == name:
            return True
    return False


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
        return "Invalid data type", 500


@app.route("/teams/<team_name>", methods=["GET", "POST"])
def team(team_name):
    if request.method == "GET":
        if request.cookies.get("sk-lol") == PASSWD:
            team_name = urllib.parse.unquote(team_name)
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
            return "{}", 404
        else:
            return redirect("/login")
    else:
        try:
            if not has_team(team_name):
                return f"No such team: {team_name}", 500
            if request.form.get("member_add") != "":
                print(f"Adding member to {team_name}")
                old_players = get_attrib(team_name, "players")
                new_players = old_players
                new_players.append(request.form.get("member_add"))
                edit_team(team_name, "players", new_players)
            if request.form.get("member_remove") != "":
                print(f"Removing member from {team_name}")
                old_players = get_attrib(team_name, "players")
                for p in old_players:
                    if p == request.form.get("member_remove"):
                        old_players.remove(p)
                edit_team(team_name, "players", old_players)
            if request.form.get("challenge_add") != "":
                print(f"Adding challenge to {team_name}")
                if has_challenge(request.form.get("challenge_add")):
                    challenges_wip = get_attrib(team_name, "challenges-working")
                    challenges_wip.append(request.form.get("challenge_add"))
                    edit_team(team_name, "challenges-working", challenges_wip)
            if request.form.get("challenge_finish") != "":
                print(f"Marking challenge as done for {team_name}")
                # TODO: add verify challenge exists in DB
                challenges_done = get_attrib(team_name, "challenges-complete")
                challenges_wip = get_attrib(team_name, "challenges-working")
                challenge_name = request.form.get("challenge_finish")
                if challenge_name in challenges_wip:
                    challenges_wip.remove(challenge_name)
                    challenges_done.append(challenge_name)
                    edit_team(team_name, "challenges-complete", challenges_done)
                    edit_team(team_name, "challenges-working", challenges_wip)
                    points = int(get_chall(challenge_name)["points"])
                    curr_points = int(get_attrib(team_name, "score"))
                    new_pts = curr_points + points
                    edit_team(team_name, "score", str(new_pts))
            save_data()
            return redirect(f"/teams/{team_name}")
        except Exception as e:
            return f"Error: {str(e)}"


@app.route("/challenges/<challenge_name>", methods=["GET", "POST"])
def challenge(challenge_name):
    if request.method == "GET":
        if request.cookies.get("sk-lol") == PASSWD:
            challenge_name = urllib.parse.unquote(challenge_name)
            for challenge in challenges:
                if challenge["name"] == challenge_name:
                    return render_template(
                        "page.html",
                        site_name="Hp Scoreboard",
                        page_name=f"Challenge Details - {challenge_name}",
                        content=render_template(
                            "admin_challenge.html",
                            points=challenge["points"],
                            description=challenge["description"],
                        ),
                    )
            return f"Could not find '{challenge_name}'", 404
        else:
            return redirect("/login")
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
