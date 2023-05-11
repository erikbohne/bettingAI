# BettingAI 🧠
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/facebook/react/blob/main/LICENSE) ![](https://img.shields.io/github/languages/top/erikbohne/bettingAI?color=purple) ![](https://img.shields.io/github/repo-size/erikbohne/bettingAI?color=gre) ![](https://img.shields.io/github/commit-activity/m/erikbohne/bettingAI?color=ff69b4) <!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
> "Can artificial intelligence beat the bookies?"

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
> "Extracting data from fotmob.com into a PostgreSQL database using Google Cloud."

The writer.py program is responsible for extracting and storing football data 📊 into a PostgreSQL database ⚙️. The program performs the following tasks:

1. Connects to the PostgreSQL database 🔗.
2. For each league ⚽:
    - Fetches team 🏃‍♂️ and player information 👤.
    - Updates the database 🛠 with team and player data.
    - Retrieves match information 🥅 for each season and stores it in the database.
    - Gathers player performance statistics 📈 for each match and updates the database.

### Module 2 - Processing 📊
> "Transforming raw data into processed input for model training."

This program is designed to process raw match data from the database and prepare it for use in `model0`. It first initializes a connection to the database using `initSession()`, then fetches both raw and already processed match IDs. After calculating the difference between these two sets, the program identifies the matches that need to be processed.

For each match, the program generates features and labels using the `features_for_model0()` and `labels()` functions, respectively. It then creates two instances of the Processed class, one for each team, and commits the processed data to the database. If an exception occurs during the commit process, the program rolls back the transaction and prints an error message.

#### POTENTIAL IMPROVEMENTS 📈: 
1. Efficiency - bring processing time down
2. Extract more features

### Module 3 - Model 🤖
> "Constructing, training, and evaluating the neural network for predicting football match outcomes 🧠⚽️"

In Module 3, we dive deep into the world of artificial intelligence, building a neural network to predict the outcomes of football matches with precision! 🎯🔮

Here's what we do step by step 🔑:

1. Load the data and split it into training and testing sets, ensuring we have a separate dataset for model evaluation 📚🔪
Normalize the data using StandardScaler, which helps the model learn faster and perform better 📏✨
2. Design a neural network model using Keras, complete with hidden layers, Batch Normalization, and Dropout to prevent overfitting and enhance generalization 🧩🚀
3. Train the model using K-Fold Cross Validation, a technique that splits the data into multiple folds, ensuring more reliable model performance 🔄💪
4. Evaluate the model on the test data and report loss and accuracy scores to understand how well it generalizes to unseen data 📈🎉
5. Discover feature importance using permutation importance analysis, helping us understand which features have the most 6. significant impact on predictions 🌟🔍
6. Save the trained model as an .h5 file, enabling us to use it in the future without retraining 🔐💾

Leveraging TensorFlow and Keras, Module 3 creates a deep learning model that learns from historical match data and identifies the most crucial features for accurate predictions. Get ready to revolutionize the world of football predictions with AI! 🚀🌐


### Module 4 - Prediction 🔮
> Interface to get an overview over performance and bets

⚽ Module 4 works tirelessly, updating the data every 24 hours. It fetches upcoming matches within the next 5 days 📆 and grabs live odds for all leagues 🌐.

Key steps 🔑:

1. Find matches in the next 5 days 🗓️
2. Get live odds for each league 🎲
3. Update the `Upcoming` table with fresh match data 🔄
4. Refresh the `Bets` table with new bet recommendations, odds, and strengths 📊
5. Use the imported model to calculate advice and strength for each match 🧠

With the help of **TensorFlow Keras**, our trusty model 🧙, and some handy helper functions, Module 4 makes sure you never miss an opportunity in the world of betting. 🎯

### Module 5 - API 🔗
> Module to connect frontend and backend

This program serves as an API that connects the backend with the frontend, providing an overview of performance and bets in the betting system. It utilizes FastAPI to handle API requests and includes three endpoints: `/matches`, `/performance`, and `/stats`.

- `/matches`: Returns a list of matches with their details, including date and time, team names, odds, and betting values.
- `/performance`: Retrieves model performance data from the database and calculates the profit for each model, returning the formatted data as JSON.
- `/stats`: Calculates various statistics, such as money won, bets won, winrate, and bets placed, and compares them to previous and goal values, returning the formatted data as JSON.

The API also handles CORS (Cross-Origin Resource Sharing) to ensure compatibility with frontend applications hosted on different domains.

## Contributing 🙋‍♂️
> Pull requests are welcome

We appreciate your interest in contributing! Please follow best practices and refer to the contribution template when submitting a pull request. Focus on improving the model's efficiency and check the 'Issues' tab for potential improvements. For questions, comment on the issues, and we'll respond promptly.

## License 🪪 • ![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
This project is licensed under the MIT License. This permissive license allows for reuse, modification, and distribution of the code, as long as the copyright notice and license text are included. The MIT License grants you the freedom to use the project in your own work, as well as contribute to its development and enhancement. Please review the [LICENSE](LICENSE) file for more details.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
        <td align="center" valign="top" width="14.28%"><a href="https://github.com/erikbohne"><img src="https://avatars.githubusercontent.com/u/79271528?v=4?s=100" width="100px;" alt="Erik Nymo Bohne"/><br /><sub><b>Erik Nymo Bohne</b></sub></a><br /><a href="https://github.com/erikbohne/bettingAI/commits?author=erikbohne" title="Code">💻</a> <a href="#data-erikbohne" title="Data">🔣</a> <a href="#ideas-erikbohne" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/erikbohne/bettingAI/commits?author=erikbohne" title="Documentation">📖</a> <a href="#research-erikbohne" title="Research">🔬</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Ahmed-Z-D"><img src="https://avatars.githubusercontent.com/u/78611096?v=4?s=100" width="100px;" alt="Ahmed Z-D"/><br /><sub><b>Ahmed Z-D</b></sub></a><br /><a href="#infra-Ahmed-Z-D" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!







