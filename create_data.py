import yaml
import os

teams = []
challenges = []

if not os.path.exists("db"):
    os.mkdir("db")


if input("Reset team data? (y/n): ") == "y":
    next = ""

    while next != "n":
        team = {}
        team["name"] = input("Team Name: ")
        team["score"] = 0
        team["challenges-done"] = []
        team["challenges-working"] = []
        team["players"] = []
        team["logo-path"] = ""
        # # # # # # # # #
        teams.append(team)
        next = input("Add another team? (y/n): ")

    with open("db/teams.yaml", "w") as f:
        yaml.dump(teams, f)


if input("Reset challenge data? (y/n): ") == "y":
    next = ""

    while next != "n":
        challenge = {}
        challenge["name"] = input("Challenge Name: ")
        challenge["points"] = int(input("Points: "))
        challenge["description"] = input("Description: ")
        challenges.append(challenge)
        next = input("Add another challenge? (y/n): ")

    with open("db/challenges.yaml", "w") as f:
        yaml.dump(challenges, f)


print("Done!")