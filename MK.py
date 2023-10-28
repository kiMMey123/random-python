import random
import string
import json
import math
import os
from prettytable import PrettyTable as pt

class tournament():
    def __init__(self):
        self.name       = None
        self.players    = []
        self.rounds     = []
        self.finals     = []
        self.current_round = 0
        self.current_split = 0
        self.current_race  = 0

        self.clear()

        while not self.name:
            self.init_tournament()

        self.clear()
        self.play_tournament()

        self.clear()
        winners = self.show_leaderboard(last_round=True)

        self.finals = [p for p in self.players if p.name in [w["name"] for w in winners[:4]]]
        self.play_finals(self.finals)
    
    def clear(self):
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")


        if self.name:
            print(f'---- {self.name.upper()} ----\n')
            print("\n")
        else:
            print(f'---- MARIO KART TOURNAMENT GENERATOR BONANZA ----\n')
            print("\n")
    
    def init_tournament(self):
        tour_name = input("Enter tournament name: ")
        if tour_name.strip() != "":
            tour_name = tour_name.strip().lower()

        if len(tour_name) < 3:
            print("tournament name must be at least 3 characters long")
            return
        if len(tour_name) > 20:
            print("tournament name must be less than 20 characters long")
            return
        self.name = tour_name
        
        jsonfile = tour_name + ".json"
        jsonpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tours", jsonfile)
        self.clear()

        if os.path.exists(jsonpath):
            self.load_tournament()
        else:
            self.new_tournament()
            self.save_tournament()

    def play_tournament(self):
        for i in range(self.current_round, len(self.rounds)):
            last_split, last_round = False, False
            self.current_round = i
            for j in range(self.current_split, len(self.rounds[i])):
                if j == len(self.rounds[i]) - 1:
                    last_split = True
                self.current_split = j
                self.play_round(self.rounds[i][j])
                self.current_split += 1
                self.current_race = 0
            self.current_split = 0
            self.current_round += 1
            if i == len(self.rounds) - 1:
                last_round = True
            if not last_round:
                self.show_leaderboard()
    
    def play_round(self, split, finals=False):
        self.clear()
        if finals:
            print(f'---- Finals ----\n')
            num_races = 8
        else:
            print(f'---- Round {self.current_round + 1} - Split {self.current_split + 1} ----\n')
            num_races = 4
        print("Players: " + ", ".join([p.name for p in split]))
        if not finals:
            print("\n")
            input("\nPress enter to start split...")
        else:
            input("\nPress enter to start finals...")
        self.clear()
        current_race = self.current_race + 1
        while current_race <= num_races:
            race_accepted = False
            while not race_accepted:
                player_positions = []
                reset_race = False
                for player in split:
                    player_entry_ok = False
                    while not player_entry_ok:
                        print(f'Race {current_race} of {num_races}')
                        # print("Race", current_race, " of " + num_races)
                        print("\n")
                        print(f'Enter position for: {player.name}')
                        position_input = input("[1-12] position / [R]eset race: ")
                        if position_input.strip().lower() == "r":
                            reset_race = True
                            self.clear()
                            break
                        elif position_input.strip() in [str(i) for i in range(1, 13)]:
                            player_pos = int(position_input.strip())
                            if player_pos in player_positions:
                                self.clear()
                                print("Invalid input, position already entered")
                                continue
                            else:
                                self.clear()
                                player_positions.append(player_pos)
                                player_entry_ok = True
                        else:
                            self.clear()
                            print("Invalid input")
                            continue
                    if reset_race:
                        break
                self.clear()
                if reset_race:
                    break
                else:
                    race_table = pt(["Position", "Player"])
                    for pos in sorted(player_positions):
                        race_table.add_row([pos, [p.name for p in split if player_positions.index(pos) == split.index(p)][0]])

                    print(race_table)
                    print("\n")

                    confirm_positions = input("[A]ccept, [R]eset race ")
                    if confirm_positions.lower() == "a":
                        race_accepted = True
                        current_race += 1
                        for player in split:
                            if finals:
                                player.add_position(player_positions[split.index(player)], None, finals=True)
                            else:
                                player.add_position(player_positions[split.index(player)], self.current_round)
                    elif confirm_positions.lower() == "r":
                        break
                    else:
                        print("Invalid input")
                        break
                    
                    self.clear()

            self.current_race += 1
            self.save_tournament()
            self.clear()
        if not finals:
            self.show_leaderboard(split=True)
        else:
            self.show_leaderboard(finals=True)
        
    def play_finals(self, winners):
        self.clear()
        print("---- Finals ----\n")
        play_finals = input("Play finals? (y/n): ")
        if not play_finals.lower() == "y":
            self.clear()
            print("Finals skipped")
            print("\n")
            print("Thank you for playing!")
            print("\n")
            print("See you next time!")
            print("\n")
            print("If you want to play the finals at a later time, you can load the tournament and play them manually")
            print("\n")
            print("To load this tournament, enter the following name: " + self.name)
            print("\n")
            input("Press enter to not continue...")
            print("<3")
            return
        else:
            self.play_round(split=self.finals, finals=True)
            self.clear()
    
    def show_leaderboard(self, split=False, last_round=False, finals=False):
        self.clear()
        leaderboard = pt(["Pos.", "Name", "Score", "Avg. pos", "Best", "Worst"])
        leaderboard.align["Pos."] = "r"
        leaderboard.align["Name"] = "l"
        leaderboard.align["Score"] = "r"
        leaderboard.align["Avg. pos"] = "r"
        leaderboard.align["Best"] = "r"
        leaderboard.align["Worst"] = "r"

        if split:
            print(f'---- Round {self.current_round + 1} - Split {self.current_split + 1} results ----\n')
            players = self.rounds[self.current_round][self.current_split]

        elif finals:
            print(f'---- Finals results ----\n')
            players = self.finals

        else:
            print(f'---- Standings after round {self.current_round} ----\n')
            players = self.players

        player_stats = []
        for player in players:
            
            if split:
                player_score = sum(player.scores[self.current_round])
                all_pos = player.positions[self.current_round]
            elif finals:
                player_score = player.finals_score
                all_pos = player.finals
            else:
                player_score = 0
                for i in range(len(player.scores)):
                    player_score += sum(player.scores[i])
                all_pos = sum(player.positions, [])

            player_data = {
                "name": player.name,
                "score": player_score,
                "all_pos": all_pos,
                "avg_pos": sum(all_pos) / len(all_pos),
                "best_pos": min(all_pos),
                "worst_pos": max(all_pos)
            }
            player_stats.append(player_data)
        
        player_stats.sort(key=lambda x: x["score"], reverse=True)

        for i in range(len(player_stats)):
            player = player_stats[i]
            position = i + 1
            if i > 0 and player["score"] == player_stats[i - 1]["score"]:
                if player["avg_pos"] < player_stats[i - 1]["avg_pos"]:
                    position = i + 1
                elif player["avg_pos"] == player_stats[i - 1]["avg_pos"]:
                    if player["best_pos"] < player_stats[i - 1]["best_pos"]:
                        position = i + 1
                    elif player["best_pos"] == player_stats[i - 1]["best_pos"]:
                        if player["worst_pos"] < player_stats[i - 1]["worst_pos"]:
                            position = i + 1
                        else:
                            position = i
                    else:
                        position = i
                else:
                    position = i
            player_stats[i]["position"] = position
            leaderboard.add_row([position, player["name"], player["score"], round(player["avg_pos"], 2), player["best_pos"], player["worst_pos"]])

        if last_round:
            print("Tournament finished!")
            print("\n")
            if len(player_stats) >= 4:
                print("Fourth place: " + player_stats[3]["name"])
                print("\n")
                input("Press enter to continue...")
                self.clear()
            if len(player_stats) >= 3:
                print("Third place: " + player_stats[2]["name"])
                print("\n")
                input("Press enter to continue...")
                self.clear()
           
            print("Second place: " + player_stats[1]["name"])
            print("\n")
            input("Press enter to continue...")
            self.clear()
            print("And the winner is...")
            print("\n")
            input("Press enter to continue...")
            self.clear()
            print(f'---- !!!! {player_stats[0]["name"].upper()} !!!! ----\n')
            print("\n")
            input("Press enter to continue...")
            self.clear()
            print("Congratulations to all players! We love you all! <3")
            print("\n")

        print(leaderboard)
        print("\n")
        input("Press enter to continue...")
        self.clear()
        if last_round:
            return player_stats

    def new_tournament(self):
        players_ok = False
        while not players_ok:
            players = input("Enter the names of the players: ").split(",")
            if len(players) < 2:
                print("must have at least 2 players")
                continue

            confirm_players = input("Confirm players: " + str(players) + " (y/n): ")
            if confirm_players.lower() != "y":
                continue
            else:
                players_ok = True
            self.clear()
            
        for ply in players:
            name = ply.strip()
            if name != "":
                new_player = player()
                new_player.name = " ".join(name.split()).title()
                self.players.append(new_player)

        confirm_rounds = False

        while not confirm_rounds:
            print("Number of rounds must be an integer between 1 and 10")
            print("Number of splits will be " + str(math.ceil(len(self.players) / 4)))
            num_rounds = input("Enter number of rounds: ")

            if num_rounds.strip() != "":
                try:
                    num_rounds = int(num_rounds)
                    if num_rounds > 0 and num_rounds < 11:
                        confirm_rounds = True
                    else:
                        print("Invalid number of rounds, must be an integer between 1 and 10")
                        continue
                except:
                    print("Invalid number of rounds, must be an integer between 1 and 10")
                    continue
            self.clear()
                
        self.rounds = self.generate_rounds(num_rounds)

    def generate_rounds(self, num_rounds):
        split_lookup = {5: [3, 2], 6: [3, 3], 7: [4, 3], 8: [4, 4], 9: [3, 3, 3], 10: [4, 3, 3], 11: [4, 4, 3], 12: [4, 4, 4], 13: [4, 3, 3, 3], 14: [4, 4, 3, 3], 15: [4, 4, 4, 3], 16: [4, 4, 4, 4], 17: [4, 4, 3, 3, 3], 18: [4, 4, 4, 3, 3], 19: [4, 4, 4, 4, 3], 20: [4, 4, 4, 4, 4]}
        splits = split_lookup[len(self.players)] if len(self.players) in split_lookup else [len(self.players)]
        players = self.players.copy()

        rounds = []
        rounds_accepted = False
        
        while not rounds_accepted:
            self.clear()
            for i in range(num_rounds):
                available_players = [p for p in players if p not in sum(rounds, [])]
                round_splits = [[] for i in range(len(splits))]
                while len(available_players) > 0:
                    available_splits = [s for s in round_splits if len(s) < splits[round_splits.index(s)]]
                    random_player = random.choice(available_players)
                    random_split  = random.choice(available_splits)
                    random_split.append(random_player)
                    available_players.remove(random_player)
                for split in round_splits:
                    split.sort(key=lambda x: x.name)

                rounds.append(round_splits)

            for r in rounds:
                headings = [f'ROUND {rounds.index(r) + 1}'] + [f'Player {str(i + 1)}' for i in range(max(splits))]
                tab = pt(headings)
                for h in headings:
                    tab.align[h] = "l"

                for s in r:
                    row = [f'Split {r.index(s) + 1}'] + [p.name for p in s]
                    if len(s) < max(splits):
                        row += [""] * (max(splits) - len(s))
                    tab.add_row(row)

                print(tab)
                print("\n")
            
            while not rounds_accepted:
                confirm_rounds = input("[A]ccept, [R]egenerate, [1-10] number of rounds: ")
                if confirm_rounds.lower() == "a":
                    rounds_accepted = True
                elif confirm_rounds.lower() == "r":
                    rounds = []
                    break
                elif confirm_rounds in [str(i) for i in range(1, 11)]:
                    rounds = []
                    num_rounds = int(confirm_rounds)
                    break
                else:
                    print("Invalid input")
                    break
        
        for player in self.players:
            player.positions = [[] for i in range(len(rounds))]
            player.scores    = [[] for i in range(len(rounds))]

        return rounds
    
    def print_players(self):
        for player in self.players:
            print(player.name)

    def load_tournament(self):
        jsonfile = self.name + ".json"
        filedir = os.path.dirname(os.path.realpath(__file__))
        tours_dir = os.path.join(filedir, "tours")
        if not os.path.exists(tours_dir):
            os.mkdir(tours_dir)
        load_path = os.path.join(tours_dir, jsonfile)

        with open(load_path, "r") as f:
            data = json.load(f)
            players = data["players"]
            for ply in players:
                loaded_player = player()
                loaded_player.__dict__ = ply
                self.players.append(loaded_player)

            rounds = data["rounds"]
            for rnd in rounds:
                loaded_round = []
                for split in rnd:
                    loaded_split = []
                    for ply in split:
                        loaded_split.append([p for p in self.players if p.id == ply][0])
                    loaded_round.append(loaded_split)
                self.rounds.append(loaded_round)
            
            finals = data["finals"]
            for ply in finals:
                self.finals.append([p for p in self.players if p.id == ply][0])

            for line in data:
                if line not in ["players", "rounds", "finals"]:
                    self.__dict__[line] = data[line]
        
        self.print_players()

    def save_tournament(self):
        jsonfile = self.name + ".json"
        filedir = os.path.dirname(os.path.realpath(__file__))
        tours_dir = os.path.join(filedir, "tours")
        if not os.path.exists(tours_dir):
            os.mkdir(tours_dir)
        save_path = os.path.join(tours_dir, jsonfile)

        save_data = {"players": [], "rounds": [], "finals": []}
        for player in self.players:
            save_data["players"].append(player.__dict__)

        for round in self.rounds:
            this_round = []
            for split in round:
                this_round.append([player.id for player in split])
            save_data["rounds"].append(this_round)

        for player in self.finals:
            save_data["finals"].append(player.id)

        with open(save_path, "w") as f:
            for x in self.__dict__:
                if x not in ["players", "rounds", "finals"]:
                    save_data[x] = self.__dict__[x]
            json.dump(save_data, f, indent=4)
                    
class player():
    def __init__(self):
        self.id          = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.name        = ""
        self.positions   = []
        self.scores      = []
        self.finals      = []
        self.finals_score= 0

    def add_position(self, position, round, finals=False):
        score_lookup = {1: 15, 2: 12, 3: 10, 4: 9, 5: 8, 6: 7, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
        if int(position) > 0:
            if finals:
                self.finals.append(position)
                self.finals_score += score_lookup[int(position)]
            else:
                self.positions[round].append(int(position))
                self.scores[round].append(score_lookup[int(position)])

if __name__ == "__main__":
    tour = tournament()
