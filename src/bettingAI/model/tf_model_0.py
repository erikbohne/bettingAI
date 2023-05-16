"""
Tensorflow model to predict the probability of 8 scenarios
[win, draw, loss, over 2.5, over 3.5, 4.5, 5.5, btts]
"""
from typing import Tuple
from sqlalchemy import text, and_
from bettingAI.googleCloud.initPostgreSQL import initSession

import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.models import Model

import matplotlib.pyplot as plt

# HYPERPARAMETERS
BATCH_SIZE = 32
EPOCHS = 80

def main() -> None:
    """Main function to train and evaluate the TensorFlow model for predicting probabilities of scenarios.

    Returns:
        None

    Note:
        The trained model is saved as an .h5 file in the 'models' folder.
    """
    X_train, X_test, y_train, y_test = load_data()
    model = bettingAI_model0()
    
    print(f"X_train shape: {X_train.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"y_test shape: {y_test.shape}")
    
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    model_checkpoint = ModelCheckpoint('models/best_model.h5', save_best_only=True, monitor='val_loss', mode='min')
    
    callbacks = [early_stopping, model_checkpoint]
    
    model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=1, validation_split=0.2, callbacks=callbacks)
    scores = model.evaluate(X_test, y_test, verbose=1)
    print("Test loss: ", scores[0])
    print("Test accuracy: ", scores[1])
    
    # Save the trained model as an .h5 file
    model.save('models/model4.h5')
    
def load_data() -> Tuple[np.ndarray, np.ndarray]:
    """Load the data for training and testing the TensorFlow model.
    
    Returns:
        tuple[np.ndarray, np.ndarray]: containing the training and testing data and labels as numpy arrays.
    """
    session = initSession()
    matches = session.execute(text("SELECT inputs, labels FROM processed_for_model0"))
    
    year = 2023
    exclude_league_id = 47

    query = text(f"""
        SELECT p.inputs, p.labels
        FROM processed_for_model0 p
        JOIN matches m ON p.match_id = m.id
        JOIN leagues l ON m.league_id = l.id
        WHERE NOT (l.id = :exclude_league_id AND m.date >= :start_date AND m.date < :end_date)
    """)

    matches = session.execute(query, {
        'exclude_league_id': exclude_league_id,
        'start_date': datetime(year, 1, 29),
        'end_date': datetime(year + 1, 1, 1)
    })

    data, labels = zip(*[(match[0], [match[1][0], match[1][1], match[1][2]]) for match in matches])
    
    data, labels = np.array(data), np.array(labels)
    
    print(f"Data shape: {data.shape}")
    print(f"Labels shape: {labels.shape}")

    return train_test_split(data, labels, test_size=0.2)
    
def bettingAI_model0() -> tf.keras.Model:
    """Creates and compiles a TensorFlow model for the bettingAI application.
    
    Returns:
    The compiled TensorFlow model.

    Model Architecture:
    - Input layer with shape (42,)
    - Fully connected layers with ReLU activation:
        - Dense layer with 64 units
        - Batch normalization layer
        - Dropout layer with a rate of 0.2
        - Dense layer with 32 units
        - Dropout layer with a rate of 0.2
        - Dense layer with 16 units
    - Output layer with softmax activation and 3 units

    Loss Function: Categorical Crossentropy
    Optimizer: Adam
    Metrics: Accuracy
    """
    input_layer = Input(shape=(42,))
    
    hidden_1 = Dense(64, activation='relu')(input_layer)
    batch_norm_1 = BatchNormalization()(hidden_1)
    dropout_1 = Dropout(0.2)(batch_norm_1)
    
    hidden_2 = Dense(32, activation='relu')(dropout_1)
    dropout_2 = Dropout(0.2)(hidden_2)
    
    hidden_3 = Dense(16, activation='relu')(dropout_2)
    
    output_layer = Dense(3, activation='softmax')(hidden_3)

    model = Model(inputs=input_layer, outputs=output_layer)
    model.summary()
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

    
if __name__ == "__main__":
    main()
