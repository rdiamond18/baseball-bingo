from flask import Flask, jsonify, request, render_template, send_from_directory
import pandas as pd
import os

app = Flask(__name__,
            static_folder='front-end/static',  # Correct path to static files (CSS, JS)
            template_folder='front-end/templates')  # Correct path to HTML templates

# Load categories and players
with open('./front-end/game_category_list.txt', "r") as file:
    categories = file.read().splitlines()

with open('./front-end/game_player_list.txt', "r") as file:
    players = file.read().splitlines()

# Read in full data as answer key and shorten list to just players in the game
full_info = pd.read_csv('./data_scraping/data/player_info.csv')
player_info_short = full_info[list(players)]

# Initialize scorecard and player index
scorecard = [False] * len(categories)
current_player_index = 0

# Game helper functions

#this function will be called whenever a user makes a guess
def check_player_category_pair(player, category):
    try:
        player_values = player_info_short[player]
    except:
        print(f'Error: player {player} not found')

    #handle edge case where MVP is a substring of postseason series MVP
    if category == 'Postseason Series MVP':
        if 'Postseason Series MVP' in list(player_values):
            return True
        return False
    else:
        if any(category in str(value) for value in player_values):
            return True
        return False

#this function handles wildcard input

def check_wildcard(player, all_categories):
    try:
        player_values = player_info_short[player]
    except:
        print(f'Error: player {player} not found')

    #initialize empty list of categories where player fits
    correct_category_list = []

    #check all categories
    for category in all_categories:
        if category == 'Postseason Series MVP':
            if 'Postseason Series MVP' in list(player_values):
                correct_category_list.append(category)
        else:
            if any(category in str(value) for value in player_values):
                correct_category_list.append(category)
    
    return correct_category_list

def check_category_already_correct(scorecard, index):
    if scorecard[index]:
        return True
    else: 
        return False
# Start the game
@app.route('/')
def index():
    return render_template('index.html')

# Serve game_category_list.txt
@app.route('/game_category_list.txt')
def game_category_list():
    # Correct path to send the file from the front-end directory
    return send_from_directory(os.path.join(app.root_path, 'front-end'), 'game_category_list.txt')

# Get current player and scorecard
@app.route('/game_status', methods=['GET'])
def game_status():
    global current_player_index

    # Check if all categories are correct
    if all(scorecard):
        return jsonify({
            'message': 'You win!',
            'scorecard': scorecard
        })

    # Check if the index has reached the end of players
    if current_player_index >= len(players):
        return jsonify({
            'message': 'You lose!',
            'scorecard': scorecard
        })
    
    return jsonify({
        'current_player': players[current_player_index],
        'current_player_index': current_player_index,
        'scorecard': scorecard
    })





# Update game state with user input
@app.route('/submit_input', methods=['POST'])
def submit_input():
    global current_player_index
    data = request.json

    if current_player_index >= len(players):
        return jsonify({
            'message': 'You lose!',
            'scorecard': scorecard,
            'correct_categories': [],
            'correct': False,
        })
    
    user_input = data['input']
    is_correct = False  # Default to incorrect
    correct_categories = []  # Default empty list

    if user_input == 'skip':
        current_player_index += 1
        if current_player_index >= len(players):
            return jsonify({
                'message': 'You lose!',
                'scorecard': scorecard,
                'correct_categories': [],
                'correct': False,
            })

        return jsonify({
            'message': 'Player skipped.',
            'scorecard': scorecard,
            'correct_categories': [],
            'correct': False,
            'current_player': players[current_player_index],
            'current_player_index': current_player_index,
        })

    elif user_input == 'wildcard':
        correct_categories = check_wildcard(players[current_player_index], categories)
        for category in correct_categories:
            index = categories.index(category)
            scorecard[index] = True
        current_player_index += 1

        if all(scorecard):
            return jsonify({
                'message': 'You win!',
                'scorecard': scorecard,
                'correct_categories': correct_categories,
                'correct': True,
            })

        if current_player_index >= len(players):
            return jsonify({
                'message': 'You lose!',
                'scorecard': scorecard,
                'correct_categories': correct_categories,
                'correct': True,
            })

        return jsonify({
            'message': 'Wildcard processed.',
            'scorecard': scorecard,
            'correct_categories': correct_categories,
            'correct': True,
            'current_player': players[current_player_index],
            'current_player_index': current_player_index,
        })

    elif user_input in categories:
        category_index = categories.index(user_input)

        if check_category_already_correct(scorecard, category_index):
            return jsonify({
                'message': 'Category already selected. Choose another.',
                'scorecard': scorecard,
                'correct_categories': [],
                'correct': False,
                'current_player': players[current_player_index],
                'current_player_index': current_player_index,
            })

        is_correct = check_player_category_pair(players[current_player_index], user_input)
        if is_correct:
            scorecard[category_index] = True
            current_player_index += 1
        else:
            current_player_index += 2

        if all(scorecard):
            return jsonify({
                'message': 'You win!',
                'scorecard': scorecard,
                'correct_categories': [],
                'correct': is_correct,
            })

        if current_player_index >= len(players):
            return jsonify({
                'message': 'You lose!',
                'scorecard': scorecard,
                'correct_categories': [],
                'correct': is_correct,
            })

        return jsonify({
            'message': 'Category processed.',
            'scorecard': scorecard,
            'correct_categories': [],
            'correct': is_correct,
            'current_player': players[current_player_index],
            'current_player_index': current_player_index,
        })

    # Invalid input
    return jsonify({
        'message': 'Invalid input.',
        'scorecard': scorecard,
        'correct_categories': [],
        'correct': False,
    })



if __name__ == '__main__':
    app.run(debug=True)
