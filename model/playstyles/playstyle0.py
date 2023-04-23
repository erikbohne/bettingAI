import pandas as pd
import json
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sqlalchemy import create_engine
from google.cloud.sql.connector import Connector
from collections import defaultdict

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../../keys/googleCloudKey.json'

def main():
    
    # TODO Create engine
    engine = initPostgreSQL()
    
    # Load data from Matches and MatchStats tables
    with engine.connect() as connection:
        matches_df = pd.read_sql_table('matches', connection)
        matchstats_df = pd.read_sql_table('matchstats', connection)
    data = pd.merge(matches_df, matchstats_df, left_on='id', right_on='match_id') # Merge the dataframes
    data.drop(columns=['id_x', 'id_y', 'match_id'], inplace=True) # try also data.dropna(inplace=True)
    data.fillna(data.mean(), inplace=True) # Handling missing values (you can use mean, median or mode imputation)
    
    # Standarize the data
    scaler = StandardScaler()
    data_scaled = pd.DataFrame(scaler.fit_transform(data.drop(columns=['home_team_id', 'away_team_id', 'league_id', 'date', 'side'])), columns=data.columns[5:])
    
    # Choose clusters
    n_clusters = 4
    
    # Create a K-means clustering model
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    
    # Fit the model
    kmeans.fit(data_scaled)
    
    # Assign labels to every row
    data['cluster'] = kmeans.labels_
    
    # Fetch team information and merge with clustered data
    with engine.connect() as connection:
        teams_df = pd.read_sql_table('teams', connection)
    team_cluster_data = data[['home_team_id', 'away_team_id', 'home_goals', 'away_goals', 'cluster']]
    team_cluster_data = team_cluster_data.merge(teams_df, left_on='home_team_id', right_on='id', suffixes=('_home', '_away'))
    team_cluster_data = team_cluster_data.merge(teams_df, left_on='away_team_id', right_on='id', suffixes=('', '_away'))

    # Analyze playstyles
    analyze_playstyles(team_cluster_data)

    
# Add this new function to analyze playstyles
def analyze_playstyles(team_cluster_data):
    playstyle_data = defaultdict(lambda: {'teams': set(), 'performance': defaultdict(int)})

    for _, row in team_cluster_data.iterrows():
        print(row.columns)
        home_team_id, away_team_id, home_goals, away_goals, cluster, _, home_team_name, _, _, _, away_team_name, _, _ = row
        playstyle_data[cluster]['teams'].add((home_team_id, home_team_name))
        playstyle_data[cluster]['teams'].add((away_team_id, away_team_name))

        winner = 'draw' if row['home_goals'] == row['away_goals'] else ('home' if row['home_goals'] > row['away_goals'] else 'away')
        if winner == 'home':
            playstyle_data[cluster]['performance']['wins'] += 1
        elif winner == 'away':
            playstyle_data[cluster]['performance']['losses'] += 1
        else:
            playstyle_data[cluster]['performance']['draws'] += 1

    for cluster, data in playstyle_data.items():
        print(f"Cluster {cluster}:")
        print(f"Teams: {', '.join(f'{team_id} ({team_name})' for team_id, team_name in data['teams'])}")
        print(f"Performance: {data['performance']}\n")
    
def loadJSON(path):
    """
    Returns data from JSON file @ path
    """
    return json.load(open(path))
    
def initPostgreSQL():
    """
    Connects and initializes PostgreSQL
    """
    # Import database creditations
    creds = loadJSON("../../../keys/postgreSQLKey.json")

    def getConnection():
        connector = Connector()
        connection = connector.connect(
            creds["connectionName"],
            "pg8000",
            user=creds["user"],
            password=creds["password"],
            db=creds["dbname"]
        )
        return connection
    
    try: # Try to connecto to database
        engine = create_engine(
            "postgresql+pg8000://",
            creator=getConnection,
        )
        return engine
    except Exception as e: # Connection failed
        return None
    
if __name__ == "__main__":
    main()
    