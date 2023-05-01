import os
import sys
import sqlalchemy
from typing import Tuple, List

from sqlalchemy.orm import sessionmaker
from sklearn.utils import shuffle

sys.path.append(os.path.join("..", "googleCloud"))
from initPostgreSQL import initPostgreSQL
from features import features_for_model0, labels

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

import time

# HYPERPARAMETERES
LEARNINGRATE = 1e-3
BATCHSIZE = 16

def main(session: sqlalchemy.orm.Session) -> None:
    
    # Get a list of all matchIDs
    matches = session.execute(sqlalchemy.text("SELECT id, home_team_id, away_team_id, season, date FROM matches")).fetchall()
    print(len(matches))
    
    # Create data generator
    data = Model0DataGenerator(matches)
    
    # Init model
    model0 = BettingModel0()
    
    # Optimizer and loss function
    optimizer = optim.Adam(model0.parameters(), lr=LEARNINGRATE)
    criterion = nn.CrossEntropyLoss()
    
    # Train the model
    epochs = 10
    for epoch in range(epochs):
        for batch in range(int(len(matches)/BATCHSIZE)):
            start_time = time.time()
            inputs, targets = next(data.generate()) # get the inputs and targets from the batch
                
            # Convert inputs and targets to tensors
            inputs = torch.tensor(inputs, dtype=torch.float32)
            targets = torch.tensor(targets, dtype=torch.float32)
            
            # Zero the optimizer gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model0(inputs)
            
            # Calculate losss
            loss = criterion(outputs, targets)
            
            # Backward pass
            loss.backward()
            
            # Update weights
            optimizer.step()
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Batch: {batch}/{len(matches)/BATCHSIZE} complete with loss -> {loss.item()} in a time of -> {elapsed_time:.2f}")
    

class Model0DataGenerator:
    def __init__(self, matches, batch_size=BATCHSIZE):
        self.matches = matches
        self.batch_size = batch_size
        
    def generate(self) -> Tuple[List[any], List[any]]:
        while True:
            # Shuffle data at the beginning of each epoch
            self.matches = shuffle(self.matches)
            for i in range(0, len(self.matches), self.batch_size):
                X_batch = []
                Y_batch = []
                batch = 1
                for matchID, teamID, opponentID, season, date in self.matches[i: + self.batch_size]:
                    X_batch.append(features_for_model0(teamID, opponentID, season, "home", date, session))
                    Y_batch.append(labels(matchID, teamID, session)) # returns the labels for the match
                    X_batch.append(features_for_model0(opponentID, teamID, season, "away", date, session))
                    Y_batch.append(labels(matchID, opponentID, session)) # returns the labels for the match
                    batch += 1
            
                yield X_batch, Y_batch  
                
class BettingModel0(nn.Module):
    def __init__(self):
        super(BettingModel0, self).__init__()
        self.h1 = nn.Linear(42, 128) # first hidden layer with 128 nodes
        self.dropout1 = nn.Dropout(0.5) # first dropout layer
        self.h2 = nn.Linear(128, 64) # second hidden layer with 128 -> 64 nodes
        self.dropout2 = nn.Dropout(0.5) # second dropout layer
        self.h3 = nn.Linear(64, 8) # output layer with 64 -> 8 nodes
    
    def forward(self, x):
        x = F.relu(self.h1(x))
        x = self.dropout1(x)
        x = F.relu(self.h2(x))
        x = self.dropout2(x)
        x = self.h3(x)
        return F.softmax(x, dim=1)
                
def initSession() -> sqlalchemy.orm.Session:
    connection = initPostgreSQL()
    Session = sessionmaker(connection)
    return Session()
    
if __name__ == "__main__":
    session = initSession()
    main(session)