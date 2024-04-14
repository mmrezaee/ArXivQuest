from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from flask_cors import CORS
from nltk.tokenize import sent_tokenize
from utils import correct_images_src,extract_content, extract_table
from nltk.tokenize import sent_tokenize
from llm_qa import find_answer
import json
from fuzzywuzzy import fuzz

app = Flask(__name__)
CORS(app)

# Route to serve the index.html page
@app.route('/')
def home():
    return render_template('index.html')

debug_candid = 'first, some biases and pressures seem to be present naturally, or universally, among different learning systems, including deep learning agents.'
def debug_writing_tables(doc_name):
    from utils import all_tables
    #print(f'all_tables: {all_tables}')
    with open('./{doc_name}_temp_tables.txt','w') as file:
        for index,table in enumerate(all_tables):
            table_index = index+1
            file.write('\n')
            file.write('\n')
            file.write(f'index is {table_index}: ')
            file.write('\n')
            file.write(table)
            file.write('\n')
            file.write('*'*50)
            print(table)
            print('*'*50)

def replace_with_highlight(element, candid, similarity_threshold=80):
    if isinstance(element, NavigableString):
        # Check similarity between the candidate text and the element'stext
        element_clean = element.text.strip().lower()
        element_senteces = sent_tokenize(element_clean)
        #if candid == debug_candid:
        #    print(f'str(element): {str(element).lower()}, ratio: {fuzz.ratio(candid, str(element))}')
        ##    print(f'element_senteces: {element_senteces}')
        #    print('+'*50)
#
        for sentence in element_senteces:
            if fuzz.ratio(candid, sentence) > similarity_threshold:
                # Highlight the whole text block since it's similar to the candidate
                #modified_text = f'<span style="background-color: yellow;">{str(sentence)}</span>'

                #print(f'sentence: {sentence}')
                modified_text = str(element).lower().replace(sentence, f'<span style="background-color: yellow;">{sentence}</span>')
                #print(f'modified_text: {modified_text}')
                #print('*'*50)
                new_soup = BeautifulSoup(modified_text, 'html.parser')
                element.replace_with(new_soup)

    elif isinstance(element, Tag):
        # Recursively apply this function to all contents of a tag if it's not a string
        for content in element.contents:
            replace_with_highlight(content, candid, similarity_threshold)


# Route to fetch content from a URL and highlight the specified sentence
@app.route('/fetch_content', methods=['POST'])
def fetch_content():
    data = request.get_json()
    url = data['url']
    question = data.get('question', '')
    index_type = data.get('index_type', '')
    metric_type = data.get('metric_type', '')
    top_k = int(data.get('top_k', 10))
    #llm_model = 'all-mpnet-base-v2'
    model_name = data.get('model_name', ' ')

    print(f'url: {url}')
    print(f'model_name: {model_name}')
    print(f'question: {question}')
    print(f'index_type: {index_type}')
    print(f'metric_type: {metric_type}')
    print(f'top_k: {top_k}')
    #url = 'https://arxiv.org/html/2404.05567v1'
    #question = 'what does Subfigure (a) show?'
    #question = None
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    #print(f'soup: {soup}')
    correct_images_src(url,soup)
    if not question:
        return jsonify({"content": str(soup)})
    doc_name = url.split('/')[-1]
    content = extract_content(soup.find('body'))
    #print(f'content: {content}')
    doc_texts_list = content.split('<sent>')
    #print(f'doc_texts_list: {doc_texts_list}')
    #debug_writing_tables(doc_name)
    #exit()
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
                            model_name=model_name,
                            top_k = top_k,
                            index_type = index_type,
                            metric_type = metric_type,
                            use_cache = True,
                            write_log = False)

    #print(f'logs_dict is {logs_dict}')
    results = logs_dict[0]['results']
    selected_answers = []
    highlight_sentences = []
    seen = set()
    #counter = 1
    for item in results:
        if item['text'] not in seen and len(item['text'])>1:
            #selected_answers.append(' '.join([str(counter),'- ',item['text'],'score: '+str(item['score']),'\n']))
            seen.add(item['text'])
            selected_answers.append((item['text'],item['score']))
            #highlight_sentences.append(item['text'])
            #counter +=1 
    #selected_answers = set([item['text'] for item in results if len(item)>1])
    #selected_answers = list(selected_answers)
    selected_answers.sort(key=lambda x: x[1])
    highlight_sentences = [item[0] for item in selected_answers]
    for candid in highlight_sentences: 
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

    #box_answers = [str(counter+1)+'- '+item[0]+' score: '+str(item[1]) for counter,item in enumerate(selected_answers)]
    box_answers = [str(counter//2+1)+'- '+selected_answers[counter//2][0]+' score: '+str(selected_answers[counter//2][1]) if counter%2==0 else " " for counter in range(2*len(selected_answers))]
    return jsonify({"content": str(soup), "answers": box_answers})

if __name__ == '__main__':
    app.run(debug=True)
