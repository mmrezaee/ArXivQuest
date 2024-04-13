
from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from flask_cors import CORS
from nltk.tokenize import sent_tokenize
from utils import correct_images_src,extract_content, extract_table
from llm_qa import find_answer
import json

app = Flask(__name__)
CORS(app)

# Route to serve the index.html page
@app.route('/')
def home():
    return render_template('index.html')

def replace_with_highlight(element,candid):
    if isinstance(element, NavigableString) and candid in element:
        modified_text = element.replace(candid, f'<span style="background-color: yellow;">{candid}</span>')
        new_soup = BeautifulSoup(modified_text, 'html.parser')
        element.replace_with(new_soup)
    elif isinstance(element, Tag):
        for content in element.contents:
            replace_with_highlight(content,candid)


# Route to fetch content from a URL and highlight the specified sentence
@app.route('/fetch_content', methods=['POST'])
def fetch_content():
    data = request.get_json()
    #url = data['url']
    question = data.get('question', '')
    url = 'https://arxiv.org/html/2404.05567v1'
    #question = 'what does Subfigure (a) show?'
    #question = None
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    correct_images_src(url,soup)
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
    logs_dict = find_answer(doc_texts_list, 
                            question,
                            doc_name,
                            use_cache = True,
                            write_log = False)

    #print(f'logs_dict is {logs_dict}')
    results = logs_dict[0]['results']
    selected_answers = set([item['text'] for item in results if len(item)>1])
    selected_answers = list(selected_answers)
    for candid in selected_answers: 
        print(f'candid: {candid}')
        try: 
            print(f'replacing with {candid}')
            replace_with_highlight(soup,candid)
            print(f'replacing with {candid} done!!!')
            print('+'*50)
        except:
            print('couldnt replace with {candid}')

    #print(json.dumps(results_list,indent=4))
    '''
    for index,sent in enumerate(splited_sents):
        print(f'{index}- {sent}')
    '''
    #print('https://arxiv.org/html/2404.05567v1')

    #if question:
    #    print(f'selected_answers: {selected_answers}')
    #    replace_with_highlight(soup,selected_answers)

    return jsonify({"content": str(soup)})

if __name__ == '__main__':
    app.run(debug=True)
