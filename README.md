# BettingAI 🧠
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/facebook/react/blob/main/LICENSE) ![](https://img.shields.io/github/languages/top/erikbohne/bettingAI?color=purple) ![](https://img.shields.io/github/repo-size/erikbohne/bettingAI?color=gre) ![](https://img.shields.io/github/commit-activity/m/erikbohne/bettingAI?color=ff69b4) <!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
> Can artificial intelligence beat the bookies?

Bookmakers worldwide, including state-owned entities, contribute to the thriving, billion-dollar betting industry. They offer services like lottery and sports betting, while promoting responsible gaming. To profit from this industry, bettors must outsmart bookmakers, using AI systems to find the most favorable deals and beat the odds.

```python
expected value = (bookmaker odds / real odds) - 1
if expecpected value > 0:
    place bet
else:
    do not place bet
```

Consistently betting on outcomes with a positive expected value will, over time, yield revenue. While the concept is simple, execution is more challenging. Revenue equals the bet amount squared, with the bet being the money placed on an outcome. The only variable Betting AI needs to determine is probability, which relies heavily on the most crucial element for accurate predictions: **Data**.

The Betting AI project involves collecting and processing data, training and fine-tuning a model, and predicting outcomes to help bettors make informed decisions.

## Table of Contents 📚
- **[Prerequisites 🤓](#Prerequisites)**
- **[Usage](#usage)**
- **[Modules ⚙️](#modules)**
  - **[Module 1 - Writer ✍🏽](#module-1---writer)**
  - **[Module 2 - Processing 📊](#module-3---processing)**
  - **[Module 3 - Model 🤖](#module-2---model)**
  - **[Module 4 - Prediction 🔮](#module-4---prediction)**
  - **[Module 5 - API 🔗](#module-4---API)**
- **[Contributing 🙋‍♂️](#contributing)**
- **[License 🪪](#license)**

## Prerequisites 🤓
In order to install the required packages make sure to start the virtual environment:
```bash
source venv/bin/activate
```
And the install the required packages:
```bash
pip install -r requirements.txt
```
This will install all the necesarry packages for all modules in BettingAI.

## Modules ⚙️
The project consists of **4** modules that each perform a specific tast in order to complete the BettingAI.

### Module 1 - Writer ✍🏽
> Extracting data from fotmob.com into a PostgreSQL database using Google Cloud.

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

```python
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

### Module 2 - Processing 📊
> Transforming raw data into processed input for model training.

This program is designed to process raw match data from the database and prepare it for use in `model0`. It first initializes a connection to the database using `initSession()`, then fetches both raw and already processed match IDs. After calculating the difference between these two sets, the program identifies the matches that need to be processed.

For each match, the program generates features and labels using the `features_for_model0()` and `labels()` functions, respectively. It then creates two instances of the Processed class, one for each team, and commits the processed data to the database. If an exception occurs during the commit process, the program rolls back the transaction and prints an error message.

#### POTENTIAL IMPROVEMENTS 📈: 
1. Efficiency - bring processing time down
2. Extract more features

### Module 3 - Model 🤖
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

### Module 4 - Prediction 🔮
> Interface to get an overview over performance and bets

*TODO*

### Module 5 - API 🔗
> Module to connect frontend and backend

This program serves as an API that connects the backend with the frontend, providing an overview of performance and bets in the betting system. It utilizes FastAPI to handle API requests and includes three endpoints: `/matches`, `/performance`, and `/stats`.

- `/matches`: Returns a list of matches with their details, including date and time, team names, odds, and betting values.
- `/performance`: Retrieves model performance data from the database and calculates the profit for each model, returning the formatted data as JSON.
- `/stats`: Calculates various statistics, such as money won, bets won, winrate, and bets placed, and compares them to previous and goal values, returning the formatted data as JSON.

The API also handles CORS (Cross-Origin Resource Sharing) to ensure compatibility with frontend applications hosted on different domains.

## Contributing 🙋‍♂️
> Pull requests are welcome

## License 🪪 • ![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Ahmed-Z-D"><img src="https://avatars.githubusercontent.com/u/78611096?v=4?s=100" width="100px;" alt="Ahmed Z-D"/><br /><sub><b>Ahmed Z-D</b></sub></a><br /><a href="#infra-Ahmed-Z-D" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!







