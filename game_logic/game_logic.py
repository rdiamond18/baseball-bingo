'''
game_logic.py
This script contains the main while loop that controls
the game logic. It takes in a grid and a list of players from the game generator
script, and then accepts user input to control the flow of the game'''

import pandas as pd

#read player and category from current directory
with open('./game_category_list.txt', "r") as file:
    categories = file.read().splitlines()

with open('./game_player_list.txt', "r") as file:
    players = file.read().splitlines()

#read in full data as answer key and shorten lust to just players
full_info = pd.read_csv('../data_scraping/data/player_info.csv')
player_info_short = full_info[list(players)]

'''GAME HELPER FUNCTIONS'''
def check_player_category_pair(player, category):
    #get all categories player belongs to
    try:
        player_values = player_info_short[player]
    except:
        print(f'Error: player {player} not found')

    #special edge case for if the category is series mvp as it overlaps with mvp
    if category == 'Postseason Series MVP':
        if 'Postseason Series MVP' in list(player_values):
            return True
        return False
    else:
        if any(category in str(value) for value in player_values):
            return True
        return False


# '''MAIN GAME LOOP'''

current_player_index = 0
#display categories
print(categories)

#create underlying list holding whether or not each category was completed
scorecard = [False] * len(categories)

while current_player_index <= 40:

    #print the current player to be selected
    print(players[current_player_index])

    #get user input
    user_input = input()
    print(f'You selected: {user_input}')
    
    #check for input
    if (user_input not in categories) and (user_input != 'skip') and (user_input != 'wildcard'):
        print(f'{input}: Invalid input! Exiting!')
        break
    
    #process input
    if user_input == 'skip':
        current_player_index += 1
        print(f'You are on player {current_player_index}')

    elif user_input == 'wildcard':
        current_player_index +- 1
    else:
        correct = check_player_category_pair(players[current_player_index], user_input)
        
        # process correct input
        if correct:
            category_index = categories.index(user_input)
            scorecard[category_index] = True
            current_player_index += 1

            print('Correct!')
            print(f'Current scorecard: {scorecard}')
            print(f'You are on player {current_player_index}')
        #process incorrect input
        else:
            #skip one player
            current_player_index += 2
            print('incorrect!')
            print(f'Current scorecard: {scorecard}')
            print(f'You are on player {current_player_index}')
    
    #check if you win or lose
    if scorecard == [True] * 16:
        print('YOU WIN!')
        break
    elif current_player_index == 41:
        print('You lose.')






    
    