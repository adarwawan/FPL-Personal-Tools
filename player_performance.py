from fetcher import get_teams_dict
import requests
import pandas as pd

# Function to get player points for a specific gameweek
def get_player_points_per_gameweek(gameweek):
    url = f"https://fantasy.premierleague.com/api/event/{gameweek}/live/"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        players = data['elements']
        point = {}
        for player in players:
            point[player['id']] = player['stats']['total_points']
        return point
    else:
        print(f"Failed to retrieve data for gameweek {gameweek}. Status code: {response.status_code}")
        return {}

def create_points_dataframe_with_gameweeks(player_points_per_gw, players, gameweeks, min_to_return):
    data = []
    team_dict = get_teams_dict()

    for player_id, player_info in players.items():
        player_name = player_info['web_name']
        team_id = player_info['team']
        team_name = team_dict.get(team_id, 'Unknown')
        position = player_info['element_type']
        points_per_game = float(player_info['points_per_game'])
        form = float(player_info['form'])
        selected_by_percent = float(player_info['selected_by_percent'])
        now_cost = float(player_info['now_cost'])
            
        player_data = {
            'Player ID': player_id,
            'Player Name': player_name,
            'Team ID': team_id,
            'Team Name': team_name,
            'Position': position,
            'Points Per Game': points_per_game,
            'Form': form,
            'Selected By Percent': selected_by_percent,
            'Now Cost': now_cost
        }

        # Add points for each gameweek
        num_return = 0
        for gw in gameweeks:
            points = player_points_per_gw[gw].get(player_id, 0)  # Default to 0 if no points are available
            player_data[f'GW{gw} Points'] = points

            if min_to_return > 0:
                if points >= min_to_return:
                    num_return = num_return + 1

        # Calculate total points across the gameweeks
        player_data['Total Points'] = sum(player_data[f'GW{gw} Points'] for gw in gameweeks)
        player_data['Number Returns'] = num_return

        data.append(player_data)

    df = pd.DataFrame(data)
    # Sort by Total Points
    sorted_df = df.sort_values(by='Total Points', ascending=False)
    return sorted_df