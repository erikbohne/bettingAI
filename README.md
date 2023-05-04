# BettingAI
> Can artificial intelligence beat Norsk Tipping?

Norsk Tipping is the sole state-owned gambling company in Norway, operating lottery, sports betting, and instant games exclusively. As a government-controlled entity, it ensures responsible gaming entertainment while maintaining a monopoly on gambling within the country.

In order to gain revenue on betting you have to beat the bookmarker. The task of the betting AI is therefor to find the best betting deals using a simple equation.

```
expected value = (odds / real odds) - 1
if expecpected value > 0:
    place bet
else:
    do not place bet
```

If you consistantly bet on outcomes that has an expected value of more than 0, you will, over time, generate a revenue. Altough the equation is simple, the task is not. Revenue is the bet times the bet, and the bet is how money you place on an outcome. The only variable in the equation BettingAI has to produce is the probability. And what is the solely most important key to predicting? **Data**

Betting AI project that includes gathering and processing data, training and tuning a model and predicting outcomes.

## Table of Contents
- **[Installation](#installation)**
- **[Usage](#usage)**
- **[Modules](#modules)**
  - **[Module 1 - Writer](#module-1---writer)**
  - **[Module 2 - Trainer](#module-2---trainer)**
  - **[Module 3 - Predictor](#module-3---predictor)**
  - **[Module 4 - Interface](#module-4---interface)**
- **[Contributing](#contributing)**
- **[License](#license)**

## Installation

### Prerequisites
Program uses mainly Python 3.X, for each of the modules you will find a **requirements.txt**. Run the following command in each modules to install the neccesary libraries: 
```
pip install {module}/requirements.txt
```

This will install all the necesarry packages for all modules in BettingAI


## Usage
To get the full expirience of the Betting AI you are ment to use the **4** modules, in the correct order. Check out each module to see what they do, how they work and how they are ment to be used.

## Modules
The project consists of **4** modules that each perform a specific tast in order to complete the BettingAI.

### Module 1 - Writer
> Extracting data from fotmob.com into a PostgreSQL databse using Google Cloud.

In order to collect data about teams, players and matches without spending thousands of NOK on an API, crawling the web was the best option. **fotmob.com** is one of the leading fotball statistics website and was therefor a solid choice.

The writer module consists of the following directories, main- and helper files:
```
# directories
reports/ # dir that stores reports
logs/ # dir that stores logs

# main files
writer.py # main file that runs the module
scraper.py # request and control scraping
gather.py # scrapes a promted page

# helper files
databaseClasses.py # contains classes for database
addRow.py # assigns values to a database class
testFunctions.py # test all functions in writer.py, scraper.py and gather.py
values.py # stores some values used in scraper.py
```

To run the module you only have to run writer.py and the main functionalities of the program will work itself through all the leagues like this:

```
fetch all leagues from db

for each league:

    get a list of all the teams
    find all matches and players for that team

    for each match that is not in the db:
        add statistics to db

    for each player that is not up to date:
        update player information
```

Each step that includes getting statistics or links utilizes scraper.py to find this information on fotmob.com in a cooperation between writer, scraper and gather.

```
writer.py -> scraper.py -> gather.py
```


### Module 2 - Trainer
> Uses the historical data in the firebase databse to train a model

There are some important steps before actually creating the model. Those include data processing and feature engineering. First of all, i want to be sure that the data i am going to use is complete and correct. This means that any missing values or duplicate entries must be removed. Furthermore we want to extract certain features based on the data. We have to both identify the features we already have present as well as creating new features based on the data that could be more informative to the model.

The input values are prepared through the processing and feature engineering. And after this process the input will look like this:
```
Statistics:
    - Average goals scored per match (total/home/away) ✅
    - Average goals conceded per match (total/home/away) ✅
    - Goal difference per match (total/home/away) ✅
    - Total wins, draws, and losses (total/home/away) ✅
    - Clean sheet percentage (total/home/away) ✅
    - Matches with more than 2.5 goals score (total/home/away)

Player info:
    - MVP score (based on importancy ranking)
    - Average player rating ✅
    - Average player age ✅
    - Average player height ✅
    - Average player market value ✅

Recent form:
    - Points won ratio in last 3, 5 and 10 matches ✅
    - Current winning/losing streak ✅
    - Home/away form ✅
    - Average goals scored in last 3, 5, and 10 matches
    - Average goals conceded in last 3, 5, and 10 matches
    - Both teams to score (BTTS) percentage in last 3, 5, and 10 matches
    - Clean sheet percentage in last 3, 5, and 10 matches
    - Over/Under 2.5 goals percentage in last 3, 5, and 10 matches
    - Form against top/bottom half teams in the league
    - Points won against direct competitors (teams with similar league positions)
    - Win percentage with/without key players in recent matches
    - Scoring patterns (e.g., early/late goals, comebacks, goals after conceding)
    - Average cards (yellow and red) in last 3, 5, and 10 matches
    - Average fouls in last 3, 5, and 10 matches
    - Average corners in last 3, 5, and 10 matches
    - Set piece goals scored (free kicks, corners, penalties) in last 3, 5, and 10 matches

Head 2 Head:
    - Outcome distribution (W%, D%, L%) ✅
    - Side distribution (H%, D%, A%) ✅
    - Most recent encounters (Last 2 years) ✅
    - Average goals per match ✅
    - Average goals conceded per match ✅
    - Goal difference per match ✅
    - Both teams to score (BTTS) percentage ✅
    - Clean sheet percentage for each team ✅
    - Over/Under 2.5 goals percentage ✅
    - Winning/losing streak in head-to-head matches ✅

Playstyle:
    - 
```


*TODO*

### Module 3 - Predictor
> Gathers information about upcoming matches and uses model to run predictions

*TODO*

### Module 4 - Interface
> Interface to get an overview over performance and bets

*TODO*

## Contributing

## License





