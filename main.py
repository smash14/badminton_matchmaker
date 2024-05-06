from pprint import pprint
from teamsParser import Teams

if __name__ == '__main__':
    print("Ligaman Gui")
    print("===== V0.2 =====")
    print("Maintainer: Bjarne Andersen - b-andersen@arkaris.de")
    print("")
    MatchPlan = Teams("teams.json")
    pprint(MatchPlan)

