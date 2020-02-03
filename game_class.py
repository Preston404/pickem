from urllib.request import urlopen
from bs4 import BeautifulSoup
import numpy as np

TEAMS = ["ari", "atl", "bal", "buf", "car", "chi", "cin", "cle",
         "dal", "den", "det", "gb", "hou", "ind", "jax", "kc",
         "lac", "lar", "mia", "min", "ne", "no", "nyg", "nyj",
         "oak", "phi", "pit", "sf", "sea", "tb", "ten", "wsh"]

class game():
    
    def __init__(self, team=None, opponent=None, points=None, points_o=None):
        win = 0
        if points >= points_o:
            win = 1
        self.stats = {
            "team": team,
            "opponent": opponent,
            "win_pct" : 0.0,
            "points": points,
            "rushingYards": 0,
            "rushingAttempts" : 0,
            "netPassingYards" : 0,
            "passes" : 0,
            "completions" : 0,
            "sacked" : 0,
            "possessionTime" : 0,
            "turnovers" : 0,
            "win_pct_o" : 0.0,
            "points_o": points_o,
            "rushingYards_o": 0,
            "rushingAttempts_o" : 0,
            "netPassingYards_o" : 0,
            "passes_o" : 0,
            "completions_o" : 0,
            "sacked_o" : 0,
            "possessionTime_o" : 0,
            "turnovers_o" : 0,
            "win" : win
        }


def get_team_season(team):
    history_and_result = []
    for week in range(5,17):
        history = get_history(week, team)
        result = get_game_stats(week, team).stats["win"]
        print(' ')
        print(get_team_extension(get_game_stats(week, team).stats["opponent"]))
        print(result)
        history_and_result.append([history, result])
        

def get_games_average(games):
    new_game = games[0]
    wins = 0
    for game in games:
        wins += game.stats["win"]
        for key in new_game.stats.keys():
            if str(key) not in "team opponent win_pct win":
                new_game.stats[key] = (new_game.stats[key] + game.stats[key]) / 2.0
    new_game.stats["win_pct"] = (wins / len(games))
    return new_game
    

def get_history(week, team):
    games = []
    for w in range(1, week):
        games.append(get_game_stats(w, team))
    return get_games_average(games)
    
    
def get_game_stats(week, team):
    
    # team is 0-31
    extension = get_team_extension(team)
    team_url = get_team_url(extension)
    url = get_game_url(team_url, week)
    
    # Get Web page
    while(True):
        try:
            html = urlopen(url)
            soup = BeautifulSoup(html, features="html.parser")
            break
        except:
            pass
    
    def get_final_score():
        scores = []
        class_str = soup.find_all(class_="final-score")[-2:]
        for score in class_str:
            scores.append(str(score).replace('</td>','').split('>')[-1])
        return scores
    
    def get_stats_by_attr(attr, double=True):
        table_row = str(soup.find_all(attrs={"data-stat-attr": attr})).replace('[','').replace(']','')
        table_row_formated = ' '.join(table_row.replace("<td>",' ').replace('</td>',' ').replace("\n", ' ').replace("</tr>",' ').split())
        return table_row_formated.split()[(-2 if double else -1):]
        
    def get_stats_by_class(c):
        class_str = str(soup.find_all(class_=c)).replace('[','').replace(']','')
        class_str_formated = ' '.join(class_str.replace("</span>",' ').split('>'))
        return class_str_formated.split()[-1]
    
    home_team = get_stats_by_class("home-team")
    away_team = get_stats_by_class("away-team")
    opponent = get_team_num(home_team) if (team == get_team_num(away_team)) else get_team_num(away_team)
    
    # Returned tuple is [away_team, home_team]
    team_i = 1 if (team == get_team_num(away_team)) else 0
    team_o = 0 if (team == get_team_num(away_team)) else 1
    
    scores = get_final_score()
    tmp_game = game(team=team, opponent=opponent, points=float(scores[team_i]), points_o=float(scores[team_o]))
    
    rushingYards = get_stats_by_attr("rushingYards")
    tmp_game.stats["rushingYards"] = float(rushingYards[team_i])
    tmp_game.stats["rushingYards_o"] = float(rushingYards[team_o])
    
    rushingAttempts = get_stats_by_attr("rushingAttempts")
    tmp_game.stats["rushingAttempts"] = float(rushingAttempts[team_i])
    tmp_game.stats["rushingAttempts_o"] = float(rushingAttempts[team_o])
    
    possessionTime = get_stats_by_attr("possessionTime")
    tmp_game.stats["possessionTime"] = float(possessionTime[team_i].split(":")[0])/60
    tmp_game.stats["possessionTime_o"] = float(possessionTime[team_o].split(":")[0])/60
    
    netPassingYards = get_stats_by_attr("netPassingYards")
    tmp_game.stats["netPassingYards"] = float(netPassingYards[team_i])
    tmp_game.stats["netPassingYards_o"] = float(netPassingYards[team_o])
    
    completionAttempts = get_stats_by_attr("completionAttempts")
    
    tmp_game.stats["passes"] = float(completionAttempts[team_i].split("-")[1])
    tmp_game.stats["passes_o"] = float(completionAttempts[team_o].split("-")[1])
    
    tmp_game.stats["completions"] = float(completionAttempts[team_i].split("-")[0])
    tmp_game.stats["completions_o"] = float(completionAttempts[team_o].split("-")[0])
    
    sacksYardsLost = get_stats_by_attr("sacksYardsLost")
    tmp_game.stats["sacked"] = float(sacksYardsLost[team_i].split("-")[0])
    tmp_game.stats["sacked_o"] = float(sacksYardsLost[team_o].split("-")[0])
    
    turnovers = get_stats_by_attr("turnovers")
    tmp_game.stats["turnovers"] = float(turnovers[team_i])
    tmp_game.stats["turnovers_o"] = float(turnovers[team_o])
            
    return tmp_game
    # Made it this far in coverting to use ESPN stats

def get_team_url(team_extension):
    url = "https://www.espn.com/nfl/team/schedule/_/name/" + team_extension
    return url

            
def get_game_url(team_url, week):
    
    while(True):
        try:
            html = urlopen(team_url)
            soup = BeautifulSoup(html, features="html.parser")
            break
        except:
            pass
        
    game_urls = []
    for link in soup.find_all('a'):
        if("gameId" in str(link)):
            game_urls.append(link)
    # Remove Preseason
    game_urls = game_urls[0:-5]
    # Remove Postseason
    if len(game_urls) != 16:
        game_urls = game_urls[(len(game_urls) - 16):]
    url = str(game_urls[week-1]).split('"')[3]
    return "https://www.espn.com/nfl/matchup?gameId=" + url.split('/')[-1] 

def get_team_num(extension):
    return TEAMS.index(extension.lower())

def get_team_extension(num):
    return TEAMS[num]
            