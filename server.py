from flask import Flask, render_template, request, redirect, url_for, make_response
import yaml

import urllib.parse
import os

app = Flask(__name__)

if not os.path.exists("db/admin.pass"):
    print("No admin.pass file found")
    exit(1)
else:
    with open("db/admin.pass", "r") as f:
        PASSWD = f.read().strip()

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


def edit_chall(name, key, value):
    global challenges

    for challenge in challenges:
        if challenge["name"] == name:
            challenge[key] = value
            return True

    return False


def has_challenge(name):
    for challenge in challenges:
        if challenge["name"] == name:
            return True
    return False


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
        return None


reload_data()


@app.route("/")
def index():
    return render_template(
        "page.html",
        page_name="Home",
        content="<p><a href='/scoreboard'>Scoreboard</a></p><p><a href='/teams'>Teams</a></p><p><a href='/challenges'>Challenges</a></p><p><a href='/admin'>Admin</a></p>",
    )


@app.route("/scoreboard")
def scoreboard():
    max_points = 0
    for challenge in challenges:
        max_points += int(challenge["points"])

    for team in teams:
        if int(team["score"]) == int(max_points):
            return render_template(
                "won.html",
                team_name=team["name"],
                players=team["players"],
                team=team,
                team_logo="/static/" + team["logo-path"],
            )

    sb_html = '<div class="grid-container">'

    for team in teams:
        if team["logo-path"] == "":
            lp = "/static/error.png"
        else:
            lp = "/static/" + team["logo-path"]
        sb_html += (
            '<div class="grid-item">'
            + render_template(
                "team_prog.html",
                team=team,
                max_points=max_points,
                team_logo=lp,
            )
            + "</div>"
        )

    sb_html += "</div>"

    return render_template(
        "page.html",
        page_name="Scoreboard",
        auto_refresh=True,
        embed=True,
        content=sb_html,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template(
            "page.html",
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


@app.route("/teams")
def teams_list():
    team_list = "<ul>"
    for team in teams:
        team_list += (
            f"<li><p><a href=/teams/{urllib.parse.quote(team['name'])}>"
            + team["name"]
            + "</a></p></li>"
        )
    team_list += "</ul>"
    return render_template(
        "page.html",
        page_name="Team List",
        content=team_list,
    )


@app.route("/teams/<team_name>", methods=["GET", "POST"])
def team(team_name):
    if request.method == "GET":
        auth = False
        if request.cookies.get("sk-lol") == PASSWD:
            auth = True
        team_name = urllib.parse.unquote(team_name)
        for team in teams:
            if team["name"] == team_name:
                return render_template(
                    "page.html",
                    page_name=f"Details - {team_name}",
                    content=render_template(
                        "admin_team.html",
                        team_name=team_name,
                        score=team["score"],
                        members=team["players"],
                        challenges_done=team["challenges-complete"],
                        challenges_working=team["challenges-working"],
                        challenges=challenges,
                        auth=auth,
                        team=team,
                    ),
                )

        return "{}", 404
    else:
        try:
            if not has_team(team_name):
                return f"No such team: {team_name}", 500
            if request.cookies.get("sk-lol") == PASSWD:
                if request.form.get("member_add") != "":
                    print(f"Adding member to {team_name}")
                    old_players = get_attrib(team_name, "players")
                    new_players = old_players
                    new_players.append(request.form.get("member_add"))
                    edit_team(team_name, "players", new_players)
                if request.form.get("member_remove") != "":
                    target = request.form.get("member_remove").strip()
                    print(f'Removing member "{target}" from {team_name}')
                    old_players = get_attrib(team_name, "players")
                    for p in old_players:
                        if target in p:
                            old_players.remove(p)
                    edit_team(team_name, "players", old_players)
                if request.form.get("challenge_add") != "none":
                    print(f"Adding challenge to {team_name}")
                    if has_challenge(request.form.get("challenge_add")):
                        challenges_wip = get_attrib(team_name, "challenges-working")
                        challenges_wip.append(request.form.get("challenge_add"))
                        edit_team(team_name, "challenges-working", challenges_wip)
                if request.form.get("challenge_finish") != "none":
                    print(f"Marking challenge as done for {team_name}")
                    if has_challenge(request.form.get("challenge_finish")):
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
                if request.form.get("challenge_remove") != "none":
                    challenges_done = get_attrib(team_name, "challenges-complete")
                    challenges_wip = get_attrib(team_name, "challenges-working")
                    challenge_name = request.form.get("challenge_remove")
                    if challenge_name in challenges_wip:
                        challenges_wip.remove(challenge_name)
                        edit_team(team_name, "challenges-working", challenges_wip)
                    if challenge_name in challenges_done:
                        challenges_done.remove(challenge_name)
                        edit_team(team_name, "challenges-complete", challenges_done)
                        points = int(get_chall(challenge_name)["points"])
                        curr_points = int(get_attrib(team_name, "score"))
                        new_pts = curr_points - points
                        edit_team(team_name, "score", str(new_pts))
                save_data()
            return redirect(f"/teams/{team_name}")
        except Exception as e:
            return f"Error: {str(e)}"


@app.route("/challenges")
def chall_list():
    chal_list = "<ol>"
    for chal in challenges:
        chal_list += (
            f"<li><p><a href=/challenges/{urllib.parse.quote(chal['name'])}>"
            + chal["name"]
            + "</a></p></li>"
        )
    chal_list += "</ol>"
    return render_template(
        "page.html",
        page_name="Challenges List",
        content=chal_list,
    )


@app.route("/challenges/<challenge_name>", methods=["GET", "POST"])
def challenge(challenge_name):
    if request.method == "GET":
        # if challenge_name == "Scoreboard Code Flag":
        #     print("Hi there CTF players! The flag is: Alohamora :)")
        auth = False
        if request.cookies.get("sk-lol") == PASSWD:
            auth = True
        challenge_name = urllib.parse.unquote(challenge_name)
        for challenge in challenges:
            if challenge["name"] == challenge_name:
                return render_template(
                    "page.html",
                    page_name=f"Challenge Details - {challenge_name}",
                    content=render_template(
                        "admin_challenge.html",
                        points=challenge["points"],
                        description=challenge["description"],
                        auth=auth,
                    ),
                )
        return f"Could not find '{challenge_name}'", 404
    else:
        if request.cookies.get("sk-lol") == PASSWD:
            if request.form.get("points_set") != "":
                edit_chall(challenge_name, "points", request.form.get("points_set"))
            if request.form.get("description_set") != "":
                edit_chall(
                    challenge_name, "description", request.form.get("description_set")
                )
            if request.form.get("challenge_rename") != "":
                old_challenge_data = get_chall(challenge_name)
                challenges.remove(old_challenge_data)
                new_challenge_data = {
                    "name": request.form.get("challenge_rename"),
                    "points": old_challenge_data["points"],
                    "description": old_challenge_data["description"],
                }
                challenges.append(new_challenge_data)

                for team in teams:
                    for challenge in team["challenges-working"]:
                        if challenge == challenge_name:
                            team["challenges-working"].remove(challenge_name)
                            team["challenges-working"].append(
                                request.form.get("challenge_rename")
                            )
                    for challenge in team["challenges-complete"]:
                        if challenge == challenge_name:
                            team["challenges-complete"].remove(challenge_name)
                            team["challenges-complete"].append(
                                request.form.get("challenge_rename")
                            )
                challenge_name = request.form.get("challenge_rename")
            save_data()
        return redirect("/challenges/" + challenge_name)


@app.route("/admin")
def admin():
    if request.cookies.get("sk-lol") == PASSWD:
        teams = dlist("teams")
        t_html = "<h3>Teams:</h3><ul>"
        for team in teams:
            t_html += (
                f"<li><p><a href=/teams/{urllib.parse.quote(team)}>"
                + team
                + "</a></p></li>"
            )
        t_html += "</ul>"
        c_html = "<h3>Challenges:</h3><ul>"
        challenges = dlist("challenges")
        for challenge in challenges:
            c_html += (
                f"<li><p><a href=/challenges/{urllib.parse.quote(challenge)}>"
                + challenge
                + "</a></p></li>"
            )
        c_html += "</ul>"
        return render_template(
            "page.html",
            page_name="Admin",
            content=render_template("admin.html", teams=t_html, challenges=c_html),
        )
    else:
        return redirect(url_for("login"))


@app.route("/hackme", methods=["GET", "POST"])
def hackme():
    if request.method == "GET":
        return render_template(
            "page.html", page_name="Hack me!", content=render_template("hackme.html")
        )
    if request.method == "POST":
        tried = str(request.form.get("phrase")).strip()
        #print("Got: " + tried + " for hackme")
        if tried == "aparecium":
            #print("They got it!")
            return render_template("page.html", page_name="Huzzah you got it!")
        else:
            #print("Goober")
            return redirect("/hackme")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
