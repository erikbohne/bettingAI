# BettingAI
> Can artificial intelligence beat Norsk Tipping?

Norsk Tipping is the sole state-owned gambling company in Norway, operating lottery, sports betting, and instant games exclusively. As a government-controlled entity, it ensures responsible gaming entertainment while maintaining a monopoly on gambling within the country.

In order to gain revenue on betting you have to beat the bookmarker. The task of the betting AI is therefor to find the best betting deals using a simple equation.

```
expected value = (revenue * probability) - bet
if expecpected value > 0:
    place bet
else:
    do not place bet
```

If you consistantly bet on outcomes that has an expected value of more than 0, you will, over time, generate a revenue. Altough the equation is simple, the task is not. Revenue is the bet times the bet, and the bet is how money you place on an outcome. The only variable in the equation BettingAI has to produce is the probability. And what is the solely most important key to predicting? **Data**

Betting AI project that includes gathering and processing data, training and tuning a model and predicting outcomes.

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Modules](#modules)
   - [Module 1 - Writer](#module-1---writer)
   - [Module 2 - Trainer](#module-2---trainer)
   - [Module 3 - Predictor](#module-3---predictor)
   - [Module 4 - Interface](#module-4---interface)
4. [Contributing](#contributing)
5. [License](#license)

## Installation

### Prerequisites
Program uses mainly Python 3.X
```
pip install requirements.txt
```

## Usage

## Modules
The project consists of **4** modules that each perform a specific tast in order to complete the BettingAI.

### Module 1 - Writer
> Extracting data from fotmob.com into a Google firebase database

In order to collect data about teams, players and matches without spending thousands of NOK on an API, crawling the web was the best option. **Fotmob.com** is one of the leading fotball statistics website and was therefor an easy choice to scrape.

The **structure of the firebase** has been changed a lot.

*TODO*

### Module 2 - Trainer
> Uses the historical data in the firebase databse to train a model

*TODO*

### Module 3 - Predictor
> Gathers information about upcoming matches and uses model to run predictions

*TODO*

### Module 4 - Interface
> Interface to get an overview over performance and bets

*TODO*

## Contributing

## License





