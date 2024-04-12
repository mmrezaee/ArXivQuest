let currentHighlight = 0; // Index of the current highlighted element
let highlights = []; // Array to store references to highlighted elements

function loadContent() {
    var url = document.getElementById('url-input').value;
    var sentence = document.getElementById('question-box').value;
    fetch('/fetch_content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({url: url, sentence: sentence})
    })
    .then(response => response.json())
    .then(data => {
        var iframe = document.getElementById('content-frame');
        iframe.srcdoc = data.content;

        // Wait for iframe to load then initialize highlights
        iframe.onload = () => initializeHighlights(iframe);
    })
    .catch(error => {
        console.error('Error loading content:', error);
        alert('Failed to load content');
    });
}

function initializeHighlights(iframe) {
    highlights = Array.from(iframe.contentWindow.document.querySelectorAll('span[style*="background-color: yellow;"]'));
    currentHighlight = 0; // Reset index
}

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

