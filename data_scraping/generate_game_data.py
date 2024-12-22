'''
generate_game_data.py
This file stacks the team and achievement dataframes together, giving 
us a complete dataset for each round of bingo.
'''
import pandas as pd

#load in dataframes
batter_teams = pd.read_csv('./data/batter_teams.csv')
pitcher_teams = pd.read_csv('./data/pitcher_teams.csv')
batter_achievements = pd.read_csv('./data/batter_achievements.csv')
pitcher_achievements = pd.read_csv('./data/pitcher_achievements.csv')

#get players dataframe, which horizontally stacks the teams dfs
players = pd.concat([batter_teams, pitcher_teams], axis=1)

#drop duplicate columns
players = players.loc[:, ~players.columns.duplicated()]

for player in players.columns:
        
    # Convert both columns into lists
    team_list = players[player].tolist()

    #get player achievement list
    if player in pitcher_achievements.columns:
        achievement_list = pitcher_achievements[player].tolist()
    elif player in batter_achievements.columns:
        achievement_list = batter_achievements[player].tolist()
    else:
        achievement_list = []



    # Combine the lists and drop na values
    combined_list = team_list + achievement_list
    cleaned_list = [item for item in combined_list if pd.notna(item)]
    
    # Convert the combined list back into a DataFrame
    players[player] = pd.Series(cleaned_list)


#dump dataframe into csv
players.to_csv('./data/player_info.csv')