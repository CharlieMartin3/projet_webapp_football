import requests
import json
import pandas as pd
import time


def leagues_standing_ingestion(league_name,HEADERS):
    API_URL = f"https://api.football-data.org/v4/competitions/{league_name}/standings"

    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        standings = data['standings'][0]['table']
        df_standings = pd.DataFrame(standings)
        df_standings['team_id'] = df_standings['team'].apply(lambda x: x['id'])
        df_standings['team_name'] = df_standings['team'].apply(lambda x: x['name'])
        df_standings['team_shortName'] = df_standings['team'].apply(lambda x: x['shortName'])
        df_standings['team_tla'] = df_standings['team'].apply(lambda x: x['tla'])
        df_standings['team_crest'] = df_standings['team'].apply(lambda x: x['crest'])

        df_standings.drop(columns=['team','team_id','form'], inplace=True)
        filename = f"/opt/airflow/data/{league_name}_standings.csv"
        df_standings.to_csv(filename, index=False)

    else:
        print("API request failed")
        print(response.status_code)
        df_standings = pd.DataFrame({"error":[404,404,404], "test":["te","s","t"]})
        filename = f"/opt/airflow/data/{league_name}_standings_test.csv"
        df_standings.to_csv(filename, index=False)


def leagues_data_ingestion():
    print("WE ARE IN leagues_data_ingestion FUNCTION")
    league_names = ["PL","FL1","BL1","SA","PD"]
    HEADERS = {"X-Auth-Token": "c01dc70ca10b4edd892c894925d77665"}  #email : charlie.s.martin...
    for league_name in league_names:
        #time.sleep(10)
        leagues_standing_ingestion(league_name, HEADERS)
        message = f"✅ Data refreshed :{league_name}"
        print(message)

if __name__ == "__main__":
    leagues_data_ingestion()
