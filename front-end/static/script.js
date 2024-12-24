document.addEventListener("DOMContentLoaded", () => {
    const gridContainer = document.getElementById("grid-container");
    const winContainer = document.getElementById("win-container");
    const loseContainer = document.getElementById("lose-container");

    // Fetch the categories from the game_category_list.txt file
    fetch('/game_category_list.txt')
        .then(response => response.text())
        .then(data => {
            const categories = data.split("\n").filter(line => line.trim() !== "");

            // Populate the grid with categories and make them clickable
            categories.forEach(category => {
                const gridItem = document.createElement("div");
                gridItem.classList.add('grid-box');  // Add a class for styling
    
                // Create the image element
                const imageName = category.replace(/ /g, '_').toLowerCase(); // Replace spaces with underscores
                const img = document.createElement("img");
                img.src = `/static/images/${imageName}.png`; //get path to image
                img.alt = category;
    
                // Create the text container
                const text = document.createElement("div");
                text.textContent = category;
    
                // Append image and text to the grid item
                gridItem.appendChild(img);
                gridItem.appendChild(text);

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

    // Function to send user input to the server
    function submitInput(input) {
        fetch('/submit_input', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: input })
        })
        .then(response => response.json())
        .then(data => {
            // Check if the response includes a list of correct categories (wildcard case)
            if (data.correct_categories) {
                data.correct_categories.forEach(category => {
                    handleCategoryFeedback(category, true); // Turn these boxes green
                });
            } else {
                // For regular inputs, use the single `correct` flag
                handleCategoryFeedback(input, data.correct);
            }
    
            // Update the game status with the new data
            updateGameStatus(data);
        })
        .catch(error => {
            console.error("Error submitting input:", error);
        });
    }
    

    function handleCategoryFeedback(input, isCorrect) {
        const gridItems = Array.from(document.querySelectorAll('.grid-box'));
        const element = gridItems.find(item => item.textContent === input);
        if (!element) return; // Guard against invalid input

        if (isCorrect) {
            element.classList.add('correct'); // Turn the box green if correct
        } else {
            element.classList.add('incorrect'); // Temporarily turn the box red if incorrect
            setTimeout(() => {
                element.classList.remove('incorrect'); // Reset to gray after 1 second
            }, 500);
        }
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

        // Show or hide the grid and win/lose messages
        if (data.message === 'You lose!') {
            // Hide grid and show lose message
            gridContainer.style.display = 'none';
            winContainer.style.display = 'none';
            loseContainer.style.display = 'block';
        } else if (data.message === 'You win!') {
            // Hide grid and show win message
            gridContainer.style.display = 'none';
            winContainer.style.display = 'block';
            loseContainer.style.display = 'none';
        } else {
            // Show grid and hide win/lose messages
            gridContainer.style.display = 'grid';
            winContainer.style.display = 'none';
            loseContainer.style.display = 'none';
        }

        // Update the game status elements
        playerNameElement.textContent = `Current Player: ${data.current_player}`;
        playerIndexElement.textContent = `Players Left: ${40 - data.current_player_index}`;
        scorecardElement.textContent = `Scorecard: ${data.scorecard.join(', ')}`;
    }

    // Fetch and update game status
    function fetchAndUpdateGameStatus() {
        fetch('/game_status')
            .then(response => response.json())
            .then(data => {
                updateGameStatus(data); // Call the updated function
            })
            .catch(error => console.error('Error fetching game status:', error));
    }

    // Initial fetch and periodic updates
    fetchAndUpdateGameStatus(); // Fetch once on page load
    setInterval(fetchAndUpdateGameStatus, 5000); // Poll every 5 seconds
});
