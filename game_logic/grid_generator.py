'''
grid_generator.py
This script generates a grid as well as a list of players that the user 
will be able to choose from. This script will also ensure that the game is solvable.
'''
import numpy as np
import pandas as pd
import random


#pick random entries out of txt file
def pick_random_entries(file_path, num_entries=16):
    try:
        # Read the file content
        with open(file_path, "r") as file:
            entries = file.read().splitlines()

        # Pick random entries
        random_entries = random.sample(entries, num_entries)
        return random_entries
    except Exception as e:
        return str(e)

# Example usage
file_path = "./categories.txt"  # Replace with the path to your .txt file

#ensure that we have at least two non-team categories
non_team_categories = ['World Series Winner', 'Postseason Series MVP', 'League MVP', 'Silver Slugger',
                    'Gold Glove', 'Cy Young', 'Batting Title', 'ERA Title']

def get_valid_grid():

    valid_grid = False
    while not valid_grid:
        categories = pick_random_entries(file_path)
        #if there are at least two non-team categories, continue
        if len(set(categories).intersection(non_team_categories)) >= 2:
            valid_grid = True
        else: 
            print('Invalid: Regenerating Grid')
    
    return categories


#get initial grid
categories = get_valid_grid()

#function to ensure that the game is solvable
def game_is_solvable(players, cats):
    # Read in df with complete player info
    player_info = pd.read_csv('../data_scraping/data/player_info.csv')

    # Shorten to just columns with players
    player_info_short = player_info[list(players)]
    
    # Flatten the array of values and convert to strings
    all_values = [str(value) for value in player_info_short.values.flatten()]
    
    # Check if each category appears as a substring in at least two values
    for category in cats:
        matches = [value for value in all_values if category in value]
        if len(matches) < 1:
            print(f'Category {category} failed.')

            return False  # The game is not solvable if any category fails the check
    
    print("The game is solvable!")
    return True  # All categories passed the check
        

#run solvability check until we get a solvable grid
solvable = False
attempt = 0
while not solvable:

    #pick 40 random players from .txt file
    random_players = pick_random_entries('./players.txt', 40)

    if game_is_solvable(random_players, categories):
        solvable = True
    #if false, continue and select a new player set incrementing attempts
    attempt +=1 
    
    #if we reach 100 attempts, generate new categories
    if attempt > 100:
        attempt = 0
        #get a new grid
        categories = get_valid_grid()
    

# Write players and categories to files
category_file_path = "../front-end/game_category_list.txt"
player_file_path = "../front-end/game_player_list.txt"

# Write categories to a .txt file, one per line
with open(category_file_path, "w") as cat_file:
    for category in categories:
        cat_file.write(category + "\n")

# Write random_players to a .txt file, one per line
with open(player_file_path, "w") as player_file:
    for player in random_players:
        player_file.write(player + "\n")



