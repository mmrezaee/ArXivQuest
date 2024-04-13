function loadContent() {
    var url = 'https://arxiv.org/html/2404.05567v1';  // Hard-coded URL
    var questionBox = document.getElementById('question-box');
    var answersContainer = document.getElementById('answers-container');  // Get the answers container

    if (!questionBox) {
        console.error("Question box element is not found!");
        return;
    }

    var question = questionBox.value;

    fetch('/fetch_content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({url: url, question: question})
    })
    .then(response => response.json())
    .then(data => {
        var iframe = document.getElementById('content-frame');
        iframe.srcdoc = data.content;
        console.log("Content loaded successfully.");

        // Wait for iframe to load then initialize highlights
        iframe.onload = () => initializeHighlights(iframe);

        // Update answers container with selected answers
        if (data.answers && data.answers.length > 0) {
            answersContainer.innerHTML = '';  // Clear previous answers
            data.answers.forEach(answer => {
                var answerElement = document.createElement('div');
                answerElement.textContent = answer;
                answersContainer.appendChild(answerElement);
            });
        } else {
            answersContainer.innerHTML = 'No answers found';  // Display no answers message
        }
    })
    .catch(error => {
        console.error('Error loading content:', error);
        alert('Failed to load content');
    });
}
let currentHighlight = 0; // Index of the current highlighted element
let highlights = []; // Array to store references to highlighted elements

function navigateHighlight(direction) {
    if (highlights.length === 0) {
        alert("No highlights found!");
        return;
    }
    // Move the index forward or backward
    currentHighlight += direction;

    // Loop around if the index goes out of bounds
    if (currentHighlight >= highlights.length) {
        currentHighlight = 0;
    } else if (currentHighlight < 0) {
        currentHighlight = highlights.length - 1;
    }

    // Scroll the highlighted element into view
    highlights[currentHighlight].scrollIntoView({behavior: "smooth", block: "center"});
}

// Initialization function to find all highlighted elements
function initializeHighlights(iframe) {
    highlights = Array.from(iframe.contentWindow.document.querySelectorAll('span[style*="background-color: yellow;"]'));
    currentHighlight = 0; // Reset index to start from the first highlight
}
