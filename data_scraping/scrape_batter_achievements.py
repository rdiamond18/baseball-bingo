'''
scrape_batter_achievements.py
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
from selenium.common.exceptions import TimeoutException


#initialize dictionary with player names and their corresponding achievements
player_achievement_dict = {}

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

for player_name, player_href in links:
    print(f"Processing player: {player_name}, Link: {player_href}")
    sleep(2)
    
    try:
        # Navigate to the player's page
        driver.get(player_href)
        
        # Wait for the element with id="bling" to appear
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="bling"]')))
        
        # Find all child elements under the "bling" element
        bling_children = driver.find_elements(By.XPATH, '//*[@id="bling"]/*')
        
        # Extract text from all child elements
        achievements = [child.text for child in bling_children if child.text.strip()]  # Filter out empty text
        
        # Add the list of achievements to the dictionary for the player
        player_achievement_dict[player_name] = achievements
        print(f'Player name {player_name}, achievements {achievements}')
        
    except TimeoutException:
        print(f"Timeout while processing {player_name}. Retrying...")
        sleep(5)  # Short delay before retrying
        continue  # Skip to the next iteration

    except Exception as e:
        print(f"Error processing {player_name}: {e}")
        # Sleep for 2 seconds to avoid exceeding limits
        sleep(2)

    

# Quit the WebDriver
driver.quit()

# Convert the dictionary to a DataFrame
df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in player_achievement_dict.items()]))

# Save to CSV
df.to_csv("./data/batter_achievements.csv", index=False)

print("Finished scraping!")
