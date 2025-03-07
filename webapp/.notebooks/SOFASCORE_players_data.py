import pandas as pd
import httpx
import asyncio

# Sofascore API Endpoints
SOFASCORE_TEAMS_API = "https://api.sofascore.com/api/v1/unique-tournament/{league_id}/season/{season_id}/teams"
SOFASCORE_PLAYERS_API = "https://api.sofascore.com/api/v1/team/{team_id}/players"
SOFASCORE_STATS_API = "https://api.sofascore.com/api/v1/player/{player_id}/statistics"

# League Mapping with IDs (Sofascore IDs for 2024 season)
LEAGUE_MAPPING = {
    "Premier League": (17, 41886),
    "La Liga": (8, 41889),
    "Serie A": (23, 41888),
    "Bundesliga": (35, 41890),
    "Ligue 1": (34, 41887),
}

async def fetch_teams(league_name, league_id, season_id):
    """Fetch all teams in a league."""
    url = SOFASCORE_TEAMS_API.format(league_id=league_id, season_id=season_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        print(f"❌ Failed to fetch teams for {league_name}")
        return []

    data = response.json()
    teams = [{"team_id": team["id"], "team_name": team["name"]} for team in data.get("teams", [])]

    return teams

async def fetch_players(team_id, team_name, league_name):
    """Fetch all players in a team."""
    url = SOFASCORE_PLAYERS_API.format(team_id=team_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        print(f"❌ Failed to fetch players for {team_name}")
        return []

    data = response.json()
    players = []
    for player in data.get("players", []):
        players.append({
            "League": league_name,
            "Team": team_name,
            "Player ID": player.get("id"),
            "Name": player.get("name"),
            "Position": player.get("position"),
            "Nationality": player.get("country", {}).get("name"),
            "Age": player.get("age"),
            "Height": player.get("height"),
            "Weight": player.get("weight"),
            "Jersey Number": player.get("shirtNumber"),
        })

    return players

async def fetch_player_stats(player_id, player_name, team_name, league_name):
    """Fetch detailed stats for a player."""
    url = SOFASCORE_STATS_API.format(player_id=player_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        print(f"❌ Failed to fetch stats for {player_name}")
        return {}

    data = response.json()
    stats = data.get("statistics", {})

    return {
        "League": league_name,
        "Team": team_name,
        "Player Name": player_name,
        "Player ID": player_id,
        "Goals": stats.get("goals"),
        "Assists": stats.get("assists"),
        "Pass Accuracy": stats.get("passAccuracy"),
        "Shots on Target": stats.get("shotsOnTarget"),
        "Tackles": stats.get("tackles"),
        "Minutes Played": stats.get("minutesPlayed"),
    }

async def collect_all_player_stats():
    """Fetch stats for all players in the top 5 leagues."""
    all_stats = []

    for league_name, (league_id, season_id) in LEAGUE_MAPPING.items():
        print(f"🔍 Fetching teams for {league_name}...")
        teams = await fetch_teams(league_name, league_id, season_id)

        for team in teams:
            print(f"📌 Fetching players for {team['team_name']}...")
            players = await fetch_players(team["team_id"], team["team_name"], league_name)

            tasks = [
                fetch_player_stats(player["Player ID"], player["Name"], player["Team"], player["League"])
                for player in players
            ]
            results = await asyncio.gather(*tasks)
            all_stats.extend(results)

    # Convert to DataFrame
    df = pd.DataFrame(all_stats)

    # Save to CSV
    df.to_csv("sofascore_player_stats.csv", index=False)
    print("✅ Data saved to sofascore_player_stats.csv")

    return df

if __name__ == "__main__":
    df = asyncio.run(collect_all_player_stats())  # Store stats in DataFrame
    print(df.head())  # Show first few rows
