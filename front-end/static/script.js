document.addEventListener("DOMContentLoaded", () => {
    const gridContainer = document.getElementById("grid-container");

    // Fetch the categories from the game_category_list.txt file
    fetch('/game_category_list.txt')
        .then(response => response.text())
        .then(data => {
            const categories = data.split("\n").filter(line => line.trim() !== "");

            // Populate the grid with categories
            categories.forEach(category => {
                const gridItem = document.createElement("div");
                gridItem.textContent = category;
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

    // Update game status dynamically based on user input
    const userInputForm = document.getElementById('user-input-form');
    userInputForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const userInput = event.target.elements['user-input'].value;

        fetch('/submit_input', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: userInput })
        })
        .then(response => response.json())
        .then(data => {
            updateGameStatus(data);
        });
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
