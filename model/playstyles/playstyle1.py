import pandas as pd
import numpy as np
import json
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sqlalchemy import create_engine
from google.cloud.sql.connector import Connector

import matplotlib.pyplot as plt
import seaborn as sns

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
    
    data['team_id'] = np.where(data['side'] == 'home', data['home_team_id'], data['away_team_id'])
    team_ids = data['team_id'].tolist()
    
    # KMeans clustering
    n_clusters = 4
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(data_scaled)

    # Function to find the most frequent cluster for a team
    def most_frequent_cluster(team_id, team_ids, cluster_labels):
        team_indices = [i for i, x in enumerate(team_ids) if x == team_id]
        team_clusters = [cluster_labels[i] for i in team_indices]
        return max(set(team_clusters), key=team_clusters.count)

    # Assigning teams to their most frequent clusters
    team_clusters = {team_id: most_frequent_cluster(team_id, team_ids, kmeans.labels_) for team_id in set(team_ids)}

    # Printing team cluster assignments
    for team_id, cluster in team_clusters.items():
        print(f"Team {team_id} is assigned to cluster {cluster}")
        
    cluster_centroids = kmeans.cluster_centers_

    # Create a DataFrame to better visualize and analyze the centroids
    centroids_df = pd.DataFrame(cluster_centroids, columns=data_scaled.columns)  # Exclude the 'team_id' column

    # You can normalize the data to make the comparison easier
    normalized_centroids_df = (centroids_df - centroids_df.min()) / (centroids_df.max() - centroids_df.min())

    # Display the centroids
    print(normalized_centroids_df)
    
    plt.figure(figsize=(12, 6))
    sns.heatmap(normalized_centroids_df, cmap="coolwarm", annot=True, linewidths=0.5)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.xlabel("Features")
    plt.ylabel("Cluster")
    plt.title("Normalized Cluster Centroids")
    plt.show()
    
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
    