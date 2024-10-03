import requests

# Function to fetch player picks for a specific manager and gameweek
def get_manager_picks(manager_id, gameweek):
    url = f"https://fantasy.premierleague.com/api/entry/{manager_id}/event/{gameweek}/picks/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [(pick['element'], pick.get('multiplier', 1)) for pick in data['picks']]  # Return list of player IDs
    else:
        print(f"Failed to retrieve picks for manager {manager_id}. Status code: {response.status_code}")
        return []

def get_top_X_managers(top_x, league_id=314, page_size=50):
    manager_ids = []
    page = 1
    
    while len(manager_ids) < top_x:
        url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?page_standings={page}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            standings = data['standings']['results']
            manager_ids.extend(manager['entry'] for manager in standings)
            
            # Check if we need to stop after this page
            #if len(standings) < page_size:
            #    print(len(standings))
            #    break  # No more pages if the number of results is less than the page size
            
            page += 1
        else:
            print(f"Failed to retrieve data on page {page}. Status code: {response.status_code}")
            break

    return manager_ids[:top_x]

def get_player_info():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        players = {player['id']: player for player in data['elements']}
        return players
    else:
        print(f"Failed to retrieve player information. Status code: {response.status_code}")
        return {}
    
def get_teams():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        teams = data['teams']
        return teams
    else:
        print(f"Failed to retrieve teams information. Status code: {response.status_code}")
        return []

def get_teams_dict():
    teams = get_teams()
    # Create a dictionary mapping 'code' to 'name'
    team_dict = {team['id']: team['name'] for team in teams}
    return team_dict

# Function to fetch fixture data
def fetch_fixtures():
    response = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch fixtures")