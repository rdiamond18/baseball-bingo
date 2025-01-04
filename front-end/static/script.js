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
        if (gameEnded) return; // Prevent further input if the game has ended
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
                    updateGrid(category, true, isWildcard = true); // Turn these boxes gold
                });
            } else {
                // For regular inputs, use the single `correct` flag
                updateGrid(input, data.correct, isWildcard = false);
            }
    
            // If game is over, display the appropriate message after updating the grid
            if (data.message === 'You win!' || data.message === 'You lose!') {
                gameEnded = true; // Set the flag
                if (data.message === 'You win!') {
                    winContainer.style.display = 'block';
                    loseContainer.style.display = 'none';
                } else {
                    winContainer.style.display = 'none';
                    loseContainer.style.display = 'block';
                }
            }
    
            // Update the game status with the new data
            updateGameStatus(data);
        })
        .catch(error => {
            console.error("Error submitting input:", error);
        });
    }
    
    

    function updateGrid(input, isCorrect, isWildcard) {
        const gridItems = Array.from(document.querySelectorAll('.grid-box'));
        const element = gridItems.find(item => item.textContent === input);
        if (!element) return; // Guard against invalid input

        //turn boxes gold if wildcard is selected (only if box is not already green)
        if (isWildcard) {
            if (!element.classList.contains('correct')) {
                element.classList.add('wildcard'); 
            }
        }    
        else if (isCorrect) {
            element.classList.add('correct'); // Turn the box green if correct
        } 
        else {
            element.classList.add('incorrect'); // Temporarily turn the box red if incorrect
            setTimeout(() => {
                element.classList.remove('incorrect'); // Reset to gray after 1 second
            }, 500);
        }
    }

    // Event listeners for Skip and Wildcard buttons
    const skipButton = document.querySelector('button.skip');
    const wildcardButton = document.querySelector('button.wildcard'); // Selects the wildcard button

    skipButton.addEventListener('click', () => {
        submitInput('skip');
    });

    wildcardButton.addEventListener('click', () => {
        submitInput('wildcard');
    });

    // Instructions section: Add event listener for instructions
    const instructionsButton = document.getElementById('instructions-button');
    const instructionsModal = document.getElementById('instructions-modal');
    const closeModal = document.getElementById('close-modal');
    const instructionsText = document.getElementById('instructions-text');

    // Open modal and fetch instructions
    instructionsButton.addEventListener('click', () => {
        fetch('../static/instructions.txt') // Path to your .txt file
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load instructions.');
                }
                return response.text();
            })
            .then(data => {
                // Split the text into sentences and join them with <br> tags
                const formattedText = data
                    .split(/(?<=[.!?])\s+/) // Split by sentence-ending punctuation followed by a space
                    .join('<br><br>'); // Add two line breaks for spacing
    
                instructionsText.innerHTML = formattedText; // Use innerHTML to include <br> tags
                instructionsModal.style.display = 'flex'; // Show modal
            })
            .catch(error => {
                instructionsText.textContent = 'Error loading instructions. Please try again later.';
                instructionsModal.style.display = 'flex'; // Show modal
            });
    });
    // Close modal
    closeModal.addEventListener('click', () => {
        instructionsModal.style.display = 'none'; // Hide modal
    });

    // Close modal when clicking outside modal content
    instructionsModal.addEventListener('click', (event) => {
        if (event.target === instructionsModal) {
            instructionsModal.style.display = 'none';
        }
    });


    let gameEnded = false; // Flag to track game end state
    let pollingInterval = setInterval(fetchAndUpdateGameStatus, 2000);

    // Function to update the game status
    function updateGameStatus(data) {
        const playerNameElement = document.getElementById('current-player-name');
        const playerIndexElement = document.getElementById('current-player-index');
        const scorecardElement = document.getElementById('scorecard');

        if (gameEnded) {
            gridContainer.style.display = 'grid';
            clearInterval(pollingInterval)
            return; // Do nothing if the game has ended
        }
        // Show or hide the grid and win/lose messages
        if (data.message === 'You Win!') {
            winContainer.style.display = 'block';
            loseContainer.style.display = 'none';
            gameEnded = true;
        } else if (data.message === 'You Lose!') {
            winContainer.style.display = 'none';
            loseContainer.style.display = 'block';
            gameEnded = true;
        } else {
            // Show grid and hide win/lose messages
            gridContainer.style.display = 'grid';
            winContainer.style.display = 'none';
            loseContainer.style.display = 'none';
        }

        // Update the game status elements
        playerNameElement.textContent = `Current Player: ${data.current_player}`;
        playerIndexElement.textContent = `Players Left: ${40 - data.current_player_index}`;
    }

    // Fetch and update game status
    function fetchAndUpdateGameStatus() {
        if (gameEnded) return;
        fetch('/game_status')
            .then(response => response.json())
            .then(data => {
                if (data.message === 'You win!' || data.message === 'You lose!') {
                    gameEnded = true;
                    clearInterval(pollingInterval);
                    return;
                }
                updateGameStatus(data);
            })
            .catch(console.error);
    }
    

    // Initial fetch and periodic updates
    fetchAndUpdateGameStatus(); // Fetch once on page load
    setInterval(pollingInterval); // Poll every 2 seconds
});
