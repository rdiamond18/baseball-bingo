'''
scrape_batter_data.py
The purpose of this file is to gather data on all the teams each of the top 100 active
batters played for to generate an answer dictionary for baseball bingo.
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from time import sleep
import re

#define list of mlb teams
mlb_teams = [
    "Braves", "Marlins", "Mets", "Phillies", "Nationals",
    "Cubs", "Reds", "Brewers", "Pirates", "Cardinals",
    "Diamondbacks", "Rockies", "Dodgers", "Padres", "Giants",
    "Mariners", "Rangers", "Astros", "Athletics", "Angels",
    "Royals", "Tigers", "Twins", "White Sox", "Indians",
    "Red Sox", "Yankees", "Blue Jays", "Rays", "Orioles"
]

#initialize dictionary with player names and their corresponding teams
player_team_dict = {}

# Initialize the WebDriver
driver = webdriver.Chrome()  # Make sure to have the right WebDriver installed

# Open the webpage
url = "https://www.baseball-reference.com/leaders/WAR_bat_active.shtml"
driver.get(url)

# Wait and grab all players from the table
wait = WebDriverWait(driver, 10)

# Function to scroll the page
def scroll_page():
    driver.execute_script("window.scrollBy(0, 500);")  # Scroll down by 500 pixels
    sleep(2)  # Allow time for content to load

# Scroll down the page once to load the player list
scroll_page()

# Wait for the table to be loaded and then find player links
table = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='all_leader_standard_WAR_bat']")))

# Find all player links in the "Player (yrs, age)" column (which is the second column in the table)
player_list = table.find_elements(By.XPATH, "//*[@id='leader_standard_WAR_bat']/tbody/tr/td[2]//a")

links = []

# Extract and store hyperlinks
for player in player_list:
    player_name = player.text
    player_href = player.get_attribute("href")  # Get the href attribute
    links.append((player_name, player_href))  # Store name and link
    print(f"Found player: {player_name}, Link: {player_href}")

# Iterate through player names and links and get list of teams
for player_name, player_href in links:
    print(f"Processing player: {player_name}, Link: {player_href}")
    sleep(2)
    
    try:
        # Navigate to the player's page
        driver.get(player_href)
        
        # Wait for the <h3> tag with the specific text to appear
        wait.until(EC.presence_of_element_located((By.XPATH, f"//h3[contains(text(), 'How many teams has {player_name} played for?')]")))
        
        # Find the <h3> tag that contains the question
        h3_tag = driver.find_element(By.XPATH, f"//h3[contains(text(), 'How many teams has {player_name} played for?')]")
        
        # Extract the number of teams from the text
        next_sibling = h3_tag.find_element(By.XPATH, "following-sibling::p")
        teams_text = next_sibling.text

        # Add the player and their teams to the dictionary
        player_team_dict[player_name] = []
        for team in mlb_teams:
            if team in teams_text:
                player_team_dict[player_name].append(team)  # Add team to the player's list
        
    except Exception as e:
        print(f"Error processing {player_name}: {e}")
        # Sleep for 2 seconds to avoid exceeding the 30 pages per minute limit
    

# Quit the WebDriver
driver.quit()

# Convert the dictionary to a DataFrame
df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in player_team_dict.items()]))

# Save to CSV
df.to_csv("./data/batter_teams.csv", index=False)

print("Finished scraping!")
