from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from flask_cors import CORS
from nltk.tokenize import sent_tokenize
from utils import correct_images_src,extract_content, extract_table_as_string
from nltk.tokenize import sent_tokenize
from llm_qa import find_answer
import json
from fuzzywuzzy import fuzz
import re

# Initialize Flask application and enable CORS
app = Flask(__name__)
CORS(app)

# Route to serve the index.html page
@app.route('/')
def home():
    """Serve the index.html as the home page."""
    return render_template('index.html')

def correct_paper_address(url):
    """
    Corrects the paper URL if it is not in HTML format.
    This function supports URL formats from the 'abs', 'html', and 'pdf' pages of arXiv.
    It ensures the URL points to the HTML version of the document.
    """
    page_type = url.split('arxiv.org/')[1].split('/')[0]
    if page_type != 'html': 
        url = url.replace('.pdf','').replace('abs','html').replace('pdf','html')
        url += 'v1'
    return url


def replace_with_highlight(element, candid, similarity_threshold=80):
    """Highlight text within the element that matches the candidate text, based on a similarity threshold."""
    if isinstance(element, NavigableString):
        # Check similarity between the candidate text and the element'stext
        element_clean = element.text.strip().lower()
        element_senteces = sent_tokenize(element_clean)
        for sentence in element_senteces:
            if fuzz.ratio(candid, sentence) > similarity_threshold:
                # Highlight the whole text block since it's similar to the candidate
                modified_text = str(element).lower().replace(sentence, f'<span style="background-color: yellow;">{sentence}</span>')
                new_soup = BeautifulSoup(modified_text, 'html.parser')
                element.replace_with(new_soup)

    elif isinstance(element, Tag):
        # Recursively apply this function to all contents of a tag if it's not a string
        for content in element.contents:
            replace_with_highlight(content, candid, similarity_threshold)


# Route to fetch content from a URL and highlight the specified sentence
@app.route('/fetch_content', methods=['POST'])
def fetch_content():
    """Fetch and process content from the specified URL, and respond to queries provided in the request."""
    # Extract details from the request
    data = request.get_json()
    url = data['url']
    print(f'input url: {url}')
    url = correct_paper_address(url)
    print(f'correct url: {url}')
    question = data.get('question', '')
    index_type = data.get('index_type', '')
    metric_type = data.get('metric_type', '')
    if data.get('top_k'): 
        top_k = int(data.get('top_k'))
    else:
        top_k = 10
    model_name = data.get('model_name', ' ')

    # Fetch the webpage content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Correct image paths in the HTML
    correct_images_src(url,soup)

    if not question:
        # If no question is asked, return the raw content
        return jsonify({"content": str(soup)})

    # Extract and clean the text content from the HTML
    doc_name = url.split('/')[-1]
    content = extract_content(soup.find('body'))
    doc_texts_list = content.split('<sent>')

    # Process the query using the specified language model
    logs_dict = find_answer(doc_texts_list, 
                            question,
                            doc_name,
                            model_name=model_name,
                            top_k = top_k,
                            index_type = index_type,
                            metric_type = metric_type,
                            use_cache = True,
                            write_log = False)

    # Process the query using the specified language model
    results = logs_dict[0]['results']
    selected_answers = []
    highlight_sentences = []
    seen = set()
    for item in results:
        if item['text'] not in seen and len(item['text'])>1:
            seen.add(item['text'])
            selected_answers.append((item['text'],item['score']))
    selected_answers.sort(key=lambda x: x[1])
    highlight_sentences = [item[0] for item in selected_answers]
    for candid in highlight_sentences: 
        try: 
            replace_with_highlight(soup,candid)
        except:
            print('couldnt replace with {candid}')

    # Prepare a list of answers for display
    box_answers = [str(counter//2+1)+'- '+selected_answers[counter//2][0]+' score: '+str(selected_answers[counter//2][1]) if counter%2==0 else " " for counter in range(2*len(selected_answers))]
    return jsonify({"content": str(soup), "answers": box_answers})

if __name__ == '__main__':
    app.run(debug=True)
