#imports
import uvicorn
from fastapi import FastAPI, Request, Query
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neighbors import NearestNeighbors
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
from sqlalchemy import create_engine


# create the engine
DB_USER = "admin_football"
DB_PASSWORD = "Cha+Nat2!0897"
DB_HOST = "database-1.cpyi2k0umh5a.eu-north-1.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "website_football_db"
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

data_joueurs = pd.read_csv("webapp/files/complete_players_data.csv") #players_data.csv
data_gk = pd.read_csv("webapp/files/complete_gk_data.csv") #gk_data.csv

standing_BL1 = pd.read_sql('SELECT * FROM "BL1_standings"', engine)
standing_PL = pd.read_sql('SELECT * FROM "PL_standings"', engine)
standing_LALIGA = pd.read_sql('SELECT * FROM "PD_standings"', engine)
standing_SERIEA = pd.read_sql('SELECT * FROM "SA_standings"', engine)
standing_LIGUE1 = pd.read_sql('SELECT * FROM "FL1_standings"', engine)


# --------------------------------------------- PLAYERS AI MODEL PART ---------------------------------------------

encoder = OneHotEncoder(sparse_output=False)
categorical_columns = data_joueurs.select_dtypes(include=['object']).columns.tolist()
one_hot_encoded = encoder.fit_transform(data_joueurs[['Pos','Comp']])
one_hot_df = pd.DataFrame(one_hot_encoded, columns=encoder.get_feature_names_out(['Pos','Comp']))
data_joueurs = pd.concat([data_joueurs, one_hot_df], axis=1)

# Select relevant features for comparison
features_players_model = ['MP','Starts','Min','90s',  # basics stats
    'Gls', 'PK', 'PKatt', 'G-PK', 'xG', 'npxG', 'Ast', 'G+A', 'xAG', 'npxG+xAG', 'G+A-PK', 'xG+xAG', # attacking stats
    'Sh_stats_shooting', 'SoT', 'SoT%', 'Sh/90', 'SoT/90', 'G/Sh', 'G/SoT', 'Dist', # Shooting stats
    'FK_stats_shooting', 'PK_stats_shooting', 'PKatt_stats_shooting', 'CK_stats_passing_types', # Free kicks and penalty stats
    'SCA','SCA90', 'PassLive', 'PassDead', 'TO', 'Sh_stats_gca','Fld', 'Def', 'GCA', 'GCA90', # Creativity stats
    'Tkl', 'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd',	'Int', 'Tkl+Int', 'Tkl%', 'Lost', 'Blocks', 'Sh', 'Pass', 'Clr', 'Err', # Defense stats
    'Cmp_stats_passing', 'Att_stats_passing', 'Cmp%_stats_passing', 'TotDist', 'PrgDist', 'xAG_stats_passing', 'xA', 'A-xAG',
    'KP', '1/3', 'PPA', 'CrsPA', 'Crs_stats_passing_types', 'Live', 'Dead', 'TB', 'Sw', 'Off_stats_passing_types', 'Blocks_stats_passing_types', # Passes stats
    'Touches', 'Live_stats_possession', 'Def Pen', 'Def 3rd_stats_possession', 'Mid 3rd_stats_possession', 'Att 3rd_stats_possession', 'Att Pen',
    'Att_stats_possession', 'Succ', 'Succ%', 'Tkld', 'Tkld%', 'Carries', 'TotDist_stats_possession', 'PrgDist_stats_possession', 'PrgC_stats_possession',
    '1/3_stats_possession', 'CPA', 'Mis', 'Dis', 'Rec', 'PrgR_stats_possession',
    'Pos_DF', 'Pos_MF', 'Pos_DF,MF', 'Pos_FW', 'Pos_MF,FW', 'Pos_FW,MF', 'Pos_MF,DF', 'Pos_FW,DF','Pos_DF,FW'
]

data_joueurs.fillna(0, inplace=True)

# Normalize numeric data
scaler = StandardScaler()
data_joueurs_scaled = scaler.fit_transform(data_joueurs[features_players_model])

# Fit Nearest Neighbors model
cosine_sim_joueurs =  cosine_similarity(data_joueurs_scaled)



# --------------------------------------------- GK AI MODEL PART ---------------------------------------------
# Select relevant features for comparison
features_gk_model = [
    "MP", "Starts", "Min", "CS%", "GA90", "Save%", "PSxG", "PSxG+/-", "PSxG/SoT",
    "PKsv", "Cmp%", "Launch%", "AvgLen", "Stp%", "AvgDist"
]

data_gk.fillna(0, inplace=True)

# Normalize numeric data
scaler = StandardScaler()
data_gk_scaled = scaler.fit_transform(data_gk[features_gk_model])

# Fit Nearest Neighbors model
cosine_sim_gk =  cosine_similarity(data_gk_scaled) #model_gk_knn = NearestNeighbors(n_neighbors=6, metric="cosine")  # Finding 5 similar goalkeepers
#model_gk_knn.fit(data_gk_scaled)


#--------------------------------------------- functions ---------------------------------------------

def get_index_from_name(df, name):
    return df[df.Player == name].index.values[0]

def get_list_of_indexes(df, sorted_similar_players, nb_joueurs, valeur_max):
    i=1
    j=1
    liste_index_finale = []
    while(i<nb_joueurs+1):
        if df.iloc[sorted_similar_players[j][0]].valeur_marchande<=valeur_max:
            liste_index_finale.append(sorted_similar_players[j][0])
            i+=1
        j+=1
    return liste_index_finale

def create_finale_df(df, sorted_similar_players, nb_joueurs, valeur_max):
    liste_index_finale = get_list_of_indexes(df, sorted_similar_players, nb_joueurs, valeur_max)
    res = df.iloc[liste_index_finale]
    return res

def select_similar_players(df, cosine_matrix, player_name,nb_joueurs,valeur_max=300):
    player_index = get_index_from_name(df, player_name)
    similar_players = list(enumerate(cosine_matrix[player_index]))
    sorted_similar_players = sorted(similar_players, key=lambda x:x[1], reverse=True)
    return create_finale_df(df, sorted_similar_players, nb_joueurs, valeur_max)

#--------------------------------------------- FAST API ---------------------------------------------

app = FastAPI()
app.mount("/static", StaticFiles(directory="webapp/html"), name="static")
templates = Jinja2Templates(directory="webapp/html")


@app.get("/")
async def root():
    return HTMLResponse(content=open("webapp/html/index.html", "r").read())

@app.get("/index")
def home():
    return HTMLResponse(content=open("webapp/html/index.html", "r").read())

@app.get("/model")
def home():
    return HTMLResponse(content=open("webapp/html/model.html", "r").read())

@app.get("/autocomplete_Player_reserch", response_model=List[str])
async def autocomplete(q: str = Query("")):
    """
    Returns a list of player names matching the query.
    """
    query = q.lower()
    matching_players = data_joueurs[data_joueurs["Player"].str.lower().str.contains(query, na=False)]["Player"].tolist()
    return matching_players

@app.get("/autocomplete_GK_reserch", response_model=List[str])
async def autocomplete_player(q: str = Query("")):
    """
    Returns a list of player names matching the query.
    """
    query = q.lower()
    matching_players = data_gk[data_gk["Player"].str.lower().str.contains(query, na=False)]["Player"].tolist()
    return matching_players


@app.get("/goalkeeper")
def home():
    return HTMLResponse(content=open("webapp/html/goalkeeper.html", "r").read())

@app.get("/goalkeeper/{joueur_nom}/nombre/{nombre}/prix_max/{prix_max}")
async def read_gk_solo(joueur_nom,nombre=10,prix_max=300):
    if (int(nombre)>30):
        nombre = 30
    df_res = select_similar_players(data_gk,cosine_sim_gk,joueur_nom,int(nombre),float(prix_max)) #find_similar_goalkeepers(joueur_nom, top_n=nombre)
    df_res = df_res.fillna('NA')
    df_res = df_res[['nom_joueur','nom_club','nom_championnat','Pos','MP','Starts','Min','Age','valeur_marchande']]
    res = {
        "columns": df_res.columns.tolist(),  # Extract column names
        "data": df_res.values.tolist()  # Extract data values
    }
    return res

@app.get("/joueur/{joueur_nom}/nombre/{nombre}/prix_max/{prix_max}")
async def read_joueur_solo(joueur_nom,nombre=10,prix_max=300):
    if (int(nombre)>30):
        nombre = 30
    df_res = select_similar_players(data_joueurs,cosine_sim_joueurs,joueur_nom,int(nombre),float(prix_max))
    df_res = df_res.fillna('NA')
    df_res = df_res[['nom_joueur','nom_club','nom_championnat','Pos','MP','Starts','Min','Age','valeur_marchande']]
    res = {
        "columns": df_res.columns.tolist(),  # Extract column names
        "data": df_res.values.tolist()  # Extract data values
    }
    return res

@app.get("/about")
def home():
    return HTMLResponse(content=open("webapp/html/about.html", "r").read())    

@app.get("/contact")
def home():
    return HTMLResponse(content=open("webapp/html/contact.html", "r").read()) 

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})

@app.get("/standings", response_class=HTMLResponse)
async def standings_page(request: Request):
    return templates.TemplateResponse("standings.html", {"request": request})


@app.get("/api/standings")
async def get_standings(league: str):
    if league == "premier-league":
        standings = standing_PL
        print(standings)
    elif league == "laliga":
        standings = standing_LALIGA
    elif league == "bundesliga":
        standings = standing_BL1
    elif league == "serie-a":
        standings = standing_SERIEA
    elif league == "ligue-1":
        standings = standing_LIGUE1
    else:
        return {"error": "Invalid league specified"}

    standings = standings.fillna('NA')
    standings = standings[['position','team_shortName','points','playedGames','won','draw','lost','goalsFor','goalsAgainst','goalDifference']]
    res = {
        "columns": standings.columns.tolist(),
        "data": standings.values.tolist() 
    }
    return res

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=80)    