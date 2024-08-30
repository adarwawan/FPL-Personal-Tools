from fetcher import get_manager_picks
from collections import Counter
import pandas as pd
from tqdm import tqdm

def calculate_ownership(top_managers, gameweek, is_play_only=True, is_captain=False):
    player_count = Counter()
    total_managers = len(top_managers)
    
    for manager_id in top_managers:
        player_picks = get_manager_picks(manager_id, gameweek)
        for player_id, multiplier in player_picks:
            if is_play_only == False:
                multiplier = 1
            if is_captain == False:
                multiplier = min(multiplier, 1)
            player_count[player_id] += multiplier
        player_count.update(player_picks)

    ownership_percentage = {player_id: (count / total_managers) * 100 for player_id, count in player_count.items()}
    # Sort by ownership percentage in descending order
    sorted_ownership = sorted(ownership_percentage.items(), key=lambda item: item[1], reverse=True)
    return sorted_ownership

def create_ownership_dataframe(sorted_ownership, players, teams, limit):
    data = []

    if limit:
        sorted_ownership = sorted_ownership[:limit]
    
    for player_id, percentage in tqdm(sorted_ownership):
        player = players.get(player_id)
        if player:
            player_name = player['web_name']
            team_id = player['team']
            team_name = teams.get(team_id, 'Unknown')
            position = player['element_type']
            points_per_game = float(player['points_per_game'])
            form = float(player['form'])
            selected_by_percent = float(player['selected_by_percent'])
            now_cost = float(player['now_cost'])
            
            data.append({
                'Player ID': player_id,
                'Player Name': player_name,
                'Team ID': team_id,
                'Team Name': team_name,
                'Ownership': percentage,
                'Position': position,
                'Points Per Game': points_per_game,
                'Form': form,
                'Selected By Percent': selected_by_percent,
                'Now Cost': now_cost
            })
    
    df = pd.DataFrame(data)
    return df

