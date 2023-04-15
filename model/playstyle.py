import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans



def main():
    
    # TODO Create engine
    engine = initPostgreSQL()
    
    # Load data from Matches and MatchStats tables
    matches_df = pd.read_sql_table('matches', engine)
    matchstats_df = pd.read_sql_table('matchstats', engine)
    data = pd.merge(matches_df, matchstats_df, left_on='id', right_on='match_id') # Merge the dataframes
    data.drop(columns=['id_x', 'id_y', 'match_id'], inplace=True) # try also data.dropna(inplace=True)
    data.fillna(data.mean(), inplace=True) # Handling missing values (you can use mean, median or mode imputation)
    
    # Standarize the data
    scaler = StandardScaler()
    data_scaled = pd.DataFrame(scaler.fit_transform(data.drop(columns=['home_team_id', 'away_team_id', 'league_id', 'date', 'side'])), columns=data.columns[5:])
    
    # Choose clusters
    n_clusters = 10
    
    # Create a K-means clustering model
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    
    # Fit the model
    kmeans.fit(data_scaled)
    
    # Assign labels to every row
    data['cluster'] = kmeans.labels_
    
    # Calculate average statistics for each cluster
    cluster_averages = data.groupby('cluster').mean()
    
    print(cluster_averages)
    
if __name__ == "__main__":
    main()
    