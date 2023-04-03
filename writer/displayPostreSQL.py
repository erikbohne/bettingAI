import pandas as pd
import sys
import os
from sqlalchemy import create_engine, text
from writer import initPostgreSQL
from colorama import Fore

def display_table_schema(table_name):
    query = text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table_name}'")
    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection)
        print(f"Data for {table_name}:")
        print(df)


def display_table_data(table_name):
    query = text(f"SELECT * FROM {table_name}")
    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection)
        print(f"Data for {table_name}:")
        print(df)

table_names = ['leagues', 'teams', 'players', 'playerstats', 'matches', 'matchstats']

# Establish connection to the database
engine = initPostgreSQL()
if engine is None:
    sys.exit(Fore.RED + "-> Could not connect to PostgreSQL")
else:
    print(Fore.GREEN + "-> Connected to PostgreSQL")

for table_name in table_names:
    display_table_schema(table_name)
    display_table_data(table_name)
    print("\n")