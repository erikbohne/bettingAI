import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.inspection import permutation_importance

from sqlalchemy import text, and_
from bettingAI.googleCloud.initPostgreSQL import initSession
from bettingAI.googleCloud.databaseClasses import Processed, Matches, Leagues

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.models import Model
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier

import matplotlib.pyplot as plt

# HYPERPARAMETERS
BATCH_SIZE = 32
EPOCHS = 80
N_SPLITS = 5

def main():
    X_train, X_test, y_train, y_test = load_data()
    X_train, X_test = normalize_data(X_train, X_test)

    # K-Fold Cross Validation
    kf = KFold(n_splits=N_SPLITS, shuffle=True, random_state=42)
    val_loss = []
    val_accuracy = []

    for train_index, val_index in kf.split(X_train):
        X_train_kf, X_val_kf = X_train[train_index], X_train[val_index]
        y_train_kf, y_val_kf = y_train[train_index], y_train[val_index]

        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        model_checkpoint = ModelCheckpoint('models/best_model.h5', save_best_only=True, monitor='val_loss', mode='min')

        callbacks = [early_stopping, model_checkpoint]

        wrapped_model = KerasClassifier(build_fn=bettingAI_model0)
        wrapped_model.fit(X_train_kf, y_train_kf, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=1, validation_data=(X_val_kf, y_val_kf), callbacks=callbacks)
        scores = wrapped_model.model.evaluate(X_val_kf, y_val_kf, verbose=1)
        val_loss.append(scores[0])
        val_accuracy.append(scores[1])

    print(f"Average validation loss: {np.mean(val_loss)}")
    print(f"Average validation accuracy: {np.mean(val_accuracy)}")

    wrapped_model.model.load_weights('models/best_model.h5')
    scores = wrapped_model.model.evaluate(X_test, y_test, verbose=1)
    print("Test loss: ", scores[0])
    print("Test accuracy: ", scores[1])

    # Feature Importance
    feature_importance(wrapped_model, X_test, y_test)

    # Save the trained model as an .h5 file
    wrapped_model.model.save('models/test.h5')

def load_data():
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

def normalize_data(X_train, X_test):
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    return X_train, X_test

def bettingAI_model0():
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

def feature_importance(wrapped_model, X_test, y_test):
    y_test_class_indices = np.argmax(y_test, axis=1)
    result = permutation_importance(wrapped_model, X_test, y_test_class_indices, scoring='accuracy', n_repeats=10, random_state=42, n_jobs=1)
    sorted_idx = result.importances_mean.argsort()

    plt.figure(figsize=(12, 6))
    plt.barh(range(X_test.shape[1]), result.importances_mean[sorted_idx])
    plt.yticks(range(X_test.shape[1]), sorted_idx)
    plt.xlabel('Permutation Importance')
    plt.show()
    
if __name__ == "__main__":
    main()