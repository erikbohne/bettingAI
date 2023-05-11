"""
Test program with the goal of retrieving odds information about matches
"""

from bettingAI.writer.scraper import tokenize_page


def main():
    
    tokenized = tokenize_page("https://www.bet365.com/#/AC/B1/C1/D1002/E76169570/G40/H^1/")
    print(tokenized)
    print(len(tokenized))
    
    
    
if __name__ == "__main__":
    main()