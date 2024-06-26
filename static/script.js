function loadContent() {
    var urlInput = document.getElementById('url-box');
    var questionBox = document.getElementById('question-box');
    var answersContainer = document.getElementById('answers-container'); 

    var topKBox = document.getElementById('top-k-box');
    var indexTypesContainer = document.getElementById('index-types'); 
    var metricTypesContainer = document.getElementById('metric-types'); 
    var modelTypesContainer = document.getElementById('model-names'); 

    //if (!urlInput || !questionBox) {
    //    console.error("Question box element is not found!");
    //    return;
   // }

    var question = questionBox.value;
    var url = urlInput.value;
    var top_k = topKBox.value;
    var metric_type = metricTypesContainer.value;
    var index_type = indexTypesContainer.value;
    var model_name = modelTypesContainer.value;

    // Construct the data object
    const data = {
        url: url,
        question: question,
        metric_type: metric_type,
        index_type: index_type,
        top_k: top_k,
        model_name: model_name
    };

    //console.log(url);
    //console.log(top_k);
    //console.log(metric_type);
    //console.log(index_type);

    fetch('/fetch_content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
        //body: JSON.stringify({url: url, question: question, metric_type: metric_type, index_type: index_type, top_k: top_k, model_name: model_name})
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
            updateAnswersContainer(data.answers, answersContainer);
        } else {
            answersContainer.innerHTML = 'No answers found';  // Display no answers message
        }
    })
    .catch(error => {
        console.error('Error loading content:', error);
        alert('Failed to load content');
    });
}

function updateAnswersContainer(answers, container) {
    container.innerHTML = '';  // Clear previous answers
    answers.forEach(answer => {
        var answerElement = document.createElement('div');
        let words = answer.split(' ');
        if (words.length > 0) {
            let firstWordSpan = document.createElement('span');
            firstWordSpan.style.fontWeight = 'bold';
            firstWordSpan.textContent = words[0] + ' ';
            answerElement.appendChild(firstWordSpan);
            answerElement.appendChild(document.createTextNode(words.slice(1).join(' ')));
        } else {
            answerElement.textContent = answer;
        }
        container.appendChild(answerElement);
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
