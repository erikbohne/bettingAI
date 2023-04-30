import os
import sys
import sqlalchemy
from typing import Tuple, List

from sqlalchemy.orm import sessionmaker
from sklearn.utils import shuffle

sys.path.append(os.path.join("..", "googleCloud"))
from initPostgreSQL import initPostgreSQL
from features import features, labels

def main(session: sqlalchemy.orm.Session) -> None:
    
    # Get a list of all matchIDs
    matches = session.execute(sqlalchemy.text("SELECT id, home_team_id, away_team_id, date FROM matches")).fetchall()
    print(len(matches))
    
    data = MatchDataGenerator(matches)
    
    x, y = next(data.generate())
    print(x, y)

class MatchDataGenerator:
    def __init__(self, matches, batch_size=16):
        self.matches = matches
        self.features = features
        self.batch_size = batch_size
        
    def generate(self) -> Tuple[List[any], List[any]]:
        while True:
            # Shuffle data at the beginning of each epoch
            self.matches = shuffle(self.matches)
            for i in range(0, len(self.matches), self.batch_size):
                X_batch = []
                Y_batch = []
                for matchID, teamID, opponentID, date in self.matches[i: + self.batch_size]:
                    X_batch.append(features(teamID, opponentID, date, session))
                    Y_batch.append(labels(matchID, teamID, session)) # returns the labels for the match
                    X_batch.append(features(opponentID, teamID, date, session))
                    Y_batch.append(labels(matchID, opponentID, session)) # returns the labels for the match
                    print("Done")
            
                yield X_batch, Y_batch  
                
def initSession() -> sqlalchemy.orm.Session:
    connection = initPostgreSQL()
    Session = sessionmaker(connection)
    return Session()
    
if __name__ == "__main__":
    session = initSession()
    main(session)