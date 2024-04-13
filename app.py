
from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from flask_cors import CORS
from nltk.tokenize import sent_tokenize
from utils import extract_content, extract_table
from llm_qa import find_answer
import json

app = Flask(__name__)
CORS(app)

# Route to serve the index.html page
@app.route('/')
def home():
    return render_template('index.html')


def replace_with_highlight(element,answer):

    if isinstance(element, NavigableString) and answer in element:
        modified_text = element.replace(answer, f'<span style="background-color: yellow;">{answer}</span>')
        new_soup = BeautifulSoup(modified_text, 'html.parser')
        element.replace_with(new_soup)
    elif isinstance(element, Tag):
        for content in element.contents:
            replace_with_highlight(content,answer)

# Route to fetch content from a URL and highlight the specified sentence
@app.route('/fetch_content', methods=['POST'])
def fetch_content():
    data = request.get_json()
    #url = data['url']
    question = data.get('question', '')
    url = 'https://arxiv.org/html/2404.05567v1'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    if not question:
        return jsonify({"content": str(soup)})
    doc_name = url.split('/')[-1]
    content = extract_content(soup.find('body'))
    doc_texts_list = content.split('<sent>')
    print(f'url: {url}')
    print(f'gathering content from {url}')
    print(f'question: {question}')
    print(f'some of sentences are ')
    print(f'doc_name is {doc_name}')
    samples = doc_texts_list[:10]
    for sample in samples:
        print(sample)
    results_list= find_answer(doc_texts_list,
                              question,
                              doc_name,
                              write_log=False)

    print(json.dumps(results_list,indent=4))
    '''
    for index,sent in enumerate(splited_sents):
        print(f'{index}- {sent}')
    '''
    #print('https://arxiv.org/html/2404.05567v1')

    if question:
        replace_with_highlight(soup,results_list)

    return jsonify({"content": str(soup)})

if __name__ == '__main__':
    app.run(debug=True)
