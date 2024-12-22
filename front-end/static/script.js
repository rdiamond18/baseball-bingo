document.addEventListener("DOMContentLoaded", () => {
    const gridContainer = document.getElementById("grid-container");

    // Fetch the categories from the game_category_list.txt file
    fetch('/game_category_list.txt')
        .then(response => response.text())
        .then(data => {
            const categories = data.split("\n").filter(line => line.trim() !== "");

            // Populate the grid with categories and make them clickable
            categories.forEach(category => {
                const gridItem = document.createElement("div");
                gridItem.classList.add('grid-box');  // Add a class for styling
                gridItem.textContent = category;

                // Add click event listener to the grid item
                gridItem.addEventListener('click', () => {
                    submitInput(category);  // Submit the category as input when clicked
                });

                gridContainer.appendChild(gridItem);
            });
        })
        .catch(error => {
            console.error("Error loading categories:", error);
        });

    // Get current game status on page load
    fetch('/game_status')
        .then(response => response.json())
        .then(data => {
            updateGameStatus(data);
        });

    // Function to send user input to the server
    function submitInput(input) {
        fetch('/submit_input', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: input })
        })
        .then(response => response.json())
        .then(data => {
            updateGameStatus(data);
        });
    }
    
    // Event listeners for Skip and Wildcard buttons
    const skipButton = document.getElementById('skip-button');
    const wildcardButton = document.getElementById('wildcard-button');

    skipButton.addEventListener('click', () => {
        submitInput('skip');
    });

    wildcardButton.addEventListener('click', () => {
        submitInput('wildcard');
    });

    // Function to update the game status
    function updateGameStatus(data) {
        const playerNameElement = document.getElementById('current-player-name');
        const playerIndexElement = document.getElementById('current-player-index');
        const scorecardElement = document.getElementById('scorecard');

        playerNameElement.textContent = `Current Player: ${data.current_player}`;
        playerIndexElement.textContent = `Players Left: ${40 - data.current_player_index}`;
        scorecardElement.textContent = `Scorecard: ${data.scorecard.join(', ')}`;
    }
});
