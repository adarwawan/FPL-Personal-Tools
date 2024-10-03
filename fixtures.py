import pandas as pd

# Function to calculate points for the last 4 gameweeks
def calculate_team_stats(fixtures, current_gw, last_gw=4):
    recent_fixtures = [f for f in fixtures if f['event'] in range(current_gw-last_gw+1,current_gw+1)]
    team_stats = {}

    # Iterate over the fixtures
    for fixture in recent_fixtures:
        if fixture['finished']:
            # Get team IDs and scores
            home_team = fixture['team_h']
            away_team = fixture['team_a']
            home_score = fixture['team_h_score']
            away_score = fixture['team_a_score']

            # Initialize stats for teams if not already done
            if home_team not in team_stats:
                team_stats[home_team] = {
                    "points": 0, 
                    "scored": 0, 
                    "conceded": 0, 
                    "played": 0
                }
            if away_team not in team_stats:
                team_stats[away_team] = {
                    "points": 0, 
                    "scored": 0, 
                    "conceded": 0, 
                    "played": 0
                }

            # Update scores and conceded goals
            team_stats[home_team]["played"] = team_stats[home_team]["played"] + 1
            team_stats[away_team]["played"] = team_stats[away_team]["played"] + 1

            team_stats[home_team]["scored"] += home_score
            team_stats[home_team]["conceded"] += away_score
            team_stats[away_team]["scored"] += away_score
            team_stats[away_team]["conceded"] += home_score

            # Assign points based on the result
            if home_score > away_score:
                team_stats[home_team]["points"] += 3  # Home team wins
            elif home_score < away_score:
                team_stats[away_team]["points"] += 3  # Away team wins
            else:
                team_stats[home_team]["points"] += 1  # Draw
                team_stats[away_team]["points"] += 1  # Draw

    return team_stats

def get_next_opponents(fixtures, current_gw, next_gw=4):
    upcoming_fixtures = [f for f in fixtures if f['event'] in range(current_gw+1, current_gw+next_gw+1)]
    team_opponent = {}

    # Iterate over the fixtures
    for fixture in upcoming_fixtures:
        # Get team IDs and scores
        home_team = fixture['team_h']
        away_team = fixture['team_a']
        event = fixture['event']
        home_fdr = fixture['team_h_difficulty']
        away_fdr = fixture['team_a_difficulty']

        # Initialize stats for teams if not already done
        if home_team not in team_opponent:
            team_opponent[home_team] = []
        if away_team not in team_opponent:
            team_opponent[away_team] = []

        team_opponent[home_team].append(
            {
                "team_id": away_team,
                "ha": "h",
                "event": event,
                "fdr": int(home_fdr)
            }
        )

        team_opponent[away_team].append(
            {
                "team_id": home_team,
                "ha": "a",
                "event": event,
                "fdr": int(away_fdr)
            }
        )

    return team_opponent

def opponents_to_dataframe(opponents, fdr_map, teams):
    data = []
    for team_id, opponent in opponents.items():
        team_data = {
            "id": team_id,
            "team_name": teams.get(team_id, "Unknown Team"),
            "diff": fdr_map.get(team_id)
        }
        count = 0
        total_diff = 0
        for op in opponent:
            count += 1
            team_data[f"next_{count}_opp"] = teams.get(op["team_id"], "Unknown Team") + " " + op["ha"]
            fdr = fdr_map.get(op["team_id"])
            if op["ha"] == "a":
                fdr += 1
            team_data[f"next_{count}_fdr"] = fdr
            total_diff += fdr

        team_data["opp_diff"] = total_diff / (count + 1)
        
        data.append(team_data)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    return df

def opponents_to_dataframe_def(opponents, teams):
    data = []
    for team_id, opponent in opponents.items():
        team_data = {
            "id": team_id,
            "team_name": teams.get(team_id, "Unknown Team"),
        }
        count = 0
        total_diff = 0
        for op in opponent:
            count += 1
            team_data[f"next_{count}_opp"] = teams.get(op["team_id"], "Unknown Team") + " " + op["ha"]
            fdr = op['fdr']
            if op["ha"] == "a":
                fdr += 1
            team_data[f"next_{count}_fdr"] = fdr
            total_diff += fdr

        team_data["opp_diff"] = total_diff / (count + 1)
        
        data.append(team_data)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    return df



def stats_to_dataframe(team_stats, teams):
    # Create a list of dictionaries to convert into DataFrame
    data = []
    for team_id, stats in team_stats.items():
        team_name = teams.get(team_id, "Unknown Team")
        data.append({
            "Team": team_name,
            "ID": team_id,
            "Points": stats['points'],
            "Goals Scored": stats['scored'],
            "Goals Conceded": stats['conceded'],
            "Points per Game": stats['points'] / stats['played'],
            "Goals Scored per Game": stats['scored'] / stats['played'],
            "Goals Conceded per Game": stats['conceded'] / stats['played'],
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    df = df.sort_values(by="Points", ascending=False)
    return df