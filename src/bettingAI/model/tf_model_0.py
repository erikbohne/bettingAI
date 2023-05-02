"""
Tensorflow model to predict the probability of 8 scenarios
[win, draw, loss, over 2.5, over 3.5, 4.5, 5.5, btts]
"""
from sqlalchemy import text
from bettingAI.googleCloud.initPostgreSQL import initSession

import numpy as np
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Dropout, Concatenate
from tensorflow.keras.models import Model

import matplotlib.pyplot as plt

# HYPERPARAMETERS
BATCH_SIZE = 32
EPOCHS = 10

def main():
    X_train, X_test, y_train, y_test = load_data()
    model = bettingAI_model0()
    
    print(f"X_train shape: {X_train.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"y_test shape: {y_test.shape}")
    
    model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=1)
    scores = model.evaluate(X_test, y_test, verbose=1)
    print("Test loss: ", scores[0])
    print("Test accuracy: ", scores[1])
    
    

def load_data():
    session = initSession()
    matches = session.execute(text("SELECT inputs, labels FROM processed_for_model0"))
    data, labels = zip(*[(match[0], match[1]) for match in matches])
    
    data, labels = np.array(data), np.array(labels)
    
    print(f"Data shape: {data.shape}")
    print(f"Labels shape: {labels.shape}")
    
    return train_test_split(data, labels, test_size=0.2, random_state=42)
    

def bettingAI_model0():
    input_layer = Input(shape=(42,))
    
    hidden_1 = Dense(128, activation='relu')(input_layer)
    dropout_1 = Dropout(0.2)(hidden_1)
    
    hidden_2 = Dense(64, activation='relu')(dropout_1)
    dropout_2 = Dropout(0.2)(hidden_2)
    
    hidden_3 = Dense(32, activation='relu')(dropout_2)
    
    output_layer = Dense(8, activation='softmax')(hidden_3)

    model = Model(inputs=input_layer, outputs=output_layer)
    model.summary()
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

    
if __name__ == "__main__":
    main()
