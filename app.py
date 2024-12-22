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

# Read in full data as answer key and shorten list to just players
full_info = pd.read_csv('./data_scraping/data/player_info.csv')
player_info_short = full_info[list(players)]

# Initialize scorecard and player index
scorecard = [False] * len(categories)
current_player_index = 0

# Game helper functions
def check_player_category_pair(player, category):
    try:
        player_values = player_info_short[player]
    except:
        print(f'Error: player {player} not found')

    if category == 'Postseason Series MVP':
        if 'Postseason Series MVP' in list(player_values):
            return True
        return False
    else:
        if any(category in str(value) for value in player_values):
            return True
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
    user_input = data['input']

    if user_input == 'skip':
        current_player_index += 1
    elif user_input == 'wildcard':
        current_player_index -= 1
    elif user_input in categories:
        correct = check_player_category_pair(players[current_player_index], user_input)
        if correct:
            category_index = categories.index(user_input)
            scorecard[category_index] = True
            current_player_index += 1
        else:
            current_player_index += 2

    return jsonify({
        'current_player': players[current_player_index],
        'current_player_index': current_player_index,
        'scorecard': scorecard
    })

if __name__ == '__main__':
    app.run(debug=True)
