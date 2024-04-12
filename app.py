from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

app = Flask(__name__)
'''
def extract_table(table):
    headers = [th.text.strip() for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr'):
        cells = [td.text.strip() for td in tr.find_all(['td', 'th'])]
        rows.append(cells)
    return '\n'.join([' | '.join(headers)] + [' | '.join(row) for row in rows])
'''

# Route to serve the index.html page
@app.route('/')
def home():
    return render_template('index.html')

# Route to fetch content from a URL and highlight the abstract
@app.route('/fetch_content', methods=['POST'])
def fetch_content():
    #url = request.json['url']
    url = "https://arxiv.org/html/2404.05567v1"
    sentence = request.json['sentence']
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    #print(f'soup: {soup}')
    #print('this was before replace')

    def replace_with_highlight(element):
        if isinstance(element, NavigableString):
            print('isinstance is NavigableString')
            if sentence in element:
                modified_text = str(element).replace(sentence, f'<span style="background-color: yellow;">{sentence}</span>')
                new_soup = BeautifulSoup(modified_text, 'html.parser')
                element.replace_with(new_soup)
        elif isinstance(element, Tag):  # Ensure element is a Tag before accessing contents
            print('isinstance is NavigableString')
            for content in element.contents:
                replace_with_highlight(content)

    replace_with_highlight(soup)
    print(soup)
    print('soup after highlight: ')
    print('*'*50)

    return jsonify({"content": str(soup)})
def old_fetch_content():
    url = request.json['url']
    sentence_to_find = request.json['sentence']
    response = requests.get(url)
    
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the sentence within the HTML content
    sentence_found = None
    for element in soup.find_all(text=True):
        if sentence_to_find in element:
            sentence_found = element
            break

    if sentence_found:
        # Apply a yellow background to the sentence for highlighting
        parent_tag = sentence_found.parent
        if isinstance(parent_tag, Tag):
            parent_tag['style'] = 'background-color: yellow;'
    else:
        return jsonify({"message": "Sentence not found"})

    # Convert the soup object back to a string
    modified_html = str(soup)
    return jsonify({"content": modified_html})
if __name__ == '__main__':
    print('hellooooooo')
    app.run(debug=True)
