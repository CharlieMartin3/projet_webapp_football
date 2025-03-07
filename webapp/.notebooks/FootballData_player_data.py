import pandas as pd
import httpx
import asyncio

# API Key from FootballData.org (Replace with your key)
API_KEY = "028efda53f8a433185a37a19ad961b5d"

# API Base URL
FOOTBALLDATA_API = "https://api.football-data.org/v4/competitions/{league}/teams"

# League Mapping
LEAGUE_MAPPING = {
    "Premier League": "PL",
    "La Liga": "PD",
    "Serie A": "SA",
    "Bundesliga": "BL1",
    "Ligue 1": "FL1",
}

HEADERS = {"X-Auth-Token": API_KEY}

async def fetch_teams(league_name, league_code):
    """Fetch all teams in a league and their players."""
    url = FOOTBALLDATA_API.format(league=league_code)

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ Failed to fetch data for {league_name}")
        return []

    data = response.json()
    teams = data.get("teams", [])

    players = []
    for team in teams:
        squad_url = team.get("squad", [])
        team_name = team.get("name")

        for player in squad_url:
            players.append({
                "League": league_name,
                "Team": team_name,
                "Player Name": player.get("name"),
                "Position": player.get("position"),
                "Nationality": player.get("nationality"),
                "Age": player.get("dateOfBirth"),
            })

    return players

async def collect_all_players():
    """Fetch players from all leagues and store in a DataFrame."""
    tasks = [fetch_teams(league, code) for league, code in LEAGUE_MAPPING.items()]
    results = await asyncio.gather(*tasks)

    # Flatten list of lists
    all_players = [player for result in results for player in result]

    # Convert to DataFrame
    df = pd.DataFrame(all_players)

    # Save DataFrame to CSV
    df.to_csv("footballData_players.csv", index=False)
    print("✅ Data saved to football_players.csv")

    return df

if __name__ == "__main__":
    df = asyncio.run(collect_all_players())  # Store the returned DataFrame
    print(df.head())  # Display first few rows for verification
