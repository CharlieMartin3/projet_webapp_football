import pandas as pd
import httpx
import asyncio

# ESPN API Base URL (Modify if necessary)
ESPN_TEAMS_API = "https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/teams"

# League Mapping
LEAGUE_MAPPING = {
    "premier-league": "eng.1",
    "ligue-1": "fra.1",
    "serie-a": "ita.1",
    "la-liga": "esp.1",
    "bundesliga": "ger.1"
}


async def fetch_teams(league_name, league_code):
    """Fetch team data for a specific league."""
    url = ESPN_TEAMS_API.format(league=league_code)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        print(f"❌ Failed to fetch data for {league_name}")
        return []

    data = response.json()

    # Extract teams
    teams = []
    for team in data.get("sports", [])[0].get("leagues", [])[0].get("teams", []):
        team_data = team.get("team", {})
        venue = team_data.get("venue", {})

        teams.append({
            "League": league_name,
            "Team ID": team_data.get("id"),
            "Name": team_data.get("displayName"),
            "Abbreviation": team_data.get("abbreviation"),
            "Short Name": team_data.get("shortDisplayName"),
            "Location": team_data.get("location"),
            "Venue Name": venue.get("fullName"),
            "City": venue.get("address", {}).get("city"),
            "Country": venue.get("address", {}).get("country"),
            "Capacity": venue.get("capacity"),
            "Logo": team_data.get("logos", [{}])[0].get("href") if team_data.get("logos") else None
        })

    return teams

async def collect_all_teams():
    """Fetch teams from all leagues and store in a DataFrame."""
    tasks = [fetch_teams(league, code) for league, code in LEAGUE_MAPPING.items()]
    results = await asyncio.gather(*tasks)

    # Flatten list of lists
    all_teams = [team for result in results for team in result]

    # Convert to DataFrame
    df = pd.DataFrame(all_teams)

    # Save DataFrame to CSV
    df.to_csv("teams_data.csv", index=False)
    print("✅ Data saved to teams_data.csv")

    return df

if __name__ == "__main__":
    df = asyncio.run(collect_all_teams())  # Store the returned DataFrame
    print(df.head())  # Display first few rows for verification
